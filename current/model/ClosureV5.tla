----------------------------- MODULE ClosureV5 -----------------------------
(* G5/2 finite abstraction: a declared complete P per window; durable full body
   registration, lock, two role prepare/receipt, authority commit, native apply,
   immutable complete reservation and first send. Crash drops volatile install
   caches only; durable rows and captured observations survive. StartFrozen is
   an explicitly post-commit fixture, never evidence for those skipped actions.
   Two-window fixture retains history/head across partial abort and resets only
   per-window quota. No cryptographic or implementation-refinement claim. *)
EXTENDS Naturals, FiniteSets, TLC

CONSTANTS Reports, Users, Owner, Pred, Bit, Eligible, NativeMin,
          StartFrozen, AllowDeadline, AllowManual, Fault, Planned, Window, MaxWindow

Roles == {"leader", "helper"}
Processes == Roles \cup {"authority"}
Genesis == "genesis"
(* The empty token is the "no share captured / no snapshot" sentinel. It is a
   record so that token equality never mixes record and string sorts; the selector
   is 0, which no real reservation ever produces (d \in {1,2}). *)
None == [members |-> {}, counts |-> [r \in {} |-> 0],
         bodies |-> [r \in {} |-> 0], selector |-> 0,
         heads |-> [u \in Users |-> Genesis], quotas |-> [u \in Users |-> 0],
         p |-> {}, r |-> {}, window |-> 0]
EligibleIn(L) == {r \in L : Eligible[r]}
Pairs(L) == L \X Roles

VARIABLE st
vars == <<st>>

(* -------- P / R / L / A / M relations ---------------------------------- *)
(* P = complete finite single-chain registration graph (st.reg).
   L = P frozen at lock (st.lockLog).  R = eligible(L) = EligibleIn(st.lockLog).
   warmup records stay in P/L only; eligible zeros stay in R/A/M.
   M(s) = merged eligible outputs at role s (the applied projection). *)
Pset == Planned[st.window]
Current(S) == {r \in S : Window[r] = st.window}
Rset == EligibleIn(st.lockLog)
M(s) == st.merged[s]
Q(u) == Cardinality({r \in st.committed : Owner[r] = u /\ Window[r] = st.window /\ Eligible[r] /\ Bit[r] = 1})
RReady == st.locked /\ ~st.abort /\ Cardinality(Rset) >= NativeMin

EmptyToken == [members |-> {}, counts |-> [r \in {} |-> 0],
               bodies |-> [r \in {} |-> 0], selector |-> 0,
         heads |-> [u \in Users |-> Genesis], quotas |-> [u \in Users |-> 0],
         p |-> {}, r |-> {}, window |-> 0]
EmptyCache == [present |-> FALSE, durable |-> FALSE, token |-> EmptyToken]

ASSUME /\ Reports # {} /\ Users # {}
       /\ Owner \in [Reports -> Users]
       /\ Pred \in [Reports -> Reports \cup {Genesis}]
       /\ Bit \in [Reports -> 0..1]
       /\ Eligible \in [Reports -> BOOLEAN]
       /\ NativeMin \in 1..Cardinality(Reports)
       /\ StartFrozen \in BOOLEAN /\ AllowDeadline \in BOOLEAN
       /\ AllowManual \in BOOLEAN
       /\ Fault \in {"none", "head", "quota", "exact", "once", "freeze",
                     "outbox", "binding", "dispatch", "durable", "cache",
                     "lock", "journal", "snapshot", "abort", "fullp", "fullr"}

Init ==
  LET L == IF StartFrozen THEN Planned[1] ELSE {}
  IN st = [window |-> 1, reg |-> L,
           anchor |-> [u \in Users |-> Genesis], continued |-> FALSE,
           abortCommitted |-> {},
           receipts |-> [s \in Roles |-> L],
           volatile |-> [s \in Roles |-> {}],
           locked |-> StartFrozen, lockLog |-> L,
           installed |-> [s \in Roles |-> L],
           journal |-> [s \in Roles |-> L],
           redo |-> [s \in Roles |-> FALSE],
           conflictSeen |-> [s \in Roles |-> FALSE],
           committed |-> L,
           head |-> [u \in Users |-> IF StartFrozen
                     THEN CHOOSE r \in L : Owner[r] = u ELSE Genesis],
           quota |-> [u \in Users |-> Cardinality(
                       {r \in L : Owner[r] = u /\ Window[r] = 1 /\ Eligible[r] /\ Bit[r] = 1})],
           boxes |-> Pairs(L), acked |-> {},
           delivered |-> [s \in Roles |-> {}],
           merged |-> [s \in Roles |-> {}],
           dup |-> [s \in Roles |-> FALSE],
           badOutput |-> [s \in Roles |-> FALSE],
           cache |-> [s \in Roles |-> EmptyCache],
           sent |-> [s \in Roles |-> None],
           backed |-> [s \in Roles |-> None],
           up |-> Processes, expired |-> FALSE, manual |-> FALSE,
           refused |-> {}, retried |-> {},
           abort |-> FALSE, abortH |-> [u \in Users |-> Genesis],
           abortQ |-> [u \in Users |-> 0],
           failed |-> FALSE, sawShare |-> FALSE, collected |-> FALSE,
           crashSeen |-> {}, recovered |-> {}]

(* -------- registration graph (P) --------------------------------------- *)
(* Complete signed body is durably verified and PendingCert issued; this extends
   P and must not move head or quota. Late registration after lock is rejected. *)
Register(r) ==
  /\ "authority" \in st.up
  /\ r \in Pset /\ r \notin st.reg
  /\ ~st.abort
  /\ Pred[r] = Genesis \/ Pred[r] \in st.reg \/ Pred[r] \in st.committed
  /\ (Fault = "freeze" \/ ~st.locked)
  /\ st' = [st EXCEPT !.reg = @ \cup {r}]

(* At the registration boundary the complete P and its eligible projection R are
   frozen and LockCert issued. A releasable cohort must meet the native minimum. *)
Lock ==
  /\ "authority" \in st.up
  /\ ~st.abort /\ ~st.locked
  /\ Cardinality(EligibleIn(st.reg)) >= NativeMin
  /\ (Fault = "fullp" \/ Fault = "freeze" \/ st.reg = Pset)
  /\ st' = [st EXCEPT !.locked = TRUE, !.lockLog = st.reg]

(* Authority-direct control plane persists the complete SignedBody + LockCert at
   each role. Installation proves durable presence, not Prio validity. *)
Install(s) ==
  /\ s \in st.up /\ st.locked
  /\ st.installed[s] # st.lockLog
  /\ st' = [st EXCEPT !.installed[s] = st.lockLog]

(* Private HPKE/sidecar/native preparation. Requires the lock (lock-before-prepare)
   and a real predecessor or K-anchor commit (ProcessPermit). The first peer input
   digest, transition, verdict and response are persisted atomically in the unique
   journal before anything is sent. *)
Prepare(s, r) ==
  /\ s \in st.up /\ ~st.abort
  /\ (~st.expired \/ st.manual)
  /\ (Fault = "lock" \/ (st.locked /\ r \in st.installed[s]))
  /\ r \in st.reg
  /\ (Pred[r] = Genesis \/ Pred[r] \in st.committed)
  /\ (Fault = "journal" \/ r \notin st.journal[s])
  /\ st' = [st EXCEPT !.journal[s] = @ \cup {r},
                  !.volatile[s] = @ \cup {r},
                  !.redo[s] = IF Fault = "journal" /\ r \in st.journal[s]
                              THEN TRUE ELSE @]

(* A signed native receipt requires the actual durable prepare journal row. *)
Receipt(s, r) ==
  /\ s \in st.up /\ ~st.abort /\ r \in Current(st.journal[s])
  /\ r \notin st.receipts[s]
  /\ st' = [st EXCEPT !.receipts[s] = @ \cup {r}]

(* A changed peer input for the same journal key is a public byte conflict: it is
   refused without recomputing the secret verdict and without replaying the old
   success to the new input. *)
PrepConflict(s, r) ==
  /\ s \in st.up /\ r \in st.journal[s]
  /\ st' = [st EXCEPT !.conflictSeen[s] = TRUE]

(* -------- authority commit (head / quota / history / outbox) ----------- *)
Commit(r) ==
  /\ "authority" \in st.up /\ ~st.abort
  /\ r \in st.reg /\ r \notin st.committed
  /\ \A s \in Roles : r \in st.receipts[s]
  /\ Pred[r] = Genesis \/ Pred[r] \in st.committed
  /\ (Fault = "freeze" \/ st.locked)
  /\ (Fault = "head" \/ st.head[Owner[r]] = Pred[r])
  /\ (Fault = "quota" \/
        st.quota[Owner[r]] + Bit[r] * (IF Eligible[r] THEN 1 ELSE 0) <= 1)
  /\ st' = [st EXCEPT !.committed = @ \cup {r}, !.head[Owner[r]] = r,
              !.quota[Owner[r]] = @ + Bit[r] * (IF Eligible[r] THEN 1 ELSE 0),
              !.boxes = IF Fault = "outbox" THEN @ ELSE @ \cup Pairs({r})]

(* -------- native apply -------------------------------------------------- *)
(* The role applies the committed, uniquely retained output exactly once; warmup
   is delivered but does not merge; the wrong-session mutant maps a wrong body. *)
Apply(s, r) ==
  /\ s \in st.up /\ ~st.abort
  /\ (~st.expired \/ st.manual)
  /\ r \in Current(st.committed) /\ r \in st.journal[s]
  /\ (Fault = "once" \/
        (r \notin st.delivered[s] /\ r \notin st.merged[s]))
  /\ st' = [st EXCEPT
              !.delivered[s] = @ \cup {r},
              !.merged[s] = IF Eligible[r] THEN @ \cup {r} ELSE @,
              !.dup[s] = IF Fault = "once" /\ Eligible[r] /\
                            (r \in st.delivered[s] \/ r \in st.merged[s])
                         THEN TRUE ELSE @,
              !.badOutput[s] = IF Fault = "binding" /\ Eligible[r] THEN TRUE ELSE @]

Ack(s, r) ==
  /\ "authority" \in st.up /\ r \in st.delivered[s]
  /\ <<r, s>> \in st.boxes \ st.acked
  /\ st' = [st EXCEPT !.acked = @ \cup {<<r, s>>}]

(* -------- complete snapshot reservation (L=P, A=R, M_S=R) -------------- *)
Snapshot(s, d) == [members |-> M(s),
                   counts |-> [r \in M(s) |-> 1],
                   bodies |-> [r \in M(s) |-> 0], selector |-> d,
                   heads |-> st.head, quotas |-> st.quota,
                   p |-> st.lockLog, r |-> Rset, window |-> st.window]

Reserve(s, d) ==
  /\ s \in st.up /\ ~st.abort
  /\ st.locked /\ st.installed[s] = st.lockLog
  /\ ~st.cache[s].present
  /\ (~st.expired \/ st.manual)
  /\ st.lockLog \subseteq st.committed
  /\ Cardinality(M(s)) >= NativeMin
  /\ (Fault = "dispatch" \/ d = 1)
  /\ (Fault = "exact" \/ Fault = "fullr" \/ M(s) = Rset)
  /\ (Fault = "fullp" \/ st.lockLog = Pset)
  /\ LET token == Snapshot(s, d)
     IN st' = [st EXCEPT !.cache[s] = [present |-> TRUE, token |-> token,
                                       durable |-> Fault # "durable"],
                         !.backed[s] = IF Fault = "durable" THEN @ ELSE token]

(* Native count/checksum refusal occurs after reservation; the durable snapshot
   survives and no observation has taken place. *)
RejectCount(s) ==
  /\ s \in st.up /\ st.cache[s].present /\ s \notin st.refused
  /\ st' = [st EXCEPT !.refused = @ \cup {s}]

(* First decryptable honest share is captured. It is sent only from the reserved
   complete snapshot; the journal must already hold every applied member. The
   snapshot mutant sends without a prior reservation. *)
Send(s) ==
  \/ /\ s \in st.up /\ ~st.abort /\ st.cache[s].present
     /\ (~st.expired \/ st.manual \/ st.sent[s] # None)
     /\ M(s) \subseteq st.journal[s]
     /\ st' = [st EXCEPT !.sent[s] = st.cache[s].token, !.sawShare = TRUE]
  \/ /\ s \in st.up /\ ~st.abort /\ Fault = "snapshot"
     /\ st' = [st EXCEPT !.sent[s] = Snapshot(s, 1), !.sawShare = TRUE]

Retry(s) ==
  /\ s \in st.up /\ st.cache[s].present /\ st.sent[s] # None
  /\ st' = [st EXCEPT !.sent[s] = st.cache[s].token, !.retried = @ \cup {s}]

Collect ==
  /\ \A s \in Roles : st.sent[s] # None
  /\ ~st.collected
  /\ st' = [st EXCEPT !.collected = TRUE]

(* -------- terminal states ---------------------------------------------- *)
(* PRE_EXPOSURE_ABORT before any honest share: committed head/quota are retained,
   not rolled back, and the terminal lock can never be exported again. *)
Abort ==
  /\ "authority" \in st.up
  /\ ~st.sawShare /\ ~st.abort
  /\ st' = [st EXCEPT !.abort = TRUE, !.abortH = st.head, !.abortQ = st.quota,
                      !.abortCommitted = st.committed,
                      !.head = IF Fault = "abort" THEN [u \in Users |-> Genesis]
                              ELSE st.head]

(* EXPOSED_COLLECTION_FAILED: an honest share was delivered but collection failed;
   the exposure cannot be relabelled as zero.-only the same snapshot may retry. *)
SettleFail ==
  /\ st.sawShare /\ ~st.collected /\ ~st.failed
  /\ st' = [st EXCEPT !.failed = TRUE]

Crash(p) ==
  /\ p \in st.up
  /\ st' = IF p = "authority" THEN [st EXCEPT !.up = @ \ {p}]
           ELSE [st EXCEPT !.up = @ \ {p}, !.volatile[p] = {},
                  !.cache[p] = IF Fault = "cache" THEN EmptyCache
                              ELSE IF @.durable THEN @ ELSE EmptyCache,
                  !.crashSeen = IF st.sent[p] # None THEN @ \cup {p} ELSE @]

Recover(p) ==
  /\ p \notin st.up
  /\ st' = [st EXCEPT !.up = @ \cup {p},
              !.recovered = IF p \in st.crashSeen THEN @ \cup {p} ELSE @]

Expire == /\ AllowDeadline /\ ~st.expired /\ st' = [st EXCEPT !.expired = TRUE]
Resume == /\ AllowManual /\ st.expired /\ ~st.manual /\ st' = [st EXCEPT !.manual = TRUE]

(* Abort is a terminal window outcome. A fresh window is permitted only from
   actual retained heads; no uncommitted predecessor may become an anchor. *)
Advance ==
  /\ "authority" \in st.up
  /\ st.abort /\ st.window < MaxWindow
  /\ st.committed # {} /\ Current(st.committed) # Pset
  /\ \A r \in Planned[st.window + 1] : Pred[r] = st.head[Owner[r]]
  /\ st' = [st EXCEPT !.window = @ + 1, !.reg = {}, !.locked = FALSE,
        !.lockLog = {}, !.installed = [s \in Roles |-> {}],
        !.quota = [u \in Users |-> 0], !.anchor = st.head,
        !.continued = TRUE, !.abort = FALSE,
        !.merged = [s \in Roles |-> {}], !.delivered = [s \in Roles |-> {}],
        !.cache = [s \in Roles |-> EmptyCache], !.sent = [s \in Roles |-> None],
        !.backed = [s \in Roles |-> None], !.sawShare = FALSE,
        !.failed = FALSE, !.collected = FALSE, !.expired = FALSE, !.manual = FALSE,
        !.retried = {}, !.refused = {}]

Next == \/ \E r \in Reports : Commit(r)
        \/ Lock \/ SettleFail \/ Abort \/ Advance
        \/ \E s \in Roles : Install(s) \/ RejectCount(s) \/ Send(s) \/ Retry(s)
                            \/ (\E d \in {1, 2} : Reserve(s, d))
                            \/ (\E r \in Reports :
                                 Register(r) \/ Prepare(s, r) \/ Receipt(s, r)
                                 \/ PrepConflict(s, r) \/ Apply(s, r) \/ Ack(s, r))
        \/ \E p \in Processes : Crash(p) \/ Recover(p)
        \/ Expire \/ Resume \/ Collect

Spec == Init /\ [][Next]_vars
ReserveAny(s) == \E d \in {1, 2} : Reserve(s, d)
FairSpec == Spec
  /\ WF_vars(Lock)
  /\ (\A r \in Reports : WF_vars(Register(r)))
  /\ (\A r \in Reports : WF_vars(Commit(r)))
  /\ (\A p \in Processes : WF_vars(Recover(p)))
  /\ (\A s \in Roles : WF_vars(Install(s)) /\ WF_vars(ReserveAny(s))
                        /\ WF_vars(Send(s))
                        /\ (\A r \in Reports : WF_vars(Prepare(s, r))
                                              /\ WF_vars(Receipt(s, r))
                                              /\ WF_vars(Apply(s, r))
                                              /\ WF_vars(Ack(s, r))))
  /\ WF_vars(Collect)

(* -------- type bounds --------------------------------------------------- *)
TypeOK ==
  /\ st.window \in 1..MaxWindow
  /\ st.reg \subseteq Reports /\ st.lockLog \subseteq Reports
  /\ st.locked \in BOOLEAN
  /\ st.committed \subseteq Reports
  /\ st.head \in [Users -> Reports \cup {Genesis}]
  /\ st.quota \in [Users -> 0..Cardinality(Reports)]
  /\ st.boxes \subseteq Pairs(Reports) /\ st.acked \subseteq st.boxes
  /\ st.installed \in [Roles -> SUBSET Reports]
  /\ st.journal \in [Roles -> SUBSET Reports]
  /\ st.redo \in [Roles -> BOOLEAN]
  /\ st.conflictSeen \in [Roles -> BOOLEAN]
  /\ st.delivered \in [Roles -> SUBSET Reports]
  /\ st.merged \in [Roles -> SUBSET Reports]
  /\ st.dup \in [Roles -> BOOLEAN]
  /\ st.badOutput \in [Roles -> BOOLEAN]
  /\ st.up \subseteq Processes
  /\ st.refused \subseteq Roles /\ st.retried \subseteq Roles
  /\ st.crashSeen \subseteq Roles /\ st.recovered \subseteq Roles
  /\ st.expired \in BOOLEAN /\ st.manual \in BOOLEAN
  /\ st.abort \in BOOLEAN /\ st.failed \in BOOLEAN
  /\ st.sawShare \in BOOLEAN /\ st.collected \in BOOLEAN
  /\ st.abortH \in [Users -> Reports \cup {Genesis}]
  /\ st.abortQ \in [Users -> 0..Cardinality(Reports)]

(* -------- safety invariants (migrated E4 + new G5) --------------------- *)
UniqueSuccessor == \A r, t \in st.committed :
  (Owner[r] = Owner[t] /\ Pred[r] = Pred[t]) => r = t
QuotaBound == \A u \in Users : st.quota[u] <= 1
QuotaAccounting == \A u \in Users : st.quota[u] = Q(u)
OutboxAtomic == st.boxes = Pairs(st.committed)
ExactlyOnce == \A s \in Roles : ~st.dup[s]
WarmupExcluded == \A s \in Roles : M(s) \subseteq EligibleIn(Current(st.committed))
AppliedOutputBound == \A s \in Roles : ~st.badOutput[s]
FrozenHistoryClosed == st.locked => st.reg = st.lockLog

(* NEW: lock-before-prepare. *)
LockBeforePrepare == \A s \in Roles :
  Current(st.journal[s]) \subseteq st.installed[s] /\ (Current(st.journal[s]) # {} => st.locked)

(* NEW: unique journal. At most one secret-relevant transition per journal key;
   every applied member was journaled at that role. *)
JournalUnique == \A s \in Roles : ~st.redo[s] /\ M(s) \subseteq st.journal[s]

FirstExposureExact == \A s \in Roles :
  st.sent[s] = None \/ (st.locked /\ st.sent[s].members = Rset)

(* NEW: complete snapshot. A share is sent only from a snapshot durably reserved
   at that role beforehand. *)
SnapshotReserved == \A s \in Roles :
  st.sent[s] = None \/ (st.cache[s].present /\ st.cache[s].token = st.sent[s])

DispatchBound == \A s \in Roles :
  st.sent[s] = None \/ st.sent[s].selector = 1
DurableBeforeSend == \A s \in Roles :
  st.sent[s] = None \/ st.backed[s] = st.sent[s]
RetryStable == \A s \in Roles :
  st.sent[s] = None \/ (st.cache[s].present /\ st.cache[s].token = st.sent[s]
                        /\ st.cache[s].durable)
ReservationSafe == \A s \in Roles :
  ~st.cache[s].present \/ (st.cache[s].durable /\ st.cache[s].token.members = Rset)

(* NEW: a partial abort preserves committed head and quota (no rollback). *)
AbortPreservesHeadQuota == st.abort =>
  (st.head = st.abortH /\ st.quota = st.abortQ /\ st.committed = st.abortCommitted)

FullP == st.locked => st.lockLog = Pset /\ st.reg = Pset
FullR == \A s \in Roles : ~st.cache[s].present \/ st.cache[s].token.members = EligibleIn(Pset)
CommitHasReceipts == \A r \in st.committed : \A s \in Roles : r \in st.receipts[s]
BodyDurable == \A s \in Roles : Current(st.journal[s]) \subseteq st.reg
SnapshotImmutable == \A s \in Roles : ~st.cache[s].present \/ st.cache[s].token = st.backed[s]
NextWindowHead == st.continued => (\A r \in Current(st.committed) : Pred[r] = st.anchor[Owner[r]])
FailureClass == (st.abort => ~st.sawShare) /\ (st.failed => st.sawShare)

FullSnapshot == \A s \in Roles : ~st.cache[s].present \/
  (st.cache[s].token.p = Pset /\ st.cache[s].token.r = Rset /\
   st.cache[s].token.window = st.window /\
   st.cache[s].token.heads = st.head /\ st.cache[s].token.quotas = st.quota /\
   st.cache[s].token.counts = [r \in st.cache[s].token.members |-> 1] /\
   st.cache[s].token.bodies = [r \in st.cache[s].token.members |-> 0])

Safety == /\ FullSnapshot /\ FullP /\ FullR /\ CommitHasReceipts /\ BodyDurable
          /\ SnapshotImmutable /\ NextWindowHead /\ FailureClass /\ TypeOK /\ UniqueSuccessor /\ QuotaBound /\ QuotaAccounting
          /\ OutboxAtomic /\ ExactlyOnce /\ WarmupExcluded /\ AppliedOutputBound
          /\ FrozenHistoryClosed /\ LockBeforePrepare /\ JournalUnique
          /\ FirstExposureExact /\ SnapshotReserved /\ DispatchBound
          /\ DurableBeforeSend /\ RetryStable /\ ReservationSafe
          /\ AbortPreservesHeadQuota

(* -------- progress ------------------------------------------------------ *)
(* Progress is conditional on eventually stable service availability AND on the
   window not suffering an unattributable PRE_EXPOSURE_ABORT; those are failure
   outcomes, not progress claims. Repeated crashes are allowed; permanent loss and
   stopped automatic retries are not progress claims. *)
AllUp == st.up = Processes
Progress == (<>[]AllUp /\ [](~st.abort)) => (RReady ~> st.collected)

(* -------- reachability predicates (negated as invariants) --------------- *)
NoZeroAfterPositive == ~\E r, t \in st.committed :
  Pred[t] = r /\ Eligible[r] /\ Bit[r] = 1 /\ Eligible[t] /\ Bit[t] = 0
NoOutOfOrder == ~\E s \in Roles : \E r \in st.delivered[s] :
  Pred[r] \in st.committed /\ Pred[r] \notin st.delivered[s]
NoLostAck == ~\E s \in Roles : \E r \in st.delivered[s] : <<r, s>> \notin st.acked
NoReservedRefusal == ~\E s \in st.refused :
  st.cache[s].present /\ st.sent[s] = None
NoRecoveredRetry == st.retried \intersect st.recovered = {}
NoMissingFrozen == ~(st.locked /\ \E s \in Roles : Rset \ M(s) # {})
NoSmallLegalRelease == ~(st.collected /\ Rset # EligibleIn(Reports)
                         /\ Cardinality(Rset) >= NativeMin)
NoWarmupRelease == ~(st.collected /\ \E r \in st.lockLog : ~Eligible[r])
NoDeadlineResume == ~(st.expired /\ st.manual /\ st.collected)
NoCompleteRelease == ~st.collected
NoPreExposureAbort == ~st.abort
NoExposedCollectionFailed == ~st.failed
NoNextWindowContinuation == ~(st.continued /\ st.collected)
NoPartialAbort == ~(st.abort /\ Current(st.committed) # {} /\ Current(st.committed) # Pset)
NoReceiptCommit == ~(st.committed # {} /\ ~StartFrozen)
NoJournalConflict == \A s \in Roles : ~st.conflictSeen[s]

=============================================================================
