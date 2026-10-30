# Detailed proofs and manuscript map

The numbered G4b documents below contain the detailed mathematical arguments referenced by the current manuscript. Document numbers are stable identifiers, not manuscript theorem numbers. Read the manuscript's source model together with these arguments. The three-key ledger does not automatically cover later setup-dependent material outside its enumerated basis.

| Manuscript entry | Proof file and sections |
| --- | --- |
| Lemma 2, related-setup extraction | [G4b 02](02-groth16-extraction-and-budget.md), §§2–3 model and complete source inventory, §4 Q/H lemmas, §5 exhaustive coefficient branches and online extraction, §§6–7 degrees and probability bound |
| Appendix B, proof-field budget g | [G4b 02](02-groth16-extraction-and-budget.md), §§3,6–7; [Groth16 budget contract](groth16-budget-contract.json) |
| Native preparation and stream bound | [G4b 03](03-native-privacy-and-query-ledger.md), §§2–4 full-verifier distribution, seven descriptors and active-peer algorithm; §§5,7 losses and raw-stream coupling; [native budget contract](native-budget-contract.json) |
| Joint privacy and online simulation | [G4b 04](04-full-view-simulation.md), §§2–3 persistent tables and HPKE routing, §§4–5 observer-specific simulators, §§6–7 adjacent hybrids, retries and causal observations |
| Appendix B, ordered composition and explicit bounds | [G4b 07](07-composition-and-explicit-bounds.md), §§2–3 primitive budgets and §5 ordered hops, endpoint accounting and two-world bound; [composition budget contract](composition-budget-contract.json) |
| Security games and ideal interfaces | [G4b 01](01-security-games-and-ideal-interface.md) |
| Closure and implementation refinement | [G4b 05](05-closure-prefix-and-refinement.md) |
| Counterexamples and scope | [G4b 06](06-counterexamples-and-scope.md) |

[PROVENANCE.json](PROVENANCE.json) records the frozen originals and these distribution derivatives. Equations are preserved, while source and profile labels are normalized in this public derivative. Links to omitted implementation assets or historical supporting runs are marked explicitly, rather than presented as downloadable dependencies. The three machine-readable budget contracts are included alongside the proof documents. These arguments are conditional on their declared model and frozen profile; distribution does not certify production setup or all later implementations.
