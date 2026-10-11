import json
import os
import sys
import tempfile
import unittest

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
        return audit.main(["audit.py", self.root, "--repo", "org/proj", *args], github=github, graphql=self.board)

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

    def test_a_recommendation_alone_does_not_fail_the_run(self):
        os.remove(os.path.join(self.root, "README.md"))
        self.assertEqual(self.run_main(), 0)

    def test_bad_arguments(self):
        self.assertEqual(audit.main(["audit.py"]), 2)
        self.assertEqual(audit.main(["audit.py", self.root, "--board", "x"]), 2)
        self.assertEqual(audit.main(["audit.py", os.path.join(self.root, "missing")]), 2)


if __name__ == "__main__":
    unittest.main()
