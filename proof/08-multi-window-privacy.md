# Multi-Window Shared-State Privacy: Conditional Joint Theorem (G4b Interface Extension)

Date: 2026-11-01. Status: **PROVED_IN_DECLARED_MODEL**. This extension formalizes §2(iii) experimental entities, observations, and successor coupling, §2(v) hop-by-hop verification, and the prefetch-aware macro ⑨ proof for multi-window releases.

Scope: contract-level multi-window interface extension for G4b under either the original 3-key source ledger or the `E′` 6-key extended source model; frozen Documents 01–07 and contract JSON files remain unmodified, and no `k`-release implementation or test suite is claimed. Conclusions hold strictly within the declared model and assumptions below. In the manuscript, this document supports predeclared multi-window privacy; the deployed codebase remains single-release (`q_release ≤ 1/task`), retained explicitly as a theorem boundary.

## 0. Executive Summary

The existing G4b machinery is already **full-execution scoped**: simulator tables persist across prefixes ([Document 04](04-full-view-simulation.md) §2), state points sample once per history node (Document 04 §1, supporting cross-window chains per [Document 01](01-security-games-and-ideal-interface.md) §2), equal-sum requirements quantify over "every authorized first-exposure complete `R`" (Document 04 §1), and all budgets `N, S, V, Q` bound the entire finite execution ([Document 07](07-composition-and-explicit-bounds.md) §1). `E ≤ 1` is a **deployment/contract constant** (`max_visible_cohorts_per_task: 1`; codebase `q_release ≤ 1/task`), which does not by itself imply multi-window security. §2 establishes hop-by-hop and event-by-event that this bound relaxes cleanly under our multi-window (MW) contract without generalizing to arbitrary output families. Specifically, the extension parameterizes the source ledger $\mathcal L \in \{\mathcal L_{\rm base}, \mathcal L_{\rm ext}\}$, separates the internal query ledger $A_{\rm queried}$ from the visible exposure ledger $A_{\rm visible}$, formalizes full-execution hybrid coupling `(CPL)` via kernels `K1–K3` and prefetch-aware macro ⑨, and quantifies cubic ($t^3$) scaling in the extraction-routing product $M_P \cdot g_{\rm coll}$.

**Explicit Scope Limitations**: Theorem-level contract guarantee only. Deployed code remains `q_release ≤ 1/task` with no multi-window implementation or tests; joint leakage exposes all released window histograms together without claiming differential privacy.

## 1. MW Game: Joint Privacy Experiment Across k Predeclared Release Windows

Fix the parties, static corruption set, execution layer, and budget semantics of [Document 01](01-security-games-and-ideal-interface.md), instantiating setup/sources via the ledger chosen in §3 with the following contract extensions. Below, `R` denotes the complete typed cohort context carrying `(task, profile, selector, window, snapshot)` (`κ` in §2(iii)), never a bare context-free RID set:

- **Predeclared Window Schedule**: Schedule `W = (w_1, ..., w_k)` (per-window task/selector, scheduled slots/eligibility, delivery boundaries, and deadlines) is fixed prior to Setup inside public skeleton `μ`; scheduling is non-adaptive and the adversary cannot spawn new windows dynamically. All windows share one `(task, profile, key)` namespace; cross-namespace extensions lie outside scope.
- **Admissible Histories**: For each honest owner, both complete admissible histories `H_0` and `H_1` span all `k` windows, obeying ADWC step constraints and real anchors throughout; cross-window continuation resumes strictly from committed heads (already present in Document 01 §2). State commitments sample once per history node with `prev`/`K`/aliases reusing original handles (Document 04 §1).
- **Separated Query and Exposure Ledgers**: Following Document 05 prefetch semantics, the simulator may query and cache the ideal output of complete `R` once **upon preparing the first transmission** of `R` (withholding unused query answers from the adversary). Consequently:
  - Every actual exposure implies a prior authorized query for `R` (`query time ≤ first send`), whereas **the converse does not hold** — crashing/aborting after prefetch leaves a cached "queried but unexposed" entry.
  - Each distinct `R` is queried at most once (reused across retries on identical snapshots); each window `w_j` admits at most one locked complete cohort $R_{w_j}$, giving **$E_q \le k$ distinct queries** independent of exposure outcome (exposure ledger `X` tracks leakage separately).
  - Document 01 §6's "no query before first exposure" is the stricter non-prefetch variant; the MW theorem holds under both variants, stated definitively under Document 05 prefetch semantics.
- **Leakage Profile**: Distinguish the **query ledger $A_{\rm queried}$** (all ideal answers retrieved internally, including unexposed prefetches) from its **visible subsequence $A_{\rm visible}$** (histograms of windows whose first decryptable share was actually sent). Permitted execution-prefix leakage is $L_{\le t} = (\mu_{\le t}, A_{\rm visible,\le t})$. For `A`, $O_A = \emptyset$ unconditionally.
- **Multi-Window Exposure Equivalence (Challenge Condition for `P`/`P+A` Only)**: Both admissible worlds yield identical $O_C(R^0_{w_j}) = O_C(R^1_{w_j})$ (including sentinels) for all $j = 1, \dots, k$. This is a verbatim instantiation of Document 04 §1 per window and is a challenge condition borne by the environment (not applicable to `A`, which proceeds independently via §2(iv) and §3 without requiring equal histograms).

## 2. Full-Execution Hybrids, Observational Relation, and Multi-Window Proof

This section proves the interface-level extension under Document 01's bounded execution, static corruption, and executor semantics without treating Document 04's single-release statement directly as a multi-window theorem. §2(iii) defines experiments and exact coupling; §2(v) verifies every hop. Mutual exclusion across windows applies solely to logical reports and retained handles, allowing shared owners and `STATE` history chains. All resource caps cover the full execution including failures and uncommitted retries.

### 2(iii). Experimental Entities, Rel_b, and Successor Coupling Across Three Kernels

**A. Context and State Space.** Fix world `b`, observer `X ∈ {P, P+A}`, history `H_b`, public skeleton `μ`, static corruption set, and budget `B` (`μ` excludes secret verdicts or timings). Each locked window pins one unique complete cohort `R_w`; a logical report's `window` never mutates, each retained handle belongs exclusively to one window, and shared history references use global tables.

Define the full-execution machine family $J_b^{(r)}$, indexed by the number `r` of substitutions applied in §2(v)'s fixed order, starting at $J_b^{(0)} = \mathsf{Real}_b^{\rm MW}$. Intermediate hybrids preserve real encodings and business checks while using internal semantic overrides for already-replaced objects (never replacing real branch logic with blanket "success"). Each state is:

$$s_r = (V, D, U, \Gamma_r, I, \mathbf{c}, \eta, \sigma).$$

- `V`: observer-visible message/table prefixes, role-known inputs and head commitments, and public versions/eligibility/status (excluding honest roles' private DBs or plaintext openings; `P+A` adds honest authority business views without authority private signing keys).
- `D`: durable control state — per-window `P_w, R_w, L_w, L_{s,w}, M_{s,w}, A_{L,w} = eligible(L_w)` plus complete `body/job/protected-step/tag/consumed` links, `install/permit/freeze/abort`, reservations, and payloads; globally `Origin/RID/body`, `head/version/history/anchor`, `quota`, certs, Helper journals/tombstones, Leader jobs/leases, and `outbox/send-intent`, following Document 01 §3 and Document 05 §§2–5.
- `U`: volatile control and uncommitted computations (Leader retries, transaction stacks, lock waits, thread stacks, network buffers) — presence in `U` never counts as committed/`retained`/`apply`, and fixed reports' underlying native random variables never resample when `U` clears.
- $\Gamma_r$: all cryptographic tables from Document 04 §2 plus level-`r` objects: `H/W/E`, typed namespace/source logs, HPKE full tuples/overrides, RO tables (`usage/offset/raw candidates/prefetch suffix`), nonces, `STATE` nodes/aliases, native descriptors, and retained handles (separating physical calls from logical descriptors). Each native descriptor pins $(v_c^{\rm orig}, z_c, \text{seeds/blinds/parts}, a, b_{jr}, r_q, \Sigma, z_h, T, r_c)$ where `b_jr` denotes joint randomness; per Document 03 §4 L116, corrupted raw share/seeds generate honestly with `z_c = Q_2(corrupt raw)` and `z_h = Σ − z_c`, caching root-aborts identically.
- `I`: private ideal ledger and exposure tracker. **$A_{\rm queried}$ stores answers at most once** as persistent map `κ → (R_w, y_w)` with `y_w = O_C(R_w)` (`|dom(A_queried)| = E_q`). `X` records actual decryptable-send `κ` and timestamps; `A_visible` projects `A_queried` onto `X` without duplicating storage. Unmodified real early hybrids maintain ghost accounting without leaking oracle values into the reduction.
- `c`: split into protocol execution counters `c_exec` (`T, Q, bytes`, crypto ops, retries enforcing Document 01 §7 protocol halt rules) and internal reduction counters `c_red` (extraction, table work, oracle simulation, prefetch summation — excluded from real service wall clock yet covered by Document 07 §1's `T_red` and common `Q`/byte caps so reductions never induce asymmetric internal halts).
- `η, σ`: internal adversarial state and executor/scheduler state (`η` acts strictly on visible `Obs`, never reading `I`).

The five-tuple cache key $\kappa = (\text{task}, \text{profile}, \text{selector}, \text{window}, \text{snapshot})$ is an **MW contract-level refinement** (without claiming multi-selector support in frozen code), derived from Document 01 §3 typed records plus Document 01 §3.7 / Document 05 §2 unique durable `selector/snapshot` bindings so retries reuse the same `κ`, mismatched digests reduce to SHA/authentication bad events, at most one `κ` exists per window (`|dom(A_queried)| ≤ k`), and re-encryptions enter `E_enc,A`.

**B. Non-Empty Initialization.** `Init_r` executes Document 01 §1 Setup using §3's chosen source model (`E′` A1–A4 when extended), fixing keys/config/manifest, static corruption, permitted auxiliary CRS/source preludes (charging prelude work to tables/counters), `H_b`, `μ`, `B`, and zero counters. Enrollment/genesis initializes actual genesis nodes, registrations, and links matching public topology without importing post-run private DBs; if the initial prefix includes reports, each proceeds explicitly through Kernel `K1`. At terminal levels, genesis `STATE` nodes couple bijectively via prime-order subgroup sampling (except corrupted known openings), `I` domains start empty, `V` matches, establishing initial `Rel_b(s, z)` cleanly. Setup bad points, source failures, and generic collisions enter endpoint error terms without post-selection conditioning.

**C. Relation `Rel_b` and Observational Projection `Z`.** Between terminal reference state `s` and simulator state `z`, `Rel_b(s, z)` requires shared control structure/counters and all five invariants simultaneously (`Z` captures observationally sufficient projections rather than secret-share byte equality; `val_b` exists solely for proof accounting):

1. **(i)** Honest `STATE` history nodes share identical subgroup handles and consistent `prev/K/alias/head/version/quota` control records (real openings may differ; corrupted known openings preserved).
2. **(ii)** Each pinned `(report, body, task, key, nonce)` descriptor carries identical corrupted-side $(v_c^{\rm orig}, z_c, \text{seeds/blinds/parts})$, shared joint/query coins, `Σ`, `z_h = Σ − z_c`, and root-abort flag; Helper retries reuse journals while uncommitted Leader recomputations deterministically reuse **the exact same `(Σ, z_h)`** without resampling per attempt.
3. **(iii)** Each retained handle `u_i` from honest `Finish` shares identity, `session/tag`, and typed output links with $val_b(u_i) = \mathbf e_{x_i^{(b)}} - v_{c,i}^{\rm orig}$; non-`H` handles store decrypted real native $w_{h,i}$ with no complementary identity imposed; symbolic batch and membership maps `M` include each eligible handle once (`warmup ∉ M`).
4. **(iv)** When complete gates and retained links hold, `κ`'s bound payload sums handle valuations on the reference side and computes:
   $$V_{h,R} = y_w - \sum_{j \in R \setminus H} \mathbf e_{x_j} - \sum_{i \in R \cap H} v_{c,i}^{\rm orig} + \sum_{j \in R \setminus H} w_{h,j}$$
   on the `S` side — equal numerically and identically encoded in fixed canonical bytes, immutable for `κ`. `A_queried` initializes solely upon first send-preparation after valid reservation; `X` appends only upon decryptable send, and crashes never revert either ledger.
5. **(v)** All `Obs_X`-visible tables, replies, messages, known role state, and public `head` values are byte-identical under identical adversarial actions, executor coins, simulated work `τ`, `Post(τ, scheduler, coins)`, and protocol counters.

**D. Observations and Successor Coupling `(CPL)`.** Define $Obs_X(s) = (\text{granted } V, \text{head}_X, \text{sent outputs/public status})$ and augmented $Obs_X^+ = (Obs_X, \mu_{\le t}, A_{\rm visible,\le t})$, excluding unexposed `A_queried` and unsent payloads prior to actual send in `X`. Given `Rel_b(s, z)` and identical legal action `a` (adversarial query/message, scheduled honest source, or scheduler step), reference kernel `K_j` and simulator kernel $\widehat K_j$ yield coupling $\pi_{j,b}(s, z, a)$ matching both marginals such that:

$$\Pr_{\pi_{j,b}}[o_s = o_z,\ d_s = d_z,\ Rel_b(s', z')] = 1. \tag{CPL}$$

Here `c_exec` and modeled `τ` match identically (not raw unmodeled host CPU instruction counts), under identical-until-bad source/programming boundaries (diverting bad-event paths cleanly to `B_X` at each endpoint without post-hoc conditioning). Note carefully: **adjacent lossy cryptographic hops (HPKE, etc.) do not promise `(CPL)`** — those compare via full-trace distinguishers in §2(v), while `(CPL)` applies uniformly at the terminal replaced level without circularity.

**E. Construction and Preservation Across Kernels K1–K3.**

- **K1 (Source / Preparation / Control Progression).** Follows Document 01/05 validation order (`context`, origin auth, `body/RID`, `head/version/quota`, permit), sampling joint coins on fresh honest sources, restoring pinned `Γ` on existing descriptors, honoring `H` HPKE overrides, decrypting non-`H` legitimately, and routing fresh statements via `H/W/E`. Honest native preparation produces `(a, b_jr, r_q, Σ)` via Document 03 §4 (`r_q ∈ Ω` triggers identical root-abort; otherwise `z_c = Q_2(...)`, `z_h = Σ − z_c`, ensuring identical `Decide(z_h + z'_c)` and seed predicates across retries), co-samples uniform `T` and `m_h = T − F(v_c^orig) − r_c` (matching Document 04 §4's joint distribution and moment verdict `m'_c + m_h = T` for any `m'_c`), updates `Finish` handles with `val_b`, couples fresh `STATE` points bijectively via subgroup blinding, applies commit CAS and single-merge `Apply`, and couples observations `π_1` with `(CPL)` via **channel-wise conjunction**: `(a)` perfect commitment hiding, `(b)` same-variable receipt joint law, `(c)` post-HPKE override routing, `(d)` permit interface, `(e1)` exact Groth16 ZK plus charged affine/extraction routing, `(e2)` Document 03 §2 per-fixed-`x` full-verifier law and §4 active kernel, and `(f)` Document 01 §8 / Document 04 §7 execution post-processing.
- **K2 (Reserve / Bind).** Checks `L_s = P`, `eligible(L_s) = R`, `M_s = R`, and full retained links cleanly: failing gates emit zero ideal queries and identical errors; passing first reservation persistently binds `κ` and queries `y_w` privately once in `S` (matched identically on reference side from `H_b` and extracted/known non-`H` claims via `(iii)` sums — single window ownership avoids cross-window double counting while preserving earlier receipt identities). Re-executions on existing `κ` reuse identical cached bytes without a second query; invalid rebinds reject at public identity gates cleanly without creating secret-comparison oracles. Visible observations exclude private `y_w` and unsent plaintexts, proving `(CPL)` under `π_2`.
- **K3 (Send / Retry / Crash / Halt).** `Send` reads durable `(κ, bound bytes)`, encrypts with matching encryption coins (`P`/`P+A` outbound generated honestly), and updates `X` and `Obs^+` synchronously on first decryptable delivery (`re-encrypt` increments `E_enc,A` without fresh queries; lost ACKs preserve `X`; conservative `send intent` without confirmed delivery avoids false zero-exposure claims). Crash resets volatile `U` per identical scheduler while retaining durable `D`, `I`, and sent wire logs (`Helper` reads journals, `Leader` restores `(Σ, z_h)` from `Γ` and contends via lease without new sources); budget stops trigger identically on public counters (`01 §7`). **Conditional non-interference** of unconsumed prefetches holds causally conditioned on visible prefix, actions, control state, and coins: identity gates ignore plaintext, legal comparisons compare identical expressions, status checks use `EXISTS`, uncompressed fixed-length `BYTEA` keeps `τ` identical, and non-`Send` steps never leak cached `y_w` even when adversarial actions adapt to prior exposed histograms. Thus `π_3` satisfies `(CPL)`.

**F. Complete Event Classification and `3 × 5` Verification Matrix.** Granular steps partition cleanly (`stutter` keeps `L/M` fixed while charging physical CPU/RO/replies):

| Operation / Sub-operation (Doc 05 §5 & Doc 01 §7) | Kernel Class | Reads, Updates, and Observations |
| --- | --- | --- |
| Setup / enrollment / genesis / auxiliary prelude | Init / K1 | Initializes per `B`; fresh nodes/sources via K1 verifying initial `Rel_b` |
| Origin / Register / Lock / Install / Permit | K1 | Complete context, `P/R`, `head`/permit; emits certs, rejects, replies |
| Prepare / Continue / Finish / receipt | K1 | Fixed `Γ`/journal/lease/native state; real peer feedback, handle/tag |
| authority commit, role commit / Apply | K1 | CAS and single symbolic merge; certs, replies |
| Freeze & non-send phase controls | K1 | `L = P`, no active permit, full `apply`; phase/certs |
| Reserve / Bind / cache-gate re-checks | K2 | `κ`, complete `R` & links; internal query, existence/conflict |
| Send / re-encrypt / retry / ACK / transport drop | K3 | Fixed payload/`X`/outbox; wire messages and counters |
| Abort / timeout / crash / recovery / budget halt | K3 | Durable recovery map and counters; visible failure/timing |
| Read-only / lock-wait / tx-rollback stutter | Parent K1/K2/K3 | Preserves bytes/calls/timing and visible replies; uncommitted state unpromoted |
| External RO / group / hash / sig / legal non-challenge decrypt | K1 oracle sub-step | Corresponding `Γ` and `c`/`η`; real primitive answers, no extra business queries |

Verification summary across `K1–K3 × (i)–(v)`:
- `K1`: couples new `STATE` nodes & aliases (`i`), pins `Σ/z_h` & peer predicates (`ii`), sets world-`b` handle `val_b` & merges once (`iii`), leaves bound `κ` untouched absent `Bind` (`iv`), satisfies channel-wise `(CPL)` (`v`).
- `K2`: leaves `(i)–(iii)` untouched aside from reading full links/sum, computes & queries `κ` privately once while pinning retries (`iv`), keeps queries outside `Obs` with `(CPL)` including gate errors (`v`).
- `K3`: preserves durable state across crash rollbacks (`i`), restores Helper cache/Leader `Γ` (`ii`), retains durable handles (`iii`), preserves `(κ, bytes)` & updates `X` on send without rolling back query cache (`iv`), establishes conditional non-interference and `(CPL)` (`v`).

**G. Trace Induction.** Combining `Init` base coupling with `(CPL)` step extension ensures identical visible prefixes and next-step distributions for `(η, σ)` up to halting under finite `(T, B)`. Dropping witness annotations (`H_b`, openings, `val_b`) from $J_b^{\rm final}$ yields executable simulator `S` with identical visible views across incomplete reports, interleaved windows, and post-exposure failures. Finally, multi-window equal-sum equivalence across all `k` windows makes `Ideal(0)` and `Ideal(1)` identically distributed under shared `μ` and coins.

### 2(iv). Independent Zero-Query Branch for A

`A` never calls `O_C` and imposes zero equal-sum condition across windows. Following Document 04 §5 directly, `S_A` shares `STATE` aliases, samples independent `T, u` per report with `(m_0, m_1) = (u, T − u)`, executes non-`H` legitimately, swaps both roles' honest inputs/sidecars and visible outbound aggregates to equal-length dummy HPKE, keeps export status `EXISTS`-only and payloads fixed-length, preserves `Bind` presence/length abstractions without querying unknown aggregates, and lifts verbatim without depending on §2(iii)'s `P`/`P+A` lemma — expanding resource bounds by `E_enc,A` only.

### 2(v). Hop-by-Hop MW Embedding of Document 04 §6 and Prefetch-Aware Macro ⑨

**1. Fixed Hybrid Sequence and Reduction Context.** Follow the exact Document 04 §6 / Document 07 §5 sequence: macro ① (`sourceproof`), `C_X` individual cipher hops, macros ②–⑩, updating packets prior to first publication while leaving delivered packets untouched. Each $J_b^{(r)}$ composes A/B–F faithfully; fixed-`b` reductions know `H_b` to evaluate complete-`R` sums online when needed while excluding witnessless subset oracles (`S` drops `H_b` only at the final step). Private `O_C` prefetches happen strictly after durable reservation of complete `κ` at first-send preparation (`05` prefetch variant), billed internally to reduction `T_red` without altering service delays or wall-clock `τ`.

**2. Macro ⑨ Pre-Lemma: Early Query, Binding, and Observation Commute.** Following persistent reservation of `κ` at complete gates, compare three machines executing identical continuation context:
- `F`: sums pinned handle valuations from real execution, binds fixed bytes, and potentially sends.
- `E`: queries `y_w` privately at the identical gate, computes/binds per `(iv)`, and may fail prior to send.
- `L`: shares identical identity/control/length state with `E`, holding the unknown payload symbolically until actual first `Send` without exposing this deferral marker to the continuation context.

By `(iii)`'s summation identity, **`F` and `E` produce identical byte payloads on every execution reaching complete `R` gates**, not merely on collection success (non-`H` adds real `w_h` without importing `C` integrity; `Bind` retries produce identical bytes and identity gates reject swaps). Before actual first `Send`, `E` and `L` expose identical reservation state, payload presence bit, fixed length, public status/errors, business tables, and execution work `τ` (`K1/K2/K3` non-send `(CPL)` induction):
- *Failure between Reserve and Bind*: `E` may hold an internal unused answer while `F/L` reveal nothing; retries on `κ` reuse or defer the identical value cleanly (`A_queried` stays durable without allowing a second distinct query).
- *Crash/abort between Bind and Send*: matching presence bits, fixed uncompressed lengths, and public states leak nothing of un-sent `y_w`, while other windows proceed cleanly over shared tables.
- *First actual Send*: `L` materializes the exact same `E/F` bytes, appends `X`, and attaches `y_w` in `Obs^+`, invariant under later ACK drops/retries/re-encryptions.
- *Never sent*: query difference lives strictly inside unobservable ghost/simulator tables across all prefixes.

Deferring evaluation preserves `E_q` ledger accounting cleanly (`dom(E)` matches ghost count in `L`), allows arbitrary correlation between unexposed answers and earlier visible histograms, and preserves disjoint window handles. Consequently, **macro ⑨ preserves zero observational distance across ALL prefixes including aborts**, replacing Document 04 §7 L146 ("no aggregate query prior to abort") verbatim with: **unsent executions reveal no `κ` answer to observers; complete-gate send preparation permits one internal prefetch for `κ`, aborts preserve that query record, and recovery stays pinned to `κ`**.

**3. Hop-by-Hop Verification Summary.** Every hop removes routing bad events `≤ B_X^L` on both sides (`M_X = 2(C_X + 10)` total endpoints):

| Hop | Reduction Embedding Under `k`-Query / Shared Tables | Prefetch & Doc 04 §7 Causality | Self Charge |
| --- | --- | --- | --- |
| ① sourceproof sampling | Doc 02 exact reparameterization per typed source pre-publication; shared `H/W/E` across windows | Fixed-`b` reduction computes full `R` without changing proof oracle permissions | Math `Z_G16 = 0`; affine/extract in endpoint `B` |
| `C_X` cipher hops | One protected challenge per fresh ciphertext index, others self-generated; exact tuple override | Private full-`R` eval follows `F/E`; CCA tag/exclusion sets invariant under `k` queries | `Σ` single-challenge HPKE Adv = `H_X` |
| ② nonce deduplication | Full-task `N`-entry honest nonce table across all windows | Prefetch creates no new sources/nonces; adaptive RO pre-queries within `Q` | `N²/W` |
| ③ initial RO programming | Single unified `(usage, seed, binders, offset)` online table | Adaptive external RO queries stay within Doc 03 budget `Q`; no hidden verdict oracle | `N[Q4 + 2(Q3 + Q6 + Q7) + Q5]/W` |
| ④ share/part programming | Real corrupt shares/seeds with honest complement translation preserving `(ii)(iii)` | `Bind` real sums stay aligned via `F/E`; shared `STATE` reuses zero report seeds | `N[Q1 + Q2 + 2Q7]/W` |
| ⑤ prover-coin removal | Maps origin/RO sources cleanly per Doc 03; disclosed seeds hit existing table | Prefetch outputs are no prover-seed oracle; guesses stay in `Q4` | `NQ4/W` |
| ⑥ FLP full-verifier | Per-fixed-`x` strong simulation `Σ` including root-abort; shared `(Σ, z_h)` across peer replies | Works regardless of report window or release outcome; pre-query peer replies need no future info | `N δ_FL,abort = 0` |
| ⑦ hidden points/receipts | Once-per-node Pedersen bijection; exact `(T, m_h)` joint coupling with preserved `v_c, r_c` | Aliases shared cleanly; arbitrary `m'_c` identical verdict; independent of aggregate | `0` |
| ⑧ raw trace coupling | Caches rejected candidates, accepted values, and prefetch suffixes per stream | Multi-window retries reuse stream with work billed cleanly; `τ` from shared bytes | `0` (truncation in ⑩) |
| ⑨ business & exposure post-proc. | `K1–K3` + `F/E/L` lemma align control, `H`/non-`H` sums, bind, and send | **Re-proved here**: replaces "no query before abort" with prefetch non-interference + shared `κ` send | `0` |
| ⑩ strict-PPT truncation | `≤ 5` fresh field streams/source with fixed `L` caps and union over `N` | Private `O_C` adds ideal set evaluation only, spawning no new rejection streams | `t_N = clip(5N·binom(10129, 129) ρ^129)` |

Note: `C_X` is a pre-challenge cap (unused slots become no-ops); `A` re-encryptions increment `E_enc,A`; `T_red` and byte budgets scale to cover all `k` cohorts without adding new macro hop types.

**4. Assembly Across Hybrids.** Summing adjacent-level losses with endpoints gives:

$$\Delta_X(b) \le \operatorname{clip}\!\left(2(C_X + 10)B_X^{\mathcal L} + H_X + b_N + t_N\right),$$

where `②–⑤` sum to `b_N` and `⑩` gives `t_N` (neither multiplied by `M_X` or `k` separately beyond full-execution counters). Terminal collapse $J_b^{\rm final} \leftrightarrow S$ has zero observation gap by §2(iii) `Init` and `(CPL)`, yielding $\mathrm{Adv}_X^{\rm MW} \le \mathrm{clip}(e_X(0) + e_X(1)) \le \mathrm{clip}(2e_X)$ for `P`/`P+A`, while `A` proceeds independently via §2(iv) without equal-sum assumptions. □

## 3. Conditional Multi-Window Privacy Theorem (Declared Model)

**Theorem (MW).** Fix the G4b instance interface and source ledger $\mathcal L \in \{\mathcal L_{\rm base}, \mathcal L_{\rm ext}\}$. Here $\mathcal L_{\rm ext}$ is **explicitly defined by the complete extended `E′` source model** ([K3-SOURCE-EXTENSION-FINAL.md](extended-setup/K3-SOURCE-EXTENSION-FINAL.md) assumptions `A1–A4`: `A1` independent phase-1 setups; `A2` six independent deltas matching the `4 + 2` final keys in [budget-v3.json](extended-setup/budget-v3.json); `A3` unchanged v5 target QAP, current-namespace verifier, zero public target `q_i/Delta_r` queries; `A4` external sources count toward `S`, inlined toward `Q`), with `budget-v3.json` supplying numeric counts only, while $\mathcal L_{\rm base}$ is Document 07 §2's 3-key ledger. Expand the release contract to `k` predeclared windows sharing one `(task, profile, key)` namespace under non-adaptive scheduling in `μ`, static corruption, and full-execution public upper bounds `(N, S, V, Q, E_enc,A, E_q ≤ k)`. Then:

**(a) `P` and `P+A` Branches:** Whenever both admissible multi-window histories satisfy multi-window exposure equivalence (§1, applicable here only):

$$\mathrm{Adv}_X^{\rm MW} \le \mathrm{clip}(2e_X^{\rm MW}), \qquad e_X^{\rm MW} = \mathrm{clip}(M_X B_X^{\mathcal L} + H_X^{\rm MW} + b_N^{\rm MW} + t_N^{\rm MW}),$$

where $M_X = 2(C_X + 10)$ scales dynamically via full-execution $C_X$ ($C_P^{\rm MW} = C_{P+A}^{\rm MW} = 2N$), $H_X^{\rm MW}$ sums single-challenge HPKE bounds over $C_X^{\rm MW}$, and $b_N^{\rm MW}, t_N^{\rm MW}$ evaluate at total `N` (including `N²` in `b_N`). All primitive, source, and execution premises remain explicit theorem conditions.

**(b) `A` Branch (Independent, Zero Query):** For `X = A`, neither per-window equal sums nor $O_C$ queries are required; the identical bound holds with $C_A^{\rm MW} = 4N + E_{\rm enc,A}$, established by lifting Document 04 §5's `S_A` verbatim via §2(iv) without relying on §2(iii)'s `P`/`P+A` lemma. Guarantees match Document 01 §5 / Document 07 §5 with zero scope narrowing.

**Asymptotic Degradation Note:** Every algebraic form persists under full-execution counters without claiming a fixed total growth multiplier for `e_X` (since uninstantiated signature/hash/HPKE primitives depend on total `T, Q, bytes`). For the explicitly evaluated extraction-routing product alone: under fixed generic oracle budgets `Q` and `S, V` linear in `k`, $M_P(k) \cdot g_{\rm coll}(k)$ still contains a positive **$k^3$ term** ($h_i(k) = a_i k + c_i$ with $a_i > 0$, recomputed coefficient `≈ 6.065 × 10^-49`); `clip` saturation never alters the cubic algebraic degree prior to saturation.

*Proof.* Fix `b` and `X`. §2(v) constructs all primitive/statistical embeddings across adjacent $J_b^{(r)}$ levels with $2(C_X + 10) B_X^{\mathcal L}$ routing cost and internal sum $H_X + b_N + t_N$; the `F/E/L` pre-lemma aligns prefetch failures cleanly; §2(iii) `Init` and `(CPL)` equate $J_b^{\rm final}$ and `S` observationally. Shared `μ`, per-window equal `O_C` sums (for `P`/`P+A`), or zero-query `S_A` (for `A`) align both ideal worlds cleanly by triangle inequality. □

## 4. Retries, Crashes, and Query Ledger Invariants

**Invariants:**
1. At most one ideal query per distinct `R`: `Reserve/Send` durably pins `(selector, snapshot, plaintext)` ([Document 01](01-security-games-and-ideal-interface.md) §3.7), retries on the identical snapshot reuse identical plaintexts ([Document 04](04-full-view-simulation.md) §4), and cached sends reuse answers while re-encryptions increment `E_enc,A` rather than queries.
2. **Query ⇒ reached first send-preparation for `R`** (Document 05 prefetch), whereas **Query ⇏ exposure**: crashing after prefetch leaves an unused cached value excluded from observer views and leakage.
3. **Exposure ⇒ prior query**: first decryptable honest share departure logs `X` after passing send-preparation, so queries strictly precede exposures.
4. $E_q \le k$: one `R` per window and at most one query per `R`, unaffected by crashes or aborts.

**Preserved Counterexamples:** Dropping durable reservations lets crash-recovery produce fresh plaintexts or repeat queries for identical `R` (violating Invariant 1), or drops exposure tracking after a share leaves trust boundaries so an adversary decrypts an unqueried `R` (violating Invariant 3) — directly corresponding to the durable-execution premise in manuscript Table 3 Row 5 for any `k ≥ 1`. Setting `k = 1` recovers single-release $E_q \le 1$, matching existing G4b ledgers verbatim.

## 5. Cross-Document Ledger Consistency Audit

All occurrences of `E_q`/`E` across Documents 01–07 and contracts reconcile cleanly:

| Location | Original Statement | Multi-Window Contract Disposition |
| --- | --- | --- |
| Document 01 §3 | One visible selector per task, hence `E ≤ 1` | Expanded to `k` windows with per-window equal sums and dedicated query ledger $E_q \le k$ |
| Document 01 §6 | No `O_C` query prior to first exposure of `R` | Stricter non-prefetch variant; MW theorem covers both (canonicalized to Doc 05 prefetch) |
| Document 04 §1 | Equal certified claimed histogram per authorized first-exposure `R` | Applies verbatim per window `w_1, ..., w_k` |
| Document 04 §6 | `C_HPKE ≤ 4N + 2E`; `E ≤ 1` cannot erase re-encryptions | `E_enc,A` counts all `k`-window re-encryptions identically |
| Document 04 §7 | Aborts prior to exposure query no aggregate | Holds under non-prefetch variant; replaced cleanly by §4 Invariants 1–3 under prefetch |
| Document 05 §2 | Simulator may pre-fetch `R` once on first send prep, hidden if unused | Authoritative origin of prefetch and query/exposure separation |
| Document 07 §1 | Budget line `E ≤ 1`; separate `E_enc,A` | Budget row updates to $E_q \le k$ distinct queries; `E_enc,A` preserved |
| Document 07 §5 | `C_A = 4N + E_enc,A`; `M_X = 2(C_X + 10)`; macro ⑨ | Formulas unchanged; numeric `M_X` grows with workload (§6) |
| Contract JSON | `max_visible_cohorts_per_task: 1` | Generalized to `k` (frozen JSON unmodified) |
| Document 03 header | `q_release ≤ 1/task` (implementation limit) | Codebase unchanged; contract-level theorem only |
| `budget-v3.json` / `K3-SOURCE-EXTENSION-FINAL.md` | Six-key extended family (`E′` A1–A4) and `epsilon_setup_sampling` | Authoritative $\mathcal L_{\rm ext}$ definition: `E′` supplies source model/assumptions, `budget-v3` supplies numerics |

**Note on Dual Notation `E`:** Document 01 §3 defined `E` as "semantic output queries" while Document 07 §1 defined `E` as "first cohort exposures" — two distinct ledgers unified cleanly by separating $E_q$ (queries) from `X` (exposures). None of `b_N, t_N, g, v_N, k_tag` depend on `E`.

## 6. Numerical Sensitivity Analysis (Exact Rational Verification)

Computed via `k_window_recheck.py` (exact `Fraction` arithmetic under $\mathcal L_{\rm ext}$). **Sensitivity analysis of the extraction-routing term only** (other primitive `Adv` terms are not set to zero, nor is total `e_X` evaluated).

- **`g_setup`:** Authoritative formula $g_{\rm setup} = 1 - \frac{p - 16385}{p}\cdot\frac{p - 4194305}{p}\cdot\left(\frac{p - 1}{p}\right)^{10}$ (excluding 16,385 points on `pot14`, 4,194,305 points on `pot22`, and zero values across `2` pairs of `α, β` plus `6` deltas) **matches `budget-v3.json` identically in exact rationals** at `1.923726827 × 10^-70`.
- Single-window check ($\mathcal L_{\rm ext}$, manuscript `groth-budget` equation): `g = 2.6737 × 10^-50` (matches manuscript `2.6738 × 10^-50` up to final-digit rounding).
- `k = 10` (`S, V × 10`, fixed `Q/I`): `g = 2.7679 × 10^-50` (`×1.035239`), still `< 2^-150` (extraction term only).
- **Workload Terms:** `M_P: 2,097,172 → 20,971,540`; `M_A` gives `4,194,324 → 41,943,060` (`E_enc,A = 0`) and **`4,194,328 → 41,943,100` (`E_enc,A = 2 → 20`, single encryption per role/window without extra re-encryptions)**; `b_N: 3.3685 × 10^-25 → 3.4412 × 10^-24` (`×10.2`, linear-dominated while `N²` grows `×100`); exact positive `t_N` has `log_10 t_N ≈ −1992.54` (non-zero in exact arbitrary precision).
- **Product Term $M_P \cdot g_{\rm coll}$:** Fixed group `Q` with scaled sources/verifications multiplies by **`×10.352303`**; scaling both sources/verifications and group `Q` by `10` multiplies by **`×995.774824`**. Algebraically, $h_i(k) = a_i k + c_i$ ($a_i = 72N_0 / 5N_0 / 14N_0$, $N_0 = 2^{19}$), `g_coll` is quadratic in `k`, and $M_P(k) = 4N_0 k + 20$ is linear, producing a positive **$k^3$ term** (coefficient `≈ 6.065000577 × 10^-49`) even at fixed `Q`.

## 7. Explicit Scope Boundaries and Premise List

1. **Contract-level, not implementation-level**: frozen source enforces `q_release ≤ 1/task` with zero multi-window runtime/tests; the manuscript retains its single-cohort scope statement.
2. **Contract constraints**: per-window exclusivity of logical reports/retained handles and unique five-tuple `κ` bindings are MW contract refinements; dynamic cohort addition and duplicate cross-window references remain unaddressed.
3. **Stronger environment requirement (`P`/`P+A`)**: environment must supply per-window equal sums across all `k` windows (`H_0` vs. `H_1`); vacuity under adaptive dropping rests with the challenge environment.
4. **No differential privacy across joint releases**: exact multi-window histograms remain jointly exposed.
5. **Non-adaptive schedule**: dynamically spawned windows fall outside scope.
6. **Single namespace**: cross-task/cross-key source extensions are unproved.
7. **Unbounded re-encryptions in `A`**: require explicit exogenous caps in `E_enc,A` (Section 6's `2k` applies strictly when zero re-encryptions occur).
8. **Fixed source ledger**: $\mathcal L_{\rm ext}$ uses `E′` (`A1–A4`) + `budget-v3.json` numerics; $\mathcal L_{\rm base}$ remains an explicit parameterized alternative.
9. **Challenge condition scope**: equal sums cover all `k` predeclared windows including unexposed ones; relaxing to visible-window-only equality requires separate adaptive feasibility analysis.
10. **Uninstantiated primitive bounds**: signatures, SHA-256, and HPKE `Adv` depend on uninstantiated byte/time budgets, restricting §6 scaling calculations cleanly to the extraction-routing term. (All arguments are non-mechanized mathematical proofs outside proof assistants.)
