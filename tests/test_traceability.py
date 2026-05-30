from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from traceability import (
    REQUIRED_PART_COLUMNS,
    REQUIRED_TEST_COLUMNS,
    REQUIRED_WORK_ORDER_COLUMNS,
    load_data,
    validate_schema,
    join_traceability,
    flag_anomalies,
    summarize,
    summarize_by_station,
    build_review_reason,
)


def test_traceability_flags_missing_build_record_and_anomalies():
    parts, work_orders, tests = load_data(ROOT / "data" / "raw")
    validate_schema(parts, work_orders, tests)
    traced = join_traceability(parts, work_orders, tests)
    flagged = flag_anomalies(traced)
    report = summarize(flagged)

    assert report.total_tests == 12
    assert report.linked_tests == 11
    assert report.missing_part_links == 1
    assert report.anomalies == 6
    assert report.open_work_order_tests == 3
    assert report.pass_rate == 0.5
    assert flagged.loc[flagged["part_id"].eq("NOZ-999"), "has_build_record"].item() is False
    assert flagged.loc[flagged["test_id"].eq("T-0003"), "pressure_out_of_family"].item() is True
    assert flagged.loc[flagged["test_id"].eq("T-0005"), "temp_out_of_family"].item() is True
    assert flagged.loc[flagged["test_id"].eq("T-0009"), "duration_out_of_family"].item() is True
    assert flagged.loc[flagged["test_id"].eq("T-0011"), "open_work_order"].item() is True


def test_schema_validation_requires_expected_columns():
    parts, work_orders, tests = load_data(ROOT / "data" / "raw")

    assert set(REQUIRED_PART_COLUMNS).issubset(parts.columns)
    assert set(REQUIRED_WORK_ORDER_COLUMNS).issubset(work_orders.columns)
    assert set(REQUIRED_TEST_COLUMNS).issubset(tests.columns)


def test_station_summary_rolls_up_counts_and_pass_rate():
    parts, work_orders, tests = load_data(ROOT / "data" / "raw")
    flagged = flag_anomalies(join_traceability(parts, work_orders, tests))
    station_summary = summarize_by_station(flagged)

    bench_1 = station_summary.loc[station_summary["station"].eq("bench-1")].iloc[0]
    bench_3 = station_summary.loc[station_summary["station"].eq("bench-3")].iloc[0]

    assert bench_1["total_tests"] == 4
    assert bench_1["review_items"] == 1
    assert bench_1["pass_rate"] == 0.75
    assert bench_3["total_tests"] == 4
    assert bench_3["review_items"] == 3


def test_review_reason_combines_hardware_data_quality_causes():
    parts, work_orders, tests = load_data(ROOT / "data" / "raw")
    flagged = flag_anomalies(join_traceability(parts, work_orders, tests))

    high_pressure = flagged.loc[flagged["test_id"].eq("T-0003")].iloc[0]
    missing_record = flagged.loc[flagged["test_id"].eq("T-0006")].iloc[0]
    open_work_order = flagged.loc[flagged["test_id"].eq("T-0011")].iloc[0]

    assert build_review_reason(high_pressure) == "pressure above threshold; vibration above threshold"
    assert build_review_reason(missing_record) == "missing build record"
    assert build_review_reason(open_work_order) == "work order still open"
