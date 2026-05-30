# Hardware test-data traceability report

Total test runs: 12
Linked to build records: 11
Missing build-record links: 1
Open work-order tests: 3
Runs needing review: 6
Pass rate: 50.0%

## Why this matters

This report connects test runs back to part/build records and highlights data that should be reviewed before a hardware team treats the test data as clean.

## Station rollup

| station   |   total_tests |   review_items |   avg_pressure_psi |   avg_temp_c |   pass_rate |
|:----------|--------------:|---------------:|-------------------:|-------------:|------------:|
| bench-1   |             4 |              1 |              122.8 |         48.8 |        0.75 |
| bench-2   |             4 |              2 |              126.8 |         47.8 |        0.25 |
| bench-3   |             4 |              3 |              121.1 |         50.6 |        0.5  |

## Review queue

- T-0003 / NOZ-003 / bench-2: pressure above threshold; vibration above threshold
- T-0005 / NOZ-005 / bench-3: temperature above threshold; operator marked review
- T-0006 / NOZ-999 / bench-3: missing build record
- T-0008 / NOZ-011 / bench-1: operator marked review
- T-0009 / NOZ-007 / bench-2: duration above threshold; work order still open
- T-0010 / NOZ-008 / bench-3: work order still open
