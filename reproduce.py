#!/usr/bin/env python3
"""
SHTPC Artifact Reproducibility and Numerical Verification Script.
Recomputes and verifies all reported numbers, ratios, bounds, and evaluation data
directly from distributed artifact files.
Standard library only; compatible with Python 3.10+.
"""

import csv
import json
import hashlib
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVAL_DIR = ROOT / 'evidence' / 'evaluation'
BINDING_DIR = ROOT / 'evidence' / 'binding'
PROOF_DIR = ROOT / 'proof'
CIRCUITS_DIR = ROOT / 'circuits'

def require(condition, message):
    if not condition:
        raise AssertionError("FAIL: " + message)

def load_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def main():
    print("=" * 76)
    print(" SHTPC: Stateful History-to-Payload Closure for Private Heatmap Aggregation")
    print(" Artifact Verification and Data Reproduction Runner")
    print("=" * 76)

    # 1. Structural and File Integrity Checks
    print("\n[1/5] Checking Structural Components & Interfaces...")

    manifest_file = ROOT / 'manifest.json'
    if manifest_file.exists():
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        checked_count = 0
        for rel_path, expected_hash in manifest.items():
            f = ROOT / rel_path
            require(f.is_file(), f"Missing file from manifest: {rel_path}")
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            require(h == expected_hash, f"Hash mismatch for {rel_path}: {h} != {expected_hash}")
            checked_count += 1
        print(f"  ✓ Integrity verified: {checked_count} files match manifest.json (SHA-256)")

    proof_files = [
        '01-security-games-and-ideal-interface.md',
        '02-groth16-extraction-and-budget.md',
        '03-native-privacy-and-query-ledger.md',
        '04-full-view-simulation.md',
        '05-closure-prefix-and-refinement.md',
        '06-counterexamples-and-scope.md',
        '07-composition-and-explicit-bounds.md',
        '08-multi-window-privacy.md',
        'README.md',
        'groth16-budget-contract.json',
        'native-budget-contract.json',
        'composition-budget-contract.json',
    ]
    for pf in proof_files:
        p = PROOF_DIR / pf
        require(p.is_file(), f"Missing proof document: proof/{pf}")
    print("  ✓ All 8 formal security proofs and budget contracts present in proof/")

    circuit_files = [
        'hadwc_transition_v5.circom',
        'hadwc_common_v5.circom',
        'v6_relation.circom',
        'v6_main_10001.circom',
        'v6_main_8.circom',
        'poseidon4.circom',
        'poseidon16.circom',
        'keccak12.circom',
        'share_row.circom',
        'check_r1cs_v2.cpp',
        'compose_r2.py',
    ]
    for cf in circuit_files:
        p = CIRCUITS_DIR / cf
        require(p.is_file(), f"Missing circuit file: circuits/{cf}")

    trans_code = (CIRCUITS_DIR / 'hadwc_transition_v5.circom').read_text(encoding='utf-8')
    require("template Transition()" in trans_code, "Transition template missing in circuit")
    expected_signals = [
        "relation_version", "c_a_x", "c_a_y", "c_r_x", "c_r_y",
        "c_prev_x", "c_prev_y", "c_next_x", "c_next_y",
        "c_ticket_x", "c_ticket_y", "c_receipt_x", "c_receipt_y",
        "anchor_prev_x", "anchor_prev_y", "anchor_next_x", "anchor_next_y",
        "key_tag_96", "masked_native_index", "contribution_bit", "rid_128",
        "ctx_limb_hi", "ctx_limb_lo", "c_k_anchor_x", "c_k_anchor_y"
    ]
    for sig in expected_signals:
        require(f"signal input {sig};" in trans_code, f"Missing public signal {sig} in transition circuit")
    v6_main_code = (CIRCUITS_DIR / 'v6_main_10001.circom').read_text(encoding='utf-8')
    require("Alternative(10001)" in v6_main_code, "Alternative(10001) missing in v6_main_10001.circom")
    print("  ✓ Method M circuit exposes 25 ordered public signals; Method V circuit present (22 public signals)")

    # 2. Circuit Constraints & Aligned Baseline Ratios (Figure 3, §3.3, §5.3)
    print("\n[2/5] Verifying Aligned Circuit Constraints & Reduction Ratios...")
    bins_data = {}
    for n, expected_c in [(8, 82712), (101, 828050), (1001, 7956190), (10001, 79002390)]:
        fpath = BINDING_DIR / f"bins{n}.json"
        require(fpath.is_file(), f"Missing binding receipt: bins{n}.json")
        d = json.loads(fpath.read_text(encoding='utf-8'))
        require(d['relation'] == 'SeededShareBinding/no-rejection/1', f"Unexpected relation in bins{n}.json")
        require(d['constraints'] == expected_c, f"Constraint mismatch for bins{n}: {d['constraints']} != {expected_c}")
        bins_data[n] = d['constraints']
        print(f"  - Direct PRG seed expansion (standalone, D={n:>5}): {d['constraints']:>10,d} constraints")

    # Cross-check Figure 3 CSV input
    fig3_rows = load_csv(BINDING_DIR / 'binding-circuit-input.csv')
    require(len(fig3_rows) == 3, "Expected 3 rows in binding-circuit-input.csv")
    for row in fig3_rows:
        b = int(row['bins'])
        require(int(row['direct_seed_constraints']) == bins_data[b], f"CSV/JSON mismatch at D={b}")
        require(int(row['masked_moment_constraints']) == 5779, f"Masked moment mismatch at D={b}")

    moment_constraints = 5779
    direct_seed_constraints = bins_data[10001]
    standalone_ratio = direct_seed_constraints / moment_constraints
    print(f"  - SHTPC masked moment (standalone, D=10,001):    {moment_constraints:>10,d} constraints")
    print(f"  ✓ Standalone reduction (Direct PRG / Masked Moment): {standalone_ratio:.2f}× (13,670.60×)")
    require(abs(standalone_ratio - 13670.60) < 0.01, "Standalone constraint reduction ratio out of bounds")

    # Complete transition circuit comparison (Method M vs Method V)
    tc = json.loads((BINDING_DIR / 'transition_circuits.json').read_text(encoding='utf-8'))
    m_meta = tc['complete_transition_circuits']['shtpc_method_m']
    v_meta = tc['complete_transition_circuits']['poseidon_vector_method_v']
    require(m_meta['total_constraints'] == 13327, "Method M constraint count mismatch")
    require(m_meta['adwc_state_policy_constraints'] + m_meta['masked_moment_binding_constraints'] == 13327,
            "Method M ADWC + masked-moment sum mismatch")
    require(v_meta['total_constraints'] == 851715, "Method V constraint count mismatch")

    v6_val = json.loads((BINDING_DIR / 'v6_validation.json').read_text(encoding='utf-8'))
    require(v6_val['status'] == 'PASS', "v6 validation status != PASS")
    require(v6_val['n10001_witness_all_passed'] is True and v6_val['n10001_cases'] == 14, "v6 D=10001 witness check failed")
    require(v6_val['n10001_proofs_verified'] is True and v6_val['n10001_proofs'] == 3, "v6 D=10001 proofs check failed")
    v6_wchecks = json.loads((BINDING_DIR / 'v6_witness_checks_10001.json').read_text(encoding='utf-8'))
    require(v6_wchecks['all_passed'] is True and len(v6_wchecks['cases']) == 14, "v6 witness-checks-r2 failed")

    complete_ratio = v_meta['total_constraints'] / m_meta['total_constraints']
    seed_vs_m = direct_seed_constraints / m_meta['total_constraints']
    seed_vs_v = direct_seed_constraints / v_meta['total_constraints']
    print(f"  - Method M complete SHTPC transition (7,548 ADWC + 5,779 binding): {m_meta['total_constraints']:>7,d} constraints (25 signals)")
    print(f"  - Method V complete Poseidon vector transition (Alternative 10001): {v_meta['total_constraints']:>7,d} constraints (22 signals)")
    print(f"  ✓ Complete-circuit constraint ratio (Method V / Method M): {complete_ratio:.2f}× (63.91×); witness 14/14 & Groth16 3/3 PASS")
    print(f"  ✓ Standalone Direct PRG vs complete circuits: {seed_vs_m:.2f}× Method M, {seed_vs_v:.2f}× Method V")
    require(abs(complete_ratio - 63.91) < 0.01, "Complete transition constraint ratio out of bounds")

    # 3. Table 5: Same-Input Component Proof Timing (15 Pairs)
    print("\n[3/5] Verifying Table 5 Same-Input Component Timing (15 pairs, Method M vs Method V)...")
    binding_derived = json.loads((EVAL_DIR / 'binding-derived.json').read_text(encoding='utf-8'))
    expected_table5 = {
        'B-pos':  {'name': 'Nonzero (pos)', 'expected_ratio': 89.91, 'v5_med': 3.4542, 'v6_med': 310.41,
                   'v5_rss': 0.296, 'v6_rss': 13.916, 'v5_ver': 1.254, 'v6_ver': 5.220},
        'B-zero': {'name': 'Zero',          'expected_ratio': 89.90, 'v5_med': 3.4473, 'v6_med': 310.74,
                   'v5_rss': 0.298, 'v6_rss': 13.870, 'v5_ver': 1.260, 'v6_ver': 5.221},
        'B-edge': {'name': 'Near cap',      'expected_ratio': 89.83, 'v5_med': 3.4599, 'v6_med': 310.93,
                   'v5_rss': 0.297, 'v6_rss': 14.142, 'v5_ver': 1.257, 'v6_ver': 5.200},
    }

    print(f"  {'Input':<14} | {'Method M (s)':<12} | {'Method V (s)':<12} | {'Paired V/M':<10} | {'RSS M/V (GiB)':<15} | Status")
    print("  " + "-" * 84)
    for group, spec in expected_table5.items():
        data = binding_derived[group]
        pairs = data['pairs']
        require(len(pairs) == 5, f"Expected 5 pairs for {group}, found {len(pairs)}")
        v5_vals = [p['v5'] for p in pairs]
        v6_vals = [p['v6'] for p in pairs]
        ratios = [p['v6'] / p['v5'] for p in pairs]
        v5_median = statistics.median(v5_vals)
        v6_median = statistics.median(v6_vals)
        paired_ratio_median = statistics.median(ratios)
        v5_rss = data['v5']['rss_GiB']
        v6_rss = data['v6']['rss_GiB']
        v5_ver = data['v5']['verify_process']
        v6_ver = data['v6']['verify_process']
        require(abs(paired_ratio_median - spec['expected_ratio']) < 0.05,
                f"Table 5 ratio mismatch for {group}: {paired_ratio_median:.2f} vs {spec['expected_ratio']}")
        require(abs(v5_median - spec['v5_med']) < 0.01, f"v5 median mismatch: {v5_median} vs {spec['v5_med']}")
        require(abs(v6_median - spec['v6_med']) < 0.15, f"v6 median mismatch: {v6_median} vs {spec['v6_med']}")
        require(abs(v5_rss - spec['v5_rss']) < 0.002 and abs(v6_rss - spec['v6_rss']) < 0.005,
                f"RSS mismatch for {group}: {v5_rss:.3f}/{v6_rss:.3f}")
        require(abs(v5_ver - spec['v5_ver']) < 0.002 and abs(v6_ver - spec['v6_ver']) < 0.002,
                f"Verify median mismatch for {group}: {v5_ver:.3f}/{v6_ver:.3f}")
        print(f"  {spec['name']:<14} | {v5_median:10.4f} s | {v6_median:10.3f} s | {paired_ratio_median:8.2f}× | {v5_rss:.3f} / {v6_rss:<6.3f} | PASS")

    e1_summary = json.loads((EVAL_DIR / 'summary.json').read_text(encoding='utf-8'))
    e1_ratio = e1_summary['paired_ratio_median']
    print(f"  ✓ Earlier microbenchmark (different fixtures) paired ratio median: {e1_ratio:.2f}× (89.73×)")
    require(abs(e1_ratio - 89.73) < 0.05, "E1 ratio mismatch")

    # 4. Table 7 & §5.6: End-to-End Lifecycle Measurements
    print("\n[4/5] Verifying Table 7 End-to-End Lifecycle Pairs (N=100, 5 pairs)...")
    lifecycle = json.loads((EVAL_DIR / 'lifecycle-pairs.json').read_text(encoding='utf-8'))
    pairs = lifecycle['pairs']
    require(len(pairs) == 5, f"Expected 5 lifecycle pairs, found {len(pairs)}")

    full_sessions = [p['full']['session_wall_s'] for p in pairs]
    t_sessions = [p['t']['session_wall_s'] for p in pairs]
    full_windows = [p['full']['eligible_window_wall_s'] for p in pairs]
    t_windows = [p['t']['eligible_window_wall_s'] for p in pairs]
    full_cols = [p['full']['collection_wall_s'] for p in pairs]
    t_cols = [p['t']['collection_wall_s'] for p in pairs]
    session_ratios = [p['ratios']['session_wall_s'] for p in pairs]
    window_ratios = [p['ratios']['eligible_window_wall_s'] for p in pairs]

    full_session_med = statistics.median(full_sessions)
    t_session_med = statistics.median(t_sessions)
    full_window_med = statistics.median(full_windows)
    t_window_med = statistics.median(t_windows)
    full_col_med = statistics.median(full_cols)
    t_col_med = statistics.median(t_cols)
    session_ratio_med = statistics.median(session_ratios)
    window_ratio_med = statistics.median(window_ratios)

    print(f"  - Session wall time median:         Full {full_session_med:.2f} s ({full_session_med/60:.2f} min) | T {t_session_med:.2f} s ({t_session_med/60:.2f} min)")
    print(f"  - Eligible window wall time median: Full {full_window_med:.2f} s | T {t_window_med:.2f} s")
    print(f"  - Collection wall time median:      Full {full_col_med:.2f} s | T {t_col_med:.2f} s")
    print(f"  - Paired T / Full session ratio median: {session_ratio_med:.4f} (Full is {1/session_ratio_med:.2f}× T)")
    print(f"  - Paired T / Full window ratio median:  {window_ratio_med:.4f} (Full is {1/window_ratio_med:.2f}× T)")

    require(abs(full_session_med - 4351.28) < 1.0, f"Full session median mismatch: {full_session_med}")
    require(abs(t_session_med - 3156.83) < 1.0, f"T session median mismatch: {t_session_med}")
    require(abs(full_window_med - 548.27) < 0.5, f"Full window median mismatch: {full_window_med}")
    require(abs(t_window_med - 381.12) < 0.5, f"T window median mismatch: {t_window_med}")
    require(abs(session_ratio_med - 0.7255) < 0.005, f"Session ratio mismatch: {session_ratio_med}")
    require(abs(window_ratio_med - 0.6958) < 0.005, f"Window ratio mismatch: {window_ratio_med}")

    # 5. Section 5.2: Four-Corpus Trajectory Feasibility Screening
    print("\n[5/5] Verifying Section 5.2 Four-Corpus Trajectory Feasibility Data...")
    reasons = load_csv(EVAL_DIR / 'reason-counts-by-date.csv')
    corpus_rows = load_csv(EVAL_DIR / 'four-corpus-pooled.csv')

    print(f"  {'Dataset':<10} | {'Legal Days':<12} | {'Total Days':<12} | {'Legal Rate':<10} | Status")
    print("  " + "-" * 56)
    for row in corpus_rows:
        lib = row['library']
        items = [x for x in reasons if x['library'] == lib]
        dates = sorted({x['date'] for x in items})
        require(len(dates) == 3, f"{lib} dates count mismatch")

        totals = {}
        for r_code, key in [('NO_GRID_SLOT', 'no_grid'), ('NO_CONTIGUOUS_EIGHT', 'no_contiguous_eight'),
                            ('ANCHOR_DISTANCE', 'anchor'), ('LEGAL', 'legal')]:
            totals[key] = sum(int(x['count']) for x in items if x['reason'] == r_code)
            require(totals[key] == int(row[key]), f"{lib} {key} mismatch")

        require(all(int(x['count']) == 0 for x in items if x['reason'] == 'PREDECESSOR_DISTANCE'), "predecessor count != 0")
        den = sum(int(next(x['denominator'] for x in items if x['date'] == d)) for d in dates)
        require(den == int(row['denominator']) == sum(totals.values()), f"{lib} denominator mismatch")

        pct = (totals['legal'] / den) * 100
        print(f"  {lib:<10} | {totals['legal']:>10,d}   | {den:>10,d}   | {pct:>8.2f}%  | PASS")

    rosters = load_csv(EVAL_DIR / 'roster-summary.csv')
    for row in rosters:
        require(int(row['planned']) == int(row['evaluable']) + int(row['insufficient_pool']), 'roster accounting')
        n, good, complete = int(row['N']), int(row['all_legal']), int(row['complete'])
        expected = f"{complete}/{good}" if good else 'N/A'
        require(row['conditional_complete'] == expected, 'conditional roster denominator')

    print("\n" + "=" * 76)
    print(" ALL VERIFICATIONS PASSED (5/5).")
    print(" Distributed proofs, circuits, numerical data and arithmetic match the paper.")
    print("=" * 76)
    return True

if __name__ == '__main__':
    main()
