# Enforcing Hidden-State Policies in Native Private Aggregation

This repository accompanies the [anonymous manuscript](paper/submission.pdf). The [LaTeX source and build instructions](paper/README.md) and [detailed security arguments](proof/README.md) are included.

[Evaluation evidence](evidence/evaluation/README.md) provides the fixed-fixture binding measurements, the Full and trusted-generation lifecycle comparison, and the four-corpus input screen. The [mechanism ablation](evidence/perf-mode.csv) and [offline replay outcomes](evidence/offline-aggregate.json) use their respective measurement contracts. The [binary identity ledger](evidence/perf-binary-identity.json) records the scope of implementation provenance.

The bounded model specification and its case inventory are in [current/model](current/model/). The repository also contains the vector-binding component sources under [evidence/v6](evidence/v6/). These files are supporting artifacts, not a complete native service or a self-contained environment for reproducing every experiment. Raw trajectories, linkable actor records, experiment secrets, private witnesses and databases are not included.

`SHA256SUMS.json` records the SHA-256 digest of each other file in the repository.
