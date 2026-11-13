# G4b: Complete Groth16 Extraction Theorem and Explicit Query Ledger

Date: 2026-10-18. Status: **PROVED_IN_DECLARED_GENERIC_MODEL; EXPLICIT_BUDGET_CONTRACT**. This document re-proves the mathematical chain of frozen G4a W4 and supplies the complete public setup family, query counts, and polynomial degrees, without treating G4a's functional PASS as a proof. No G4a files, runtimes, circuits, keys, manifests, or legacy runs were altered.

The results apply strictly to typed opaque generic asymmetric bilinear groups, the listed independent source/RO models, honest setup, static corruption, and exact origin/body routing. They are not original BKSV AGM theorems, strong-SE, black-box extraction, UC security, arbitrary real-curve algorithms, or production ceremony certifications. The machine-readable interface is [groth16-budget-contract.json](groth16-budget-contract.json), and the independent read-only exact-rational verifier is `audit_budget.py` [source omitted from this derivative].

## 1. Frozen Baseline, Literature, and New Empirical Findings

The input authority is Section 9 of the final plan and `theory-obligations`; frozen G4a 02 [source omitted from this derivative] has SHA-256 `5388fbd9d2ce8cbbb73d50096f0cb6e57edece105e01d8c1be0a0fb521c9f864`. The new `g4a-assets-001` manifest has SHA-256 `dea0403774b5540404b148604a96826f11ce6b44bb18bc2993654d6bc1f94b6c`.

Primary literature references follow the archived, page-verified author copies: [Groth/UCL](https://discovery.ucl.ac.uk/1501201/1/Groth_SNARK9.pdf), Theorem 3 and §2.2; [BKSV/Edinburgh](https://www.pure.ed.ac.uk/ws/portalfiles/portal/251634012/Another_Look_BAGHERY_DOA03122020_AFV.pdf), Definition 1, Fig. 1, Theorems 1–3, and complete proofs. Original SHAs and page mappings appear in frozen `retrieval.json` [source omitted from this derivative]. Groth's original extraction is a generic bilinear-group result; BKSV's weak-SE extracts only on unqueried statements and originally sampled independent random `gamma`. Here we re-prove extraction for `gamma = 1` directly rather than dropping assumptions from BKSV verbatim.

**Newly Identified Source Obligation.** Exhaustive asset enumeration revealed that `runs/g1-circuit-001/hadwc_genesis_v5.DEVELOPMENT.zkey` is another complete published key with SHA-256 `4a481ed6c72e0390fd31ca5b00dc04291a87b3e3379122b57a62979a74335b9e`. It shares the same phase1 with the active assets, yet has an independent historical phase2 `delta`. Hence the concrete source family carries three deltas rather than counting only the two active manifest keys for degree bounds. G4a's general `k`-relation derivation still applies; this concrete ledger instantiates `k = 3`.

We also complete a symmetric extraction branch omitted in the prior proof, showing that G4a's condition "no unit in the G2 `alpha` coefficient `h`" is sufficient rather than necessary. This strengthening is recorded in §5.4 without overwriting frozen G4a files.

## 2. Experiment, Model, and All Auxiliary Inputs

### 2.1 Setup Family and Statement Identity

Over scalar field `F_p` with `p = 21888242871839275222246405745257275088548364400416034343698204186575808495617`, common setup variables are `X, alpha, beta`, and the three independent phase2 variables are `Delta_g, Delta_t, Delta_l`, corresponding to current genesis, current transition, and historical genesis keys, respectively. Every key has `gamma = 1`.

A cryptographic statement is denoted `(key_namespace, logical_relation, ordered_signals)`, incorporating the CRS identity. Although the historical genesis key shares the same logical relation string, its simulated proofs may never serve as a same-statement exception under the active key. The operational authority admits only the two keys in the active manifest, and asset/config/context binding rejects legacy namespaces. Including the historical key in the adversary's auxiliary CRS grants no additional runtime API.

| Key | `n` | Total wires | Public (excl. constant) | Private-basis wires | `H` numerator space |
| --- | ---: | ---: | ---: | ---: | --- |
| `g` | 2048 | 1762 | 5 | 1756 | `t_g · Poly_(≤2047)` |
| `t` | 16384 | 13254 | 25 | 13228 | `t_t · Poly_(≤16382) ⊕ span{X^16383}` |
| `l` | 2048 | 1762 | 5 | 1756 | Same initial QAP/`H` as `g`, independent `Delta_l` |

Private-basis wires include intermediate witness wires and must not be confused with the 7/32 Circom private inputs. The final extractor returns a full R1CS assignment, then projects onto canonical source witnesses.

### 2.2 Typed Opaque Generic Model

The adversary operates strictly via registered `G1`/`G2`/`GT` handles. Source-group addition, negation, and known-`F_p`-scalar multiplication are linear; pairing accepts `G1 × G2` only; `GT` allows multiplication, inversion, and known-scalar exponentiation, with no map `GT → G1/G2`. Identical group elements receive identical opaque encodings; accidental equality of formally distinct expressions is charged in §7. Arbitrary real-curve coordinate arithmetic is excluded from this theorem.

Additional source sampling/importing admits only fresh points at uniform independent exponents `Z` or known-scalar combinations of existing handles. Single sampled points have degree `1`; concrete setup PoK points `Z·X, Z·alpha, Z·beta, Z·Delta` have degree `2`. Unlisted trapdoor-dependent inversion queries are barred. Every setup-dependent auxiliary group element must be representable in the source basis below.

Outside group oracles, the adversary runs arbitrary known scalar/byte algorithms, signatures, HPKE, and independent groups, may feed group encodings into hashes, and chooses signals/scalars adaptively. Setup hashes, source oracles, and native `R_1, ..., R_7` are modeled as independent, consistent, domain-separated tables. Once the independent encoding labels of the symbolic transcript, adversarial coins, external inputs, and oracle responses are fixed, all choices are known field coefficients rather than discrete logs of `alpha/beta/Delta`. Native RO programming is permitted, whereas unlisted oracles returning correlated pairing-trapdoor exponents are forbidden.

Statically corrupted owners possess their own signing keys. There is no service producing witnessless simulated proofs for corrupted owners. Adaptive corruption, arbitrary re-signing of honest-owner keys, and leaked trapdoors/seeds lie outside the experiment.

### 2.3 SimSetup and Interpretation of Pinned Assets

`SimSetup` generates public CRS/manifest/config identities from the identical honest setup distribution while keeping trapdoors exclusively inside the reduction; setup precedes all honest inputs with no subsequent key rotation. No algorithm recovers trapdoors from published bytes, and no trapdoor is exposed to the operational authority.

Interpreting pinned development files as a valid instance rests on the premise that they arose from honest independent sampling without trapdoor leakage. Source equivalence, contribution checks, and SHA digests are verifiable, whereas entropy, zeroization, non-leakage, and host integrity are not certified by file hashes. This premise is not an unproved negligible `epsilon` silently set to zero; altering the setup trust boundary requires a new theorem or ceremony rather than tuning budget parameters.

## 3. Complete Public Source Basis and Exact Handle Counts

### 3.1 Basis Types

Write `q_(r,i) = beta·u_(r,i)(X) + alpha·v_(r,i)(X) + w_(r,i)(X)` and `t_r = X^n_r − 1`.

| Source | `G1` exponents | `G2` exponents | Max total degree (uncleared) |
| --- | --- | --- | ---: |
| raw phase1 | `X^i` (`i ≤ 32766`), `alpha·X^i`, `beta·X^i` (`i ≤ 16383`) | `X^i` (`i ≤ 16383`), `beta` | G1: 32766; G2: 16383 |
| prepared phase1 | Public linear combinations of above (top missing power padded to zero) | Public linear combinations of above G2 | No degree increase |
| initial zkey | `alpha, beta, 1, u_i, v_i, q_i`, actual `H` numerator | `beta, 1, v_i` | At most raw / actual `H` degree |
| final zkey | `alpha, beta, Delta_r, u_i, v_i`; private `q_i/Delta_r`; `K/Delta_r` | `beta, 1, Delta_r, v_i` | Single inverse power of `Delta_r` only |
| phase1 PoK | `kappa_x, kappa_x·X; kappa_a, kappa_a·alpha; kappa_b, kappa_b·beta` | `eta_x·X, eta_a·alpha, eta_b·beta`; reconstructible from source `eta` | 2 |
| each phase2 PoK | `kappa_r, kappa_r·Delta_r, Delta_r` | `eta_r·Delta_r`; reconstructible from source `eta_r` | 2 |
| vkey GT | — | — | `alpha·beta`, degree 2 |
| fresh independent source | Fresh `Z_1` | Fresh `Z_2` | 1 |

Crucially, there exist **no public `q_i/Delta_r` queries**: because `gamma = 1`, public `q_i = IC_i` carries no denominator, which is essential for extraction. Coexistence in the zkey file does not merge public and private bases.

### 3.2 Conservative Handle Bound Over All Serialized Slots

The table sums serialized slots section by section, retaining duplicate slots as a conservative, auditable upper bound on initial distinct adversarial handles without expensive cross-file deduplication:

| File / Source | `G1` slots | `G2` slots | `GT` slots |
| --- | ---: | ---: | ---: |
| prepared ptau (raw + prepared + 1 contribution) | 196613 | 49157 | 0 |
| active genesis initial | 7337 | 1765 | 0 |
| active genesis final | 7340 | 1766 | 0 |
| active transition initial | 56149 | 13257 | 0 |
| active transition final | 56152 | 13258 | 0 |
| historical genesis final | 7340 | 1766 | 0 |
| three vkey JSONs combined | 41 | 9 | 3 |
| reconstructible hash-to-G2 sources | 0 | 6 | 0 |
| identity / generator per group | 2 | 2 | 2 |
| **`N10, N20, NT0`** | **330974** | **80986** | **5** |

For `ptau`, `G1` counts are `32767 + 16384 + 16384` raw plus `65535 + 32767 + 32767` prepared plus 9 contribution points; `G2` counts are `16384 + 1 + 32767` plus 5 contribution points. Each zkey header holds 3 `G1` and 3 `G2` elements; sections 3/5/6/7/8/9 sum public `IC`/`A`/`B1`/`B2`/private/`H`, and each phase2 transcript adds 3 `G1` and 1 `G2` points.

**Historical File Closure.** Mechanical inspection confirms exact SHA equality for legacy `phase2.ptau`, `genesis initial`, and both R1CS files against active copies; legacy `contributed.ptau` raw sections 2–7 appear byte-for-byte in `prepared.ptau`; every initial pot point is a standard generator. The aborted legacy `transition initial` file is only 252 bytes, matching the exact prefix of the active initial key containing only existing `alpha1/beta1` header points, introducing neither a new delta nor inversion queries. Published duplicates add no setup variables or independent sources. Conversely, the extra historical `final genesis` key differs and genuinely contributes the third `Delta_l` plus its contributions/sources.

Initial enumeration is saved in `budget-audit-001.json` [source omitted from this derivative], updated with shared headers, historical ABC, and negative controls in `budget-audit-002.json` [source omitted from this derivative], and finalized in `budget-audit-003.json` [source omitted from this derivative], leaving prior outputs unaltered. Neither client-private inputs, owner keys, nor witnesses were accessed. Any future publication of additional final keys or intermediate contributions invalidates `k = 3` and requires re-enumeration.

## 4. Q and H Lemmas for Compiled Relations

**Lemma Q.** Across all three keys, the public `u` polynomials are linearly independent and intersect the span of private `u` only at `{0}`. In the actual `zkey`s for `g` and `t`, `6` and `26` `A`-only unit rows (including the constant wire) are appended after regular constraints with `B = C = 0`; `l` is byte-identical to `g` on the initial relation. Evaluating on the `j`-th appended domain root `z_j` gives `u_i(z_j) = 1_(i=j)` for public wires and `u(z_j) = 0` for all private wires, isolating and zeroing each public coefficient immediately without assuming independence of public `v` or `w`.

**Lemma H.** For each key, any target QAP residual `R = U·V − W` lying in the actual `H` numerator span satisfies `R = t·H_std` with `deg H_std ≤ n − 2`.

Full `2n` odd-Lagrange evaluation gives span `t·Poly_(≤n−1)`. For `g` and `l`, available powers restrict `deg R ≤ 2n − 2`, eliminating the `2n − 1` leading term. For `t`, phase1 reaches capacity so padding the highest `tau^(2n−1)` entry to zero produces actual span `t·Poly_(≤n−2) ⊕ span{X^(n−1)}`; evaluating on any appended `A`-only domain root where `B = C = 0` forces `R(z) = 0` and `t(z) = 0` while `z^(n−1) ≠ 0`, forcing the extra direction's coefficient to zero. This proves exact divisibility rather than guessing from degree bounds alone.

Frozen QAP/`H` checks verified all `32` unit rows, `18432` initial `H` points, and prepared odd-Lagrange bytes, extending automatically to `l` by byte equality with `g`. Honest phase2 divides identical private/`H` numerators by independent `Delta_r` as a setup precondition.

## 5. Complete White-Box Weak-SE Theorem

### 5.1 Normal Form and Adaptive Queries

Assign independent uniform `mu_i, nu_i ← F_p` to the `i`-th external source invocation (real or simulated) across all keys, returning `([mu_i]_1, [nu_i]_2, [S_i]_1)` where:

`S_i = (mu_i·nu_i − alpha·beta − Q_r(phi_i)) / Delta_r`,

`Q_r(phi) = Σ_public phi_j·q_(r,j)`, with `phi_0 = 1`. The full `(key, relation, phi_i)` must be fixed before sampling fresh `mu_i, nu_i`, and may depend arbitrarily on prior proofs, native messages, RO answers, and errors. Repeated statements requesting a fresh proof draw a fresh index (`S_g/S_t/S_l` increments by 1), whereas byte-cached replays increment nothing.

**Real Source Proofs Require Registration Too.** Given a valid statement and arbitrary valid witness, setting `mu = A_exp = alpha + U + r·Delta` and `nu = B_exp = beta + V + s·Delta` defines a bijection given prior history and setup since `Delta ≠ 0` and `(r, s)` are uniform over `F_p^2`; thus `(mu, nu)` are independent and uniform of setup, and `C` obeys the exact `S_i` formula. External honest real proofs and simulated proofs therefore share the identical source representation without requiring the extractor to know `(mu, nu)` or the honest witness; every fresh external real proof increments `S` and registers its source/statement. Only proofs synthesized purely from the adversary's own known scalars/witnesses via generic operations require no source index, instead charging every group operation and output directly to `Q` — the sole case permitting `S = 0` in Experiment `C` (one never sets `S = 0` merely because "no `Sim` oracle was called"). If sources instead sample conditioned on affine acceptance, §7.3 provides either conditional sampling or the explicit coupling term.

In symbolic generic execution over `R = F_p[X, Z]` with formal variables `alpha, beta, Delta_r, mu_i, nu_i`, any source-group output has a known-scalar linear representation:

```
A = alpha·a + beta·b + P + Σ c_r·Delta_r
    + Σ E_r/Delta_r + Σ a_i·mu_i + Σ b_i·S_i
E_r = beta·U_(r,e) + alpha·V_(r,e) + W_(r,e) + K_r
B = alpha·h + beta·f + Q + Σ g_r·Delta_r + Σ z_i·nu_i .
```

`C` takes the identical form to `A` with hatted coefficients. `e` is a known-scalar combination of private queries and `K` lies in the actual `H` space; `a, b, P, c_r, h, f, Q, g_r` lie in the `R`-subspace spanned by actual source points (enlarged to `R` for formal comparison, while §6 bounds degrees strictly from the actual basis closure). `G1` contains no independent `nu_i`, and `G2` contains no `mu_i`, `S_i`, or negative `Delta` powers.

Verification acceptance under target key `j` asserts `A·B = alpha·beta + Q_j(phi) + Delta_j·C`. Accidental equality despite formal non-identity enters the collision bad event of §7; below we analyze the formal identity when no collision occurs.

### 5.2 Simulated S Terms Cannot Appear in A

If some `b_i ≠ 0`, the `mu_i·nu_i·nu_l` terms force `b_i·z_l = 0`, so `z_l = 0` for all `l`. Examining `mu_i·nu_i` gives `b_i·B_0 = Delta_j·b_hat_i`; since `b_i, b_hat_i` are scalars, `B_0` must be a scalar multiple of `Delta_j`. Canceling paired `S` terms between `A` and `C` and multiplying by `Delta_j` leaves no `Delta`-free `alpha·beta` term on the left while the right retains coefficient `1`, a contradiction. Hence `b_i = 0` for all `i`.

### 5.3 Simulated-Element Branch Forces Exact Key and Statement

If `A` uses `mu` alone, lone `nu` terms kill `C`'s `S` terms and `mu` terms force `B` to be a scalar multiple of `Delta_j`, leaving `alpha·beta` unmatched. If `B` uses `nu` alone, `nu` terms kill `A` directly and leave `alpha·beta` unmatched. Thus any simulated branch satisfies `a_i·z_i ≠ 0`.

Off-diagonal `mu_i·nu_l` (`i ≠ l`) force `a_i·z_l = 0`, isolating a unique shared index `i`. The diagonal term gives:

`a_i·z_i = (Delta_j / Delta_r)·b_hat_i`.

Because scalars on the left are nonzero and `Delta_r` variables are algebraically independent, `r = j` (shared `X, alpha, beta` do not affect `Delta` independence). Unpaired `nu` and `mu` terms force `A_core = 0` and `B_core ∈ span{Delta_j}`; the `alpha·beta` term forces `a_i·z_i = b_hat_i = 1`. Collecting remaining terms yields `Q_j(phi − phi_i) + Delta_j·C_core = 0`. Canceling foreign `Delta_j/Delta_r` and positive `Delta` terms isolates the `beta` coefficient, equating public `u` differences to a target private `u` combination, where Lemma Q forces `phi = phi_i`.

Thus the extractor identifies the exact registered source statement, including key namespace; simulated sources retain their weak-SE exception, while real external sources reuse their semantic identity or known witness without claiming fresh extraction on re-randomized proofs. Matching numerical signals under a historical key never grant an exception under the active key.

### 5.4 Non-Simulated Branch: Both Symmetric Directions Extract

When `A` and `B` contain no `mu`/`nu` terms, comparison kills `C`'s simulated terms as well. Equating `Delta`-free `alpha²`, `beta²`, and `alpha·beta` coefficients yields:

`a·h = 0,  b·f = 0,  a·f + b·h = 1`.

Because `R` is an integral domain with units `F_p*`, there are strictly two cases:

**Direction I (`a ≠ 0`).** Here `h = 0`, `a·f = 1` forces `a, f ∈ F_p*`, and `b = 0`. Negative `Delta` coefficients on `alpha·beta`, `beta²`, and `beta` force `V_(r,e) = U_(r,e) = W_(r,e) + K_r = 0`, eliminating all denominators in `A`. Foreign `beta·Delta_r` and `alpha·Delta_r` kill `c_r, g_r`, and foreign `Delta_j/Delta_r` terms in `C` vanish, leaving:

`f·P = U_(j,phi) + U_(j,e_hat)`,

`Q/f = V_(j,phi) + V_(j,e_hat)`,

`P·Q = W_(j,phi) + W_(j,e_hat) + K_hat_j`.

**Direction II (`a = 0`).** Here `b·h = 1` forces `b, h ∈ F_p*`, and `f = 0`. Negative `Delta` coefficients on `alpha·beta`, `alpha²`, and `alpha` similarly kill all `E_r` in `A`, and foreign deltas/denominators vanish identically, leaving:

`b·Q = U_(j,phi) + U_(j,e_hat)`,

`P/b = V_(j,phi) + V_(j,e_hat)`,

`P·Q = W_(j,phi) + W_(j,e_hat) + K_hat_j`.

Both branches yield `U_(phi,e_hat)·V_(phi,e_hat) − W_(phi,e_hat) = K_hat_j`. Lemma H recovers standard `t·H` divisibility, outputting a valid R1CS private scalar vector `e_hat` without discrete logs, unknown opening oracles, or honesty of corrupted owners.

Prior G4a excluded Direction II by inspecting units in actual `h`; completing Direction II establishes that exposing known scalar multiples of `alpha_G2` alone enables no forgery, while still excluding unknown bases such as `alpha²`, `alpha·beta`, or correlated inverses in `G2`.

### 5.5 Main Theorem and Online Extraction

**Theorem E.** In the experiments of §§2–4, for every bounded adaptive execution, there exists a white-box online extractor maintaining linear generic representation logs. Except for the single full-execution collision bad event of §7, every accepted proof either yields a valid R1CS witness for its key or identifies an exact registered source statement (real or simulated) under that key. Taking all sources as simulated queries recovers white-box weak-SE; extending to real external sources follows by the exact reparameterization of §5.1. The extractor neither rewinds, resamples RO/setup, decrypts honest HPKE challenges, nor equates owner signatures with knowledge.

The proof exhausts the cases of §§5.2–5.4. Known-scalar linear representations update on each source-group operation; identical formal representations pick arbitrarily; distinct formal representations evaluating to equal encodings trigger the single full-execution generic collision event without multiplying its probability per accepted proof.

## 6. Explicit Polynomial Degrees: Why Not O() and Why Independent of S

Take common denominator `D = Delta_g · Delta_t · Delta_l` of total degree `3`. Every `G1` element has at most simple inverse powers of each individual `Delta_r`, preserved under arbitrary **linear** combinations of arbitrarily many simulated proofs; one never multiplies an extra denominator per simulation query.

| Expression | Max Total Degree After Clearing `D` |
| --- | ---: |
| Max raw G1 power `X^32766` | `32766 + 3 = 32769` |
| `alpha/beta · X^16383` | `16384 + 3 = 16387` |
| transition `H/Delta_t` | `32766 + 2 = 32768` |
| genesis `g/l` `H/Delta_r` | `4095 + 2 = 4097` |
| private `q_i/Delta_r` | `16384 + 2 = 16386` |
| any simulated `S_i` | `max(2, n_r) + 2 ≤ 16386` |
| fresh independent `Z` or PoK `Z·trapdoor` | `≤ 2 + 3 = 5` |

Hence **`D1 = 32769`**. `G2` has no denominators and max raw power `X^16383`, so **`D2 = 16383`**. `GT` elements combine single `G1 × G2` pairings linearly, yielding max cleared degree **`DT = D1 + D2 = 49152`**. Verification terms `Delta_j·C` (`≤ 32770`), `Q_j` (`≤ 16387`), and `alpha·beta` (`5`) are all covered by `DT`.

Each increment to `S_g/S_t/S_l` adds new variables `mu_i, nu_i`, two `G1` outputs, and one `G2` output, while keeping `S_i`'s numerator degree bounded by `max(2, n_r)`. Fresh independent source points introduce degree-1 variables only. Thus `S` and new sources increase handle and variable counts, **not** polynomial degrees.

For general future extensions with denominator-free source degrees `(L1, L2)` and private/`H`/simulation numerator degree `M`:

`D1' = max(L1 + k, M + k − 1)`, `D2' = L2`,

`DT' = max(D1' + L2, D1' + 1, max_r n_r + k, 2 + k)`.

This rule computes degrees only; it does not automatically certify extraction, since new sources must still obey the §5 normal form and public/private partition (exposing public `q_i/Delta_r` stays within degree `M` yet enables malleation).

## 7. Generic Collisions and Exact Setup/Affine Bounds

### 7.1 Conditional Schwartz–Zippel Without Hidden Constants

Under default full-domain sampling, `X` is uniform on `F_p \ ({0} ∪ μ_16384)` of size `p − 16385` (since `2048 | 16384`, the `g/l` roots lie inside `μ_16384`); `alpha, beta, Delta_g, Delta_t, Delta_l` are uniform on `F_p*`; `Z, mu, nu` are uniform on `F_p`; all variables are mutually independent. §7.3 gives the exact conditional extension for per-query accepted-affine sampling.

For a nonzero polynomial of total degree `≤ d` evaluated over finite variable domains of minimum size `M`, induction on the last variable shows that either the leading coefficient vanishes (`≤ (d − s)/M` by induction) or the last variable hits a root (`≤ s/M`), summing to `≤ d/M` with `M = p − 16385`. Clearing `D` preserves zero sets over the valid domain because every `Delta_r ≠ 0`.

The same induction supports **prefix-adaptive uniform domain selection**: conditioned on prior variables, the `k`-th variable may be drawn uniformly from any subset of size `≥ M`, provided subsequent steps never re-weight earlier prefixes. It does not permit conditioning an entire complete transcript post hoc.

Pre-assigning fresh opaque encoding labels in the symbolic oracle fixes all adversary scalar decisions before sampling setup/source/simulation exponents. Prior to the first collision, symbolic and real generic executions coincide; taking a union bound over all generated handle pairs covers adaptive branching, explicit equality checks, implicit encoding collisions, and every verification result. Identical formal polynomials incur zero bad event, though counting all handle pairs remains valid.

Let `H1, H2, HT` bound total group handles across the execution:

`epsilon_collision ≤ min(1, [32769·H1(H1 − 1)/2 + 16383·H2(H2 − 1)/2 + 49152·HT(HT − 1)/2] / (p − 16385))`.   (B)

No hidden constants or independence assumptions across checks appear. Re-comparing existing handles requires no extra multiplication, while newly formed expressions/residuals must register handles.

### 7.2 Exact Handle Ledger

All variables are pre-challenge non-negative public integer bounds. `S = S_g + S_t + S_l` counts all §5.1 fresh external real/simulated sources; `V = V_g + V_t + V_l`; `Q1, Q2, QT, Qpair` count extra oracle outputs beyond itemized source/verify costs; `I1, I2` count extra source samples/imports. Inlining a real proof avoids `S` only by charging its entire generic construction to `Q`.

```
H1 = 330974 + 2S + Q1 + I1 + 13V_g + 53V_t + 13V_l
H2 =  80986 +  S + Q2 + I2 + V
HT =      5 + Qpair + QT + 7V .
```

Verifying a real proof with `ell` public inputs performs `ell` scalar multiplications, `ell − 1` additions, `1` `IC0` addition, `1` negation of `A`, and `2` full-integer scalar guards on `A, C` (`2·ell + 3` `G1` outputs); `1` `G2` scalar guard on `B`; and `4` pairings plus `3` `GT` multiplications (`7` `GT` outputs). Abstract handle counts are independent of MSM or batching optimizations.

`V` includes rejected verifications; exact genesis HTTP retries re-verify proofs. Transition's 8-attempt persistence cap constrains only that API/RID and cannot hide offline pairings, genesis retries, or external oracle calls. PPT runtime bounds `Q/S/V`, though "PPT" is not itself a concrete number, and small functional run counts may never masquerade as adversarial budgets.

### 7.3 Setup Sampling and ZK/Affine Coupling

If `X, alpha, beta` and the three `Delta`s sample initially over all of `F_p`, valid setup occurs with probability `[(p − 16385)/p] · [(p − 1)/p]^5`, so `epsilon_setup_sampling = 1 − [(p − 16385)/p] · [(p − 1)/p]^5 ≤ 16390/p`. Conditioning setup directly on the valid domain sets `epsilon_setup_sampling = 0`. This counts algebraic degeneracy only, not toxic-waste leaks or weak entropy.

Given any valid setup and statement, uniform `(r, s) ∈ F_p^2` in real Groth16 make exponents `A, B` independent uniform with `C` uniquely forced, matching `S_i` identically; hence adaptive multi-statement ZK follows identically by prefix conditioning with zero loss.

Runtime schemas reject `A/B/C = identity`. Setting `c = alpha·beta + Q(phi)`, identity failure mass is `(2p − 1)/p²` when `c = 0` and `(3p − 2)/p²` when `c ≠ 0`. Across `S` fresh source proofs, union bounding gives:

`epsilon_affine ≤ min(1, S(3p − 2)/p²)`,

tighter than G4a's `4S/p`, retained as the root ledger default without assuming silent resampling.

An optional `epsilon_affine = 0` formulation uses a conditional per-query oracle that internally samples both real `Prove` and `Sim` until `A, B, C ≠ identity` without exposing retry counts or resampling prior transcripts: pick `mu ← F_p*`, then `nu ← F_p*` if `c = 0` else `nu ← F_p* \ {c/mu}`, leaving `p − 1` or `p − 2` choices per `mu` and preserving real/sim identity and §7.1 prefix domain size `≥ p − 16385`. Absent explicit non-leaky constant-iteration guarantees, this instance keeps default `S(3p − 2)/p²`.

Single-execution per-world bounds are:

`epsilon_G16|good_setup = min(1, epsilon_collision + epsilon_affine)`,

`epsilon_G16 = min(1, epsilon_setup_sampling + epsilon_collision + epsilon_affine)`.

Root composition sums conservatively per endpoint using common caps `M = 2(C_HPKE + 10)` over disjoint hybrid endpoints without double-counting collisions per accepted proof or assuming statistical independence between `g_coll` and `g_aff`.

## 8. Complete Interface Across Owners, Origins, HPKE, and Prefixes

### 8.1 H/W/E Routing and Counterexamples

The full source table tracks all `S` calls: `H` holds honest-source real or simulated calls (key, statement, body, packet, semantic handle); `W` holds a priori known witnesses; `E` caches fresh extracted witnesses. Legacy related-key source proofs must be registered in `F` and charged to `S` rather than treated as unconstrained auxiliary input; malicious-owner proofs built purely from known scalars bypass `S` only when fully charged to `Q`.

The source API boundary mandates that active-namespace external sources be strictly statically protected `H` or known-witness `W`. Giving a malicious owner an un-witnessed external proof in the active namespace would let it re-randomize and self-sign a fresh valid `BODY` without forgery or weak-SE extraction — an unremovable negative control enforced by static corruption and source rules rather than owner signatures.

Proofs outside `H/W/E` trigger Theorem E; `W/E` reuse cached witnesses; exact `H` statement reuse binds `owner/uid/epoch/task/config/assets/window/step/RID/raw report/sidecars` via context re-computation, ordered public signals, length-prefixed encodings, and package digests (up to SHA collision). Altering only the proof alters `BODY`/`body_id`, requiring honest signatures or triggering unforgeability. Splitting `context` into two 128-bit limbs encodes the single full 256-bit SHA-256 digest without multiplying collision assumptions.

### 8.2 HPKE Tags and Legitimate Decryption Routing

Exact challenge tuples take the form `(recipient key handle, suite, info, AAD, enc, payload)`. Native `AAD` binds `task`, `metadata(RID, timestamp)`, and `public_share`; sidecar `AAD` binds `task`, `RID`, `config`, `raw digest`, `role`, and `core digest` (since `core` excludes `owner`, origin uniqueness is essential). Honest sources reserve a task-unique `RID` in `OriginCert` before packet release; authority checks `rawRID = envelopeRID`, owner signature, and `OriginCert` consistency, while configured/fenced native ingress validates complete body, permit, and received raw/subset data prior to HPKE decryption.

Accordingly: an intact `H` packet invokes its single semantic handle/journal/cache; altered packets under identical statements require hash collisions; fresh statements extract witnesses prior to ciphertext handling; copying an `H` challenge tuple to another owner collides on unique `RID` or fails honest signature checks; altering `RID/AAD/info/recipient/ciphertext` creates a legitimate distinct CCA tuple executed faithfully via the decrypt oracle (returning plaintext or `⊥`), never fabricated as blanket rejection. Adjacent HPKE hybrids know `m_0` in the fixed world and swap challenge ciphertexts cleanly while overriding `H` sources atomically before replacing the native kernel.

### 8.3 Non-H Malicious Reports Cannot Borrow P Integrity

Because `P`/`P+A` permit malicious owners and a corrupted role to collude, W4 witness extraction gives claimed bucket `x_j` and commitment openings without extracting native cipher plaintexts or forcing non-`H` native shares to be one-hot. Non-`H` honest retained output `w_(h,j)` comes from legal CCA decryption and real native execution, while `H` obeys `v_(h,i) = e_(I_i) − v_(c,i)^orig`. At first authorized exposure of complete `R`, a single query to `O_C(R)` suffices to compute:

`V_h,R = O_C(R) − Σ_(j ∈ R \ H) e_(x_j) − Σ_(i ∈ R ∩ H) v_(c,i)^orig + Σ_(j ∈ R \ H) w_(h,j)`.

Sentinel counts are recovered from public `b` if stripped. Non-`H` failures block `R` release; exact retries reuse cached states without leaking individual histograms. Experiment `A` never queries `O_C`.

## 9. Substantive Model Counterexamples and Audit Boundaries

Exposing public `q_i/Delta_j` enables `C' = C + Σ_public(phi_i − phi'_i)[q_i/Delta_j]_1` with constant `A, B` and low degree, proving degree checks insufficient on their own (illustrated via a private-free `x·1 = 0` R1CS example moving `x = 0` to `x = 1`); the frozen keys contain no such public inverse queries. Conversely, pure `alpha_G2` causes no break (§5.4 Direction II), and legacy non-prime `G2` optimal-ate projection failures are blocked by explicit full-integer `[r]P = O` subgroup guards.

First-pass read-only checks exited 0 across enumeration, historical closure, exact rationals, degrees, and negative controls. Supporting scripts verify arithmetic and bytes without substituting for §§4–8 proofs or running provers/native/G5/G6.

## 10. Verification Record and Stable Delivery

Final `audit_budget.py` [source omitted from this derivative] recomputed read-only: complete source slot enumeration and historical closure; shared `alpha/beta/gamma` headers across all five keys with identical ABC and distinct `Delta`s for historical genesis; derived section degrees; exact algebraic equality of `H1/H2/HT` and collisions; exhaustive branch checking in `F_7`; exhaustive `10201` proof-coin bijection and `C` check in `F_101`; exhaustive `101 × 10201` affine mass checks; and conditional domain size checks per `mu`. Results were saved in `budget-audit-004.json` [source omitted from this derivative] without altering `001–003`.

Example caps in `groth16-budget-contract.json` (`S_g = S_t = V_g = V_t = 2^19`, `S_l = V_l = 0`, `Q1 = Q2 = QT = Qpair = 2^40`, `I1 = I2 = 2^20`) evaluate in exact rational arithmetic to single-endpoint `epsilon_G16 < 2^-150` — an arithmetic illustration inside the generic model rather than runtime enforcement, system-wide security bit-level, or performance measurement. Execution errors/patch call history are logged in `execution-record.json` [source omitted from this derivative]. W4 signs solely the conditional theorem and explicit ledger herein; overall G4b acceptance follows root composition, independent review, and final checks.
