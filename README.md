# Hardware Test Data Traceability

A one-day portfolio project that connects software engineering to hardware manufacturing and test-data workflows.

This repo is designed to strengthen my Stoke Space Software Internship application by showing that I can build software tools for hardware teams: ingesting test data, linking it to build records, validating quality gates, and producing review-ready reports.

## Project goal

Build a small traceability pipeline for mock hardware test data.

The project answers:

- Which test runs are linked to a known part/build record?
- Which part records connect to open or closed work orders?
- Which runs exceed pressure, temperature, vibration, or duration thresholds?
- Which records should a hardware/test team review before trusting the data?
- Which test stations have the most review items?

## Why this is relevant to Stoke Space

Stoke's software roles are not generic web/backend roles. They support reusable rocket development, hardware manufacturing, engineering data, and test workflows.

This project demonstrates:

- hardware-adjacent software thinking
- test-data validation
- traceability between parts, work orders, and test runs
- data-quality gates before downstream analysis
- station-level reporting for engineering review
- clear reporting for engineers and operators

## Current status

Completed MVP:

- [x] Built a local Python/pandas traceability pipeline.
- [x] Added mock `parts.csv`, `work_orders.csv`, and `test_runs.csv` data.
- [x] Expanded the dataset from 6 to 12 test runs across 3 bench stations.
- [x] Added validation gates for pressure, temperature, vibration, duration, result values, missing records, and open work orders.
- [x] Generated `reports/summary.md`, `reports/anomalies.csv`, and `reports/station_summary.csv`.
- [x] Added pytest coverage for schema validation, traceability joins, station summaries, and review reasons.
- [x] Added GitHub Actions CI.
- [x] Added `docs/architecture.md`.

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
- `reports/station_summary.csv`

## Sample output

```text
Wrote reports/summary.md, reports/anomalies.csv, and reports/station_summary.csv
TraceabilityReport(total_tests=12, linked_tests=11, missing_part_links=1, anomalies=6, open_work_order_tests=3, pass_rate=0.5)
```

Generated summary:

```text
Total test runs: 12
Linked to build records: 11
Missing build-record links: 1
Open work-order tests: 3
Runs needing review: 6
Pass rate: 50.0%
```

Station rollup:

| station | total_tests | review_items | avg_pressure_psi | avg_temp_c | pass_rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| bench-1 | 4 | 1 | 122.8 | 48.8 | 0.75 |
| bench-2 | 4 | 2 | 126.8 | 47.8 | 0.25 |
| bench-3 | 4 | 3 | 121.1 | 50.6 | 0.50 |

Review queue examples:

```text
- T-0003 / NOZ-003 / bench-2: pressure above threshold; vibration above threshold
- T-0005 / NOZ-005 / bench-3: temperature above threshold; operator marked review
- T-0006 / NOZ-999 / bench-3: missing build record
- T-0009 / NOZ-007 / bench-2: duration above threshold; work order still open
```

## Data model

### `data/raw/parts.csv`

Build-side records:

- `part_id`
- `batch_id`
- `revision`
- `build_date`
- `material`
- `work_order`

### `data/raw/work_orders.csv`

Manufacturing/work-order records:

- `work_order`
- `build_cell`
- `owner`
- `status`
- `planned_close_date`

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

The pipeline flags a run for review when:

- the test run has no linked build record
- the part points to a missing work-order record
- pressure is above 130 psi
- temperature is above 65 C
- vibration is above 0.30 g
- duration is above 160 seconds
- result is marked `review`
- result is outside the allowed values: `pass`, `fail`, `review`
- a non-passing run is tied to an open work order

These thresholds are mock values for a portfolio project, not real aerospace limits.

## What I learned

- Traceability matters because test data is less useful if it cannot be connected back to the part, batch, revision, and work order that produced it.
- Validation gates should separate raw data collection from engineering decision-making.
- A small review queue is more useful than a large undifferentiated data dump.
- Station-level summaries help identify whether issues are isolated to a part/batch or concentrated around a test station.
- Even a mock hardware dataset needs clear boundaries: this project demonstrates software/data workflow thinking, not professional aerospace test-stand operation.

## Resume bullet this project can support

> Built a Python/pandas traceability pipeline for mock hardware test data, linking part, work-order, and bench-test records while flagging missing records, threshold violations, and review items before downstream analysis.

Shorter version if resume space is tight:

> Built a Python hardware test-data traceability pipeline that links part/build records to bench-test runs and generates anomaly reports for engineering review.

## What to be honest about

This is a mock portfolio project, not professional manufacturing-floor experience.

Do not claim:

- machine shop experience
- pressure testing experience
- cryogenic handling experience
- production aerospace test operations

Do claim:

- built a hardware-adjacent data workflow
- implemented validation gates
- connected test records to part/build/work-order records
- generated review reports for engineering decision-making
- used pytest and GitHub Actions to verify the project

## Next improvement ideas

- Add a small Streamlit dashboard: station filters, batch filters, anomaly table, pass-rate chart.
- Add richer mock data with repeated tests per part.
- Add schema validation with units/ranges and clearer error messages.
- Add trend charts for pressure, temperature, and vibration by station.
