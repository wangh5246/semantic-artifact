#!/usr/bin/env python3
"""Check the distributed artifact and recompute its reported summary values."""
import csv
import hashlib
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'evidence' / 'evaluation'

def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)

def csv_rows(name):
    with (DATA / name).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

manifest = json.loads((ROOT / 'SHA256SUMS.json').read_text())
for name, digest in manifest.items():
    path = ROOT / name
    require(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == digest,
            'missing or altered file ' + name)
print(f'Integrity: {len(manifest)} files match SHA256SUMS.json')

summary = json.loads((DATA / 'summary.json').read_text())
rows = csv_rows('e1-pairs.csv')
ratios = []
for relation, label in [('state', 'Masked moment'), ('vector', 'Vector commitment')]:
    sample = [row for row in rows if row['relation'] == relation]
    require(len(sample) == 5, label + ' sample count')
    measures = [('fullprove_wall_s', 'fullprove_wall'), ('fullprove_cpu_s', 'fullprove_cpu'),
                ('internal_verify_wall_s', 'internal_verify_wall'), ('max_rss_kib', 'max_rss_kib')]
    for column, key in measures:
        values = [float(row[column]) for row in sample]
        reference = summary['e1'][relation][key]
        require(abs(statistics.median(values) - reference['median']) < 1e-8, label + ' ' + key)
        require(abs(min(values) - reference['min']) < 1e-8 and abs(max(values) - reference['max']) < 1e-8, label + ' range')
    values = [float(row['fullprove_wall_s']) for row in sample]
    print(f'{label}: fullProve median {statistics.median(values):.4f} s, range {min(values):.4f}–{max(values):.4f} s')
for pair in range(1, 6):
    values = {r['relation']: float(r['fullprove_wall_s']) for r in rows if int(r['pair']) == pair}
    require(set(values) == {'state', 'vector'}, 'pair membership')
    ratios.append(values['vector'] / values['state'])
require(abs(statistics.median(ratios) - summary['paired_ratio_median']) < 1e-8, 'paired ratio')
require(summary['same_business_input'] is False, 'fixture correspondence')
print(f'Paired ratio median: {statistics.median(ratios):.2f} (different fixed fixtures)')

reasons = csv_rows('reason-counts-by-date.csv')
for row in csv_rows('four-corpus-pooled.csv'):
    items = [x for x in reasons if x['library'] == row['library']]
    dates = sorted({x['date'] for x in items})
    require(len(dates) == 3, row['library'] + ' dates')
    totals = {}
    for reason, key in [('NO_GRID_SLOT', 'no_grid'), ('NO_CONTIGUOUS_EIGHT', 'no_contiguous_eight'),
                        ('ANCHOR_DISTANCE', 'anchor'), ('LEGAL', 'legal')]:
        totals[key] = sum(int(x['count']) for x in items if x['reason'] == reason)
        require(totals[key] == int(row[key]), row['library'] + ' ' + reason)
    require(all(int(x['count']) == 0 for x in items if x['reason'] == 'PREDECESSOR_DISTANCE'), 'predecessor count')
    den = sum(int(next(x['denominator'] for x in items if x['date'] == day)) for day in dates)
    require(den == int(row['denominator']) == sum(totals.values()), row['library'] + ' denominator')
    print(f"{row['library']}: {totals['legal']}/{den} legal actor-days ({100*totals['legal']/den:.2f}%)")

rosters = csv_rows('roster-summary.csv')
for row in rosters:
    require(int(row['planned']) == int(row['evaluable']) + int(row['insufficient_pool']), 'roster accounting')
    n, good, complete = int(row['N']), int(row['all_legal']), int(row['complete'])
    expected = f'{complete}/{good}' if good else 'N/A'
    require(row['conditional_complete'] == expected, 'conditional roster denominator')
    if row['library'] == 'rome':
        print(f'Rome N={n}: all-legal {good}/{row["evaluable"]}, common start {expected}')

for arm, label in [('full', 'Full'), ('t', 'Trusted generation')]:
    item = summary['pair'][arm]
    require(item['window_wall_s'] == item['phases_s']['window'], label + ' window')
    require(item['phases_s']['collection_complete'] <= item['window_wall_s'], label + ' collection nesting')
    print(f"{label}: window {item['window_wall_s']:.3f} s, session {item['total_wall_s']:.3f} s")
print('PASS: distributed data and arithmetic are internally consistent')
print('Scope: no native execution, proof generation, or raw trajectory scan was performed')
