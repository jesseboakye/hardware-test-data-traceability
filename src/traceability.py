"""Hardware test-data traceability portfolio project.

Goal: show a Stoke-style software project that connects manufacturing/build records
(parts/work orders) to hardware test data, validation gates, and anomaly reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

PRESSURE_LIMIT_PSI = 130.0
TEMP_LIMIT_C = 65.0
VIBRATION_LIMIT_G = 0.30
DURATION_LIMIT_S = 160.0
VALID_RESULTS = {"pass", "fail", "review"}

REQUIRED_PART_COLUMNS = [
    "part_id",
    "batch_id",
    "revision",
    "build_date",
    "material",
    "work_order",
]
REQUIRED_WORK_ORDER_COLUMNS = [
    "work_order",
    "build_cell",
    "owner",
    "status",
    "planned_close_date",
]
REQUIRED_TEST_COLUMNS = [
    "test_id",
    "part_id",
    "timestamp",
    "operator",
    "station",
    "pressure_psi",
    "temp_c",
    "vibration_g",
    "duration_s",
    "result",
]


@dataclass(frozen=True)
class TraceabilityReport:
    total_tests: int
    linked_tests: int
    missing_part_links: int
    anomalies: int
    open_work_order_tests: int
    pass_rate: float


def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    parts = pd.read_csv(data_dir / "parts.csv", parse_dates=["build_date"])
    work_orders = pd.read_csv(data_dir / "work_orders.csv", parse_dates=["planned_close_date"])
    tests = pd.read_csv(data_dir / "test_runs.csv", parse_dates=["timestamp"])
    return parts, work_orders, tests


def validate_schema(parts: pd.DataFrame, work_orders: pd.DataFrame, tests: pd.DataFrame) -> None:
    missing = {
        "parts.csv": sorted(set(REQUIRED_PART_COLUMNS) - set(parts.columns)),
        "work_orders.csv": sorted(set(REQUIRED_WORK_ORDER_COLUMNS) - set(work_orders.columns)),
        "test_runs.csv": sorted(set(REQUIRED_TEST_COLUMNS) - set(tests.columns)),
    }
    errors = [f"{name} missing columns: {cols}" for name, cols in missing.items() if cols]
    if errors:
        raise ValueError("; ".join(errors))


def join_traceability(
    parts: pd.DataFrame, work_orders: pd.DataFrame, tests: pd.DataFrame
) -> pd.DataFrame:
    part_links = tests.merge(parts, on="part_id", how="left", indicator=True)
    part_links["has_build_record"] = part_links["_merge"].eq("both")
    part_links = part_links.drop(columns=["_merge"])

    full_links = part_links.merge(work_orders, on="work_order", how="left")
    full_links["has_work_order_record"] = full_links["status"].notna()
    full_links["open_work_order"] = full_links["status"].eq("open")
    return full_links


def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pressure_out_of_family"] = out["pressure_psi"] > PRESSURE_LIMIT_PSI
    out["temp_out_of_family"] = out["temp_c"] > TEMP_LIMIT_C
    out["vibration_out_of_family"] = out["vibration_g"] > VIBRATION_LIMIT_G
    out["duration_out_of_family"] = out["duration_s"] > DURATION_LIMIT_S
    out["invalid_result"] = ~out["result"].isin(VALID_RESULTS)
    out["needs_review"] = (
        ~out["has_build_record"]
        | ~out["has_work_order_record"]
        | out["pressure_out_of_family"]
        | out["temp_out_of_family"]
        | out["vibration_out_of_family"]
        | out["duration_out_of_family"]
        | out["invalid_result"]
        | out["result"].eq("review")
        | (out["open_work_order"] & ~out["result"].eq("pass"))
    )
    return out


def summarize(df: pd.DataFrame) -> TraceabilityReport:
    total = len(df)
    linked = int(df["has_build_record"].sum())
    missing = total - linked
    anomalies = int(df["needs_review"].sum())
    open_work_order_tests = int(df["open_work_order"].sum())
    pass_rate = float(df["result"].eq("pass").mean()) if total else 0.0
    return TraceabilityReport(total, linked, missing, anomalies, open_work_order_tests, pass_rate)


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
    grouped["avg_pressure_psi"] = grouped["avg_pressure_psi"].round(1)
    grouped["avg_temp_c"] = grouped["avg_temp_c"].round(1)
    grouped["pass_rate"] = grouped["pass_rate"].round(2)
    return grouped


def build_review_reason(row: pd.Series) -> str:
    reasons: list[str] = []
    has_build_record = bool(row["has_build_record"])
    if not has_build_record:
        reasons.append("missing build record")
    if has_build_record and not bool(row.get("has_work_order_record", True)):
        reasons.append("missing work order record")
    if bool(row.get("pressure_out_of_family", False)):
        reasons.append("pressure above threshold")
    if bool(row.get("temp_out_of_family", False)):
        reasons.append("temperature above threshold")
    if bool(row.get("vibration_out_of_family", False)):
        reasons.append("vibration above threshold")
    if bool(row.get("duration_out_of_family", False)):
        reasons.append("duration above threshold")
    if bool(row.get("invalid_result", False)):
        reasons.append("invalid result value")
    if row.get("result") == "review":
        reasons.append("operator marked review")
    if bool(row.get("open_work_order", False)):
        reasons.append("work order still open")
    return "; ".join(reasons) if reasons else "within validation gates"


def write_outputs(df: pd.DataFrame, report: TraceabilityReport, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    review = df[df["needs_review"]].copy()
    review["review_reason"] = review.apply(build_review_reason, axis=1)
    review.to_csv(reports_dir / "anomalies.csv", index=False)

    station_summary = summarize_by_station(df)
    station_summary.to_csv(reports_dir / "station_summary.csv", index=False)

    lines = [
        "# Hardware test-data traceability report",
        "",
        f"Total test runs: {report.total_tests}",
        f"Linked to build records: {report.linked_tests}",
        f"Missing build-record links: {report.missing_part_links}",
        f"Open work-order tests: {report.open_work_order_tests}",
        f"Runs needing review: {report.anomalies}",
        f"Pass rate: {report.pass_rate:.1%}",
        "",
        "## Why this matters",
        "",
        "This report connects test runs back to part/build records and highlights data that should be reviewed before a hardware team treats the test data as clean.",
        "",
        "## Station rollup",
        "",
        station_summary.to_markdown(index=False),
        "",
        "## Review queue",
        "",
    ]
    if review.empty:
        lines.append("No review items found.")
    else:
        for _, row in review.iterrows():
            lines.append(f"- {row['test_id']} / {row['part_id']} / {row['station']}: {row['review_reason']}")
    (reports_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parts, work_orders, tests = load_data(root / "data" / "raw")
    validate_schema(parts, work_orders, tests)
    traced = join_traceability(parts, work_orders, tests)
    flagged = flag_anomalies(traced)
    report = summarize(flagged)
    write_outputs(flagged, report, root / "reports")
    print("Wrote reports/summary.md, reports/anomalies.csv, and reports/station_summary.csv")
    print(report)


if __name__ == "__main__":
    main()
