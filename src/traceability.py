"""Hardware test-data traceability starter project.

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
VALID_RESULTS = {"pass", "fail", "review"}


@dataclass(frozen=True)
class TraceabilityReport:
    total_tests: int
    linked_tests: int
    missing_part_links: int
    anomalies: int
    pass_rate: float


def load_data(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    parts = pd.read_csv(data_dir / "parts.csv")
    tests = pd.read_csv(data_dir / "test_runs.csv", parse_dates=["timestamp"])
    return parts, tests


def join_traceability(parts: pd.DataFrame, tests: pd.DataFrame) -> pd.DataFrame:
    merged = tests.merge(parts, on="part_id", how="left", indicator=True)
    merged["has_build_record"] = merged["_merge"].eq("both")
    return merged.drop(columns=["_merge"])


def flag_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pressure_out_of_family"] = out["pressure_psi"] > PRESSURE_LIMIT_PSI
    out["temp_out_of_family"] = out["temp_c"] > TEMP_LIMIT_C
    out["vibration_out_of_family"] = out["vibration_g"] > VIBRATION_LIMIT_G
    out["invalid_result"] = ~out["result"].isin(VALID_RESULTS)
    out["needs_review"] = (
        ~out["has_build_record"]
        | out["pressure_out_of_family"]
        | out["temp_out_of_family"]
        | out["vibration_out_of_family"]
        | out["invalid_result"]
        | out["result"].eq("review")
    )
    return out


def summarize(df: pd.DataFrame) -> TraceabilityReport:
    total = len(df)
    linked = int(df["has_build_record"].sum())
    missing = total - linked
    anomalies = int(df["needs_review"].sum())
    pass_rate = float(df["result"].eq("pass").mean()) if total else 0.0
    return TraceabilityReport(total, linked, missing, anomalies, pass_rate)


def write_outputs(df: pd.DataFrame, report: TraceabilityReport, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    review = df[df["needs_review"]].copy()
    review.to_csv(reports_dir / "anomalies.csv", index=False)

    lines = [
        "# Hardware test-data traceability report",
        "",
        f"Total test runs: {report.total_tests}",
        f"Linked to build records: {report.linked_tests}",
        f"Missing build-record links: {report.missing_part_links}",
        f"Runs needing review: {report.anomalies}",
        f"Pass rate: {report.pass_rate:.1%}",
        "",
        "## Why this matters",
        "",
        "This report connects test runs back to part/build records and highlights data that should be reviewed before a hardware team treats the test data as clean.",
        "",
        "## Review queue",
        "",
    ]
    if review.empty:
        lines.append("No review items found.")
    else:
        for _, row in review.iterrows():
            reasons = []
            if not row["has_build_record"]:
                reasons.append("missing build record")
            if row["pressure_out_of_family"]:
                reasons.append("pressure above threshold")
            if row["temp_out_of_family"]:
                reasons.append("temperature above threshold")
            if row["vibration_out_of_family"]:
                reasons.append("vibration above threshold")
            if row["result"] == "review":
                reasons.append("operator marked review")
            lines.append(f"- {row['test_id']} / {row['part_id']}: {', '.join(reasons)}")
    (reports_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parts, tests = load_data(root / "data" / "raw")
    traced = join_traceability(parts, tests)
    flagged = flag_anomalies(traced)
    report = summarize(flagged)
    write_outputs(flagged, report, root / "reports")
    print(f"Wrote reports/summary.md and reports/anomalies.csv")
    print(report)


if __name__ == "__main__":
    main()
