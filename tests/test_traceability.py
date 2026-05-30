from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from traceability import load_data, join_traceability, flag_anomalies, summarize


def test_traceability_flags_missing_build_record_and_anomalies():
    parts, tests = load_data(ROOT / "data" / "raw")
    traced = join_traceability(parts, tests)
    flagged = flag_anomalies(traced)
    report = summarize(flagged)

    assert report.total_tests == 6
    assert report.linked_tests == 5
    assert report.missing_part_links == 1
    assert report.anomalies == 3
    assert flagged.loc[flagged["part_id"].eq("NOZ-999"), "has_build_record"].item() is False
    assert flagged.loc[flagged["test_id"].eq("T-0003"), "pressure_out_of_family"].item() is True
    assert flagged.loc[flagged["test_id"].eq("T-0005"), "temp_out_of_family"].item() is True
