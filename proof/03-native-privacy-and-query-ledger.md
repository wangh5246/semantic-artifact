# G4b: Native FLP, Privacy Simulation, and Complete Query Ledger

Date: 2026-10-18. Target: the accepted G4a `janus-v5-g4a/vendor/prio` instance (Prio 0.16.8 / VDAF-08, single task, pre-fixed verification key, two aggregators, `TimeInterval`, `NoDP`, `q_release ≤ 1/task`). This document does not modify G4a, source code, assets, or historical runs. The machine-readable budget interface is [native-budget-contract.json](native-budget-contract.json), and integration into full business views appears in [Document 04](04-full-view-simulation.md).

Status: **PROVED_IN_DECLARED_MODEL**. Below we directly prove abort-aware strong HVZK for this concrete FLP instance, active-peer two-party native simulation, rejection-sampling raw traces, and itemized query bounds, rather than assuming "native privacy already holds". The RO, honest setup, underlying primitives, and standard executor are explicit premises; all numeric terms derive from concrete games under those premises, separating integrity, honest failures, and privacy loss.

## 1. Version and Concrete Parameters

DPRS23 revised full text (2024-09-25) [source omitted from this derivative] has SHA-256 `016eb1e83902d30eebc0836b5ca736c40e1bed10841fbc2e4cb5a1f0c447ab98`, citing its §2, Theorems 1/2, and §C.1/C.2 rather than unrevised robustness bounds. Because page 14 writes `s > 2`, §4 here supplies the explicit `s = 2, t = 1` derivation. We also cross-checked [VDAF-08](https://www.ietf.org/archive/id/draft-irtf-cfrg-vdaf-08.html) and [BBCGGI19 author-archived proceedings](https://people.eecs.berkeley.edu/~henrycg/files/academic/papers/proofs-secret-proceedings.pdf); the latter's Theorem 11 / Corollary 14 renumber the full-version Theorem 4.3 cited in source comments, and §2 directly handles the fact that final validity is not solely the last gadget output. Direct ePrint full PDF fetch returned HTTP 403 and is logged honestly in read records [source omitted from this derivative].

Concrete `flp/types.rs:320–472` and `flp.rs:229–500, 590–746` specify:

| Quantity | Concrete Value / Derivation |
| --- | --- |
| native field | `q = 340282366920938462946865773367900766209`, `W = 2^128` |
| input/output | `d = 10001`: indices `0..9999` plus sentinel `10000` |
| gadget | Single `ParallelSum(Mul, 100)`, arity `a_g = 200`, degree `2` |
| gadget calls | `ceil(10001/100) = 101`, last chunk holds `1` real input and `99` fixed padding pairs |
| wire interpolation roots | `m = next_power_of_two(1 + 101) = 128` roots of unity |
| wire / gadget degree | At most `127` / `254` |
| proof / verifier | `200 + 2(128 − 1) + 1 = 455` / `1 + 200 + 1 = 202` field elements |
| joint / prove / query coins | `2` / `200` / `1` field elements; single proof |
| shard independent seeds | Helper measurement, Helper proof, two role blinds, prove seed (`5 × 16 B` seeds) |
| tag | `08 || 00 || 00000003 || u16BE(usage)`; alg class `0`, Histogram ID `3` |
| public key tag | `vdaf_key_tag = int(SHA256(verify_key)[:12])`, at most 96 bits (metadata only, not an uplink XOF domain tag) |

`new_histogram_multithreaded` alters parallel gadget scheduling only while preserving identical algebra and tags. `AggregationParam = ()`. Actual range checks omit the extra `r` multiplier shown in draft-08 pseudocode; all bounds below follow the frozen Rust code rather than draft examples.

## 2. Concrete Strong HVZK: Zero Distance Including Abort

Let valid encoding be `x = e_I ∈ F_q^d`, with independent uniform joint coins `(a, b)` and uniform query coin `r`. The validity circuit evaluates:

`R_x(a) = Σ_(j=0)^(d−1) a^(j+1) x_j(x_j − 1)`, `S_x = Σ_j x_j − 1`,

`V_x(a, b) = b·R_x(a) + b²·S_x`.

For every valid `x` and all `(a, b)`, `R = S = V = 0`. Each chunk gadget evaluates `G(z_0, ..., z_199) = Σ_(u=0)^99 z_(2u) z_(2u+1)` on input wires `(a^(j+1) x_j, x_j − 1)`, padded in the final chunk with `(0, −1)` and zero-padded at the `26` unused interpolation nodes. `ProveShimGadget` samples `z_l ← F_q` independently per wire at node `0`, with remaining nodes fixed by actual wires. Writing `f_l` for the interpolating polynomials, the honest proof consists of `{z_l}` and the `255` coefficients of `H(X) = G(f_0(X), ..., f_199(X))`.

Let `Ω` be the `128` roots of unity and `λ_0(r)` the node-`0` Lagrange basis polynomial. For `r ∉ Ω`:

`λ_0(r) = (r^128 − 1) / (128(r − 1)) ≠ 0`,

`f_l(r) = λ_0(r) z_l + c_l(x, a, r)`.

Thus for **every fixed** `x, a, b, r ∉ Ω`, the `200` values `{f_l(r)}` are i.i.d. uniform over `F_q` (not merely equal on marginal average). The full verifier message is:

`Σ = (V_x(a, b), f_0(r), ..., f_199(r), H(r))`.

An honest proof sets the first coordinate identically to `0` and the last to `G(f_0(r), ..., f_199(r))`. The exact simulator samples uniform `a, b, r`, and if `r ∉ Ω` samples independent `U ← F_q^200` and outputs `(a, b, r, (0, U, G(U)))` without knowing `I`, preserving exact joint correlation between `a, b, r` and `Σ`. Even though final validity combines all `101` gadget outputs plus input sum-check rather than reading only the final gadget output, it vanishes identically for all valid `x`, so this distributional proof covers the source code verbatim.

When `r^128 = 1`, `Type::query` returns deterministic `FlpError::Query` without resampling `r`. The simulator returns the identical error whenever uniform `r` hits `Ω`, caching on `(key, nonce)`. Therefore:

`δ_FL,abort = ||View_FL,abort(x) − Sim_FL,abort||_1 = 0`.

This matches DPRS strong HVZK extended with the root-abort symbol (factor-2 vs. factor-1/2 TV conventions agree at zero). Conditioning on `r ∉ Ω` gives the exact non-abort distribution too, but **conditional non-abort may never be misrepresented as zero-error completeness for uniform source `r`**. An honest report's per-Query root failure probability is:

`p_root = 128 / q ≈ 3.76158 × 10^−37`.

This counts availability/abort probability, not privacy leakage. In joint native execution with random-oracle pre-queries or nonce collisions, those events are handled by §5 budgets rather than re-conditioned away.

### 2.1 Distributed Query Constant Split

The codebase evaluates `Query(x, π)` non-homogeneously by scaling constants by `1/num_shares`. Denoting the `s`-share query with constant `1/s` by `Q_s(x_s, π_s; a, b, r)`, interpolation, polynomial evaluation, and validity checks are linear in `(x_s, π_s, 1/s)`:

`Q_2(x_A, π_A) + Q_2(x_R, π_R) = Q_1(x_A + x_R, π_A + π_R)`.

Each coordinate adds directly: seed nodes and gadget wires sum linearly, `(x_A − 1/2) + (x_R − 1/2) = x − 1`, the two `−1/2` paddings sum to `−1`, sum-check constants combine to `−1`, and `Query` reads gadget values directly from proof coefficients without multiplying local secret shares. Hence this identity holds for arbitrary inputs/proofs regardless of whether `Decide` passes; for `r ∈ Ω` both roles hit identical simulatable root-abort. §4 relies on this exact linearity for `z_h = Σ − z_c^orig`.

### 2.2 FLP Validity and Explicit Accounting of Honest Failures

For a pre-committed invalid `x`: if `S_x ≠ 0`, `b R_x(a) + b² S_x` is nonzero of degree `≤ 2` in `b` for every `a`, failing detection with probability `≤ 2/q`. If `S_x = 0` while `x` is invalid, some `x_j(x_j − 1) ≠ 0` (since all-binary `x` summing to `1` over `d < q` would be uniquely one-hot), making `R_x` nonzero of degree `≤ d`, so `Pr[V_x(a, b) = 0] ≤ d/q + (1 − d/q)/q ≤ (d + 1)/q = 10002/q`.

Given `(a, b)`, a malicious prover chooses an arbitrary `455`-element proof yielding `f_l` and claimed degree-`≤ 254` polynomial `P`. If `P = G(f)`, verifier coordinate 1 equals `V_x(a, b)` and rejects whenever `V ≠ 0`; otherwise nonzero `P − G(f)` has degree `≤ 254`, accepting for uniform `r` (rejecting on `Ω`) with probability unconditionally `≤ 254/q` (tightened to `254/(q − 128)` only under non-root conditioning). Single-proof abort-aware soundness therefore satisfies:

`ε_FLP ≤ (10002 + 254)/q = 10256/q`.

Single-proof execution does not square this term. Native robustness must additionally bound offline joint-seed grinding and key-tag guessing (§6); Experiment `P` permits corrupted-role collusion and does not inherit two-honest-role output integrity.

## 3. Seven Usages, Four Counters, and Concrete Byte Streams

Write `U_i` for source usage `i`. Because DPRS's RO numbering differs from source `usage` numbers, rename explicitly: `(RO1, ..., RO7) = (U3, U1, U2, U4, U5, U6, U7)`.

| Usage | Seed and Binders | Outputs and First-Use Accepted Values per `H` Source |
| --- | --- | --- |
| `U1` measurement | helper `xseed`; `[agg_id=1]` | `10001` field elements; re-expanded cleanly across Helper init/Finish |
| `U2` proof share | helper `pseed`; `[num_proofs=1, agg_id=1]` | `455` field elements; Helper init |
| `U3` joint rand | `jseed`; `[num_proofs=1]` | `2` field elements; reused across role inits |
| `U4` prove rand | prover seed; `[num_proofs=1]` | `200` field elements; local client generation |
| `U5` query rand | pinned `verify_key`; `[num_proofs=1] || nonce16` | `1` field element; reused across both role inits |
| `U6` joint seed | fixed zero 16 B; two ordered joint parts | `16 B`; shared across sharding/init/prep merge |
| `U7` joint part | role blind; `agg_id || nonce16 || encode(inputshare)` | `16 B` per role (`2` total); canonical `10001 × 16 B` encoding |

Each TurboSHAKE invocation absorbs `u8(len(dst)) || dst8 || seed16 || binders` with injective fixed/prefixed fields so distinct usages never collide. All usages query **one unified** lazily extended table keyed by exact input bytes and offset. Because `task` is omitted from some native XOF binders, this proof pins a single `(task, key)` pair.

Accounting keeps four metrics strictly separate:

1. `Q_i`: total XOF input/extension calls for usage `i`, covering external pre-queries, internal source/role processing, and rollback recomputations; distinct descriptors are counted without substituting accepted field counts.
2. `A_i`: accepted field counts; first complete `H` expansion draws `10001 + 455 + 2 + 200 + 1 = 10659` accepted elements (`U6/U7` output seeds directly without rejection sampling).
3. `C_i`: physical 16 B raw candidates read, **including rejected words and unused words in 32-element prefetch buffers** (`C_i ≥ A_i`; re-expansions read the same sequence while physical work still enters the execution budget).
4. `B_i`: total RO output bytes (`16 C_i` for field streams, `16 B`/call for seed streams) plus absorbed bytes (`160016 B` share input in `U7`). Primitive/executor parameters use these exact byte counts.

`N = N_shard` counts all honest `H` packet constructions including unprepared reports; `N_prep` counts all distinct reports entering private preparation (including warmup, eligible-zero, failures, aborted prefixes, and non-`H` physical work). Helper exact journal retries and Leader recomputations on identical raw handles create no new logical source/query coins.

Because transaction rollbacks can rerun CPU work, journaling never caps physical invocations at `1`. Writing `C_init,L, C_init,R, C_msg,L, C_msg,R, C_finish,R` for actual calls including retries/rollbacks:

`Q_int ≤ 7N_shard + 4C_init,L + 6C_init,R + C_msg,L + C_msg,R + C_finish,R`.

Stage-level breakdowns appear in `native-budget-contract.json`. The `≤ 20` XOF-init figure holds only for a clean single execution without retries — it is **never a runtime or adversarial budget cap**. On the Helper, the explicit first-input/response journal rejects changed requests prior to private processing; on the Leader, `leader_continued` executes outside the final write transaction before `writer.write + release_aggregation_job` atomically enforces lease token/expiry fencing so at most one transition commits. Uncommitted or stale-lease Leader attempts can therefore receive **distinct** Helper responses without failing pre-computation, while fixed `(body, report, key, nonce, raw share, committed state)` keeps the exact same underlying native random variables (§4 simulates those extra peer responses while charging all physical work).

## 4. Two-Party Active-Peer Native Simulation Algorithm

Maintain a task-wide RO/cache/nonce ledger, fixing statically corrupted role `c` and honest role `h`. `H` holds marked honest-source reports only; non-`H` reports are decrypted legitimately per Document 04 and executed natively.

For each `H` entry, sample uniform `nonce n`. If `c = Leader`, sample explicit measurement/proof share vectors; if `c = Helper`, sample `xseed/pseed` and expand from cached `U1/U2` streams. Either way `v_c^orig` is explicitly known to the simulator with no honesty assumption on `c`. Sample blinds/parts/`jseed` maintaining `U6/U7` consistency and pre-program the corresponding RO entries prior to public release, charging programming collisions under §5.

Invoke §2's exact strong simulator for `(a, b, r, Σ)`. If `r ∈ Ω`, cache the real `FlpError::Query` without creating verifier/receipt handles. Otherwise run real `Q_2` on the corrupted raw share to get `z_c`, setting `z_h = Σ − z_c`. For arbitrary active-peer inputs `(z'_c, parts, seed)`, the simulator evaluates real PingPong `Decide(z_h + z'_c)` and seed equality using known simulated state, emitting faithful `Continue`/`Finish`/failure outcomes (or clean `Finish` projections where verifiers are omitted).

This full-verifier simulator covers arbitrarily many differing Helper responses seen during uncommitted Leader retries: under fixed `(report, body, key, nonce, raw share)`, honest init uses identical joint/query coins and the same `z_h`, so every `Decide(z_h + z'_c)` and seed check is efficient adaptive post-processing of the **identical `(Σ, z_h)`** without consuming fresh `N_shard` or independent FLP randomness, while physical retries, visible errors, and timings enter the budget and only the unique committed transition commits/exports.

Upon honest `Finish`, create only an output handle carrying identity-truncated `v_h = e_I − v_c^orig`, with active peers affecting completion/errors rather than valid output values. Compute masked receipt `m_h = T − F(v_c^orig) − r_c` (Document 04) without opening handles; honest aggregates assemble via Document 04's `H`/non-`H` identity solely after authorized first exposure of complete `R`.

DPRS §C.2 specializes cleanly to `s = 2`: there is a single honest `z` (`v_h` via helper vector subtraction when `c = Leader`, or uniform Leader vectors with programmed Helper seed shares when `c = Helper`), `z_h = Σ − z_c`, and an identity wrapper. Extensions allowing per-source inputshare changes, key/nonce swaps, fresh independent query coins, or cross-report hidden-seed reuse lie outside this scope.

## 5. Per-Hop Privacy Loss and Hidden Seed Ledger

Moving from one world to the final simulator, let `Q = Σ_(i=1)^7 Q_i` conservatively upper-bound all internal and external invocations, with `κ = 128` (`W = 2^128`), applying DPRS §C.2 fresh-input programming atop §7's concrete raw streams (indexed by source usage numbers):

| Hop | Single-World Loss Bound and Reason |
| --- | --- |
| nonce deduplication | `N²/W`: honest nonce birthday collisions (malicious `RID`s not treated as uniform) |
| initial `joint/prover/query/seed` RO programming | `N[Q4 + 2(Q3 + Q6 + Q7) + Q5]/W`: collision on prior RO entries guessing hidden seeds/blinds or unpublished nonces |
| measurement/proof/part share randomization | `N[Q1 + Q2 + 2Q7]/W`: `s = 2` Helper seed and both blind programming collisions |
| dropping unknown prover coins for full verifier | `N·Q4/W`: guessing undisclosed prover seeds reveals un-preserved coins |
| full-verifier strong simulation | `N·δ_FL,abort = 0`: exact §2 conditional distribution, not an unproved native assumption |
| wire/receipt/timing post-processing | `0`: joint equations and caching proven in Document 04 |

Total auditable single-world bound:

`b_N = N·δ_FL,abort + [N² + N(2Q4 + 2Q3 + 2Q6 + 4Q7 + Q5 + Q1 + Q2)] / W`.

Substituting total `Q` gives `b_N ≤ [N² + 4NQ] / W`, tightening DPRS's generic `2N[δ + (Q + N)/W + 2Q/2^127]`. Root composition uses `2b_N` directly without multiplying `b_N` internally by the outer endpoint factor `M_X`, while assigning two routing endpoints `M_X = 2(C_X + 10)` across all `C` HPKE hops plus 10 macro hops in Documents 04 and 07 so routing failures are never omitted alongside lossy native sub-hops.

Clip each term with `min(1, ·)`. Legitimate reads of already disclosed/known seeds query the programmed table without fresh collisions; hidden internal seed reuse is already absorbed into `Q` inside `N·Q_i/W` (with finer `n(n − 1)/(2W)` splits avoiding double counting). Pre-known fixed `verify_key` allows adversary choice of `K` while unannounced honest nonces keep `N·Q5/W` intact; pre-publication honest `RID` guesses are accounted separately under origin bounds in Documents 04 and 07.

## 6. Offline Grinding and Birthday Terms in Integrity (Experiment C)

In Experiment `C`, both roles are honest and `K` is sampled uniformly during honest setup, **hidden from malicious clients except via its public 96-bit tag `vdaf_key_tag = prefix96(SHA256(K))`**, fixed prior to nonces and sources (`Q` covers offline and internal queries). Write `P` for distinct legal first-prepare attack attempts over complete protected inputs. Substituting §2.2 into revised DPRS §C.1 and inserting two secret-key replacement hops using the exact public-tag reduction gives:

`ε_N,valid ≤ min(1, (Q + P)·10256/q + 2κ_tag + (2P + Q)²/2^128)`,

where without extra primitives `κ_tag = min(1, Q/2^32)`, or taking the minimum with the explicit SHA random-input `OW128` advantage below.

**Public-Tag Average Guessing Lemma.** For uniform `K` over `W` keys and public `Z = f(K)` taking `≤ 2^96` values (with no uniformity assumption on `f`), fixing external coins yields at most `G5_ext ≤ Q5` external 16-byte candidate keys `A_z` per tag realization in the lazy-`U5` game prior to first hit (`< Q5` honest `hidden-handle` calls excluded from `A_z`). Summing across tag fibers gives `Pr[K ∈ A_Z] = (1/W) Σ_z |f^−1(z) ∩ A_z| ≤ min(1, 2^96 G5_ext / W)`, so two hops contribute `≤ 2·2^96 Q5/W ≤ Q/2^31`. Source locations `g4a_native_stack.py:182` and `g4a_native_drivers.py:745` fix the concrete 12-byte tag.

**Standard One-Wayness Corollary and Reduction.** Define `Adv_OW128^SHA256(T_ow, Q_ow, B_ow)` as the success probability of outputting any `k'` with `SHA256(k') = h` given `h = SHA256(K)` for uniform `K ← {0, 1}^128` (a plain hash one-wayness assumption distinct from CR and not turning SHA into a random oracle). Given `h`, the reduction publishes only `int(h[:12])` to the `C` adversary, generates remaining parameters independently, simulates honest internal `U5` lazily by `(hidden-task-key-handle, nonce)` in the unified RO table (with §7 raw streams), runs all honest roles/authority/DB honestly, and inspects every external `U5` candidate `k`: if `SHA256(k) == h`, the reduction immediately outputs `k` and wins `OW128`; otherwise `k ≠ K` is guaranteed and the external RO entry returns cleanly. Prior to the first hash hit, the view couples identically to the real-key game with zero guessing factor (`G5_ext` loss avoided):

`κ_tag = min(1, 2^96 G5_ext / W, Adv_OW128^SHA256(T_ow, Q_sha + G5_ext, B_sha + 16 G5_ext))`.

`derive_query_rands:534–542` and `prepare_init:1303` confirm `K` enters only `U5` inside honest roles while `internal/test/add_task` returns only the 96-bit tag to control layers, preserving secrecy of `K` from `C`.

The complete game chain proceeds cleanly without assuming an uninstantiated native soundness oracle:

1. Each protected `(nonce, context)` admits at most one committed `prepare` branch (Helper journal caches exact retries; Leader recomputations share fixed state/coins), matching joint seeds at `Finish` for valid export while handling aborting branches cleanly (`≤ κ_tag` per key hop).
2. Replacing `U5(K, nonce)` by fresh uniform `r` costs `≤ κ_tag`, charging all failed/offline candidates in `G5_ext/Q5`.
3. `U6` (two ordered parts) and `U7` (role, nonce, full inputshare) forbid duplicate joint seeds and delayed preimage hits via `≤ (2P + Q6 + Q7)²/W` (`128`-bit birthday/union over all offline and online records, restoring offline `Q` omitted by naive `P²`).
4. Each fresh `U3(jseed)` pins total native input `x` deterministically from logged `U6`/`U7` inputs prior to sampling lazy `(a, b)`, reducing directly to §2.2 single-instance FLP soundness.
5. Guessing among at most `Q3 + P` fresh `U3` candidates gives `(Q3 + P)·10256/q`, adding via §2.1 constant linearity without needing a third aggregator; replacing `Q3, Q5, Q6, Q7` by `Q` gives `(V)`.

Pure information-theoretic `k_info` makes `Q ≈ 2^20` degrade to `≈ 2^−11` and saturates at `Q ≥ 2^31`, whereas the conditional `OW128` corollary supplies an explicit primitive reduction; neither claims unconditional 128-bit integrity, and honest root-abort probability across `N_prep` honest prepares stays tracked separately as `min(1, 128 N_prep / q)`.

## 7. Accepted Values and Rejection Traces: Exact Joint Programming

The PRNG prefills `32` little-endian 16 B candidates, accepting integers `< q` followed by Montgomery conversion (bijective with field elements). With `ρ = (W − q)/W = 516508834063867445247 / 2^128`, each accepted `Y_i` and preceding rejection count `K_i` in a fresh uniform stream obey:

`Pr[K_i = k_i, Y_i = y_i] = ρ^(k_i) / W = (ρ^(k_i) · q/W) · (1/q)`.

Independent vectors factor identically: generate `Y` from native/FLP hybrids, insert independent `Geom(q/W)` uniform `[q, W)` rejection words before each `Y`, encode as little-endian bytes, and pad unused words of the `32`-element prefetch buffer with uniform bytes — zero approximation loss (`N_candidate · ρ` error does not exist). Full candidate sequences, accepted offsets, and prefetch buffers cache by `(dst, seed, binders, raw-offset)` across `Finish`, rollbacks, exact retries, and subsequent queries, while adversarial/known seeds expand deterministically from the same table.

For strict-PPT reductions (without modifying the real runtime), each fresh stream caps candidate search at `C_acc = L + 128` words (buffer budget `C_raw = 32 · ceil(C_acc / 32)` billed to bytes and `T`):

`Tail(L, C_acc) = Σ_(j=0)^(L−1) binom(C_acc, j) (q/W)^j ρ^(C_acc−j)`.

The `≤ 31` trailing prefetch words add buffer bytes/steps without altering tail probability (`≤ binom(C_acc, 129) ρ^129`). Across at most `5N` fresh `H` streams of max `L = 10001`, total tail bound is `5N binom(10129, 129) ρ^129`, retaining the explicit strict cutoff rather than omitting geometric loop tails under strict-PPT claims.

## 8. Checks and Scope

`check_native_privacy.py` [source omitted from this derivative] verified finite-field `Prove/Query`, Lagrange identities, and raw rejection traces (`check-r1`: `235,824` exact `Prove/Query` cases; `2,176` constant-split queries; `4,225` rejection paths; `6,561` non-`H` aggregate identities plus negative controls; extended `check-r3`: `84,375` partial-chunk and zero-padding distributions, totaling `333,161` cases across `16` read-only pins, exit `0`). Exhaustive key-tag verification `check_public_key_tag.py` [source omitted from this derivative] checked `65,792` tag functions, `131,840` average-guess bounds, and `14,040` first-hit implications, formally recording withdrawal of legacy untagged `C` examples in `keytag-supersession` [source omitted from this derivative]. Read-only verification against frozen sources is logged in `delivery-check-r4` [source omitted from this derivative]. All abort prefixes, warmup, unprepared sources, rollbacks, and offline queries enter the budget; guarantees exclude physical GPS truth, DP, malicious authority, dual-role collusion, adaptive corruption, unpinned key rotation, and arbitrary hardware side channels.
