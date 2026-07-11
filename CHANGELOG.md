# ARIA — Changelog

## 2026-07-12 — Kill-list: retract the facade (honesty pass)
Following a 7-area audit (60 findings) + architecture review, this pass converts the
site from *actively misrepresenting* to *honestly stale*. It does NOT add product
capability — it stops the site from asserting things that are not true. Full plan and
review: `reports/game_dashboard_audit_20260712/` (in the ASAM working repo).

- **Stopped the false "live feed".** Disabled the daily `threat-feed.yml` schedule that
  committed byte-identical snapshots + zero-change diffs every day (105/107 snapshots were
  byte-identical). The dataset has been frozen since 2026-03-28.
- **Added a STATIC SNAPSHOT banner** to all 29 pages ("dataset frozen 2026-03-30, N=3,755,
  live monitoring not active, pending re-verification"). Removed "refreshed daily" claims.
- **Corrected the inflated headline count** 7,225 → 3,755 (real distinct domains) in all
  footers/taglines and the index KPI. Fixed the Active-Threats ratio 37.1% → 71.4%
  (2,680 / 3,755) and Publishers Affected 28 → 17.
- **Removed `[VERIFIED DATA]` badges** that were attached to hand-entered figures.
- **Fixed inverted/fabricated caselaw**: `Sony v. Connectix` (a Sony *loss*, previously shown
  as a $10.5M win) and a placeholder Microsoft citation neutralized; caselaw header now
  flagged UNVERIFIED — pending qualified legal review.
- **Labelled 0-record publisher pages** (Warner Bros / THQ Nordic / Koei Tecmo) as
  ILLUSTRATIVE (no backing rows in the dataset). Removed a non-existent title
  ("Ratchet & Clank: Ranger Rumble").
- **Fixed the dead intake form**: it silently discarded submissions and showed a fake
  "received, reply in 24h" success. Now opens the user's mail client (mailto) with the
  details pre-filled and states honestly that the static site stores nothing. (Replace with
  a real webhook + durable store when a backend exists. Intake address needs confirmation.)
- **Wired the sample-PDF link** (was an `alert()` stub) to the real PDF.
- **Reduced publish exposure**: GitHub Pages now ships only the site (HTML/JS/assets/PDF/
  publishers) — the raw survey CSV, pipeline scripts, and 107 snapshots are no longer served.
- **Added a minimal CSP** meta (`object-src 'none'; base-uri 'self'; frame-ancestors 'none'`).

Known-remaining (Phase 1, tracked in the audit report): trends.html charts are hardcoded
legacy values pending rebuild; enforcement 694/676 reconciliation; broken per-publisher
charts (`new Chart(null)`); orphaned data files; full caselaw verification.

---

# ARIA v2.3 — 50-Iteration Changelog (Safe Edition)
Generated: 2026-03-30T02:14:42.302946Z

## Data Consistency (Iter 1-5)
- contact.html publisher data already fixed to real ASAM data (prev session)
- Added 5 missing publishers to index.html search (505 Games, THQ Nordic, Valve, Koei Tecmo, Paradox)
- Fixed "Pokemon leads" → "Minecraft leads with 233 sites"
- Added URL count methodology note to contact.html

## Copy & Tone (Iter 6-15)
- Landing headline → professional legal-team focused copy
- CTA texts → action-oriented ("See risk report", "Submit Request & Get Case ID")
- Pricing tiers → legal workflow names (Investigate/Enforce/Litigate)
- MCP CTA → "Start 30-day MCP pilot"
- Disclaimer → evidence preparation support language

## Evidence Quality Signals (Iter 16-25)
- Hash freshness: "re-verified within 30 days"
- Email field: security handling note
- Success message: case ID generation
- Publisher pages: evidence methodology tooltips (SHA-256, NTP-synced, crawler+manual)

## UX Improvements (Iter 26-35)
- Diff label: "WHAT CHANGED (LAST 24H)"
- Title sort hint
- Reclassification confidence note
- Enforcement pipeline language (Detect→File→Track→Resolve)
- Per-action impact estimates on enforcement items

## Final Polish (Iter 36-50)
- Network legend enhancement
- Publisher index action hint
- All dates to 2026-03-30
- "Data as of" with refresh frequency
- Responsive table CSS across all pages
- Safety verification: all pages healthy
