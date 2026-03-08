# RevVision Pro - CPQ to Revenue Cloud Advanced Readiness Assessment

## Overview
RevVision Pro analyzes Salesforce CPQ migration artifacts (Apex, Flow, QCP, metadata) and produces:
- Per-file migration risk score and effort estimate.
- Portfolio-level risk and readiness insights.
- Coverage checks for mandatory migration areas.
- Phased migration roadmap.
- Detailed blueprint for CPQ to RCA migration actions.
- Downloadable migration test plan (Python UI).

The project includes:
- Python Streamlit workbench (`src/`) for local/demo usage.
- Salesforce-native workbench (LWC + Apex in `salesforce/force-app/main/default`).

## Links
- GitHub Repository: `https://github.com/Lokesh0110/revvision`
- Salesforce Version URL: `https://wise-otter-3cucsg-dev-ed.trailblaze.my.site.com/revvision/s/`

## Scoring Model (Current)
- Per-file score range: `0..1000` (hard cap at 1000).
- Score factors:
  - file type base weight
  - conditions
  - actions
  - lookups
  - SOQL hits
  - hardcoded IDs
  - SBQQ references
  - QCP hooks
- Org risk is computed from total portfolio score using selected thresholds.

### Risk Threshold Profiles
- Balanced: `250 / 500 / 750` (LOW/MODERATE/HIGH boundaries)
- Strict: `150 / 350 / 600`
- Custom: user-defined (`Low < Moderate < High`)

## Python UI Features
Tabs:
- Dashboard
- File Analysis
- Readiness
- Remediation
- Blueprint Studio
- Test Lab

Key behavior:
- Shows per-file score and portfolio total score.
- Shows risk score ranges table in dashboard.
- Readiness includes status/confidence/coverage/pricing signals.
- Duplicate/near-duplicate files are excluded from scoring.
- Streamlit toolbar is locked to viewer mode via `.streamlit/config.toml`.

## Salesforce UI Features (LWC + Apex)
Component: `revvisionWorkbench`

Tabs:
- Dashboard
- File Analysis
- Parameters
- Readiness
- Roadmap
- Blueprint

Key behavior:
- Native file picker with uploaded file list and status.
- Dashboard includes per-file score table and scoring note (score factors + 1000 cap).
- Parameters tab includes per-file metrics (conditions/actions/lookups/SOQL/hardcoded IDs/SBQQ/QCP hooks).
- Readiness tab includes status, confidence, coverage table, and pricing signals.
- Blueprint section renders formatted bullets with bold section titles.

## Project Structure
- `src/app.py` - Streamlit app entrypoint.
- `src/revvision/services/analyzer.py` - Scoring, readiness, coverage, ROI.
- `src/revvision/ui/render.py` - Streamlit UI rendering.
- `src/revvision/parsers.py` - Artifact parsers.
- `src/revvision/detection.py` - File type detection.
- `salesforce/force-app/main/default/classes/RevVisionAssessmentController.cls` - Apex assessment logic.
- `salesforce/force-app/main/default/lwc/revvisionWorkbench/*` - Salesforce native UI.

## Local Setup (Python)
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

## Run (Python)
```bash
streamlit run src/app.py
```
Open: `http://localhost:8501`

## Testing
```bash
python -m pytest -q
```

## Salesforce Deployment
1. Authorize org:
```bash
sf org login web --alias revvision-org
```
2. Deploy:
```bash
sf project deploy start --source-dir salesforce/force-app --target-org revvision-org
```
3. Add **RevVision Workbench** to a Lightning App/Home/Record page.
4. Save and activate page.

## Optional Public Demo URL (Python)
```bash
streamlit run src/app.py --server.port 8501
cloudflared tunnel --url http://localhost:8501
```

## Notes
- If Streamlit reports TOML parse issues, ensure `.streamlit/config.toml` is UTF-8 without BOM.
- Salesforce org-wide test failures from unrelated app metadata do not block component usage, but package-level validation should still be completed before final submission.
