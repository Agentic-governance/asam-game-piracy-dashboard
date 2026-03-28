#!/usr/bin/env python3
"""
diff_alerts.py — Compare latest 2 snapshots, generate diff alerts.
Output: diff_data.js for index.html consumption.
"""
import json, os, sys
from pathlib import Path
from datetime import datetime

SNAPSHOT_DIR = Path('snapshots')

def _sev(info):
    try:
        return int(info.get('severity', 0))
    except:
        return 0

def write_empty_diff():
    output = """// ARIA Diff Alerts — No previous snapshot available
const ARIA_DIFF = { summary: { net_change: 0, new_domains: 0, generated_at: "%s" }, alerts: [] };
""" % datetime.utcnow().isoformat()
    with open('diff_data.js', 'w') as f:
        f.write(output)
    print("No diff available (< 2 snapshots). Empty diff_data.js written.")

# Get sorted snapshot files
snapshots = sorted(SNAPSHOT_DIR.glob('*.json'))
if len(snapshots) < 2:
    write_empty_diff()
    sys.exit(0)

prev_file = snapshots[-2]
curr_file = snapshots[-1]

prev = json.loads(prev_file.read_text())
curr = json.loads(curr_file.read_text())

prev_domains = prev['domains']
curr_domains = curr['domains']
prev_date = prev['date']
curr_date = curr['date']

# ━━━ Diff calculation ━━━

new_domains = {d: info for d, info in curr_domains.items() if d not in prev_domains}
removed_domains = {d: info for d, info in prev_domains.items() if d not in curr_domains}

newly_active = {
    d: curr_domains[d] for d in curr_domains
    if d in prev_domains
    and str(prev_domains[d].get('active', '')).lower() != 'true'
    and str(curr_domains[d].get('active', '')).lower() == 'true'
}

newly_inactive = {
    d: curr_domains[d] for d in curr_domains
    if d in prev_domains
    and str(prev_domains[d].get('active', '')).lower() == 'true'
    and str(curr_domains[d].get('active', '')).lower() != 'true'
}

sev_escalated = {
    d: {
        'prev_sev': prev_domains[d].get('severity', ''),
        'curr_sev': curr_domains[d].get('severity', ''),
        **curr_domains[d]
    }
    for d in curr_domains
    if d in prev_domains and _sev(curr_domains[d]) > _sev(prev_domains[d])
}

new_critical = {d: info for d, info in new_domains.items() if _sev(info) == 5}

# ━━━ Generate alerts ━━━
alerts = []

if new_critical:
    alerts.append({
        'id': 'new_critical',
        'severity': 'CRITICAL',
        'type': 'new_critical',
        'title': f'{len(new_critical):,} new CRITICAL (Severity 5) domains',
        'detail': f'Highest-risk domains added since {prev_date}: ' + ', '.join(list(new_critical.keys())[:5]),
        'count': len(new_critical),
        'samples': [{'domain': d, **info} for d, info in list(new_critical.items())[:10]],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'enforcement',
    })

if new_domains:
    top_new = sorted(new_domains.items(), key=lambda x: _sev(x[1]), reverse=True)[:10]
    alerts.append({
        'id': 'new_domains',
        'severity': 'HIGH' if len(new_domains) > 20 else 'MEDIUM',
        'type': 'new_domains',
        'title': f'{len(new_domains):,} new piracy domains detected',
        'detail': f'Newly discovered since {prev_date}. Top: {", ".join(d for d, _ in top_new[:3])}' + (f' +{len(new_domains)-3} more.' if len(new_domains) > 3 else '.'),
        'count': len(new_domains),
        'samples': [{'domain': d, **info} for d, info in top_new],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'monitoring',
    })

if newly_active:
    alerts.append({
        'id': 'newly_active',
        'severity': 'HIGH',
        'type': 'newly_active',
        'title': f'{len(newly_active):,} domains became active',
        'detail': f'Previously inactive domains resumed activity since {prev_date}.',
        'count': len(newly_active),
        'samples': [{'domain': d, **info} for d, info in list(newly_active.items())[:10]],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'monitoring',
    })

if newly_inactive:
    alerts.append({
        'id': 'newly_inactive',
        'severity': 'LOW',
        'type': 'takedown_success',
        'title': f'{len(newly_inactive):,} domains went offline',
        'detail': f'Possible takedown or self-shutdown since {prev_date}.',
        'count': len(newly_inactive),
        'samples': [{'domain': d, **info} for d, info in list(newly_inactive.items())[:10]],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'enforcement',
    })

if removed_domains:
    alerts.append({
        'id': 'removed_domains',
        'severity': 'LOW',
        'type': 'removed',
        'title': f'{len(removed_domains):,} domains removed from dataset',
        'detail': f'No longer detected in survey since {prev_date}.',
        'count': len(removed_domains),
        'samples': [],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'monitoring',
    })

if sev_escalated:
    alerts.append({
        'id': 'sev_escalated',
        'severity': 'MEDIUM',
        'type': 'severity_change',
        'title': f'{len(sev_escalated):,} domains escalated in severity',
        'detail': 'These domains increased their threat level since last update.',
        'count': len(sev_escalated),
        'samples': [{'domain': d, **info} for d, info in list(sev_escalated.items())[:10]],
        'timestamp': curr_date,
        'source': 'ARIA Diff Engine',
        'category': 'monitoring',
    })

summary = {
    'prev_date': prev_date,
    'curr_date': curr_date,
    'prev_total': len(prev_domains),
    'curr_total': len(curr_domains),
    'net_change': len(curr_domains) - len(prev_domains),
    'new_domains': len(new_domains),
    'removed_domains': len(removed_domains),
    'newly_active': len(newly_active),
    'newly_inactive': len(newly_inactive),
    'new_critical': len(new_critical),
    'sev_escalated': len(sev_escalated),
    'generated_at': datetime.utcnow().isoformat() + 'Z',
}

output = f"""// ARIA Diff Alerts — Auto-generated by diff_alerts.py
// Comparing: {prev_date} → {curr_date}
// DO NOT EDIT MANUALLY

const ARIA_DIFF = {{
  summary: {json.dumps(summary, ensure_ascii=False, indent=2)},
  alerts:  {json.dumps(alerts, ensure_ascii=False, indent=2)}
}};
"""

with open('diff_data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"diff_data.js: {len(alerts)} alerts")
print(f"  New: {summary['new_domains']:,}  Removed: {summary['removed_domains']:,}")
print(f"  Active: {summary['newly_active']:,}  Inactive: {summary['newly_inactive']:,}")
print(f"  Critical: {summary['new_critical']:,}  Escalated: {summary['sev_escalated']:,}")
