# Artifact Evaluation and Replication Package
# SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation

This package contains the code, circuits, formal proofs, formal state models, and machine-readable evaluation evidence for the research paper:
> **SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation**  
> IEEE Symposium on Security and Privacy (S&P) 2027  
> *Package Version: Final S&P 2027 Submission Baseline (November 12, 2026)*

*(Note: Manuscript LaTeX sources and PDFs are maintained separately and omitted from this replication bundle so paper revisions never desynchronize artifact files.)*

---

## 1. Overview and Target Badges

This package is prepared for Artifact Evaluation and supports:
- **Artifacts Available**: All formal security proofs, arithmetized circuit relations, formal TLA+ state models, and evaluation data receipts are self-contained in this archive.
- **Artifacts Functional**: The verification runner (`reproduce.py`) executes turnkey out of the box with zero external package dependencies.
- **Results Replicated**: All numerical claims, constraint counts across all three comparison tiers, same-input prover speedups (**Table 5**, Figure 3), end-to-end lifecycle overheads (**Table 7**, Section 5.6), and four-corpus trajectory feasibility rates (**Section 5.2**) are directly recomputed and verified against retained records.

### Aligned Constraint Calibration Summary ($D = 10{,}001$ Histogram Bins)
To prevent any ambiguity between standalone binding modules and complete state-transition circuits, every comparison tier is separated explicitly below:
1. **Direct PRG seed expansion (standalone module, `SeededShareBinding/no-rejection/1`)**: **79,002,390** constraints at $D=10{,}001$ (`82,712` / `828,050` / `7,956,190` / `79,002,390` across $D \in \{8, 101, 1001, 10001\}$). Compared against SHTPC's standalone masked-moment binding module (**5,779** constraints), this gives the **13,670.60×** standalone module reduction plotted in **Figure 3** (`binding-circuit-input.csv`). (No Groth16 proving run is executed for the 79M-constraint relation.)
2. **Constructed Poseidon vector-binding baseline (Method V, `Alternative(10001)`)**: **851,715** constraints (22 public signals) for the **complete** state-transition circuit replacing SHTPC's masked-moment check with per-role Poseidon-16 commitments over retained secret-shared vectors (`circuits/v6_relation.circom`, `circuits/v6_main_10001.circom`).
3. **SHTPC state transition (Method M, `hadwc_transition_v5.circom`)**: **13,327** constraints (25 public signals) for the **complete** transition circuit (**7,548** constant ADWC state/policy constraints + **5,779** masked-moment payload-binding constraints). Comparing complete transition circuits gives a **63.91×** constraint reduction ($\frac{851{,}715}{13{,}327}$) and measured **89.83×–89.91×** Xeon `fullProve` paired timing speedups (**Table 5**).

---

## 2. System and Environment Requirements

### Hardware Requirements
- **Processor**: Any standard x86_64 or ARM64 (Apple Silicon) processor.
- **Memory**: < 100 MB RAM.
- **Disk Space**: < 20 MB free space.
- **Execution Time**: The complete reproduction suite executes in **under 2 seconds**.

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04/22.04 or later), macOS (12.0 or later), or Windows (via WSL2).
- **Python Runtime**: Python 3.10 or later (**standard library only**; no `pip` packages required).

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
  ✓ Integrity verified: 79 files match manifest.json (SHA-256)
  ✓ All 8 formal security proofs and budget contracts present in proof/
  ✓ Method M circuit exposes 25 ordered public signals; Method V circuit present (22 public signals)

[2/5] Verifying Aligned Circuit Constraints & Reduction Ratios...
  - Direct PRG seed expansion (standalone, D=    8):     82,712 constraints
  - Direct PRG seed expansion (standalone, D=  101):    828,050 constraints
  - Direct PRG seed expansion (standalone, D= 1001):  7,956,190 constraints
  - Direct PRG seed expansion (standalone, D=10001): 79,002,390 constraints
  - SHTPC masked moment (standalone, D=10,001):         5,779 constraints
  ✓ Standalone reduction (Direct PRG / Masked Moment): 13670.60× (13,670.60×)
  - Method M complete SHTPC transition (7,548 ADWC + 5,779 binding):  13,327 constraints (25 signals)
  - Method V complete Poseidon vector transition (Alternative 10001): 851,715 constraints (22 signals)
  ✓ Complete-circuit constraint ratio (Method V / Method M): 63.91× (63.91×); witness 14/14 & Groth16 3/3 PASS
  ✓ Standalone Direct PRG vs complete circuits: 5928.00× Method M, 92.76× Method V

[3/5] Verifying Table 5 Same-Input Component Timing (15 pairs, Method M vs Method V)...
  Input          | Method M (s) | Method V (s) | Paired V/M | RSS M/V (GiB)   | Status
  ------------------------------------------------------------------------------------
  Nonzero (pos)  |     3.4542 s |    310.415 s |    89.91× | 0.296 / 13.916 | PASS
  Zero           |     3.4473 s |    310.741 s |    89.90× | 0.298 / 13.870 | PASS
  Near cap       |     3.4599 s |    310.925 s |    89.83× | 0.297 / 14.142 | PASS
  ✓ Earlier microbenchmark (different fixtures) paired ratio median: 89.73× (89.73×)

[4/5] Verifying Table 7 End-to-End Lifecycle Pairs (N=100, 5 pairs)...
  - Session wall time median:         Full 4351.28 s (72.52 min) | T 3156.83 s (52.61 min)
  - Eligible window wall time median: Full 548.27 s | T 381.12 s
  - Collection wall time median:      Full 61.62 s | T 61.56 s
  - Paired T / Full session ratio median: 0.7255 (Full is 1.38× T)
  - Paired T / Full window ratio median:  0.6958 (Full is 1.44× T)

[5/5] Verifying Section 5.2 Four-Corpus Trajectory Feasibility Data...
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
- **Description**: Contains the SHA-256 digests for all 79 distributed artifact files. `reproduce.py` reads `manifest.json` and asserts that every file is present and unaltered.

### Step 2: State Transition Circuits (Method M vs. Method V)
- **Paper Reference**: Section 3.3 (Cross-field canonical encoding and transition relation) and Section 5.3
- **Artifact Paths**: `circuits/hadwc_transition_v5.circom` (Method M, 13,327 constraints), `circuits/v6_relation.circom`, `circuits/v6_main_10001.circom` (Method V, 851,715 constraints)
- **Verification**: `reproduce.py` verifies all 25 ordered public signals of SHTPC Method M (`hadwc_transition_v5.circom`) and checks that Method V (`Alternative(10001)`) is present and backed by 14/14 positive/negative witness checks (`evidence/binding/v6_witness_checks_10001.json`) and 3/3 verified Groth16 proofs (`evidence/binding/v6_crypto_events_10001.jsonl`).
- **Enforced Conditions**:
  - Spatial Grid mapping: $p = \mathsf{Grid}(\mathbf{x}_r)$
  - Speed-tier drift bounding: $\|\mathbf{x}_r - \mathbf{x}_{\rm prev}\|^2 \le \tau_u^2 \Delta t_t^2$
  - Anchor distance cap: $\|\mathbf{x}_r - \mathbf{a}_t\|^2 \le \min\{\tau_u^2 (\Delta T_t^{(K)})^2, c_{\rm policy}^2\}$
  - Cross-field canonical scalar relation: $x + r_A + r_B = T + \chi q$ with $\chi \in \{0, 1, 2\}$

### Step 3: Constraint Counts & Reduction Ratios (Figure 3 & Section 5.3)
- **Paper Reference**: Section 1, Section 3.3, Section 5.3, Figure 3
- **Artifact Paths**: `evidence/binding/bins8.json` .. `bins10001.json`, `evidence/binding/binding-circuit-input.csv`, `evidence/binding/transition_circuits.json`
- **Verification**:
  - Standalone masked-moment module: **5,779 constraints** vs. Direct PRG seed expansion ($D=10{,}001$): **79,002,390 constraints** $\to$ **13,670.60×** (Figure 3).
  - Complete transition circuit SHTPC Method M: **13,327 constraints** (`7,548` ADWC + `5,779` masked moment) vs. Poseidon vector binding Method V: **851,715 constraints** $\to$ **63.91×**.

### Step 4: Same-Input Prover Speedup (Table 5)
- **Paper Reference**: Section 5.3, Table 5
- **Artifact Paths**: `evidence/evaluation/binding-derived.json`, `evidence/evaluation/binding-full-table.tex`
- **Verification**:
  - Recomputes 15 paired proving runs on Xeon Gold 6148 under identical secret-share inputs (`M` = SHTPC 13,327-constraint masked-moment transition; `V` = constructed 851,715-constraint Poseidon vector transition):
    - **Nonzero (`B-pos`)**: Method M median 3.4542 s vs Method V median 310.415 s $\to$ **89.91×** paired median speedup (`0.296 / 13.916 GiB` RSS; `1.254 / 5.220 s` fresh-process verify).
    - **Zero (`B-zero`)**: Method M median 3.4473 s vs Method V median 310.741 s $\to$ **89.90×** paired median speedup (`0.298 / 13.870 GiB` RSS; `1.260 / 5.221 s` verify).
    - **Near cap (`B-edge`)**: Method M median 3.4599 s vs Method V median 310.925 s $\to$ **89.83×** paired median speedup (`0.297 / 14.142 GiB` RSS; `1.257 / 5.200 s` verify).

### Step 5: End-to-End Lifecycle Overhead (Table 7 & Section 5.6)
- **Paper Reference**: Section 5.6, Table 7
- **Artifact Path**: `evidence/evaluation/lifecycle-pairs.json`
- **Verification**:
  - Recomputes 5 paired runs of $N=100$ clients across 600 history-priming steps:
    - Full SHTPC session median: **4,351.28 s** (72.52 min) vs Trusted generator (T) session median: **3,156.83 s** (52.61 min); paired T / Full ratio **0.7255** (Full is 1.38× T).
    - Full SHTPC eligible-window median: **548.27 s** vs T eligible-window median: **381.12 s**; paired T / Full ratio **0.6958** (Full is 1.44× T).
    - Collection medians: **61.62 s** (Full) vs **61.56 s** (T).

### Step 6: Four-Corpus Trajectory Feasibility (Section 5.2)
- **Paper Reference**: Section 5.2
- **Artifact Paths**: `evidence/evaluation/four-corpus-pooled.csv`, `evidence/evaluation/reason-counts-by-date.csv`, `evidence/evaluation/roster-summary.csv`
- **Verification**:
  - Recomputes legal observed actor-days and validates that `sum(reason_counts) == denominator` for each observed day:
    - **T-Drive**: 12,162 / 29,658 legal actor-days (41.01%)
    - **Porto**: 116 / 1,200 legal actor-days (9.67%)
    - **GeoLife**: 9 / 85 legal actor-days (10.59%)
    - **Rome**: 836 / 871 legal actor-days (95.98%)
  - Confirms zero predecessor distance violations (`PREDECESSOR_DISTANCE == 0`).

---

## 5. Security Proofs and Theorem Navigation

All reduction arguments, game definitions, hybrid sequences, and multi-window extensions are stored in `proof/` (with a mirror at `artifact/proof/` to match the exact citation path in the paper's Artifact Availability section).

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
├── manifest.json                  # SHA-256 integrity manifest for all 79 package files
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
│   ├── hadwc_transition_v5.circom # SHTPC Method M complete transition (13,327 constraints, 25 signals)
│   ├── hadwc_common_v5.circom     # Common Pedersen & range primitives
│   ├── v6_relation.circom         # Constructed Poseidon vector-binding alternative (Method V)
│   ├── v6_main_10001.circom       # Method V instantiation (D=10,001: 851,715 constraints, 22 signals)
│   ├── v6_main_8.circom           # Method V small-scale instantiation (D=8: 10,530 constraints)
│   ├── poseidon4.circom           # Poseidon sponge kernels
│   ├── poseidon16.circom
│   ├── keccak12.circom            # Keccak / PRG comparison kernel
│   ├── share_row.circom           # Per-bin secret-share reconstruction row
│   ├── check_r1cs_v2.cpp          # C++ streaming R1CS constraint verifier
│   └── compose_r2.py              # Multi-bin R1CS/witness composer
├── model/                         # Formal state machine specification
│   ├── ClosureState.tla           # TLA+ specification
│   └── cases.json                 # Model checker configurations
└── evidence/                      # Numerical records & evaluation data
    ├── binding/                   # Direct PRG receipts (bins 8..10001), Fig. 3 CSV, & Method V receipts
    └── evaluation/                # Table 5, Table 7, Section 5.2 corpus screening, & microbenchmarks
```

---

## 7. Scope and Evaluation Boundaries

- **Admitted Claims**: SHTPC security guarantees hold for admitted reports within the dual trust model (honest client origin and non-colluding Aggregators). SHTPC does not establish physical GPS ground truth or defend against Sybil identity generation.
- **Strict Membership Contract**: Release requires the entire eligible cohort. In accordance with strict privacy guarantees, dropouts trigger durable server redelivery rather than dynamic cohort intersection release.
- **Differential Privacy**: SHTPC protects protocol views and execution transcripts. Differential privacy applied to released histogram totals is orthogonal and complementary.
- **Data Protection and Double-Blind Anonymity**: In accordance with user privacy and double-blind review policies, raw user trajectories, private commitment openings, witness caches, and secret keys are excluded. All numerical claims are verified against retained execution records.
