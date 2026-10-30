# Reproducing the manuscript results

This repository contains the manuscript, detailed arguments, component sources and aggregate evaluation data. The instructions below rebuild the paper and check the reported numbers from the distributed data. They do not rerun the native service, generate proofs or rescan the original trajectory corpora.

## 1. Obtain and check the artifact

Download or clone this repository and enter its root directory. Python 3.10 or later is sufficient for the data checks, with no third-party Python packages.

```sh
python3 reproduce.py
```

The script first verifies the files listed in `SHA256SUMS.json`. It then recomputes the binding timing medians and ranges, the median of the five paired time ratios, the four-corpus actor-day counts and percentages, the roster denominators, and the Full and trusted-generation window and session values. A successful run ends with `PASS`.

The binding measurements use a fixed fixture per relation. The fixtures do not represent the same business input. The Full and trusted-generation results are one observation per arm with different trust assumptions, and collection is included in the window. The four-corpus results are an offline input screen, not native release rates. The underlying tables and their definitions are in [evaluation evidence](evidence/evaluation/README.md).

## 2. Rebuild the manuscript

Install a TeX distribution with IEEEtran, `pdflatex`, `biber`, `stfloats`, and the packages used by the manuscript. From the repository root run:

```sh
cd paper
pdflatex -interaction=nonstopmode -halt-on-error submission.tex
biber submission
pdflatex -interaction=nonstopmode -halt-on-error submission.tex
pdflatex -interaction=nonstopmode -halt-on-error submission.tex
```

The resulting `paper/submission.pdf` contains the paper and appendix. A build can differ in PDF metadata or byte-level output across TeX installations. Run `python3 reproduce.py` before rebuilding to check the distributed PDF and source against the manifest.

## 3. Inspect the technical artifacts

- [Proof guide](proof/README.md) maps the manuscript statements to the detailed security arguments and their assumptions.
- [Bounded model specification](current/model/ClosureV5.tla) and [case inventory](current/model/cases.json) document the model and configurations. This repository does not include the model runner or all configurations needed to repeat the full campaign.
- [Binding component sources](evidence/) and the evaluation tables support inspection of the component comparison. The [mechanism ablation data](evidence/perf-mode.csv) uses a server-only endpoint. The [offline replay data](evidence/offline-aggregate.json) is distinct from the native runs.

The complete native service, the receiver used for the lifecycle comparison, original trajectory inputs, experiment keys and witnesses are not included. Repeating those experiments requires obtaining the appropriate inputs and implementation separately, preparing new keys and configurations, and following the original experimental contracts. The available summary tables do not establish that such a rerun has been performed. The [implementation provenance record](evidence/perf-binary-identity.json) documents the scope of the retained binary evidence.
