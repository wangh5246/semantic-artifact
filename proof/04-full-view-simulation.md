# G4b: Online Simulation and Per-Hybrid Cost for Full Business Views

Date: 2026-10-18. Target: the identical `v5` instance pinned in Documents 00 [source omitted from this derivative] and 01. This document expands frozen G4a Documents 01 [source omitted from this derivative] and 03 [source omitted from this derivative], replacing uninstantiated native placeholders with the concrete FLP/RO bounds of [Document 03](03-native-privacy-and-query-ledger.md), using Document 02 for related-setup Groth16 extraction/ZK bounds and Document 05 for source-level prefixes/refinement. Conclusion: **PROVED_IN_DECLARED_MODEL**. Standard primitive `Adv` functions remain explicit; neither target-level composition nor native privacy is assumed as a free axiom.

## 1. Input Permissions, Admissible Worlds, and Complete View

`μ` contains strictly pre-fixed profiles/configs/assets, task/key commitments, owners/`uid`/epochs, budgets, windows/slots, accepted-step indices, predecessor/`K` reference topology, warmup/eligibility, public `b`, wire formats, and exogenous resource caps. `σ` specifies adversarial delivery/drops/retries and independent executor coins. Actual points, proofs, ciphertexts, `T`/receipts, hashes/roots/certs, verdicts, commit/abort outcomes, delivery success, and execution latencies may never be hardwired into `μ` or `σ`.

Admissible worlds `H0` and `H1` give every honest owner a fresh valid genesis, authentic step predecessors, real `max(0, t − 6)` anchors, valid range/ADWC constraints, and matching public `b`. State commitments are sampled **once per history node**, with `prev`/`K`/aliases reusing the original handle rather than equalizing only the final window sum. Both `P` and `P+A` require identical certified claimed histograms on every permitted first-exposure `R` and prior release (`O_C(R) = Σ_(i ∈ R) e_(I_i)` including sentinel, with sentinel count recovered from public `b` if stripped). `A`'s interface satisfies `O_A = ∅`, permitting differing world histograms.

The observer view includes all historical public signals and authentication chains, both roles' complete input ciphertexts/sidecars, all proofs/points/`T`, origins and `Pending/Lock/Permit/receipt/commit/freeze/abort` records, modeled business DB/WAL/backup contents, outbox/HTTP responses and diagnostics, exact replays, all prefixes, and modeled business timings. `P` additionally sees one statically corrupted role's complete secrets/inputs and Collector decryption view; `P+A` further adds the honest authority's complete business view **without** its signing private key or permission for malicious signing (`A` creates its own initial keys via Setup and runs honest signing cleanly, distinct from handing that signing key to `P+A`).

Simultaneous dual-role corruption, active malicious authority, post-challenge key rotation or adaptive corruption, cross-task inputshare reuse, extra cohort releases, unbuffered local client proving times, and physical hardware attacks lie outside the game and are never smuggled in under an unexplained leakage symbol.

## 2. Execution-Wide Tables and Primitive Advantage Interfaces

Simulator `S` maintains the following **cross-prefix persistent tables**, never reset across windows or retries:

- `H[(key_namespace, logical_relation, orderedSignals)]`: origin, full first-published body/packet, and native semantic handle per honest-source simulated proof (retaining per-source tags on repeated statements); `key_namespace` spans all current and legacy keys of Document 02 so shared numerical signals never alias across keys.
- `W / E`: a priori known and white-box extracted witnesses keyed by complete typed statement; no witnessless simulation oracle is ever served to malicious owners.
- `RO[usage, seed, binders, offset]`: accepted field elements, rejected candidates, prefetch suffixes, and physical/logical counters separated explicitly.
- `HPKE[fullTuple]`: resolved `(recipient key, suite, info, AAD, enc, payload)` and unique authorized source override; config aliases resolve to canonical underlying key handles.
- State nodes/aliases, origin/body/slot/RID, `P/R/L/A/M`, authentic `head/K/quota`, certificates, journals, retained outputs/tags, receipts, outbox, unique export snapshots/payloads, and the exposure ledger.

Table `H` also holds non-native genesis and related-key prelude proofs; in native/aggregate expressions below, `H` restricts cleanly to transition reports carrying actual honest native source tags (`S_G16` tracks all proof simulations, whereas `N_shard` tracks native sources only). Having a historical-key simulated proof confers no active-task owner/origin/body identity.

Each primitive advantage uses a concrete game parameterized by total reduction runtime `T` and query limits:

| Notation | Game and Accounting |
| --- | --- |
| `Z_G16,alg(S, T) = 0` | Exact projective honest-to-simulated proof distribution (Document 02); concrete identity/affine exclusions `A_G16(S) ≤ S(3p − 2)/p²` enter `B_route` at every hybrid endpoint conservatively, avoiding reliance on per-attempt caps like `8`. |
| `X_G16(T, typedHandles, queries, S)` | Document 02 white-box extraction bad event for fresh non-`H`/`W`/`E` statements; bounded per hybrid execution by a single generic collision/degree ledger rather than unknown per-report `SE` factors. |
| `Adv_HPKE,k^cca2(T, 1, D_k, L_k)` | Single-shot Base HPKE IND-CCA2 under fixed suite/key and complete `(info, AAD)` tags: one challenge, `≤ D_k` legitimate decryption queries, and byte cap `L_k`; summed across challenges. |
| `Adv_Sig,k^euf-cma(T, S_k)` | EUF-CMA restricted strictly to key set `K_sig,X` whose private keys are hidden from the observer without arbitrary signing rights (`S_k` counts fresh genuine signings, omitting cached replays; corrupted keys and `A`'s known passive authority key are excluded from `K_sig,A`, while `P`/`P+A` include the authority key). |
| `Adv_SHA256^cr(T, Q_sha, B_sha)` | Whole-execution collision resistance of the **single** SHA-256 function combining contexts, packages, bodies, roots, certificates, and external calls (two 128-bit limbs preserve all 256 bits cleanly). |
| `Adv_Com^bind(T, Q_Com)` | Multi-instance computational binding against double-openings of same-source commitments (`0` hiding cost from perfect blinding; counted once cleanly in Document 07). |
| `b_N(N, Q_i)` | Concrete single-world native RO programming bound from Document 03 §5 with `δ_abort = 0`. |

All simulator/reduction CPU, RO, signing, and hashing costs enter `T`, `Q`, and byte budgets. Signing/decryption counters are maintained per key and SHA-256 globally, retaining ROM/generic restrictions explicitly; constant-time executor semantics remain an independent premise not implied by CCA/EUF. Experiment `C` uses Document 03's `2κ_tag` and `OW128` corollary for integrity (never merged into privacy `B_route`), whereas `P`/`P+A` allow prior knowledge of the native verification key and preserve fresh-nonce privacy under Document 03 §5.

Define `B_route` for **one full execution of a single hybrid endpoint** as the union bound `X_G16 + A_G16 + Adv_SHA256^cr + Σ_(k ∈ K_sig,X) Adv_Sig,k + Adv_Com^bind + B_origin` (including `g_setup` per Document 07). Origin pre-publication `RID` guessing uses `B_origin = N_RID · G_origin / 2^128`, where `N_RID` covers all honest `RID` draws/reservations (including pre-shard rejections) and `G_origin` bounds adversarial guesses before public disclosure. Because no cross-hybrid master coupling is assumed, §6 multiplies `B_route` cleanly by total endpoints `M_X = 2(C_X + 10)`.

## 3. Two-Layer Routing Over Sources, Statements, and Chosen Ciphertexts

Executing public schema, context, owner, `OriginCert`, lock, permit, Helper journal, and Leader persistent checks first, routing handles sources/statements and non-`H` ciphertexts in strict pipeline order (exhaustive algorithm, not mutually exclusive assumptions):

1. Intact `H` complete body on initial authorized processing invokes its pinned semantic handle; Helper exact retries return committed journal/receipt bytes, while uncommitted/stale-lease Leader recomputations execute on the same original handle with updated peer responses under at most one committed transition. Full challenge tuples never enter the CCA decryption oracle, nor do differing peer responses spawn new input shares.
2. Modified packet bytes sharing an identical statement fail via Document 02 `Lemma O` (context/package SHA collision) since `owner/uid/epoch/window/step/RID` and package digest are pinned; re-randomizing proofs alone changes `BODY` and requires fresh honest signatures or signature unforgeability.
3. Fresh statements outside `H`/`W`/`E` extract witnesses online into `E` via Document 02 (`W`/`E` reuse cached witnesses), providing claims and `STATE`/`MASK` openings **without** leaking native cipher plaintexts, before entering steps 4–5.
4. Any new malicious body reusing an `H` exact HPKE challenge tuple hits `RID`-embedded `AAD`: because honest sources persistently claim unique `RID` in `OriginCert` before publication (`origins.report_id` globally unique, `rawRID = envelopeRID`), another owner cannot claim that `RID`, impersonating an honest owner hits unforgeability, and guessing an unpublished `RID` enters `B_origin`. Direct native ingress validates full body, permit, and tuple checks prior to decryption.
5. All remaining ciphertexts — including reusing `enc/payload` under altered `AAD/RID/key/info` — form legal non-challenge queries: the single-challenge reduction queries the honest-key CCA oracle for true plaintext or `⊥` (or decrypts self-generated keys directly) and executes real codec/`MASK`/native logic faithfully, caching retained outputs, receipts, and errors without falsely returning `⊥` blindly on modified ciphertexts.

Native HPKE labels use `dap-09 input share || Client || role` with `AAD = task || metadata(RID, timestamp) || encoded public_share`; sidecar `info` uses `SHTPC-HADWC-v5-SIDECAR` with `AAD = task/RID/config/raw_report_digest/role/core_digest` (requiring unique origin since `core` omits owner). Plaintexts are fixed 93 B binaries (16 B `mask`, 32 B `rho`, 109 B AES-GCM payload) pinned against secret-decimal parsers. `H` overrides only the exact canonical key/suite/info/AAD/enc/payload tuple; config aliases resolve to the underlying recipient key handle.

## 4. Online Simulator S for P and Augmented P+A

Fix statically corrupted role `c` and honest role `h`. Generate `c`'s known input share, plaintext, `r_c ← F_q`, `ρ_c ← Z_ℓ`, and valid `MASK` commitments, honestly encrypting `c`'s HPKE ciphertexts. For `H`, sample each hidden history node/`STATE`, honest `MASK`, `TICKET`, and `RECEIPT` once uniformly in the prime-order subgroup and reuse handles across aliases (`ρ ↦ mG + ρH` is bijective so joint hiding is exact without discrete logs, leaving corrupted known-opening `MASK` points untouched).

For each `H` report, sample `T ← F_q` and run Document 03's native kernel to obtain the preparation transcript and `v_c^orig`. Upon honest `Finish`, cache the opaque tag and compute:

`F(v) = Σ_(j=0)^10000 j·v[j]`, `m_h = T − F(v_c^orig) − r_c`.

Given the real native view and `r_c`, uniform `r_h ← F_q` makes `T = I + r_c + r_h` uniform with `m_h = I − F(v_c^orig) + r_h`, so `(T, m_h)` matches `(U, U − F(v_c^orig) − r_c)` identically as an exact joint law coupled to the same native variables (not merely independent marginals). For arbitrary adaptive adversarial `m'_c`, the new moment verdict is `m'_c + m_h = T ⇔ m'_c = F(v_c^orig) + r_c`. Both receipts are given to the adversary, and root-abort/FLP/seed/session/quota verdicts derive purely from known simulated variables without touching real secret verdicts.

Non-`H` reports run real honest plaintext recovery (§3), extracted/known `x_j`, native execution, and honest receipt generation, caching `w_(h,j)` without assuming `w_(h,j) = e_(x_j) − v_(c,j)` or requiring `c`'s private key.

Only upon authorized first exposure of complete `R` (at Document 05's reservation/bind gate) does `S` query `O_C(R)` once, partitioning `R_H = R ∩ H` and `R_N = R \ H` to assemble:

`V_h,R = O_C(R) − Σ_(j ∈ R_N) e_(x_j) − Σ_(i ∈ R_H) v_(c,i)^orig + Σ_(j ∈ R_N) w_(h,j)`.

Subtracting known non-`H` claims leaves the authorized `H` total cleanly with zero subset oracle; `H` identity-truncation yields complementary shares and non-`H` adds actual honest outputs. Encoding the canonical `Field128` vector into Collector HPKE uses the cached plaintext across retries on identical snapshots, while `c` remains free to send forged shares.

`S` executes the exact authority state machine, signing service, and business DB/WAL/backup logic, producing `P+A`'s authority business view from the identical generated bytes without extra secrets or ideal outputs. Prefixes advance `L/P/R/M`, real `head/K/quota`, and exposure monotonically per Document 05; Helper journals reject altered peer requests pre-computation, while uncommitted Leader recomputations across varying Helper replies evaluate via the identical `(Σ, z_h)` of Document 03 under single-transition lease fencing.

## 5. Independent Zero-Output Simulator S_A for A

`S_A` takes no `O_C` oracle whatsoever (never built by projecting a `P+A` simulator). Generating independent Setup keys for authority/roles/Collector (and calling honest signing oracles for honest owner keys), `S_A` runs the real public state machine and constructs:

1. Uniform subgroup `STATE` commitments sampled once per history node alongside independent `MASK`/`TICKET`/`RECEIPT` points, preserving aliases/`K` without disclosing openings.
2. Independent uniform `T, u ← F_q` per `H` report with `m_A = u, m_R = T − u`; for fixed native shares `(v_A, v_R)`, `(r_A, r_R) ↦ (T, m_A)` is a bijection on `F_q^2`, giving the exact joint distribution without any aggregate.
3. Public joint parts programmed via `U7` with independent secret blinds (pre-hits charged to Document 03), generating FLP/query/seed transcripts via Document 03's aggregate-free prefix kernel (optionally fixing an undisclosed uniform `v_A` and `r_A = u − F(v_A)` to generate compatible dual `Q_2` verifiers without calling `O_C`).
4. Equal-length dummy HPKE ciphertexts for both roles' native shares and sidecars (`H` sources via source override, non-`H` via honest decryption/execution), plus fixed-plaintext 160016 B dummy HPKE for `A`-visible outbound role-to-Collector aggregates via IND-CCA (since `A` is not Collector and lacks its key).
5. SQL `EXISTS`-only `export-status` and uncompressed fixed 160016 B `BYTEA` export payloads; `S_A` faithfully executes authority DB/WAL/backups from simulated public/encrypted bytes without seeing honest roles' private DBs or address traces.

Steps 2–3 share the same `T`/receipts seamlessly; `O_A = ∅` throughout, permitting worlds with different aggregates cleanly.

## 6. Single-World Hybrid Sequence and Exact Accounting

Each hybrid constructs complete consistent bodies **prior to first packet publication**, preserving previously delivered bodies intact. Fixed-world HPKE reductions know `m_0` and process `H` sources natively until the final witness-free simulator `S` takes over:

| Transition | Joint Construction / Information | Single-World Charge |
| --- | --- | --- |
| Preserving source/route & blocking illegal substitution | §3 checks, `H`/`W`/`E`, Document 02 online extraction; malicious own-key signing excluded | `≤ B_route` per endpoint across adjacent games; scaled by endpoint count below |
| Real honest proofs → simulated proofs | Fix statements first; preserve node handles; charge fresh `Sim` calls to `S` | `Z_G16,alg = 0`; affine exclusions included per endpoint in `B_route` |
| Replacing hidden HPKE plaintexts with dummies | Equal length; update raw/package/core/context/proof/body/signature prior to register; pin source override | `Σ_challenges Adv_HPKE,k^cca2(T', 1, D_k, L_k)` |
| Native RO / raw share randomization → Document 03 kernel | Preserve usages/offsets/query-nonce constraints and strong FLP full-verifier simulation | `b_N` (with `δ_abort = 0`) |
| History/hidden points and `T`/receipt coupling | Subgroup bijection, inputshare identity, real `r_c` & known `MASK` preserved | `0` |
| Nonce/candidate traces, canonical codecs, DB, timings | Identical post-processing of simulated random bytes and audited execution trace | `0` (explicit model premises) |
| First complete `R` aggregate | `P`/`P+A` use §4 `H`/non-`H` formula; `A` uses dummy aggregate ciphertexts from HPKE row | `0` beyond HPKE challenges already counted |

Ciphertext challenge counts satisfy `C_HPKE ≤ 2N` for `P`/`P+A` (native inputshare plus sidecar per `H`) and `C_HPKE ≤ 4N + E_enc,A` for `A` (both roles' inputs plus `E_enc,A` outbound aggregate encryptions, explicitly counting snapshot re-encryptions rather than collapsing them under `E ≤ 1`). `P`/`P+A` outbound aggregates have known plaintexts and require no HPKE challenge.

Unfolding `C_X` cipher hops and 10 ordered macro hops conservatively: (1) source-proof sampling (`Z_G16 = 0`; affine in `B_route`), (2) nonce deduplication (`N²/W`), (3) initial RO programming (`N[Q4 + 2(Q3 + Q6 + Q7) + Q5]/W`), (4) shares/parts programming (`N[Q1 + Q2 + 2Q7]/W`), (5) prover-coin removal (`NQ4/W`), (6) FLP full-verifier (`N δ_abort = 0`), (7) hidden points/receipts (`0`), (8) raw candidate trace coupling (`0`), (9) business/first-exposure post-processing (`0`), (10) strict-PPT truncation (`Tail_sum`). Every lossy sub-hop carries dedicated routing endpoints, giving `M_X = 2(C_X + 10)`. Each endpoint retains one unified SHA-256 ledger while `b_N` sums natively without extra multiplication by `M_X`:

`e_X ≤ M_X B_route + Σ_(j=1)^(C_HPKE,X) Adv_HPKE,k(j)^cca2(T_j, 1, D_k(j), L_j) + b_N + Tail_sum`,

with `Tail_sum = Σ_(fresh hidden streams) Tail(L_s, L_s + 128)` across `≤ 5N` streams. Comparing both admissible worlds under identical `μ`, `O_C`, and witness-free `S` yields `Adv_X^two-world ≤ 2 e_X` (normalized cleanly in Document 07).

## 7. Online Causality of Timing, Diagnostics, Aborts, and Replays

Secret arithmetic for shares, proofs, `MASK`, and retained vectors is covered by G4a08 constant-time audits and fixed-work Field/FFT/FLP kernels. Document 03 attaches rejection counts independently to the shared RO table; `r`-root and FLP/seed verdicts depend solely on simulated coins and peer inputs. Secret sidecar plaintexts are fixed 93 B without secret decimal parsers, retained/aggregate vectors are fixed `10001 × 16 B`, `BYTEA` and WAL compression remain disabled, and status uses `EXISTS`. Public moment/point/proof lengths derive directly from the simulated bytes.

Under the Document 00/08 standard executor, constant-time primitives, audited address/IO patterns, public sizes, and exogenous storage/network coins yield simulated work `τ`, with HTTP completions, timeouts, and aborts determined causally via `Post(τ, adversary_schedule, exogenous_coins)`. Physical data-dependent hardware delays, cache co-residency, power/EM, faults, and pre-input-ready local prover timings remain excluded. Transaction rollbacks, Helper first-input journals, uncommitted Leader recomputations under differing Helper replies, lease-fenced `step_aggregation_job_2` commits, and crash recovery preserve identical prefixes inductively: prior to first exposure `S` never queries `O_C`, and post-exposure collection failures retain `O_C` and exposure monotonicity without retroactively leaking unexposed subsets.

## 8. Checks and Delivery Scope

`native-budget-contract.json` fixes counters `N, Q`, bytes, physical calls, and primitive hooks, corroborated finitely by Document 03 checks (`check-r1`/`check-r3`/tag checks) without substituting finite checks for the hybrid proofs above. Frozen G4a proofs/sources/binaries match read-only, with new scripts/outputs SHA-pinned in the delivery manifest and composed cleanly in Document 07.
