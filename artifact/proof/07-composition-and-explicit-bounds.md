# G4b: Complete Composition Theorems, Finite Budgets, and Explicit Bounds

Date: 2026-10-18. Target: the hardened G4a instance pinned in Documents 00/01. This document composes the arguments of Documents 02–06 into the four security results `C`, `A`, `P`, and `P+A`, supplying explicit finite expressions and reduction interfaces for every error term. The model assumes typed opaque generic bilinear groups, a programmable native XOF random oracle, honest setup/durable storage, and the audited standard executor; it is not an unconditional theorem over arbitrary concrete curve algorithms or hardware.

## 1. Notation and Resource Experiments

Let `clip(z) = min(1, max(0, z))` and `choose2(h) = h(h − 1)/2`. Three distinct algebraic orders/fields appear:

- Groth16 source group order / circuit scalar field: `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`;
- BabyJub commitment prime subgroup order: `ℓ = 2736030358979909402780800718157159386076813972158567259200215660948447373041`;
- Native Field128 modulus: `q = 340282366920938462946865773367900766209`; seed/nonce space `W = 2^128`, `ρ = (W − q)/W`.

Budget `B` is fixed prior to the challenge. Every parameter is a public non-negative integer upper bound over the entire finite experiment (covering honest packet construction, legacy related-key prelude, adversarial offline grinding, failures, unprepared reports, warmup, zero reports, transaction rollbacks, and retries), not a claim that source code enforces these caps globally. Execution halts according to public rules upon hitting exogenous bounds; one may not plug in only the successful subset observed post hoc.

| Quantity | Exact Definition / Units |
| --- | --- |
| `N = N_shard` | Total `H` honest native packet constructions/public sources, including unprepared public packets; not final `|R|`. |
| `S_g, S_t, S_l` | All fresh external source proofs across the three keys, including Document 02's exact reparameterization of honest real proofs and simulated proofs; cached byte reads do not increment `S`. Genesis calls without native packets still increment `S`. |
| `V_g, V_t, V_l, Q_G1, Q_G2, Q_GT, Q_pair, I1, I2` | All Document 02 verification/typed-oracle/source output counts; Document 02's `Q1/Q2/QT/Qpair` are renamed here to `Q_G1/Q_G2/Q_GT/Q_pair` to avoid collision with native usage counts `Q_i`. Failed genesis verifications and extra offline group operations must be included. |
| `Q_i, Q = Σ_(i=1)^7 Q_i` | All XOF input/expansion invocations for native usage `i`, covering both external and internal calls; raw candidates and byte volumes are counted separately rather than substituting accepted-field counts for `Q`. |
| `G5_ext ≤ Q5` | Number of 16 B candidate keys appearing in external adversarial `U5` queries; honest internal `hidden-handle` calls using true `K` are not adversarial guesses. |
| `P_att` | Distinct first attack `prepare` attempts over protected complete inputs in Experiment `C`, including failures; physical rollbacks create no new input, while their RO/CPU calls still count toward `Q`/`T`. |
| `N_RID, G_origin` | Total honest `RID` sampling / `Origin` reservation attempts (including rejections prior to packet construction); adversarial pre-publication reservation guesses targeting an honest `RID`. Adversary-chosen `RID`s are not uniform random variables. |
| `E ≤ 1` | Number of permitted first semantic exposures of complete cohorts per pinned task; collection failures do not reset `E`. |
| `E_enc,A` | Number of fresh honest aggregate HPKE encryptions visible to `A`, counting re-encryptions of the same snapshot; not bounded by `E` alone. |
| `S_sig[k], D_hpke[k], L_hpke[k]` | Per-key signing counts, legitimate non-challenge decryption counts, and total absorbed/output/plaintext byte limits. |
| `Q_sha, B_sha, Q_Com` | Calls and byte volumes for the single SHA-256 function across all uses; all known-scalar group operations, openings/comparisons, and generation work across the five commitment classes. |

Every hybrid endpoint uses the same budget bounds `B`. Handles from mutually exclusive endpoint experiments never coexist in a single real execution; Section 5 accounts for them explicitly via endpoint union factors. Resource `T_red,j` denotes the worst-case abstract-machine step count of the `j`-th reduction under `B` and the strict truncation below; security terms take `T_red,j` or a larger pre-declared bound. Each reduction maintains finite linear representation logs from Document 02, fixed-length FLP/RO simulation from Document 03, and single-challenge routing from Document 04, without rewinding or unbounded oracles. Because messages, group outputs, RO bytes, and loops are all bounded by `B` and Section 3's raw prefix cutoff, every `T_red,j` is finite; primitive advantages must be instantiated with total reduction runtime rather than adversary runtime alone. Abstract step counts are not native hardware benchmarks.

Below, unsubscripted `Q1, ..., Q7` denote native XOF usages from Document 03 only and are never merged with generic group output counts. Both classes may be bounded under an overarching total runtime budget while preserving distinct units.

## 2. Single-Endpoint Cryptographic Bad-Event Ledger

### 2.1 Related CRSs, Generic Collisions, and Affine Exclusions

Current genesis, transition, and historical genesis introduce `k = 3` independent deltas. Document 02 enumerates every public serialized section, giving conservative initial handles `(330974, 80986, 5)` over a common denominator equal to the product of the three deltas. Cleared polynomial degrees are `(D1, D2, DT) = (32769, 16383, 49152)`, independent of simulation query count `S`.

Writing `S = S_g + S_t + S_l` and `V = V_g + V_t + V_l`, define:

```
H1 = 330974 + 2S + Q_G1 + I1 + 13V_g + 53V_t + 13V_l
H2 =  80986 +  S + Q_G2 + I2 + V
HT =      5 + Q_pair + Q_GT + 7V
g_coll = clip((32769 choose2(H1) + 16383 choose2(H2)
               + 49152 choose2(HT)) / (p − 16385))
g_aff  = clip(S(3p − 2) / p²).
```

If setup samples initially over full `F_p`, then `g_setup = 1 − ((p − 16385)/p)((p − 1)/p)^5`; if the game conditions directly on the valid domain of Document 02, then `g_setup = 0`. This contract sets `g_setup = 0` while retaining the explicit unconditional expression for alternative experiment definitions. Honest independent entropy, unknown trapdoors, and non-leakage are preconditions outside what `g_setup` certifies.

Set `g = clip(g_setup + g_coll + g_aff)`. Because identity checks and all typed expression comparisons are already contained in `g_coll`, retaining `g_aff` is an intentional conservative union bound requiring neither statistical independence nor equal probability. Every endpoint carries the same `g`, avoiding missing affine events on non-leading statements.

The extractor of Document 02 returns a witness for fresh non-`H`/`W`/`E` statements or triggers event `g`; matching statements identify their `H` source within the full key namespace. Real external honest proofs also increment `S`: conditioned on an admissible statement, uniform `(r, s)` map bijectively to `(μ, ν)` with `C` uniquely determined by verification, matching Document 02's source equation. Omitting calls to `SimAPI` never implies `S = 0`. Runtime rejection of identity group elements may reduce completion rate, never causing unsound acceptance; retaining `g_aff` inside `C` merely yields a slightly looser bound.

### 2.2 SHA-256, Authentication, and Commitment Binding

`h = Adv_SHA256^cr(T_red, Q_sha, B_sha)` upper-bounds finding any pair of distinct messages colliding under the **single** SHA-256 function over one full execution. Sources, packages, bodies, contexts, record/`P`/`R` roots, requests, journals, and signing messages all draw from this unified ledger. Deterministic injectivity of canonical length prefixes and bounded integers incurs zero charge; splitting a full digest into two 128-bit limbs adds no separate truncated collision term.

Let `K_X` be the set of active honest signing keys unknown to the adversary in experiment `X`:

`a_X = Σ_(k ∈ K_X) Adv_EUF-CMA,k(T_red,k, S_sig[k], message_bytes[k])`.

For any first accepted forged signature, the reduction outputs a `(message, signature)` pair under key `k` never queried to the signing oracle; if an already-signed message parses inconsistently across contexts, canonical codecs or `h` handle it. Plain EUF-CMA suffices without strong-EUF, since swapping signatures on an identical message cannot alter `BODY`/certificate semantics. Each key's reduction simulates all other keys natively, summing per distinct key without multiplying by report count. Adversarially owned owner/role keys lie outside `K_X`. Although `A` holds its own authority key, its experiment interface limits `A` to passive observation of honest authority runs without injecting extra control signatures; thus `A`'s key lies outside `K_A` and is not grounded in EUF for Experiment `A`. `P` and `P+A` do not receive that signing key and therefore include it in `K_P`.

`c = Adv_Pedersen5^bind(T_red, Q_Com)` denotes the standard multi-instance computational binding game across the five commitment usages (`STATE`, `MASK_A`, `MASK_R`, `TICKET`, `RECEIPT`): given pre-fixed non-identity prime-subgroup generator pairs and independent public parameters, outputting two distinct canonical openings `(m, r) ≠ (m', r')` with `m ≠ m' mod ℓ` for any usage. Canonical messages lie strictly below `ℓ`. From `(m − m')G + (r − r')H = 0`, it follows that `r ≠ r'` and `log_G(H) = −(m − m')/(r − r') mod ℓ`. This grounds `c` in standard discrete-logarithm/binding hardness rather than an ad hoc target-wrapper assumption, and decomposes cleanly across the five targeted usages. Honest hash-to-group generator derivation and unknown discrete logs remain prerequisites; file-hash equality does not certify entropy. Full-`F_ℓ` blinding gives exact perfect hiding (`0` privacy loss). BabyJub binding is kept cleanly separate from BN254 generic collisions.

Pre-publication origin `RID` guessing contributes `o = clip(N_RID · G_origin / W)`. Honest native nonce collisions are already accounted for in Section 3 and are not double-counted in `o`. Taking a union bound over potentially overlapping events yields the conservative single-endpoint routing bound:

`B_X = clip(g + h + a_X + c + o)`.                     (R)

Bound `(R)` covers one entire finite execution at a single endpoint without multiplying `g` by the number of accepted proofs; scaling across distinct hybrid endpoints is explicit in Section 5.

## 3. Native Bounds and Strict Simulation Runtime

Document 03 re-proves strong HVZK directly from the concrete Histogram implementation (`128` roots, wire degree `127`, gadget degree `254`, `455`-element proof, `202`-element verifier), returning the identical fixed abort whenever uniform `r` hits the `128` roots; hence `δ_FL,abort = 0`.

Single-world native privacy loss is:

```
b_N = clip((N² + N(2Q4 + 2Q3 + 2Q6 + 4Q7
                       + Q5 + Q1 + Q2)) / W).
```

Usage indices follow the source code. Because `Q` includes internal invocations, fresh seed collisions and pre-computations are already charged under programming collisions, while post-disclosure queries read the programmed table. Bound `b_N` assumes neither honesty of the corrupted role nor FLP soundness.

Rejection sampling caches complete raw streams by offset. Each fresh hidden field stream drawing `L` accepted elements uses search prefix `C_acc = L + 128` and buffer budget `C_raw = 32 · ceil(C_acc / 32)`, incurring strict-simulator truncation tail:

`Tail(L, C_acc) = Σ_(j=0)^(L−1) binom(C_acc, j) (q/W)^j ρ^(C_acc−j)`.

Each report has at most 5 fresh field streams with `L ≤ 10001, 455, 2, 200, 1`, conservatively charged even for unprepared reports, yielding the closed-form bound:

`t_N = clip(5N · binom(10129, 129) · ρ^129)`.              (T)

Failing to collect `L` accepted values within `C_acc` candidates forces at least `129` rejections, bounded by taking a union over rejection subsets. Up to `31` extra buffered prefetch words enter `C_raw`, `T`, and byte budgets without enlarging the failure probability. Re-expanded streams reuse cached candidates with no extra tail cost, while physical recomputations still count toward call/byte totals:

`Q_int ≤ 7N + 4C_init,L + 6C_init,R + C_msg,L + C_msg,R + C_finish,R`.

Descriptors, physical invocations, accepted fields, and raw bytes are kept strictly distinct. Adopting the strict-PPT formulation adds `t_N` explicitly rather than claiming strict runtime while silently truncating geometric loops.

### 3.1 Public 96-Bit Key Tag: Information Bound vs. Standard SHA One-Wayness

Because the setup publishes `vdaf_key_tag = prefix96(SHA256(K))`, withholding `K` does not preserve `128` bits of conditional entropy, invalidating naive `2Q/W` key-guessing formulas. This correction is retained without altering earlier historical budget records.

First, without extra SHA assumptions: for each 96-bit tag realization, pre-hit RO responses are simulated via the hidden key-handle; at most `G5_ext` external candidates appear. Summing over at most `2^96` fibers yields:

`k_info = clip(2^96 · G5_ext / W) = clip(G5_ext / 2^32)`.

This average hitting bound requires neither uniform tag behavior nor deriving secrecy from CR. It can saturate quickly and never certifies 128-bit integrity on its own.

Optionally, adding an **explicit standard one-wayness assumption** `Adv_SHA256^OW128(T_ow, Q_ow, B_ow)`: given `h = SHA256(K)` for uniform `K ← {0, 1}^128`, the adversary wins by outputting any 16-byte `k` with `SHA256(k) = h`. This is a plain random-preimage assumption, distinct from 96-bit prefix collision finding and not derived from SHA collision resistance.

The reduction receives `h`, passes only `prefix96(h)` to the `C` adversary, and lazily answers internal honest `U5(K, nonce)` calls by `(hidden-handle, nonce, offset)` in the same RO table while running all remaining usages honestly. Whenever the adversary issues an external `U5` query on 16-byte candidate `k`, the reduction first evaluates `SHA256(k)`: if it equals `h`, it outputs `k` and wins `OW128`; otherwise `k ≠ K` is certain and the standard external RO table answers. Because the first true-key query wins immediately without index guessing, there is no multiplicative `G5_ext` loss. This reduction holds provided `C`-visible leakage of `K` consists strictly of the public tag and `U5`, as verified in Document 03 (private admin configs and role DBs remain hidden).

Resources satisfy `Q_ow ≤ Q_sha + G5_ext` and `B_ow ≤ B_sha + 16 · G5_ext`, with `T_ow` covering full wrapper/native simulation, candidate hashes, and table maintenance. Since the two independent bounds hold simultaneously:

`k_tag = min(k_info, Adv_SHA256^OW128(T_ow, Q_sha + G5_ext, B_sha + 16 · G5_ext))`.

Without the extra `OW128` premise, `k_tag = k_info`; one never zeros out `Adv^OW128` or treats it as verified by file tests.

### 3.2 Experiment C Validity and Honest Failures

When the verification key is properly randomized and hidden from `C` aside from `vdaf_key_tag`, with `P_att` distinct protected first-prepare attempts and `Q` covering all offline grinding, applying `k_tag` to both key-replacement hops in Document 03 gives:

`v_N = clip((Q + P_att) · 10256 / q + 2k_tag + (2P_att + Q)² / W)`.   (V)

Here `10256 / q` combines `10002 / q` (invalid input polynomial) and `254 / q` (forged gadget polynomial), alongside the two key-replacement hops and joint-seed birthday/grinding bound. Single-proof mode never squares `10256 / q`. Under the pure information-theoretic branch `k_info`, setting `Q` conservatively gives the looser `2Q / 2^32` term, displayed transparently rather than hidden behind a PASS label; the conditional `OW128` branch gives a meaningful bound while still avoiding claims of unconditional 128-bit security. Under `P` and `P+A`, the corrupted role knows `K` and privacy guesses unannounced nonces instead, leaving `Q5 / W` in `b_N` unchanged while never claiming non-`H` output validity via `(V)`.

**Honest Root Failures.** Conditioned on fresh honest native randomness, across `N_h,p` distinct honest prepared reports, the root-abort probability is at most `clip(128 N_h,p / q)` (shared `r` across both roles counts once, with public RO pre-queries already bounded). This tracks availability/failure rather than privacy loss, and promises no completion under network drops or permanent denial of service. Groth16 affine exclusions are tracked separately by `g_aff`. None of these failures cause unsound acceptance, nor are aborts hidden by post-selection.

## 4. C: Statement Integrity Over All Prefixes

**Theorem (Closure Integrity C).** Under Experiment `C` of Document 01 and all explicit premises of Documents 02–06, there exist primitive reductions such that:

`ε_C ≤ clip(B_C + v_N)`.                             (C)

*Proof.* Along any prefix avoiding bad events `B_C` and `v_N`, Document 02 provides a valid R1CS assignment for every fresh statement outside `H`/`W`/`E`; `H` holds pinned honest sources, and malicious owners' own signatures never constitute knowledge. Because canonical `STATE` messages lie strictly below `ℓ`, distinct openings would break commitment binding `c`; all coordinate bounds, squared distances, and mask carries lie strictly below `p`, lifting field equations to exact ADWC integer relations. Induction over all events in Document 05 maintains closed `L` dependencies, authentic `head`/`K`, and monotonic quotas. By `(V)`, both honest native outputs sum to a valid one-hot vector; masked-moment receipts are computed solely from the same retained output, and `F` is injective on `E = {e_0, ..., e_D}`, tying each reconstructed cell index to the certified claim. Durable reservations and bound payloads on every honest exit require complete `P = L_s`, `R = M_s = eligible(L_s)`, and matching retained links, and failures/crashes never roll back exposed states, pinning every first exposure to the unique locked `R`.

Before writing PostgreSQL batches, per-report counts cast via `i64::try_from`, and collection checks validate aggregate `report_count ≤ 2^63 − 1 < q`, ensuring non-negative per-bin counts strictly below `q`; thus successful Decoder outputs return exact integer histograms rather than values wrapped modulo `q`. Future expansion of batch count formats requires re-proving non-wrapping. Atomic durable storage, honest service execution, and compiler/ISA faithfulness remain explicit premises rather than probabilities covered by `(C)`; permanent stalls, disk corruption, or malicious-role share forgery lie outside `C` integrity. □

## 5. A, P, and P+A: Full-View Online Privacy Theorems

For each `X ∈ {A, P, P+A}`, run the online simulator of Document 04: `Sim_A` takes no aggregate interface, while `Sim_P` / `Sim_(P+A)` query `O_C(R)` once upon authorized first exposure of complete `R` and synthesize the honest aggregate via:

`V_h(R) = O_C(R) − Σ_(j ∈ R \ H) e_(x_j) − Σ_(i ∈ R ∩ H) v_(c,i)^orig + Σ_(j ∈ R \ H) w_(h,j)`.

Challenge ciphertext budgets are `C_A = 4N + E_enc,A` and `C_P = C_(P+A) = 2N`. Each fresh HPKE encryption counts as one hop (cached byte reads add `0`, re-encryptions add `1` each). Indexing challenges by recipient key:

`H_X = Σ_(j=1)^(C_X) Adv_HPKE,k(j)^IND-CCA2(T_red,j, 1, D_hpke[k(j)], L_hpke[j])`.

Each single-challenge IND-CCA2 game fixes single-shot Base mode (`X25519/HKDF-SHA256/AES-128-GCM`) with full `(info, AAD)` tags and bans decrypting the exact challenge tuple. Document 04's origin and context checks route identical challenge tuples exclusively to their authorized `H` handle while decrypting modified tuples `(AAD, RID, key, info, enc)` honestly via the CCA oracle. All internal randomness and decryption bytes count toward the challenge budget.

To account conservatively for routing bad events across adjacent hybrids without claiming an unproven master coupling, enumerate `C_X` cipher hops plus ten ordered macro hops: ① source-proof sampling; ② native nonce deduplication; ③ initial RO programming; ④ measurement/proof shares and parts programming; ⑤ removing unknown prover coins; ⑥ FLP full-verifier substitution; ⑦ coupled hidden points and receipts; ⑧ raw candidate trace coupling; ⑨ business and first-exposure post-processing; ⑩ strict-PPT truncation. Every lossy native sub-hop in Document 03 receives dedicated routing endpoints alongside `b_N`. Each hop between two adjacent hybrids removes routing bad events on both sides (`≤ 2B_X`), yielding total endpoint factor:

`M_X = 2(C_X + 10)`.

Within a single fixed world `b`, the triangle inequality across all hybrids yields:

`Δ_X(b) ≤ e_X = clip(M_X B_X + H_X + b_N + t_N)`.         (P1)

Identity and affine exclusions already reside inside `B_X` at every endpoint. SHA-256 retains a single unified call ledger per endpoint without fabricating independent random functions across hops.

Both admissible worlds share `μ`, and for `P`/`P+A` also yield identical `O_C(R)` at every authorized first exposure (whereas `A` requires no equal sums). Because each simulator depends solely on those public/authorized inputs, fresh coins, adversarial messages, and internal state, `Ideal_X(0)` and `Ideal_X(1)` are identically distributed:

`Adv_X^two-world ≤ clip(e_X(0) + e_X(1)) ≤ clip(2e_X)`.     (P2)

*Joint View and Timing Justification.* Document 04 co-samples commitments, source proofs, ciphertexts, and native verifiers/receipts. For `P`/`P+A`, `m_h = T − F(v_c^orig) − r_c` makes the adversary's moment check inspect only its own original share; for `A`, `(T, m_0, m_1) = (U, V, U − V)` is exact without invoking any aggregate. Commit/abort/error outcomes, business DB/WAL/backups, and public wire lengths derive causally from the same simulated state, never peeking at real secret verdicts or timings. Document 03 attaches geometric rejection counts consistently in the shared RO table, Document 05 aligns transaction rollbacks, exact journals, and durable send ordering, and timeouts in the standard executor are causal post-processing of simulated work and exogenous scheduling. Induction covers every prefix including post-exposure collection failures, while excluding local pre-input-ready proving time, physical side channels, and unverified hardware. □

## 6. Computable Ledger, Negative Controls, and Scope

The [machine-readable composition contract](composition-budget-contract.json) instantiates every term above using exact integers and rational `Fraction` arithmetic rather than floating-point security claims. The standalone checker [source omitted from this derivative] verifies consistency across the specialized contracts, bounds/monotonicity, all three keys, endpoint factors, the four resource classes, and counterexamples; illustrative evaluations do not set primitive advantages to zero to claim total system security or measured attacker budgets.

Full G4b acceptance signifies that the complete mathematical arguments, explicit ledgers, source-level refinements, and negative controls required by this contract are finished and validated across these exact documents; mathematical proofs are not mechanized in a proof assistant, and development setups carry no production ceremony certification. Parallel G3 fixes, G5 native extensions, G6 experiments, and manuscript gates sign off independently. Frozen G4a historical files remain untouched, and unrelated G3 test-helper drift remains isolated rather than treated as protocol source for these theorems.
