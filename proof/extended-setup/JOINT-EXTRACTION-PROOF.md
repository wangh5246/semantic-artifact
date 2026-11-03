# Joint extraction proof for the pot14 + pot22 source family (candidate rev2)

2026-11-01. This is the expanded joint derivation requested by the local
review. It replaces the earlier L4 sketch. It is a **candidate proof** for
independent review; it is not an independently reviewed theorem. The actual
old N8 and old D10001 key bytes were read through the `wang` account and their
section counts are now exact (K2 v3), so this proof uses actual key profiles,
not structural source classes.

## 1. Variables and source normal form

**Family F0 (pot14).** `X, alpha, beta` and deltas `Delta_1,...,Delta_4` for
the current genesis, current transition (`t`), historical genesis and N8 keys.
The target key is `t`; its delta is `Delta_t`; its QAP is
`U_t,V_t,W_t`, public form `Q_t(phi)`, `t_t=X^n_t-1`.

**Family F1 (pot22).** `X', alpha', beta'` and deltas `Delta_5,Delta_6` for
the old and new D=10001 keys. The public pot22 ptau and both keys are in the
source basis. F1 has no target QAP; its keys are auxiliary/foreign.

Every G1 handle in the execution is written, using the actual source basis,

```
A = alpha*a + beta*b + P0 + sum_{r in F0, r!=?} c_r Delta_r
    + sum_{r in F0} E_r/Delta_r
    + alpha'*a' + beta'*b' + P1 + sum_{s in F1} c'_s Delta_s
    + sum_{s in F1} E'_s/Delta_s
    + sum_i a_i mu_i + sum_i b_i S_i
B = alpha*h + beta*f + Q0 + sum_{r in F0} g_r Delta_r
    + alpha'*h' + beta'*f' + Q1 + sum_{s in F1} g'_s Delta_s
    + sum_i z_i nu_i
C = alpha*hat_a + beta*hat_b + Phat0 + sum_{r in F0} hat_c_r Delta_r
    + sum_{r in F0} Ehat_r/Delta_r
    + alpha'*hat_a' + beta'*hat_b' + Phat1
    + sum_{s in F1} hat_c'_s Delta_s
    + sum_{s in F1} Ehat'_s/Delta_s
    + sum_i hat_a_i mu_i + sum_i hat_b_i S_i ,
```

where `E_r=beta U_{r,e}+alpha V_{r,e}+W_{r,e}+K_r` and
`E'_s=beta' U'_{s,e'}+alpha' V'_{s,e'}+W'_{s,e'}+K'_s`; all coefficients are
known scalars. `P0,Q0,Phat0` are in the actual F0 source span; `P1,Q1,Phat1` in
the F1 span. A source proof under key `kappa` is registered as

```
(mu_i, nu_i, S_i),   S_i = (mu_i nu_i - alpha_kappa beta_kappa - Q_kappa(phi_i))/Delta_kappa
```

with `alpha_kappa=alpha,beta_kappa=beta` for F0 and `alpha',beta'` for F1. The
target verification equation is

```
A B = alpha beta + Q_t(phi) + Delta_t C .                         (T)
```

The source equations are not additional target equations; they define the
registered source terms. The target QAP and its Lemma Q/H are unchanged.

## 2. Lemma J1 — mixed top terms

Compare the **delta-free degree-two monomials** in `alpha,beta,alpha',beta'`
in (T). The source `E_r/Delta_r`, `E'_s/Delta_s` and `S_i` terms carry a delta
denominator and do not contribute to these monomials; the RHS has coefficient
`1` on `alpha beta` and `0` on every other delta-free degree-two monomial.
Hence

```
alpha^2:   a h = 0                         (1)
beta^2:    b f = 0                         (2)
alpha beta: a f + b h = 1                  (3)
alpha'^2:  a' h' = 0                       (4)
beta'^2:   b' f' = 0                       (5)
alpha'beta': a' f' + b' h' = 0             (6)
alpha beta': a f' + b' h = 0               (7)
alpha'beta: a' f + b h' = 0                (8)
```

The F0 equations (1)-(3) are the G4b branch equations. There are exactly two
cases:

**Case I (`a != 0`).** `h=0`, `a f=1`, `b=0`. From (7), `a f'=0`, so `f'=0`.
From (8), `a' f=0`, so `a'=0`. The `beta beta'` and `alpha alpha'` coefficients
of `A B` are `b' f` and `a h'`; both vanish with `b=0,h=0` for all `b',h'`.
Equations (4)-(6) then hold. Thus `a'=b'=f'=h'=0`.

**Case II (`a=0`).** `b h=1`, `f=0`. From (7), `b' h=0`, so `b'=0`. From (8),
`b h'=0`, so `h'=0`. The `alpha alpha'` coefficient is `a' h` and the
`beta beta'` coefficient is `b f'`; both vanish with `h,b != 0`, so
`a'=f'=0`. Equations (4)-(6) hold. Again `a'=b'=f'=h'=0`.

Therefore the F1 **constant** `alpha'/beta'` components vanish in both target
branches; the target branch remains the G4b direction I or II. This lemma does
not by itself handle `X'`-dependent F1 terms (`alpha' X'^i`, `beta' X'^i`) or
F1 denominators/source terms; those are separated next.

## 3. Lemma J2 — F1 interior and foreign-source separation

Let `V1` be the formal span of all F1 setup handles (pot22 ptau and both D10001
key/vkey sections) plus F1 source terms. Decompose the polynomial identity (T)
by its `V1` component. The RHS `V1` component is exactly `Delta_t C1`, where
`C1` is the F1 part of C; the LHS `V1` component is the `V1` component of
`A B`. Two cases:

1. The two `V1` components are equal as formal expressions. Then all F1
   terms cancel; the remaining F0 equation is the G4b target equation, with
   only F0 keys and target key `t`. The F1 source terms may have been used,
   but they are registered/auxiliary; no target statement exception arises
   from them because their key namespace is not `t` (old/new D10001 are
   distinct F1 namespaces; N8 is F0 with a different key/delta/circuit).
2. They are unequal as formal expressions. This is a generic collision/bad
   event counted in the global collision bound, unless the difference is a
   registered source term. In the latter case the extractor names the
   registered foreign source; it cannot name it as a target-source exception
   because the key/relation namespace differs. A real foreign proof is charged
   to `S_ext`; a fully inlined one has its generic operations charged to Q.
   It is not free merely because it is foreign.

For a source term under a foreign key `r != t` (including N8 and both D10001
keys), apply the G4b Section 5.2-5.3 source-index argument: independent `nu_i`
terms kill the source coefficients; a surviving diagonal term forces the same
source index and `r=t`. Since the target key is `t` and the foreign key
namespace is different, the diagonal same-key branch is impossible for a
foreign source. Thus a foreign source cannot be the target same-key exception;
it is either auxiliary (charged to `S_ext`/Q) or part of a formal-inequality
bad event. The old and new D10001 keys are distinct `Delta_5`/`Delta_6`
namespaces; a proof under one cannot be transported to the other or to `t`.

After J2, the target equation's F0 part is the G4b equation with target key
`t` and any target-namespace source terms; foreign terms are registered or
bad. This is the point where the earlier sketch incorrectly put "Theorem E
unchanged" in A4; it is a conclusion of J1+J2, not an assumption.

### J2.1 Mixed-term table

The `V1` component of `A B` is the sum of the following families; each entry
is compared with the target RHS `Delta_t C1`:

| product | F1 form | target RHS | handling |
| --- | --- | --- | --- |
| `A0 B1` | `(alpha,beta,Delta_r,E_r/Delta_r) * (alpha',beta',Q1,Delta_s)` | only `Delta_t C1` | equal/cancel or formal inequality (collision) |
| `A1 B0` | `(alpha',beta',P1,Delta_s,E'_s/Delta_s) * (alpha,beta,Delta_r)` | only `Delta_t C1` | same |
| `A1 B1` | F1 x F1 (including `alpha'beta'`, `P1 Q1`, delta products) | none except registered source terms | must vanish or be a registered F1 source; otherwise collision |
| source `a_i mu_i * z_j nu_j` | F1 source mu/nu | target RHS has no mu/nu except through `Delta_t C1` | G4b Section 5.2-5.3 source-index argument |
| F1 `S_i` / `Delta_s` terms | denominator `Delta_s` | `Delta_t C1` and source registration | foreign source; no target same-key exception |

The constant `alpha'/beta'` rows are already zero by J1. The remaining F1
terms are `X'`-dependent setup/source terms; their formal equality with
`Delta_t C1` is a linear condition in the logged source basis. If it holds,
the F1 terms cancel and the F0 target equation remains. If it fails, the
difference is a formal-inequality generic collision; it cannot be silently
dropped. If the difference is exactly a registered F1 source term, the
extractor names that foreign source; it is charged to `S_ext` (real/simulated)
or Q (full inline).

### J2.2 Foreign-source extraction branches

For a source under key `r`:

1. **Target-namespace source** (`r=t`, same relation/signals). The extractor
   returns the target-source exception; this is the only source exception.
2. **Foreign source** (`r != t`: N8, old/new D10001). The same-index/delta
   branch would require `r=t`; it is impossible. The source is auxiliary; it
   is registered in `S_ext` or Q. If the target proof has no target witness
   and no target source, the target equation's F0 residual cannot be satisfied
   by a foreign source alone; that case is a formal-inequality collision, not
   an accepted target proof.
3. **No source** (source coefficients zero). The F0 G4b branches I/II apply and
   extract the target witness by J3.

The old and new D10001 namespaces are distinct (`Delta_5` versus `Delta_6`);
a proof under one cannot be the same-key exception for the other or for `t`.
N8 is F0 but has a different key/delta/circuit; it is foreign to `t` by
namespace and delta.

## 4. Lemma J3 — target extraction branches

On the remaining F0 equation, apply the G4b Section 5.2-5.4 derivation:

- If a registered target source term is the reason for acceptance, the
  extractor names the exact target `(key=t, relation, ordered signals)` source
  and stops.
- Otherwise, the G4b directions I (`a != 0`) or II (`a=0`) apply to the target
  `U_t,V_t,W_t`; the `E_r` and private terms are killed by the independent
  target deltas; the equations reduce to
  `U_t(phi,e_hat)V_t(phi,e_hat)-W_t(phi,e_hat)=K_hat_t`, and Lemma H
  recovers a standard `t_t H` and a complete private scalar vector `e_hat`.
  This is the target witness.

The F1 source terms do not appear in the target Lemma H; they are auxiliary.
The target Q/H is reused because the target QAP is unchanged; the expanded
auxiliary input is handled by J1/J2, and the extraction conclusion is **not**
assumed in A4.

## 5. Lemma J4 — bad event, handles and degree

All formal expressions in (T), the source equations and all oracle outputs are
covered by one all-execution generic collision union bound, as in G4b Section 7.
The source counts include the known extra-key proofs and any target-key
external source proofs or Q inlining; they are not free because of namespace.
The handle counts are the v3 source basis (actual old/new key sections and
pot22 ptau). The common denominator is

```
D = Delta_1 Delta_2 Delta_3 Delta_4 Delta_5 Delta_6 ,  k=6 .
```

The six-delta degree rule is G4b Section 6's `D1'=max(L1+k,M+k-1)`,
`D2'=L2`, `DT'=max(D1'+L2,D1'+1,max_r n_r+k,2+k)`. Using the actual pot22 raw
G1 degree `L1=8,388,606`, `L2=4,194,303`, `k=6`, and `M <= 1,048,576`:

```
D1_candidate = 8,388,612
D2_candidate = 4,194,303
DT_candidate = 12,582,915 .
```

This corrects the v2 `8,388,609 / 12,582,912` (which used the k=3 `+3`).
It is a **candidate correction for the full re-derivation**, not a certified
complete new bound; all source columns and contribution transcript terms still
need the full enumeration. See `DEGREE-DERIVATION.md`.

## 6. What this proof does and does not establish

It establishes, conditionally and pending independent review, the joint
extraction conclusion for the target key under the explicit setup model:
after the old keys are actual (K2 v3), the two-family top terms and foreign
source terms are separated; the target witness or target source is extracted;
the extra keys are auxiliary. It does not prove the v6 relation's own privacy,
does not claim the v6 receiver, and does not make the old/new visibility
facts a publication claim. The setup correctness/unknown-trapdoor and latent
independence assumptions remain explicit; actual old key file membership is
now checked by SHA/sections, while the correctness/entropy of the setup remains
a premise.

Remaining review blockers: independent mathematical review of J1-J4; the full
degree/source enumeration and S_ext completeness; the ceremony independence
assumption; and the manuscript decision.
