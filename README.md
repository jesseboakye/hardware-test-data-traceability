# Hardware Test Data Traceability

A one-day portfolio project that connects software engineering to hardware manufacturing and test-data workflows.

This repo is designed to strengthen my Stoke Space Software Internship application by showing that I can build software tools for hardware teams: ingesting test data, linking it to build records, validating quality gates, and producing review-ready reports.

## Project goal

Build a small traceability pipeline for mock hardware test data.

The project answers:

- Which test runs are linked to a known part/build record?
- Which runs have missing traceability?
- Which runs exceed pressure, temperature, or vibration thresholds?
- What should a hardware/test team review before trusting the data?

## Why this is relevant to Stoke Space

Stoke's software roles are not generic web/backend roles. They support reusable rocket development, hardware manufacturing, engineering data, and test workflows.

This project demonstrates:

- hardware-adjacent software thinking
- test-data validation
- traceability between parts, work orders, and test runs
- data-quality gates before downstream analysis
- clear reporting for engineers and operators

## MVP scope for tomorrow

Tomorrow's target is intentionally small enough to finish in a few focused hours.

### Must finish

- [ ] Run the starter pipeline locally.
- [ ] Review the mock `parts.csv` and `test_runs.csv` data.
- [ ] Add 5-10 more realistic test rows.
- [ ] Improve the anomaly rules or thresholds.
- [ ] Generate `reports/summary.md` and `reports/anomalies.csv`.
- [ ] Add one screenshot of the report or terminal output to this README.
- [ ] Write a short "What I learned" section.

### Nice to add if time allows

- [ ] Add a simple Streamlit dashboard.
- [ ] Add charts for pass rate by station or batch.
- [ ] Add a `work_orders.csv` table and link it into the traceability report.
- [ ] Add a small architecture diagram showing data flow.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/traceability.py
pytest -q
```

Expected outputs:

- `reports/summary.md`
- `reports/anomalies.csv`

## Data model

### `data/raw/parts.csv`

Build-side records:

- `part_id`
- `batch_id`
- `revision`
- `build_date`
- `material`
- `work_order`

### `data/raw/test_runs.csv`

Test-side records:

- `test_id`
- `part_id`
- `timestamp`
- `operator`
- `station`
- `pressure_psi`
- `temp_c`
- `vibration_g`
- `duration_s`
- `result`

## Current validation gates

The starter pipeline flags a run for review when:

- the test run has no linked build record
- pressure is above 130 psi
- temperature is above 65 C
- vibration is above 0.30 g
- result is marked `review`
- result is outside the allowed values: `pass`, `fail`, `review`

These thresholds are mock values for a portfolio project, not real aerospace limits.

## Resume bullet this project can support after completion

Possible bullet:

> Built a Python traceability pipeline for mock hardware test data, linking part/build records to test runs and flagging missing records, threshold violations, and review items before downstream analysis.

Stronger version if a dashboard is added:

> Built a Python hardware test-data traceability dashboard with pandas validation gates, linking part/build records to test runs and surfacing review queues for pressure, temperature, vibration, and missing-record anomalies.

## What to be honest about

This is a mock portfolio project, not professional manufacturing-floor experience.

Do not claim:

- machine shop experience
- pressure testing experience
- cryogenic handling experience
- production aerospace test operations

Do claim, if completed:

- built a hardware-adjacent data workflow
- implemented validation gates
- connected test records to part/build records
- generated review reports for engineering decision-making

## Next improvement ideas

- Add Streamlit dashboard: station filters, batch filters, anomaly table, pass-rate chart.
- Add CI with pytest through GitHub Actions.
- Add richer test data with multiple stations and batches.
- Add schema validation with required columns and allowed units.
- Add `docs/architecture.md` explaining the ingest -> validate -> report flow.
