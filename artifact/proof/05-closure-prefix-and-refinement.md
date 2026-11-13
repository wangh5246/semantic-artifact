# G4b: Statement Closure, All-Prefix Invariants, and Source-Level Refinement

Date: 2026-10-18. Target: the frozen `SHTPC-native-hidden-adwc-strict/v5` G4a hardened instance (`authority_v5_g4a`, `janus-v5-g4a`); no source files, assets, G4a proofs, or historical evidence are altered. This document establishes parameterized state-machine induction, operation-by-operation forward refinement, and concrete source correspondence; bounded scripts verify paths, hashes, and small models only, without substituting for formal verification of compilers or the full G5 campaign.

## 1. Target Instance, Parameters, and Execution Premises

Pinned task, pre-generated verification key, profile/config/asset identities, `TimeInterval`, `NoDifferentialPrivacy`, and two-party single-proof `Prio3Histogram(10001, 100)` over native field `q`. By pinned per-task unique dispatch, this instance admits at most one visible cohort (other windows may form declared histories without authorizing separate releases). Entry documents for the frozen instance are G4a model [source omitted from this derivative], 04 [source omitted from this derivative], 05 [source omitted from this derivative], execution layer [source omitted from this derivative], and composition [source omitted from this derivative].

Integrity experiment `C` requires honest authority, both roles, Finalizer, and Decoder, with the native verification key sampled randomly at setup and hidden from malicious clients. Privacy experiments `P`/`P+A` allow one role to be actively malicious and know that native key while requiring honest-role collection, retention, and dispatch paths to obey this document; two-honest-role integrity and secret-query bounds from `C` never transfer to malicious-role outputs in `P`. Standalone authority experiment `A` has no aggregate oracle.

Execution premises require: complete honest `SignedBody` delivered prior to the registration boundary over an independent authenticated confidential channel; client witness/proving completed prior to `input-ready` and delivered on schedule; honest durable storage and atomic DB commits/recovery without rolling back committed states; and no compromise of honest keys. Arbitrary message delays, drops, duplicates, and process crashes are permitted, without assuming eventual business completion or injecting real time, timeouts, or secret verdicts into metadata.

PostgreSQL runs at `REPEATABLE READ` rather than global `SERIALIZABLE`; below we prove only the specific linearization and monotonic-read properties required per operation. Honest databases never commit silently across ignored conflicts or corrupt persisted fields; those remain execution premises rather than negligible bad events.

## 2. Abstract State and Refinement Mapping

Per window, `P` is the locked ordered map of complete `LockedRecord`s, `R = eligible(P)`, `L` is the authority's committed map, and `A = eligible(L)`. For role `s`, `L_s` holds locally accepted records sharing the same `CommitCert`, and `M_s` holds eligible records actually merged into the native batch. Identities across `P`, `L`, `A`, and `M` are never conflated.

State further includes per-`uid` authentic `head/version/history`, per-`(uid, window)` `quota`, `Origin` table, immutable `body/slot/RID`, `install/permit`, protected input identity and journals, retained outputs, outbox, freeze/abort, reservations `E_s`, unique payloads `Z_s`, and exposure ledger `X`. Retained linkage maps:

`(task, profile, config, body, RID, job, protected-step, request-hash, aggregation-param, role) → typed output + opaque retained tag`.

Locked records contain no future uncreated sessions/outputs, which attach afterward via receipts, `CommitCert`, local retained state, and reservations without mutating `P`. Every `M_s` element carries this full link; RID/count/checksum equality alone never certifies record equality.

The abstraction function `α` projects **committed** SQLite/PostgreSQL rows to abstract state: authority `bodies.committed/commits/history/quota/identities` yields `L`/`head`; role `commit/head/history` yields `L_s`; eligible retained `APPLIED` plus consumed membership and batch totals yield `M_s` (`warmup` may reach `APPLIED` without entering `M`). Uncommitted transactions, thread stacks, lock waits, and network buffers do not advance these sets; reading journals/immutable bytes is a stutter step, while authorized first writes trigger abstract transitions.

`X` logs semantic exposure, appending upon the first transmission of a decryptable honest share toward a recipient with decryption capability. Implementations may log conservative send intent — over-reporting potential exposure is permitted, whereas under-reporting or claiming zero exposure under unknown status is barred. Persistent reservation prior to actual transmission is not identical to physical delivery: ideal proofs allow pre-fetching the identical `R` output once when preparing first send, hiding unused pre-fetches from the adversary without querying other cohorts.

## 3. Linearization Points and Crash Boundaries

| Operation Family | Linearization Point & Mechanism | Obligations Before Visible Return |
| --- | --- | --- |
| authority origin / register / lock / permit / receipt / freeze / abort | `service._transaction` SQLite `COMMIT`; `guard` uses `BEGIN IMMEDIATE` serialized writes | Return only after `COMMIT`; exceptions `ROLLBACK`. Proof verification may run outside final register tx, yet pre-reserves attempts persistently and final tx re-validates immutable slot/origin/lock invariants |
| authority → role dispatch | `_proxy_queue` commits exact request; `_proxy_deliver` commits attempt prior to wire send; replies/acks follow in separate tx | Authority commit and two-role apply do not span distributed XA; `CommitCert` persists recoverably and drivers redeliver from commit tables rather than assuming cross-DB atomic outboxes |
| role control & Helper init/continue | `Datastore::run_tx` final Pg commit; control advisory lock precedes prepare lock; shared `prepare_serialization` epoch write | `REPEATABLE READ` stale snapshots retry on epoch conflicts prior to authorization/private prepare; journal, native state, retained output, and response commit atomically without sending temporary failure responses |
| Leader native task | Under unit aggregation param, setting `aggregation_started`, creating job/report-state, and scrubbing raw report share one tx; each step reads committed state then computes out-of-tx | `step_aggregation_job_2` commits writer/retained updates atomically with `release_aggregation_job`, checking lease expiry/token fence so stale leases abort cleanly and never overwrite newer committed branches |
| role apply | Inside control/epoch tx: batch merge, consumed membership, `head/quota/history`, retained/body status, and commit row share one commit | Exact existing `CommitCert` returns cached reply idempotently; conflicting cert rejects; merges once regardless of lost acks |
| role reserve/bind | Inside control lock: verify full `P/R/retained/M` and write unique reservation; bind re-reserves, writes fixed 160016 B `BYTEA` with full-length CT comparison before Pg commit | Helper fresh/cache and Leader finished/cache each `await` bind tx prior to HPKE; Leader also reserves completely before querying Helper |
| freeze / abort / outcome | Authority freezes only when `L = P` and no active permit; role checks local `L/M`; abort preserves committed rows | `FREEZE` excludes new `ABORT`/commits for the lock; `proxy_abort` marks uncertain send state `UNKNOWN` and keeps prior possible sends permanently in exposed class |

The Helper's HADWC journal locks **one committed protected input branch and response**, returning public conflicts on altered requests before private computation. The Leader lacks an identical first-peer-input journal, instead enforcing single committed transitions per step via persistent jobs/states and lease fencing: its initial `Prepare` message to Helper depends strictly on persisted report/nonce/key data (not aggregate first exposure) and may precede step commit; on crash/lease loss before commit, retries may observe differing Helper responses and recompute using the exact same raw share, nonce/query/joint coins, and committed native state via Document 03's shared `(Σ, z_h)` without pre-computation conflict claims. Only successfully committed state/retained outputs enter `α`, while stale-lease writes abort cleanly.

PostgreSQL `run_tx` may also re-invoke closures on serialization/deadlock errors; all mechanisms enforce **one committed logical branch**, not "CPU instructions run once". Identical-input recomputations reuse cached RO streams, while varying peer responses simulate via Document 03 and count every physical call/failure/message/timing toward `Q/T`.

Export reservation writes no shared prepare epoch, relying instead on monotonic phases: stale `REPEATABLE READ` snapshots failing to see `FREEZE` or complete `M` reject safely, whereas once `FREEZE` is visible, authority has finalized complete `P` (barring later commits/aborts) and role `L/M` grow monotonically up to fixed `P/R` without mutating retained links. Write constraints, full-record checks, and full-length equality handle concurrent reservations without falsely assuming `SERIALIZABLE`.

Crashes cleanly partition transactions into uncommitted/rolled-back or committed; aggregates, receipts, and cached Helper responses dispatch solely after commit. Send-ack drops never erase exposure, and dual-DB recovery proceeds idempotently via persisted certificates. Disk corruption and administrative DB edits lie outside the crash model.

## 4. All-Prefix Invariants

Across any finite prefix `τ`, all six invariants hold simultaneously ("equality" denotes full typed record and link equality):

1. `P/R`, `task/profile/config/assets`, aggregation parameter, and selector freeze upon lock with `R = eligible(P)`; origin/slot/`RID`/body identities never mutate after first write.
2. `L ⊆ P` with closed history dependencies; each `uid` head terminates a unique committed chain with authentic `K = max(0, t − 6)`, monotonic `version`, and exact non-rollback `quota`.
3. `L_s ⊆ L`, `M_s ⊆ eligible(L_s)`, every member carries one exact retained/body/session/link chain and contributes once to the batch (`warmup ∉ M`, eligible `b = 0 ∈ M`).
4. Each Helper journal key holds at most one committed `(first-input, result, native-state, response)` and report tombstones block switching jobs (`exact` retries replay cached bytes, changes raise public conflicts). Unique persistent Leader jobs, per-step state, and lease fences admit at most one committed transition per step; pre-commit peer variations leave committed state unchanged and simulate via one `(Σ, z_h)`.
5. Existing `E_s` implies `L_s = P`, `eligible(L_s) = R`, `M_s = R`, complete ordered records, matching retained links, and pinned selector/snapshot; bound payload `Z_s = Σ_(i ∈ R) v_(s,i)` equals the authentic native encoding and cannot swap afterwards.
6. Every decryptable honest aggregate share transmission is preceded by durable `E_s` and bound `Z_s`; outer HPKE re-encryption reuses identical semantic payload without withdrawing `X` across crashes or aborts.

Pre-lock states track monotonically growing candidate map `P_reg`, promoted atomically to `P` upon lock.

## 5. Event-by-Event Inductive Proof

**Init / Enrollment / Origin.** Fixed configurations/roles/owners and validated genesis encodings start with empty `L/M/journal/export`, zero quota, and unique origin reservations that do not advance `head`; all six invariants hold.

**Register.** After source/owner/`rawRID`/OriginCert checks, proof verification, and canonical record assembly, final tx confirms pre-deadline unlocked state, unique slot/`RID`, and matching reservation, inserting solely into `P_reg`, `PendingCert`, and business logs while leaving `L/head/quota/M` untouched. Concurrent writes are serialized by uniqueness constraints up to SHA collision.

**Lock.** Requires all scheduled slots present, continuous candidate chains anchored at current committed heads, valid canonical `prev/K` links, ordered `P/R` root computation, and distinct eligible `uid` threshold before writing `P/R/LockCert` once and closing further registration — never taking partial receiver intersections or advancing `head`.

**Install / Permit.** Roles verify full packages, `LockCert`, records, and roots immutably; after dual install acks, authority checks real `head/version`, committed `prev/K`, and `quota` before signing one active permit; roles re-verify full context upon receipt. Asynchronous `L_s` lagging behind `L` never relaxes export gates.

**Prepare / Retain.** Upload and Helper init/continue validate full install package and active permit prior to HPKE/FLP. Helper shared prepare epoch rejects stale snapshots pre-computation and pins `(first job, context, input, committed response)`, blocking missing/changed inputs from branching. Leader assigns one unit-param job per persistent report and commits native step state under lease fencing (with out-of-tx recomputations covered per §3). Finished outputs stage isolated inside `retained` (atomically with Leader state/lease release) without entering `M`; repeated finish verifies identical body/job/output/tag.

**Receipt.** Honest roles compute masked moments solely from identical retained outputs and matching sidecars via G4a08 constant-time mask/`rho` decoding, binding `lock/permit/body/statement/session/nonce/step/tag` under signature. First receipt persistence does not commit; after freeze only cached exact replays remain allowed, and errors leave `L/M` untouched.

**Authority Commit.** Second receipt transaction verifies both signatures, full binders, session, and moment equation, then verifies authentic `head/version`, real `prev/K` digests, and `quota` atomically with CAS, history, quota deduction, permit deactivation, `body.committed`, and `CommitCert`. Failed attempts leave no partial history; concurrent siblings serialize cleanly; exact replays avoid duplicate quota deductions.

**Role Commit / Apply.** Checks authority cert, stored local receipt, both receipts, installed records, and retained job/tag; exact duplicate certs short-circuit idempotently. Eligible records merge their raw retained vector into the batch and log consumed membership (`warmup` advances local history only), atomically with `head/version/quota` CAS and commit tracking (any failure rolls back batch merge), guaranteeing `M_s` multiplicity 1 and `L_s ⊆ L` under honest role code.

**Freeze.** Authority requires `L = P`, unchanged records, and zero active permits before signing complete `p/r` lists and marking `FROZEN`. Roles verify local committed/applied state prior to freezing, never assuming remote role progress from authority commit alone.

**Reserve / Bind / Send.** Every dispatch gate re-validates full `P/R`, eligible projection, session/tags, and exact consumed set difference (`R \ M_s = ∅` and no extras), persisting unique `E_s` and fixed native payload bytes `Z_s` before awaiting commit prior to HPKE and network dispatch — tying every first share strictly to complete `R` across both fresh and cache exits without exemption.

**Abort / Timeout / Recovery.** Unfrozen aborts close locks/permits while retaining commits, heads, quotas, journals, and tombstones rather than shrinking `P/R` to re-export. Post-freeze collection failures retry on the identical snapshot. Lost proxy states conserve `UNKNOWN` without downgrading potential exposure to `PRE`, and `X` updates cleanly on actual share sends. Recovery resumes durable state idempotently across §3 crash cuts, completing arbitrary-prefix induction over every state-mutating event class.

## 6. Statement Closure and Successful Reconstruction

Excluding Document 02 extraction errors, signature forgeries, commitment double-openings, SHA binding collisions, and native validity failures: induction from genesis fixes unique canonical `STATE < ℓ`, forcing identical predecessor/`K` coordinates, while coordinate differences, squared distances, and mask carries stay below `p`, lifting field checks to exact ADWC integer relations (for admitted claims, not physical GPS truth).

Honest finished outputs satisfy `v_A + v_R = e_y` (`0 ≤ y ≤ D`) in the one-hot `Histogram` domain `E = {e_0, ..., e_D}` (distinct from `SumVec` multi-1/zero vectors). Retained receipts and valid `MASK` openings enforce `F(v_A + v_R) = m_A + m_R − r_A − r_R = T − r_A − r_R = x (mod q)` with `x, y ≤ D < q`, forcing `y = x`. Even `b = 0` emits authentic sentinel `e_D` and joins retained/consumed membership. By all-prefix invariants, matching snapshots accumulate each `R` member strictly once; stripping sentinel yields exact `Σ_(i ∈ R) b_i e_(j_i)`.

Integer histogram interpretation experiences no modulo-`q` wrap-around: deferred apply casts batch `report_count` via `i64::try_from` at `models.rs:1498`, failing on overflow (`u64` increment from `≤ 2^63 − 1` never wraps), and both Helper `put_aggregate_share_job` (`datastore.rs:4412`) and Leader `update_collection_job` (`datastore.rs:3512`) re-validate total `report_count` via `i64::try_from`, matching audited `u64` debug summation. Thus every successfully collected `R` satisfies `|R| ≤ 2^63 − 1 < q`.

In `P`/`P+A`, non-`H` records need not emit one-hot outputs, so simulated aggregates strictly use:

`O_C(R) − Σ_(i ∈ R \ H) e_(x_i) − Σ_(i ∈ R ∩ H) v_(c,i)^orig + Σ_(i ∈ R \ H) w_(h,i)^actual`,

combining extracted/known non-`H` claims with decrypted/executed honest outputs `w_(h,i)^actual` solely upon authorized complete-`R` exposure.

## 7. Source Mapping and Bounded Corroboration

`source-map.json` [source omitted from this derivative] indexes 52 concrete functions/exits with repo-relative paths, line ranges, and full-file SHA-256 digests confirming all 288 `G4a build003` pins unchanged (`check001–004` stay historical).

`bounded-controls.json` [source omitted from this derivative] exhaustively explores two independent eligible records (positive + zero) across dual-role crashes/recovery, prepare/commit/apply/freeze/reserve/bind/send, and failure tags: `840` states and `2,652` edges with zero invariant violations (`PRE`/`EXPOSED`/`EXPOSED_FAILED` reachable) plus shortest counterexamples across 8 guard-removal mutants (modeling **committed** transitions in `prepare`, without equating finite graphs to TLC, full-scale histories, or G5). Daily G5 `E5/1` (`35` cases) maps via `G5.lockLog → P`, `G5.committed → L`, `EligibleIn(committed) → A`, `merged[s] → M_s`, noting finite-flag abstractions and remaining outside unbounded source refinement ([Document 06](06-counterexamples-and-scope.md)).

### 7.1 Concrete Function / Line / SHA Matrix

The SHA column shows the leading 12 hex characters for readability (full 64-char digests and paths appear in `source-map.json`).

| Event / Obligation | Source File & Line Range | SHA-256 Prefix (12 hex) |
| --- | --- | --- |
| authority-tx | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 184–191 | `ced8a6fd317b` |
| origin | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 239–259 | `ced8a6fd317b` |
| register | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 274–321 | `ced8a6fd317b` |
| lock | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 323–346 | `ced8a6fd317b` |
| permit | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 375–399 | `ced8a6fd317b` |
| authority-commit | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 400–444 | `ced8a6fd317b` |
| authority-freeze | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 446–474 | `ced8a6fd317b` |
| authority-abort | `runtime/authority_v5_g4a/service.py` [source omitted from this derivative]: 476–489 | `ced8a6fd317b` |
| outbox | `runtime/authority_v5_g4a/proxy.py` [source omitted from this derivative]: 76–98 | `58f26a8f51da` |
| exposure-outcome | `runtime/authority_v5_g4a/proxy.py` [source omitted from this derivative]: 277–338 | `58f26a8f51da` |
| pg-tx | `aggregator_core/src/datastore.rs` [source omitted from this derivative]: 265–399 | `eb55dcd64b06` |
| control-epoch | `src/commands/hadwc_v5.rs` [source omitted from this derivative]: 690–709 | `c815f7b9c341` |
| prepare-epoch | `src/datastore/hadwc_v5.rs` [source omitted from this derivative]: 104–127 | `7b07ae066b2a` |
| native-identity | `src/datastore/hadwc_v5.rs` [source omitted from this derivative]: 150–191 | `7b07ae066b2a` |
| journal | `src/datastore/hadwc_v5.rs` [source omitted from this derivative]: 188–238 | `7b07ae066b2a` |
| native-authorization | `src/datastore/hadwc_v5.rs` [source omitted from this derivative]: 262–328 | `7b07ae066b2a` |
| retained | `aggregator_core/src/datastore.rs` [source omitted from this derivative]: 8430–8513 | `eb55dcd64b06` |
| receipt | `src/commands/hadwc_v5.rs` [source omitted from this derivative]: 1263–1400 | `c815f7b9c341` |
| role-apply | `src/commands/hadwc_v5.rs` [source omitted from this derivative]: 1402–1558 | `c815f7b9c341` |
| batch-add | `src/commands/janus_interop_aggregator.rs` [source omitted from this derivative]: 3780–3851 | `b57fa7732f98` |
| reserve | `src/datastore/hadwc_v5_export.rs` [source omitted from this derivative]: 38–133 | `9f75a0121baf` |
| bind-payload | `src/datastore/hadwc_v5_export.rs` [source omitted from this derivative]: 136–162 | `9f75a0121baf` |
| dispatch | `aggregator_core/src/datastore.rs` [source omitted from this derivative]: 7619–7676 | `eb55dcd64b06` |
| context-codec | `runtime/g1_authority.py` [source omitted from this derivative]: 126–146 | `dbe0c086128b` |
| records-codec | `runtime/authority_v5_g4a/codec.py` [source omitted from this derivative]: 185–206 | `961258d8b9da` |
| helper-reserve | `aggregator/src/aggregator.rs` [source omitted from this derivative]: 4038–4077 | `54181d45dce3` |
| helper-send | `aggregator/src/aggregator.rs` [source omitted from this derivative]: 4398–4425 | `54181d45dce3` |
| leader-send | `aggregator/src/aggregator.rs` [source omitted from this derivative]: 3760–3791 | `54181d45dce3` |
| leader-before-helper | `src/aggregator/collection_job_driver.rs` [source omitted from this derivative]: 304–311 | `c6504db3927a` |
| state-domain | `circuits/hadwc_common_v5.circom` [source omitted from this derivative]: 23–34 | `fa8580bc4923` |
| commit-domain | `circuits/hadwc_common_v5.circom` [source omitted from this derivative]: 35–48 | `fa8580bc4923` |
| distance-domain | `circuits/hadwc_common_v5.circom` [source omitted from this derivative]: 49–63 | `fa8580bc4923` |
| genesis-relation | `circuits/hadwc_genesis_v5.circom` [source omitted from this derivative]: 3–17 | `c2559a9de9b9` |
| transition-relation | `circuits/hadwc_transition_v5.circom` [source omitted from this derivative]: 3–75 | `9988f8a7998a` |
| policy-relation | `circuits/hadwc_policy_bounds_v5.circom` [source omitted from this derivative]: 4–12 | `78aa19c40e1f` |
| histogram-domain | `src/flp/types.rs` [source omitted from this derivative]: 380–444 | `5284c42c8326` |
| original-output | `src/vdaf/prio3.rs` [source omitted from this derivative]: 1392–1435 | `ef7d09e5d725` |
| opening-core | `interop_binaries/src/hadwc_ct.rs` [source omitted from this derivative]: 153–187 | `70cea07d0fa0` |
| moment-core | `interop_binaries/src/hadwc_ct.rs` [source omitted from this derivative]: 188–230 | `70cea07d0fa0` |
| batch-count-merge | `src/datastore/models.rs` [source omitted from this derivative]: 1353–1357 | `f3b1ca2dd2fe` |
| batch-count-storage | `src/datastore/models.rs` [source omitted from this derivative]: 1498–1502 | `f3b1ca2dd2fe` |

| Event / Obligation | Source File & Line Range | SHA-256 Prefix (12 hex) |
| --- | --- | --- |
| leader-job-claim | `runtime/janus-v5-g4a/aggregator_core/src/datastore.rs` [source omitted from this derivative]: 1312–1373 | `eb55dcd64b06` |
| leader-job-create | `runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_creator.rs` [source omitted from this derivative]: 567–781 | `11c9703337b9` |
| leader-read-state | `runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs` [source omitted from this derivative]: 187–252 | `b6c30ff4f59d` |
| leader-peer-compute | `runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs` [source omitted from this derivative]: 769–1003 | `b6c30ff4f59d` |
| leader-transition-commit | `runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs` [source omitted from this derivative]: 982–999 | `b6c30ff4f59d` |
| leader-lease-fence | `runtime/janus-v5-g4a/aggregator_core/src/datastore.rs` [source omitted from this derivative]: 2057–2111 | `eb55dcd64b06` |
| leader-retained-write | `runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_writer.rs` [source omitted from this derivative]: 257–315 | `23d0aa5e1fcd` |

| Event / Obligation | Source File & Line Range | SHA-256 Prefix (12 hex) |
| --- | --- | --- |
| collection-count-storage | `runtime/janus-v5-g4a/aggregator_core/src/datastore.rs` [source omitted from this derivative]: 3512–3516 | `eb55dcd64b06` |
| helper-aggregate-count-storage | `runtime/janus-v5-g4a/aggregator_core/src/datastore.rs` [source omitted from this derivative]: 4412–4416 | `eb55dcd64b06` |
| stack-secret-key-tag | `tools/g4a_native_stack.py` [source omitted from this derivative]: 182–184 | `866030563c84` |
| driver-secret-key-tag | `tools/g4a_native_drivers.py` [source omitted from this derivative]: 745–747 | `bb1d935484c1` |

## 8. Bad-Event Interface and Non-Circularity Principles

The source refinement argument is a deterministic conditional proposition given honest storage/services, valid authentication, and verified relations, never assuming full-view privacy. Cryptographic failures partition cleanly across Groth16 collisions/weak-SE/ZK/affine exclusions, native FLP validity/HVZK/ROM and nonce/seed guesses, commitment binding, SHA-256 collisions, signature unforgeability, labeled HPKE IND-CCA2, and execution-layer premises, respecting the following mandatory accounting rules:

- Failed proofs, genesis re-verifications, warmup/zero/failed candidates, corrupt-owner grinding, native RO calls, and observable retries all enter `Q`/`N` rather than counting only final `R` or committed steps.
- Same-statement re-randomization passes through `H`/`W`/`E` without triggering fresh extraction; self-signed malicious-owner messages never count as forgeries; two-honest-role `C` and active-role `P` keep distinct bad events and execution conclusions.
- Canonical encodings, bodies/packages/contexts/`P`/`R` roots, journal contexts, and request hashes all draw from one SHA-256 collision budget (domain separation prevents type confusion without creating independent random functions). Both 128-bit `context` limbs encode one full 256-bit digest without doubling collision charges; the fixed 96-bit `SHA256(verify_key)[:12]` tag restricts scope to pre-fixed `(task, key, config)` while triggering the explicit `min(1, 2^96 Q5 / 2^128)` / `OW128` key-guessing accounting in Documents 03 and 07 (leaving `P`'s unannounced-nonce space untouched).
- `APPLIED` status, counts, checksums, and opaque tags alone never establish output identity without the complete `body/session/retained` chain.
- Wall-clock timings and timeouts follow standard constant-time and rejection-sampling execution mappings (G4a08), with honest setup/unknown trapdoors, durable storage, and compiler/ISA faithfulness kept as explicit preconditions rather than hidden `ε` terms.

Pending G3/G5 tests are never pre-certified as PASS; subsequent runs validate concrete faults/implementations without replacing this inductive proof.
