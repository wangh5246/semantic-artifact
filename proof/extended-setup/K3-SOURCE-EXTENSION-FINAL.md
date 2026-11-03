# K3 final: extended source-family theorem E'

2026-11-01. Status: **PROVED IN THE DECLARED MODEL.** The target extraction
conclusion is a theorem under the explicit setup/source assumptions below; no
"unknown visibility" or "pending extraction" field remains. This is a
self-contained formal package, not a production ceremony certification and not
an independent peer-review claim.

## Model and source family

The target relation is the frozen v5 current transition/genesis. The extra
keys are auxiliary sources, not target proving keys. The model includes all
known setup-dependent material:

- pot14: current genesis, current transition, historical genesis, N8;
- pot22: old D=10001 `3b87…`, new D=10001 `d32e…`, public Hermez pot22;
- v6 N8/D10001 circuit sources;
- public source proofs under those keys; a source cap `S_ext=2^19` covers the
  31 known extra-key proofs.

The old N8/D10001 keys are actual bytes (hashes/sections in K2 v3); the
old/new D10001 keys share the initial key `6098…` and pot22 but have distinct
final contributions. The v5-only subset reproduces G4b N10/N20/NT0; the v3
total is N1/N2/NT = 65,293,168/16,131,831/8.

## Explicit model assumptions (not unknowns)

A1. Each phase 1 is a correct setup with unknown trapdoors; X/alpha/beta are
independently sampled; all deltas are nonzero and independent; the pot14 and
pot22 ceremonies are independent and each has at least one honest
contribution. The pot22 file is the public Hermez ceremony; no independent
ceremony audit is part of this theorem.

A2. Latent setup variables and phase-2 contribution randomness are sampled
from their declared distributions; every serialized QAP, private
`q_i/Delta_r`, and key point is a deterministic function of the same
R1CS/algorithm/variables. We do not replace correlated points by independent
random points. The actual old files are checked by SHA/sections; their
membership in the declared family is a file check, not an entropy claim.

A3. The target v5 QAP and Lemma Q/H are unchanged; the target verifier
accepts only the current v5 namespace; no target public `q_i/Delta_r` query is
exposed. A runtime namespace rejection does not remove auxiliary input.

A4. Source proofs are registered by key namespace/relation/ordered signals;
real/simulated external sources are charged to S; fully inlined sources are
charged to Q. The source cap is a budget parameter.

## Theorem E' (target extraction extended)

For every finite adaptive execution in the declared model with source caps,
except with probability at most `g_v3`, every accepted target proof yields a
complete R1CS witness or names a registered **target-namespace** source
(`key=t`, same relation and ordered signals). Foreign sources (N8, old/new
D10001) are auxiliary: they can be registered/charged but cannot be the
target-source exception.

**Proof.** The joint derivation is `JOINT-EXTRACTION-PROOF.md`:

1. J1: two-family source normal form; the delta-free top `alpha,beta,alpha',beta'`
   coefficient equations; both target branches force the F1 constant
   `alpha'/beta'` components to zero.
2. J2: mixed F1 terms are compared with the target RHS `Delta_t C1`; equality
   cancels them, inequality is a formal-inequality bad event, and registered
   foreign sources are charged. The source-index/delta branch cannot make a
   foreign key a target exception; old/new D10001 namespaces are distinct.
3. J3: the remaining F0 target equation is the G4b equation; Section 5.4
   directions I/II and Lemma H extract the target witness; a target source is
   the only source exception.
4. J4: one all-execution generic collision union bound covers all formal
   inequalities, source equations and verification results. The degree
   enumeration is `DEGREE-DERIVATION-REV2.md`: D1=8,388,612, D2=4,194,303,
   DT=12,582,915. The v3 budget is `budget-v3.json`.

The target QAP/Lemma Q/H are reused because the target QAP is unchanged; the
expanded auxiliary input is handled by J1/J2, and the extraction conclusion is
J3, not an assumption.

## Budget

With the declared `S_ext` cap `2^19` (covering the known 31 extra-key proofs),
tight caps `Q=2^32`, `S_g=S_t=V_g=V_t=2^19`, `I=2^20`:

- `epsilon_G16 = 2.67372523e-50 < 2^-150`;
- the known-31 sensitivity is `2.67350513e-50`;
- the old G4b `Q=2^40` example is `1.73749815e-45`, not below 2^-150; the
  three-key old example is not the extended-family bound.

The arithmetic is exact-rational; the formulas are the G4b §7 formulas with
the extended counts/degrees. The v3 caps are a declared attack budget, not a
claim that the old 2^40 example carries over.

## Scope and non-claims

- This proves the **target v5 extraction/combination** in the declared model.
  It does not prove the v6 relation's own privacy, live Janus receiver,
  production ceremony security, physical location, Sybil resistance, DP, or a
  global publication fact.
- `visibility/publication` is not an applicability condition: all known
  materials are conservatively granted. The bounded publication audit found no
  actual key bytes in the checked local channels, but no global
  non-publication claim is made.
- The actual old keys are read and checked; the source family is no longer a
  structural guess.
- Independent external peer review is a publication process, not an open
  model assumption. The formal package is provided for that review.

## Manuscript

The current paper's three-key numerical example is a subset; the extended E'
and v3 budget are in this artifact. If the paper is updated to cite E', the
proposed wording is in `MANUSCRIPT-CONDITIONS.md`; the experiment itself is
complete without changing the paper's three-key conservative scope.
