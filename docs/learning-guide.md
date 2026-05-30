# Stoke Traceability Project Learning Guide

Goal: rebuild and understand the hardware test-data traceability project yourself, step by step.

This guide is written so you can learn the project instead of only having a finished repo. It explains what to do, why each step matters, which files to touch, how to test your work, and which official docs to use when you get stuck.

Repo:
https://github.com/jesseboakye/hardware-test-data-traceability

Local path:
`C:\Users\jesse\OneDrive\Documents\Claude\Projects\PostGrad\02_Job_Search\hardware-test-data-traceability`

WSL path:
`/mnt/c/Users/jesse/OneDrive/Documents/Claude/Projects/PostGrad/02_Job_Search/hardware-test-data-traceability`

---

## Important: how to practice without losing the finished version

The finished project is already on `main`. To learn by rebuilding it, make a separate branch.

### Option A — safest: create a learning branch from the original starter commit

Use this if you want to redo the project from the simple starter version.

```bash
cd "/mnt/c/Users/jesse/OneDrive/Documents/Claude/Projects/PostGrad/02_Job_Search/hardware-test-data-traceability"
git checkout -b learning-rebuild 52bf907
```

Then rebuild the finished functionality yourself while checking `main` only when you need hints.

To return to the finished version later:

```bash
git checkout main
```

### Option B — practice on top of the finished project

Use this if you want to add improvements instead of rebuilding from scratch.

```bash
cd "/mnt/c/Users/jesse/OneDrive/Documents/Claude/Projects/PostGrad/02_Job_Search/hardware-test-data-traceability"
git checkout main
git checkout -b learning-improvements
```

---

## Project story in plain English

This project pretends you are helping a hardware/test team manage bench-test data.

A hardware team has:

1. Parts that were built.
2. Work orders that describe the build process.
3. Test runs that produce measurements.

Your software job is to connect those records and answer:

- Does every test run connect to a real part?
- Does every part connect to a work order?
- Are any measurements outside expected limits?
- Which records need engineering review?
- Which test station has the most review items?

This is useful for Stoke-style software because it shows hardware-adjacent thinking: traceability, data quality, validation gates, and useful reporting for engineering teams.

---

## What you should know before coding

You do not need to be an aerospace engineer to understand this project.

You do need to understand:

- CSV files are simple tables.
- pandas DataFrames are table-like objects in Python.
- A merge/join connects rows from different tables using a shared key.
- A validation gate is a rule that decides whether data is clean enough to trust.
- A test verifies that the code does what you expect.

---

## Official documentation links

### Python basics

- Python tutorial:
  https://docs.python.org/3/tutorial/
- Python `pathlib` for file paths:
  https://docs.python.org/3/library/pathlib.html
- Python dataclasses:
  https://docs.python.org/3/library/dataclasses.html

### pandas

- pandas Getting Started:
  https://pandas.pydata.org/docs/getting_started/index.html
- `pandas.read_csv`:
  https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- `DataFrame.merge`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
- `DataFrame.groupby`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
- `DataFrame.agg`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html
- `DataFrame.to_csv`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
- `DataFrame.to_markdown`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_markdown.html

### pytest

- pytest getting started:
  https://docs.pytest.org/en/stable/getting-started.html
- pytest assertions:
  https://docs.pytest.org/en/stable/how-to/assert.html
- pytest usage and command-line options:
  https://docs.pytest.org/en/stable/how-to/usage.html

### Git and GitHub

- GitHub Git handbook:
  https://guides.github.com/introduction/git-handbook/
- GitHub Actions for Python:
  https://docs.github.com/actions/guides/building-and-testing-python
- `actions/setup-python`:
  https://github.com/actions/setup-python
- GitHub Markdown guide:
  https://docs.github.com/get-started/writing-on-github

### CSV / data quality background

- CSV format overview:
  https://docs.python.org/3/library/csv.html
- Data validation concept overview:
  https://en.wikipedia.org/wiki/Data_validation
- Traceability concept overview:
  https://en.wikipedia.org/wiki/Traceability

Use official docs first. Use blog posts or videos only when the official docs are too dry.

---

## Setup instructions

From WSL:

```bash
cd "/mnt/c/Users/jesse/OneDrive/Documents/Claude/Projects/PostGrad/02_Job_Search/hardware-test-data-traceability"
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the project:

```bash
python src/traceability.py
```

Run tests:

```bash
pytest -q
```

Expected final test result on the finished project:

```text
4 passed
```

---

## Learning path overview

Work through these stages in order:

1. Understand the input CSV files.
2. Load the CSV files with pandas.
3. Validate required columns.
4. Join test runs to part records.
5. Join part records to work orders.
6. Add validation/anomaly flags.
7. Summarize project-level metrics.
8. Summarize station-level metrics.
9. Write output reports.
10. Add tests.
11. Add README learning notes.
12. Commit and push.

Each stage below has a purpose, files, commands, and checkpoints.

---

## Stage 1 — Understand the input data

Files to inspect:

- `data/raw/parts.csv`
- `data/raw/work_orders.csv`
- `data/raw/test_runs.csv`

Commands:

```bash
python3 - <<'PY'
from pathlib import Path
for path in Path('data/raw').glob('*.csv'):
    print('\n---', path, '---')
    print(path.read_text())
PY
```

What to learn:

- `part_id` connects `test_runs.csv` to `parts.csv`.
- `work_order` connects `parts.csv` to `work_orders.csv`.
- `station` tells you where the test happened.
- `pressure_psi`, `temp_c`, `vibration_g`, and `duration_s` are mock measurements.
- `result` is the operator/test result: `pass`, `fail`, or `review`.

Checkpoint questions:

- Which file tells you a part's batch and material?
- Which file tells you whether a work order is open or closed?
- Which test row has a fake/missing part ID?

---

## Stage 2 — Load CSV files with pandas

File to modify:

- `src/traceability.py`

Function to understand or rebuild:

```python
def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    parts = pd.read_csv(data_dir / "parts.csv", parse_dates=["build_date"])
    work_orders = pd.read_csv(data_dir / "work_orders.csv", parse_dates=["planned_close_date"])
    tests = pd.read_csv(data_dir / "test_runs.csv", parse_dates=["timestamp"])
    return parts, work_orders, tests
```

Docs to use:

- https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
- https://docs.python.org/3/library/pathlib.html

Practice command:

```bash
python3 - <<'PY'
from pathlib import Path
from src.traceability import load_data
parts, work_orders, tests = load_data(Path('data/raw'))
print(parts.head())
print(work_orders.head())
print(tests.head())
PY
```

Checkpoint:

You should see three DataFrames printed without errors.

---

## Stage 3 — Validate required columns

Why this matters:

If a CSV is missing a required column, the project should fail clearly instead of crashing later with a confusing error.

Function to understand or rebuild:

```python
def validate_schema(parts: pd.DataFrame, work_orders: pd.DataFrame, tests: pd.DataFrame) -> None:
    missing = {
        "parts.csv": sorted(set(REQUIRED_PART_COLUMNS) - set(parts.columns)),
        "work_orders.csv": sorted(set(REQUIRED_WORK_ORDER_COLUMNS) - set(work_orders.columns)),
        "test_runs.csv": sorted(set(REQUIRED_TEST_COLUMNS) - set(tests.columns)),
    }
    errors = [f"{name} missing columns: {cols}" for name, cols in missing.items() if cols]
    if errors:
        raise ValueError("; ".join(errors))
```

Docs to use:

- Python sets:
  https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
- pandas DataFrame columns:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.columns.html

Practice task:

Temporarily remove a column name from `REQUIRED_TEST_COLUMNS`, run tests, and observe what changes. Then undo it.

Command:

```bash
pytest tests/test_traceability.py::test_schema_validation_requires_expected_columns -q
```

Checkpoint:

You understand why schema validation is safer than assuming every file is correct.

---

## Stage 4 — Join test runs to part records

Why this matters:

A test run is much more useful when you know which part, batch, revision, material, and work order produced it.

Code concept:

```python
part_links = tests.merge(parts, on="part_id", how="left", indicator=True)
part_links["has_build_record"] = part_links["_merge"].eq("both")
```

Docs to use:

- https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html

Important idea:

`how="left"` keeps every test run, even if the part record is missing. This is important because missing traceability is itself something you want to flag.

Practice command:

```bash
python3 - <<'PY'
from pathlib import Path
from src.traceability import load_data
parts, work_orders, tests = load_data(Path('data/raw'))
merged = tests.merge(parts, on='part_id', how='left', indicator=True)
print(merged[['test_id', 'part_id', 'batch_id', 'work_order', '_merge']])
PY
```

Checkpoint:

Find the row where `_merge` is `left_only`. That is the missing build-record case.

---

## Stage 5 — Join part records to work orders

Why this matters:

The work-order record tells you whether a part came from an open or closed build process.

Code concept:

```python
full_links = part_links.merge(work_orders, on="work_order", how="left")
full_links["has_work_order_record"] = full_links["status"].notna()
full_links["open_work_order"] = full_links["status"].eq("open")
```

Docs to use:

- pandas merge:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
- pandas `Series.notna`:
  https://pandas.pydata.org/docs/reference/api/pandas.Series.notna.html
- pandas `Series.eq`:
  https://pandas.pydata.org/docs/reference/api/pandas.Series.eq.html

Checkpoint:

You should be able to explain why an open work order might matter for engineering review.

---

## Stage 6 — Add validation/anomaly flags

Why this matters:

Raw measurements are not enough. A hardware/test workflow needs rules that decide which rows need review.

Current mock thresholds:

```python
PRESSURE_LIMIT_PSI = 130.0
TEMP_LIMIT_C = 65.0
VIBRATION_LIMIT_G = 0.30
DURATION_LIMIT_S = 160.0
VALID_RESULTS = {"pass", "fail", "review"}
```

Flag examples:

```python
out["pressure_out_of_family"] = out["pressure_psi"] > PRESSURE_LIMIT_PSI
out["temp_out_of_family"] = out["temp_c"] > TEMP_LIMIT_C
out["vibration_out_of_family"] = out["vibration_g"] > VIBRATION_LIMIT_G
out["duration_out_of_family"] = out["duration_s"] > DURATION_LIMIT_S
```

Docs to use:

- pandas Boolean indexing:
  https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing

Practice task:

Add one more mock rule, for example:

- flag very short tests below 100 seconds
- flag pressure below a minimum threshold
- flag station names outside a known list

Do it test-first:

1. Add a test row that should trigger the rule.
2. Write a failing pytest assertion.
3. Implement the rule.
4. Run tests again.

Checkpoint:

You understand the difference between raw data and review-ready data.

---

## Stage 7 — Summarize project-level metrics

Function to understand:

```python
def summarize(df: pd.DataFrame) -> TraceabilityReport:
    total = len(df)
    linked = int(df["has_build_record"].sum())
    missing = total - linked
    anomalies = int(df["needs_review"].sum())
    open_work_order_tests = int(df["open_work_order"].sum())
    pass_rate = float(df["result"].eq("pass").mean()) if total else 0.0
    return TraceabilityReport(total, linked, missing, anomalies, open_work_order_tests, pass_rate)
```

Docs to use:

- Python dataclasses:
  https://docs.python.org/3/library/dataclasses.html
- pandas `Series.mean`:
  https://pandas.pydata.org/docs/reference/api/pandas.Series.mean.html

Checkpoint:

You should understand why a Boolean column can be summed to count `True` values.

---

## Stage 8 — Summarize by station

Why this matters:

If one station has more review items than others, that might point to equipment, procedure, calibration, or operator-process issues.

Function to understand:

```python
def summarize_by_station(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("station", as_index=False)
        .agg(
            total_tests=("test_id", "count"),
            review_items=("needs_review", "sum"),
            avg_pressure_psi=("pressure_psi", "mean"),
            avg_temp_c=("temp_c", "mean"),
            pass_rate=("result", lambda s: float(s.eq("pass").mean())),
        )
        .sort_values("station")
    )
    return grouped
```

Docs to use:

- pandas groupby:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.groupby.html
- pandas aggregate:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.agg.html

Practice task:

Add a second summary grouped by `batch_id`.

Suggested output file:

- `reports/batch_summary.csv`

Checkpoint:

You can explain how a grouped summary helps engineering teams find patterns.

---

## Stage 9 — Write output reports

Current outputs:

- `reports/summary.md`
- `reports/anomalies.csv`
- `reports/station_summary.csv`

Docs to use:

- pandas `to_csv`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
- pandas `to_markdown`:
  https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_markdown.html
- Markdown guide:
  https://docs.github.com/get-started/writing-on-github

Practice task:

Open the generated Markdown report:

```bash
python src/traceability.py
sed -n '1,180p' reports/summary.md
```

Checkpoint:

The report should be understandable by someone who does not read the code.

---

## Stage 10 — Add tests

Why this matters:

Tests prove that your traceability and anomaly logic keeps working after changes.

Test file:

- `tests/test_traceability.py`

Docs to use:

- pytest getting started:
  https://docs.pytest.org/en/stable/getting-started.html
- pytest assertions:
  https://docs.pytest.org/en/stable/how-to/assert.html

Current test categories:

1. Schema validation.
2. Missing build-record detection.
3. Threshold anomaly detection.
4. Open work-order detection.
5. Station summary counts.
6. Review reason strings.

Recommended learning workflow:

```bash
pytest tests/test_traceability.py -q
```

Then run one test at a time:

```bash
pytest tests/test_traceability.py::test_station_summary_rolls_up_counts_and_pass_rate -q
```

Practice task:

Add a new test for a batch summary if you build Stage 8's optional `batch_summary.csv` feature.

---

## Stage 11 — Add GitHub Actions CI

File:

- `.github/workflows/ci.yml`

Why this matters:

GitHub Actions proves the project runs outside your machine.

Docs to use:

- GitHub Actions Python guide:
  https://docs.github.com/actions/guides/building-and-testing-python
- `actions/setup-python`:
  https://github.com/actions/setup-python

Current CI steps:

1. Check out code.
2. Install Python.
3. Install dependencies.
4. Run pytest.
5. Generate reports.

Checkpoint:

After pushing, the GitHub Actions tab should show a passing CI run.

---

## Stage 12 — Commit and push your learning branch

Use small commits as you learn.

Example:

```bash
git status
git add src/traceability.py tests/test_traceability.py
git commit -m "learn: add batch summary validation"
git push -u origin learning-rebuild
```

If you are on a branch that GitHub does not know about yet, the first push needs `-u origin branch-name`.

---

## Suggested self-directed improvements

Pick only one or two. Do not try to build everything.

### Improvement 1 — Batch summary

Add:

- `summarize_by_batch(df)`
- `reports/batch_summary.csv`
- tests for batch-level counts and review items

What this teaches:

- grouped data analysis
- engineering pattern detection

### Improvement 2 — Minimum pressure rule

Add:

- `MIN_PRESSURE_PSI = 110.0`
- `pressure_below_minimum` flag
- review reason text
- tests

What this teaches:

- adding validation gates safely
- updating tests and reports together

### Improvement 3 — Station whitelist

Add:

- `VALID_STATIONS = {"bench-1", "bench-2", "bench-3"}`
- `invalid_station` flag
- tests

What this teaches:

- categorical validation
- catching data-entry problems

### Improvement 4 — Simple dashboard later

Only do this after you understand the pipeline.

Useful docs:

- Streamlit docs:
  https://docs.streamlit.io/
- Streamlit `st.dataframe`:
  https://docs.streamlit.io/develop/api-reference/data/st.dataframe
- Streamlit charts:
  https://docs.streamlit.io/develop/api-reference/charts

What this teaches:

- turning data into an interactive tool
- making a portfolio project more visual

---

## How to explain this project in an interview

Short answer:

> I built a Python/pandas traceability pipeline for mock hardware test data. It links bench-test runs to part and work-order records, applies validation gates for missing records and out-of-family measurements, and generates a review queue and station summary for engineering review.

If asked what you learned:

> I learned that test data is only useful if it stays connected to build context. A pressure or vibration reading by itself is not enough. You need to know which part, batch, revision, work order, and station produced the data, then apply validation gates before using it for decisions.

If asked whether this is real aerospace test experience:

> No. It is a mock portfolio project. I am not claiming production aerospace test-stand experience. I built it to show that I understand the software side of hardware workflows: traceability, validation, anomaly reporting, and clear engineering handoff.

---

## Resume bullet after you understand the project

Use this only after you can explain the code and reports yourself:

> Built a Python/pandas traceability pipeline for mock hardware test data, linking part, work-order, and bench-test records while flagging missing records, threshold violations, and review items before downstream analysis.

Shorter version:

> Built a Python hardware test-data traceability pipeline that links part/build records to bench-test runs and generates anomaly reports for engineering review.

---

## Final checklist before adding it to your resume

You should be able to answer yes to all of these:

- [ ] I can explain what each CSV file represents.
- [ ] I can explain why `part_id` and `work_order` are the join keys.
- [ ] I can explain what a left join does and why it matters here.
- [ ] I can explain every validation gate.
- [ ] I can run `python src/traceability.py` successfully.
- [ ] I can run `pytest -q` successfully.
- [ ] I can explain what is in `reports/summary.md`.
- [ ] I can explain what this project does not claim.

If any answer is no, revisit the matching stage above.
