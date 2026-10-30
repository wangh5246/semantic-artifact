# SHTPC manuscript and evidence update — 30 October 2026

This update accompanies the [anonymous manuscript](paper/submission.pdf) and its [source](paper/submission.tex). Build instructions and the exact manuscript dependencies are in [paper](paper/README.md).

The detailed frozen-profile proof arguments and their reading map are in [proof](proof/README.md). These are conditional on their stated models and do not cover additional setup-dependent sources automatically.

The [current result summary](evidence/results-20261030/README.md) separates fixed-fixture E1 component timings, the Full/T lifecycle pair and the four-corpus offline input screen. The earlier [mechanism ablation](evidence/perf-mode.csv) uses a different host and a server-only window. Its M/A/Z runs have three observations each and Full has two. The earlier [offline replay outcomes](evidence/offline-aggregate.json) are not native executions. The [binary identity ledger](evidence/perf-binary-identity.json) records the remaining source-to-binary provenance limitation.

The historical vector-commitment sources and overlap record are retained as historical evidence, not the component timing in the current paper. See [historical v6 contract](evidence/v6-contract.md) and [overlap](evidence/v6-timing-overlap.json). The base repository's `current/` tree supplies the implementation and model paths referenced by the manuscript and remains a separate earlier source release. This update does not assert that its receiver implements the later Full/T control or that all experiments share a binary.

Raw trajectories, linkable actor records, experiment secrets, private witnesses and databases are not included. Source hashes identify retained local records, not publicly downloadable raw data. The figures are descriptive and the checks do not establish production security or independent proof validation.
