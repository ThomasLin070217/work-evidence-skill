import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "work-evidence"
spec = importlib.util.spec_from_file_location("work_evidence_report", SKILL / "scripts" / "report.py")
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((SKILL / "assets" / "example-ledger.json").read_text())

    def test_synthetic_totals_and_forecast(self):
        result = report.render(self.data)
        self.assertIn("11.5h", result)
        self.assertIn("历史投入7.5h，预计投入4h", result)
        self.assertIn("待评审", result)

    def test_duplicate_entry_is_not_counted_twice(self):
        self.data["entries"].append(copy.deepcopy(self.data["entries"][0]))
        with self.assertRaisesRegex(report.LedgerError, "Duplicate entry"):
            report.validate(self.data)

    def test_overlapping_work_across_tasks_is_rejected(self):
        item = copy.deepcopy(self.data["entries"][1])
        item.update(id="overlap", task_id="research")
        self.data["entries"].append(item)
        with self.assertRaisesRegex(report.LedgerError, "Overlapping"):
            report.validate(self.data)

    def test_future_activity_must_be_forecast(self):
        self.data["entries"][3]["kind"] = "recalled"
        with self.assertRaisesRegex(report.LedgerError, "cutoff"):
            report.validate(self.data)

    def test_month_boundary_rejected(self):
        self.data["entries"][3]["date"] = "2026-05-01"
        with self.assertRaisesRegex(report.LedgerError, "outside reporting period"):
            report.validate(self.data)

    def test_partial_week_and_31st(self):
        self.assertEqual(report.week_number(report.parse_date("2026-10-01")), 1)
        self.assertEqual(report.week_number(report.parse_date("2026-10-04")), 1)
        self.assertEqual(report.week_number(report.parse_date("2026-10-05")), 2)
        self.assertEqual(report.week_number(report.parse_date("2026-10-31")), 5)

    def test_missing_offset_rejected(self):
        self.data["entries"][1]["start"] = "2026-04-08T14:00:00"
        with self.assertRaisesRegex(report.LedgerError, "offset"):
            report.validate(self.data)

    def test_daily_limit_for_untimed_recollections(self):
        self.data["entries"][0]["minutes"] = 1500
        with self.assertRaisesRegex(report.LedgerError, "24 hours"):
            report.validate(self.data)

    def test_evidence_cannot_embed_credentials(self):
        self.data["tasks"][0]["evidence"][0]["url"] = "https://user:password@example.org/doc"
        with self.assertRaisesRegex(report.LedgerError, "credentials"):
            report.validate(self.data)

    def test_forecast_replacement_changes_accounting_without_duplication(self):
        self.data["as_of"] = "2026-04-30"
        self.data["entries"][3]["kind"] = "recalled"
        result = report.render(self.data)
        self.assertIn("历史投入11.5h，预计投入0h", result)


if __name__ == "__main__":
    unittest.main()
