# Detailed proofs and manuscript map

The current manuscript uses the extended source-family extraction and budget in the [extended setup materials](#extended-setup-source-family). The numbered G4b documents below supply the target-relation arguments and other supporting proofs. Their original three-key ledger and budget describe the earlier source family and do not by themselves cover the additional setup-dependent material. Document numbers are stable identifiers, not manuscript theorem numbers.

| Manuscript entry | Proof file and sections |
| --- | --- |
| Lemma 2, related-setup extraction | [Extended theorem](extended-setup/K3-SOURCE-EXTENSION-FINAL.md) and [joint derivation](extended-setup/JOINT-EXTRACTION-PROOF.md); target Q/H lemmas and extraction branches in [G4b 02](02-groth16-extraction-and-budget.md), §§4–5 |
| Appendix B, proof-field budget g | [Extended degree derivation](extended-setup/DEGREE-DERIVATION-REV2.md) and [extended budget](extended-setup/budget-v3.json); earlier three-key derivation in [G4b 02](02-groth16-extraction-and-budget.md), §§3,6–7 |
| Native preparation and stream bound | [G4b 03](03-native-privacy-and-query-ledger.md), §§2–4 full-verifier distribution, seven descriptors and active-peer algorithm; §§5,7 losses and raw-stream coupling; [native budget contract](native-budget-contract.json) |
| Joint privacy and online simulation | [G4b 04](04-full-view-simulation.md), §§2–3 persistent tables and HPKE routing, §§4–5 observer-specific simulators, §§6–7 adjacent hybrids, retries and causal observations |
| Appendix B, ordered composition and explicit bounds | [G4b 07](07-composition-and-explicit-bounds.md), §§2–3 primitive budgets and §5 ordered hops, endpoint accounting and two-world bound; [composition budget contract](composition-budget-contract.json) |
| Security games and ideal interfaces | [G4b 01](01-security-games-and-ideal-interface.md) |
| Closure and implementation refinement | [G4b 05](05-closure-prefix-and-refinement.md) |
| Counterexamples and scope | [G4b 06](06-counterexamples-and-scope.md) |
| Theorem 5, predeclared multi-window privacy | [G4b 08](08-multi-window-privacy.md): k pre-declared windows, per-prefix simulation, per-hop re-derivation and prefetch-variant macro ⑨; review chain and v7 completion recorded in the repository `outputs/` directories named in its provenance header. One task/profile/key namespace with per-report window ownership, reusable accepted-state references and joint execution budgets. The deployed contract stays single-release |

[PROVENANCE.json](PROVENANCE.json) records the frozen originals and these distribution derivatives. Mathematical prose and equations are preserved. Links to omitted implementation assets or historical supporting runs are marked explicitly, rather than presented as downloadable dependencies. The three machine-readable budget contracts are included alongside the proof documents. These arguments are conditional on their declared model and frozen profile; distribution does not certify production setup or all later implementations.

## Extended setup source family

The extended source family, its assumptions and joint extraction argument are in [Theorem E′](extended-setup/K3-SOURCE-EXTENSION-FINAL.md), [joint derivation](extended-setup/JOINT-EXTRACTION-PROOF.md), [degree derivation](extended-setup/DEGREE-DERIVATION-REV2.md), and [budget](extended-setup/budget-v3.json). The prior G4b target QAP and extraction results remain dependencies. The expanded source model is conditional on the listed setup, independence and budget assumptions, and is not an independent ceremony audit.

The optimized export transaction refines the full-scan transaction on the legal reachable install domain. Unique unsigned-decimal window text selects the same reference row. For integer-only records, fixed JSON ordering, escaping and integer text make canonical equality equivalent to parsed equality. Floats are excluded, and other records use parsed comparison. Projection preserves body, window, record and lock identifiers. Both transactions read complete records and the lock certificate, checking the same freeze, lock, count, commit, eligible retained links, consumed membership, frozen set, reservation and payload conditions under one control lock and repeatable-read snapshot. Locking the complete P preserves reference consistency. Installation rejects records outside this domain.
