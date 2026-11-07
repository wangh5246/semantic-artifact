# Artifact Evaluation and Replication Package
# SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation

This package contains the replication artifact for the research paper:
> **SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation**  
> IEEE Symposium on Security and Privacy (S&P) 2027

This artifact evaluation package provides the complete mathematical proofs, arithmetized circuit relations, formal TLA+ state models, numerical evaluation records, and a self-contained reproduction runner to verify all claims and tables in the paper.

---

## 1. Overview and Target Badges

This package is prepared for Artifact Evaluation and supports:
- **Artifacts Available**: All formal proofs, circuit code, formal models, evaluation data, and LaTeX paper sources are self-contained in this archive.
- **Artifacts Functional**: The verification runner executes turnkey out of the box with zero external package dependencies.
- **Results Replicated**: All numerical claims, constraint reduction ratios, prover timing speedups (Table 6), end-to-end lifecycle overheads (Table 8), and trajectory feasibility rates (Section 5.2) are directly recomputed and verified against the reported values.

---

## 2. System and Environment Requirements

### Hardware Requirements
- **Processor**: Any standard x86_64 or ARM64 (Apple Silicon) processor.
- **Memory**: < 100 MB RAM.
- **Disk Space**: < 50 MB free space.
- **Execution Time**: The complete reproduction suite executes in **under 2 seconds**.

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04/22.04 or later), macOS (12.0 or later), or Windows (via WSL2).
- **Python Runtime**: Python 3.10 or later (**standard library only**; no `pip` packages required).
- *(Optional for rebuilding the paper PDF)*: TeX Live 2022+ with `pdflatex`, `biber`, and `IEEEtran.cls`.

---

## 3. Quick Start: One-Command Verification

To run the complete evaluation suite, open a terminal in the root directory of this package and execute:

```bash
python3 reproduce.py
```

### Expected Console Output
Upon successful verification, the script will output:

```text
============================================================================
 SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation
 Artifact Verification and Data Reproduction Runner
============================================================================

[1/5] Checking Structural Components & Interfaces...
  ✓ Integrity verified: 161 files match manifest.json (SHA-256)
  ✓ All 8 formal security proofs and budget contracts present in proof/
  ✓ State transition circuit exposes all 25 ordered public signals (Section 3.3)

[2/5] Verifying Circuit Constraints & Reduction Ratios...
  - Vector commitment (D=    8):     82,712 constraints
  - Vector commitment (D=  101):    828,050 constraints
  - Vector commitment (D= 1001):  7,956,190 constraints
  - Vector commitment (D=10001): 79,002,390 constraints
  - SHTPC Masked Moment (D=10,001):      5,779 constraints
  ✓ Standalone constraint reduction ratio: 13670.60× (13,670.60×)

[3/5] Verifying Table 6 Same-Input Component Timing (15 pairs)...
  Family             | SHTPC M (s)  | Vector V (s)   | Speedup   | Status
  ------------------------------------------------------------------
  Positive shares    |     3.4542 s |       310.41 s |   89.91× | PASS
  Zero coordinate    |     3.4473 s |       310.74 s |   89.90× | PASS
  Boundary elements  |     3.4599 s |       310.93 s |   89.83× | PASS
  ✓ Earlier microbenchmark (different fixtures) paired ratio median: 89.73× (89.73×)

[4/5] Verifying Table 8 End-to-End Lifecycle Pairs (N=100, 5 pairs)...
  - Full session wall time median: 4351.28 s (~72.52 min)
  - Trusted (T) session wall time median: 3156.83 s (~52.61 min)
  - Paired T / Full session ratio median: 0.7255 (Full is 1.38× T)
  - Paired T / Full window ratio median:  0.6958 (Full is 1.44× T)
  ✓ T stage medians: Reg 92.414s, Driver 105.581s, Freeze 41.403s, Collection 61.555s

[5/5] Verifying Four-Corpus Trajectory Feasibility Data...
  Dataset    | Legal Days   | Total Days   | Legal Rate | Status
  --------------------------------------------------------
  t-drive    |     12,162   |     29,658   |    41.01%  | PASS
  porto      |        116   |      1,200   |     9.67%  | PASS
  geolife    |          9   |         85   |    10.59%  | PASS
  rome       |        836   |        871   |    95.98%  | PASS

============================================================================
 ALL VERIFICATIONS PASSED (5/5).
 Distributed proofs, circuits, numerical data and arithmetic match the paper.
============================================================================
```

---

## 4. Step-by-Step Claim-to-Evidence Verification

### Step 1: Package Integrity Verification
- **Artifact Path**: `manifest.json`
- **Description**: Contains the SHA-256 digests for all 161 distributed artifact files. `reproduce.py` reads `manifest.json` and asserts that every file is present and unaltered.

### Step 2: State Transition Circuit & 25 Public Signals
- **Paper Reference**: Section 3.3 (Cross-field canonical encoding and transition relation)
- **Artifact Path**: `circuits/hadwc_transition_v5.circom`
- **Verification**: `reproduce.py` inspects the transition circuit AST to ensure that all 25 ordered public signals match the formal profile contract:
  ```circom
  signal input relation_version;
  signal input c_a_x; signal input c_a_y;
  signal input c_r_x; signal input c_r_y;
  signal input c_prev_x; signal input c_prev_y;
  signal input c_next_x; signal input c_next_y;
  signal input c_ticket_x; signal input c_ticket_y;
  signal input c_receipt_x; signal input c_receipt_y;
  signal input anchor_prev_x; signal input anchor_prev_y;
  signal input anchor_next_x; signal input anchor_next_y;
  signal input key_tag_96;
  signal input masked_native_index;
  signal input contribution_bit;
  signal input rid_128;
  signal input ctx_limb_hi; signal input ctx_limb_lo;
  signal input c_k_anchor_x; signal input c_k_anchor_y;
  ```
- **Enforced Conditions**:
  - Spatial Grid mapping: $p = \mathsf{Grid}(\mathbf{x}_r)$
  - Speed-tier drift bounding: $\|\mathbf{x}_r - \mathbf{x}_{\rm prev}\|^2 \le \tau_u^2 \Delta t_t^2$
  - Anchor distance cap: $\|\mathbf{x}_r - \mathbf{a}_t\|^2 \le \min\{\tau_u^2 (\Delta T_t^{(K)})^2, c_{\rm policy}^2\}$
  - Cross-field canonical scalar relation: $x + r_A + r_B = T + \chi q$ with $\chi \in \{0, 1, 2\}$

### Step 3: Standalone Constraint Reduction Ratio
- **Paper Reference**: Section 3.3, Section 5.3, Figure 4
- **Artifact Path**: `evidence/binding/bins8.json` .. `bins10001.json`
- **Verification**:
  - SHTPC masked-moment circuit: **5,779 constraints**
  - Direct seed binding circuit ($D=10{,}001$): **79,002,390 constraints**
  - Constraint reduction ratio: $\frac{79{,}002{,}390}{5{,}779} = \mathbf{13{,}670.60\times}$

### Step 4: Same-Input Prover Speedup (Table 6)
- **Paper Reference**: Section 5.3, Table 6
- **Artifact Path**: `evidence/evaluation/binding-derived.json`, `evidence/evaluation/binding-full-table.tex`
- **Verification**:
  - Recomputes 15 paired proving runs across three share distributions under identical secret-share inputs (`M` = SHTPC masked-moment binding; `V` = constructed Poseidon vector binding):
    - **Positive shares (`B-pos`)**: SHTPC (`M`) median 3.4542 s vs Vector (`V`) median 310.41 s $\to$ **89.91×** paired median speedup.
    - **Zero coordinate (`B-zero`)**: SHTPC (`M`) median 3.4473 s vs Vector (`V`) median 310.74 s $\to$ **89.90×** paired median speedup.
    - **Boundary elements (`B-edge`)**: SHTPC (`M`) median 3.4599 s vs Vector (`V`) median 310.93 s $\to$ **89.83×** paired median speedup.
  - Prover peak memory: SHTPC (`M`) ~0.30 GiB RSS vs Vector (`V`) baseline ~13.92 GiB RSS.

### Step 5: End-to-End Lifecycle Overhead (Table 8 & Section 5.6)
- **Paper Reference**: Section 5.6, Table 8
- **Artifact Path**: `evidence/evaluation/lifecycle-pairs.json`
- **Verification**:
  - Recomputes 5 paired runs of $N=100$ clients across 600 history-priming steps:
    - Full SHTPC session median: **4,351.28 s** (~72.52 min)
    - Trusted generator (T) session median: **3,156.83 s** (~52.61 min)
    - Paired T / Full session ratio median: **0.7255** (Full session is 1.38× T)
    - Paired T / Full window ratio median: **0.6958** (Full window is 1.44× T)
    - T stage medians: Construction & registration 92.41 s, Driver ingestion 105.58 s, Server freeze 41.40 s, Collection 61.56 s.

### Step 6: Four-Corpus Trajectory Feasibility
- **Paper Reference**: Section 5.2, Table 5, Figure 3
- **Artifact Path**: `evidence/evaluation/four-corpus-pooled.csv`, `evidence/evaluation/reason-counts-by-date.csv`
- **Verification**:
  - Recomputes legal actor-days and validates that `sum(reason_counts) == denominator` for each observed day:
    - **T-Drive**: 12,162 / 29,658 legal actor-days (41.01%)
    - **Porto**: 116 / 1,200 legal actor-days (9.67%)
    - **GeoLife**: 9 / 85 legal actor-days (10.59%)
    - **Rome**: 836 / 871 legal actor-days (95.98%)
  - Confirms zero predecessor distance violations (`PREDECESSOR_DISTANCE == 0`).

---

## 5. Security Proofs and Theorem Navigation

All reduction arguments, game definitions, hybrid sequences, and multi-window extensions are stored in `proof/` (with a mirror at `artifact/proof/` to match the exact citation path in Section 8 of the paper).

| Paper Theorem / Lemma | Statement Title in Paper | Artifact Document | Key Sections |
| :--- | :--- | :--- | :--- |
| **Theorem 1** | Accepted-history composition at first exposure | [`proof/07-composition-and-explicit-bounds.md`](proof/07-composition-and-explicit-bounds.md), [`proof/05-closure-prefix-and-refinement.md`](proof/05-closure-prefix-and-refinement.md) | §§2–3, 5; §§3–5 |
| **Theorem 2** | Joint privacy of admission and aggregation views | [`proof/04-full-view-simulation.md`](proof/04-full-view-simulation.md) | §§2–7 |
| **Theorem B.1** | Concrete two-party native privacy | [`proof/03-native-privacy-and-query-ledger.md`](proof/03-native-privacy-and-query-ledger.md) | §§2–5, 7 |
| **Theorem B.2** | Joint privacy of admission and native release | [`proof/07-composition-and-explicit-bounds.md`](proof/07-composition-and-explicit-bounds.md) | §5 |
| **Theorem B.3** | Predeclared multi-window privacy | [`proof/08-multi-window-privacy.md`](proof/08-multi-window-privacy.md) | §§1–8 |
| **Lemma 1** | Native moment fidelity | [`proof/03-native-privacy-and-query-ledger.md`](proof/03-native-privacy-and-query-ledger.md) | §2 |
| **Lemma 2** | Related-setup extraction | [`proof/extended-setup/K3-SOURCE-EXTENSION-FINAL.md`](proof/extended-setup/K3-SOURCE-EXTENSION-FINAL.md), [`proof/02-groth16-extraction-and-budget.md`](proof/02-groth16-extraction-and-budget.md) | Theorem E′; §§4–5 |
| **Lemma B.1** | Origin isolation | [`proof/04-full-view-simulation.md`](proof/04-full-view-simulation.md) | §§2–3 |
| **Lemma B.2** | Concrete Histogram preparation view | [`proof/03-native-privacy-and-query-ledger.md`](proof/03-native-privacy-and-query-ledger.md) | §§2–4 |

Machine-readable budget ledgers:
- `proof/groth16-budget-contract.json`: Group element handle counts and cleared degree polynomials.
- `proof/native-budget-contract.json`: Random oracle query bounds and stream truncation limits.
- `proof/composition-budget-contract.json`: Joint composition resource accounting.

---

## 6. Directory Layout

```text
.
├── README.md                      # This replication guide
├── reproduce.py                   # Turnkey verification script (0 external dependencies)
├── manifest.json                  # SHA-256 integrity manifest for all 161 package files
├── paper/                         # Anonymized manuscript sources and build environment
│   ├── submission.pdf             # Compiled 18-page manuscript (IEEE S&P 2027)
│   ├── submission.tex             # LaTeX source code
│   ├── reference.bib              # Bibliography database (45 references)
│   ├── build.sh                   # Compilation script
│   └── check_submission.py        # Submission page-limit and format gate checker
├── artifact/
│   └── proof/                     # Path mirror matching paper citation "artifact/proof/"
├── proof/                         # Complete formal security proofs and budget ledgers
│   ├── 01-security-games-and-ideal-interface.md
│   ├── 02-groth16-extraction-and-budget.md
│   ├── 03-native-privacy-and-query-ledger.md
│   ├── 04-full-view-simulation.md
│   ├── 05-closure-prefix-and-refinement.md
│   ├── 06-counterexamples-and-scope.md
│   ├── 07-composition-and-explicit-bounds.md
│   ├── 08-multi-window-privacy.md # Theorem B.3 (Multi-window extension)
│   ├── groth16-budget-contract.json
│   ├── native-budget-contract.json
│   ├── composition-budget-contract.json
│   └── extended-setup/            # Extended setup source family & joint extraction
├── circuits/                      # Zero-knowledge circuits & verification kernels
│   ├── hadwc_transition_v5.circom # Fixed transition circuit (25 public signals)
│   ├── hadwc_common_v5.circom     # Common primitives & range checkers
│   ├── poseidon4.circom           # Poseidon sponge kernel
│   ├── poseidon16.circom
│   ├── keccak12.circom            # Keccak comparison kernel
│   ├── share_row.circom
│   └── check_r1cs_v2.cpp          # C++ streaming R1CS constraint verifier
├── model/                         # Formal state machine specification
│   ├── ClosureState.tla           # TLA+ specification
│   └── cases.json                 # Model checker configurations
└── evidence/                      # Numerical records & evaluation data
    ├── binding/                   # Vector baseline constraint receipts (bins 8..10001)
    └── evaluation/                # Experimental timing, lifecycle pairs, corpus logs
```

---

## 7. Scope and Evaluation Boundaries

- **Admitted Claims**: SHTPC security guarantees hold for admitted reports within the dual trust model (honest client origin and non-colluding Aggregators). SHTPC does not establish physical GPS ground truth or defend against Sybil identity generation.
- **Strict Membership Contract**: Release requires the entire eligible cohort. In accordance with strict privacy guarantees, dropouts trigger durable server redelivery rather than dynamic cohort intersection release.
- **Differential Privacy**: SHTPC protects protocol views and execution transcripts. Differential privacy applied to released histogram totals is orthogonal and complementary.
- **Data Protection and Double-Blind Anonymity**: In accordance with user privacy and double-blind review policies, raw user trajectories, private commitment openings, witness caches, and secret keys are excluded. All numerical claims are verified against retained, certified execution records.
