import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit  # noqa: E402
import audit_common  # noqa: E402
import test_audit_board  # noqa: E402
import test_audit_files  # noqa: E402
import test_audit_git  # noqa: E402


def good_github(repo):
    report = audit_common.Report("github")
    report.add("github.x", "10 section 3", audit_common.RULE, "fine", True)
    report.add("github.y", "10 section 3", audit_common.RECOMMENDATION, "unknown", None)
    return report


def bad_github(repo):
    report = audit_common.Report("github")
    report.add("github.x", "10 section 3", audit_common.RULE, "broken", False, "m", "h")
    return report


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        test_audit_files.build_project(self.root)
        test_audit_git.run(self.root, "init", "-b", "main")
        test_audit_git.commit(self.root, "Start", "x.txt")
        test_audit_git.run(self.root, "config", "core.hooksPath", ".githooks")
        self.board = test_audit_board.Fake()

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *args, github=good_github):
        md = [] if "--md" in args else ["--md", os.path.join(self.root, "report.md")]
        return audit.main(["audit.py", self.root, "--repo", "org/proj", *md, *args], github=github, graphql=self.board)

    def test_all_four_audits_run_in_order(self):
        reports = audit.audit(self.root, repo="org/proj", github=good_github, graphql=self.board)
        self.assertEqual([r.area for r in reports], ["files", "git", "github", "board"])

    def test_offline_runs_only_the_local_audits(self):
        reports = audit.audit(self.root, offline=True)
        self.assertEqual([r.area for r in reports], ["files", "git"])

    def test_no_remote_makes_the_github_part_not_checkable(self):
        reports = audit.audit(self.root)
        self.assertEqual([r.area for r in reports], ["files", "git", "github"])
        self.assertEqual(reports[-1].checks[0].result, audit_common.NOT_CHECKABLE)

    def test_summary_keeps_rules_and_recommendations_apart(self):
        reports = audit.audit(self.root, repo="org/proj", github=bad_github, graphql=self.board)
        counts = audit.summary(reports)
        self.assertGreaterEqual(counts["rule"]["fail"], 1)
        self.assertEqual(counts["recommendation"]["fail"], 0)
        self.assertIn("rules:", audit.format_all(reports))
        self.assertIn("recommendations:", audit.format_all(reports))

    def test_exit_code_and_json(self):
        out = os.path.join(self.root, "audit.json")
        self.assertEqual(self.run_main("--json", out), 0)

        with open(out, encoding="utf-8") as f:
            data = json.load(f)

        self.assertEqual([a["area"] for a in data["audits"]], ["files", "git", "github", "board"])
        self.assertEqual(data["summary"]["rule"]["fail"], 0)
        self.assertEqual(self.run_main(github=bad_github), 1)

    def test_markdown_report_lists_every_check_and_the_totals(self):
        out = os.path.join(self.root, "out.md")
        self.assertEqual(self.run_main("--md", out, github=bad_github), 1)

        with open(out, encoding="utf-8") as f:
            text = f.read()

        self.assertIn("# Audit report", text)
        self.assertIn("| Rules |", text)
        self.assertIn("| Recommendations |", text)

        for area in ("Files", "Git", "Github", "Board"):
            self.assertIn("## " + area, text)

        self.assertIn("| PASS | `files.location.CHANGELOG.md` |", text)
        self.assertIn("| FAIL | `github.x` | rule | 10 section 3 | broken | m Fix: h |", text)

    def test_markdown_report_escapes_pipes_and_dates_the_run(self):
        report = audit_common.Report("files")
        report.add("a.b", "01", audit_common.RULE, "x | y", False, "line\nbreak", "")
        now = datetime(2026, 10, 12, 9, 5, tzinfo=timezone.utc)
        text = audit.format_markdown([report], "/p", now)
        self.assertIn("x \\| y", text)
        self.assertIn("line break", text)
        self.assertIn("**Date:** 2026-10-12 09:05 UTC", text)
        self.assertNotIn("\r", text)

    def test_markdown_report_defaults_to_audit_report_md_in_the_current_directory(self):
        here = os.getcwd()
        os.chdir(self.root)

        try:
            self.assertEqual(audit.main(["audit.py", self.root, "--repo", "org/proj"], github=good_github,
                                        graphql=self.board), 0)
        finally:
            os.chdir(here)

        self.assertTrue(os.path.isfile(os.path.join(self.root, "audit-report.md")))

    def test_details_are_bullets_under_failed_checks_only_unless_verbose(self):
        def failing(repo):
            report = audit_common.Report("github")
            report.add("github.x", "10 section 3", audit_common.RULE, "broken", False, "2 bad", "h", ["one", "two"])
            report.add("github.y", "10 section 3", audit_common.RULE, "fine", True, details=["examined a", "examined b"])
            return report

        plain = os.path.join(self.root, "plain.md")
        full = os.path.join(self.root, "full.md")
        self.assertEqual(self.run_main("--md", plain, github=failing), 1)
        self.assertEqual(self.run_main("--md", full, "--verbose", github=failing), 1)

        with open(plain, encoding="utf-8") as f:
            text = f.read()

        self.assertIn("**`github.x`** (fail)\n\n- one\n- two", text)
        self.assertNotIn("examined a", text)

        with open(full, encoding="utf-8") as f:
            text = f.read()

        self.assertIn("**`github.y`** (pass)\n\n- examined a\n- examined b", text)

    def test_verbose_shows_the_details_of_passes_on_the_screen_and_in_json(self):
        report = audit_common.Report("files")
        report.add("a.b", "01", audit_common.RULE, "fine", True, details=["looked at x"])
        report.add("a.c", "01", audit_common.RULE, "bad", False, "m", "h", ["offender 1", "offender 2"])
        plain, verbose = audit.format_all([report]), audit.format_all([report], True)
        self.assertNotIn("looked at x", plain)
        self.assertIn("- offender 1", plain)
        self.assertIn("- offender 2", plain)
        self.assertIn("[PASS] a.b", verbose)
        self.assertIn("- looked at x", verbose)
        self.assertEqual(audit.to_json([report])["audits"][0]["checks"][0]["details"], [])
        self.assertEqual(audit.to_json([report], True)["audits"][0]["checks"][0]["details"], ["looked at x"])
        self.assertEqual(audit.to_json([report])["audits"][0]["checks"][1]["details"], ["offender 1", "offender 2"])

    def test_since_is_passed_on_and_written_in_the_reports(self):
        md = os.path.join(self.root, "since.md")
        js = os.path.join(self.root, "since.json")
        self.assertEqual(self.run_main("--md", md, "--json", js, "--since", "2099-01-01"), 0)

        with open(md, encoding="utf-8") as f:
            self.assertIn("**History judged from:** 2099-01-01", f.read())

        with open(js, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["since"], "2099-01-01")

    def test_a_bad_since_is_a_bad_argument(self):
        self.assertEqual(self.run_main("--since", "not-a-commit"), 2)
        self.assertEqual(audit.main(["audit.py", self.root, "--since"]), 2)

    def write_baseline(self, data, name=None):
        path = name or os.path.join(self.root, ".github", "audit-baseline.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            f.write(data if isinstance(data, str) else json.dumps(data))

        return path

    def test_the_baseline_of_the_project_turns_an_accepted_failure_into_accepted(self):
        self.write_baseline({"accepted": [{"check": "github.x", "reason": "no plan", "date": "2026-10-12",
                                           "agreed_by": "the owner"}]})
        md = os.path.join(self.root, "b.md")
        self.assertEqual(self.run_main("--md", md, github=bad_github), 0)

        with open(md, encoding="utf-8") as f:
            text = f.read()

        self.assertIn("| ACCEPTED | `github.x` |", text)
        self.assertIn("accepted: no plan (2026-10-12, agreed by the owner)", text)
        self.assertIn("| Rules | ", text)
        self.assertIn("Accepted", text)

    def test_the_baseline_option_names_another_file(self):
        other = self.write_baseline({"accepted": [{"check": "github.x", "reason": "r", "date": "d",
                                                   "agreed_by": "a"}]}, os.path.join(self.root, "elsewhere.json"))
        self.assertEqual(self.run_main("--baseline", other, github=bad_github), 0)
        self.assertEqual(self.run_main(github=bad_github), 1)

    def test_a_stale_entry_is_reported_but_never_fails_the_run(self):
        self.write_baseline({"accepted": [{"check": "files.location.doc", "reason": "r", "date": "d", "agreed_by": "a"}]})
        reports = []
        original = audit.audit

        def keep(*args, **kwargs):
            reports.extend(original(*args, **kwargs))
            return reports

        audit.audit = keep

        try:
            self.assertEqual(self.run_main(), 0)
        finally:
            audit.audit = original

        self.assertEqual(reports[-1].area, "baseline")
        self.assertEqual(reports[-1].checks[0].result, audit_common.FAIL)

    def test_a_bad_baseline_is_a_bad_argument(self):
        self.write_baseline("not json")
        self.assertEqual(self.run_main(), 2)
        self.assertEqual(self.run_main("--baseline", os.path.join(self.root, "missing.json")), 2)

    def test_the_plan_is_on_the_screen_in_the_markdown_and_in_the_json(self):
        md = os.path.join(self.root, "plan.md")
        js = os.path.join(self.root, "plan.json")
        os.remove(os.path.join(self.root, ".gitignore"))
        self.assertEqual(self.run_main("--md", md, "--json", js), 0)

        with open(md, encoding="utf-8") as f:
            text = f.read()

        self.assertIn("## Adoption plan", text)
        self.assertIn("### Stage 2: the adoption branch, files and automation", text)
        self.assertIn("| `files.location.gitignore` | recommendation | Fix | Dev | Yes |", text)

        with open(js, encoding="utf-8") as f:
            plan = json.load(f)["plan"]

        self.assertEqual(plan[0]["stage"], 2)
        self.assertEqual(plan[0]["findings"][0]["id"], "files.location.gitignore")

    def test_a_recommendation_alone_does_not_fail_the_run(self):
        os.remove(os.path.join(self.root, "README.md"))
        self.assertEqual(self.run_main(), 0)

    def test_bad_arguments(self):
        self.assertEqual(audit.main(["audit.py"]), 2)
        self.assertEqual(audit.main(["audit.py", self.root, "--board", "x"]), 2)
        self.assertEqual(audit.main(["audit.py", os.path.join(self.root, "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
