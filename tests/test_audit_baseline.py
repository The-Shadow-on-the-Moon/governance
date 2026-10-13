import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_baseline  # noqa: E402
import audit_common  # noqa: E402


def entry(check, **more):
    return dict({"check": check, "reason": "history", "date": "2026-10-12", "agreed_by": "the owner"}, **more)


def report_with(check_id, details, ok=False):
    report = audit_common.Report("git")
    report.add(check_id, "06 section 4.1", audit_common.RULE, "title", ok, "m", "h", details)
    return report


class BaselineTests(unittest.TestCase):
    def write(self, data):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = os.path.join(folder.name, "baseline.json")

        with open(path, "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

        return path

    def test_no_file_means_no_entries(self):
        self.assertEqual(audit_baseline.load("/nowhere/audit-baseline.json"), [])
        self.assertIsNone(audit_baseline.apply([report_with("a.b", ["x"])], []))

    def test_a_valid_file_is_loaded(self):
        path = self.write({"accepted": [entry("a.b", items=["x"])]})
        self.assertEqual(audit_baseline.load(path)[0]["check"], "a.b")

    def test_invalid_files_are_refused(self):
        for data in ("not json", {"accepted": "x"}, {"accepted": ["x"]}, {"other": []},
                     {"accepted": [{"check": "a.b", "reason": "r", "date": "2026-10-12"}]},
                     {"accepted": [entry("a.b", reason=" ")]}, {"accepted": [entry("a.b", items="x")]},
                     {"accepted": [entry("a.b", items=[3])]}):
            with self.assertRaises(audit_baseline.BaselineError, msg=str(data)):
                audit_baseline.load(self.write(data))

    def test_an_entry_without_items_accepts_the_whole_check(self):
        report = report_with("a.b", ["x", "y"])
        stale = audit_baseline.apply([report], [entry("a.b")])
        check = report.checks[0]
        self.assertEqual(check.result, audit_common.ACCEPTED)
        self.assertEqual(check.details[-1], "accepted: history (2026-10-12, agreed by the owner)")
        self.assertEqual(stale.checks[0].result, audit_common.PASS)
        self.assertEqual(report.failures(), [])
        self.assertEqual(report.counts()[audit_common.ACCEPTED], 1)

    def test_items_accept_only_the_lines_they_start(self):
        report = report_with("a.b", ["abc1 first", "def2 second", "ghi3 third"])
        audit_baseline.apply([report], [entry("a.b", items=["abc1", "def2"])])
        check = report.checks[0]
        self.assertEqual(check.result, audit_common.FAIL)
        self.assertEqual(check.message, "1 item(s) are not covered by the baseline")
        self.assertEqual(check.details, ["ghi3 third", "2 item(s) accepted by the baseline"])

    def test_items_that_cover_everything_accept_the_check(self):
        report = report_with("a.b", ["abc1 first", "def2 second"])
        audit_baseline.apply([report], [entry("a.b", items=["abc1"]), entry("a.b", items=["def2"], reason="two")])
        check = report.checks[0]
        self.assertEqual(check.result, audit_common.ACCEPTED)
        self.assertEqual(check.details[:2], ["abc1 first", "def2 second"])
        self.assertEqual(len(check.details), 4)

    def test_entries_that_accept_nothing_are_reported_as_stale(self):
        passing = report_with("a.b", ["looked"], ok=True)
        failing = report_with("c.d", ["x"])
        stale = audit_baseline.apply([passing, failing], [entry("a.b"), entry("c.d", items=["zzz"]), entry("e.f")])
        check = stale.checks[0]
        self.assertEqual((check.id, check.result, check.strength),
                         ("baseline.stale", audit_common.FAIL, audit_common.RECOMMENDATION))
        self.assertEqual(len(check.details), 3)
        self.assertEqual(passing.checks[0].result, audit_common.PASS)
        self.assertEqual(failing.checks[0].result, audit_common.FAIL)

    def test_a_check_that_is_not_failing_is_never_touched(self):
        report = report_with("a.b", ["x"], ok=None)
        audit_baseline.apply([report], [entry("a.b")])
        self.assertEqual(report.checks[0].result, audit_common.NOT_CHECKABLE)


if __name__ == "__main__":
    unittest.main()
