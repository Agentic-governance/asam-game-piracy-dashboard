#!/usr/bin/env python3
"""
snapshot.py — Save current state of full_survey_all.csv as daily JSON snapshot.
Run daily via GitHub Actions. Stores to snapshots/YYYY-MM-DD.json.
"""
import csv, json, sys, os
from datetime import date
from pathlib import Path

# Find the survey CSV (try multiple locations)
SURVEY_CANDIDATES = [
    'data/full_survey_all.csv',
    'full_survey_all.csv',
    os.path.expanduser('~/aria_dashboard/data/full_survey_all.csv'),
]

survey_path = None
for p in SURVEY_CANDIDATES:
    if os.path.exists(p):
        survey_path = p
        break

if not survey_path:
    print("WARNING: full_survey_all.csv not found. Creating empty snapshot.")
    snapshot_dir = Path('snapshots')
    snapshot_dir.mkdir(exist_ok=True)
    today = date.today().isoformat()
    out = snapshot_dir / f'{today}.json'
    with open(out, 'w') as f:
        json.dump({'date': today, 'domains': {}}, f)
    print(f"Empty snapshot: {out}")
    sys.exit(0)

csv.field_size_limit(sys.maxsize)

SNAPSHOT_DIR = Path('snapshots')
SNAPSHOT_DIR.mkdir(exist_ok=True)

domains = {}
with open(survey_path, encoding='utf-8') as f:
    for row in csv.DictReader(f):
        domain = row.get('domain', '').strip()
        if not domain:
            continue
        domains[domain] = {
            'active':   row.get('active', ''),
            'severity': row.get('severity', ''),
            'ecotype':  row.get('ecotype', ''),
            'country':  row.get('country', ''),
            'asn':      row.get('asn', ''),
        }

today = date.today().isoformat()
out = SNAPSHOT_DIR / f'{today}.json'
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'date': today, 'domains': domains}, f, ensure_ascii=False)

print(f"Snapshot saved: {out} ({len(domains):,} domains)")
