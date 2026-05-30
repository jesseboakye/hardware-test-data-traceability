# Architecture

This project is intentionally small, but it mirrors a real hardware-data workflow.

```text
parts.csv + work_orders.csv + test_runs.csv
        |
        v
load_data()
        |
        v
validate_schema()
        |
        v
join_traceability()
        |
        v
flag_anomalies()
        |
        +--> reports/anomalies.csv
        +--> reports/station_summary.csv
        +--> reports/summary.md
```

## Workflow

1. Load build records, work orders, and bench-test records.
2. Validate that each input file has the required columns.
3. Join test runs to part/build records using `part_id`.
4. Join parts to work orders using `work_order`.
5. Flag records that need engineering review.
6. Produce CSV and Markdown outputs that an engineer/operator could scan quickly.

## Validation gates

The mock validation gates check for:

- missing build records
- missing work-order records
- pressure above threshold
- temperature above threshold
- vibration above threshold
- duration above threshold
- invalid result values
- operator-marked review runs
- open work orders attached to non-passing test runs

## Portfolio note

This is not real rocket-test data and does not claim professional aerospace test-stand experience. The point is to show hardware-adjacent software judgment: traceability, data validation, report generation, and clear review queues for engineering teams.
