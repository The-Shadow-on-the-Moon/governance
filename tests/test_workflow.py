import os
import re
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import bypass  # noqa: E402
from versions import Version  # noqa: E402

PATH = os.path.join(ROOT, ".github", "workflows", "versioning.yml")


def workflow():
    with open(PATH, encoding="utf-8") as handle:
        return handle.read()


class WorkflowTests(unittest.TestCase):
    """Structure checks. The workflow itself is proven by a real run (see the level-1 proof)."""

    def test_no_tabs(self):
        for number, line in enumerate(workflow().split("\n"), 1):
            self.assertNotIn("\t", line, f"tab on line {number}")

    def test_triggers(self):
        text = workflow()
        for trigger in ("pull_request:", "push:", "workflow_dispatch:", "- '**'"):
            self.assertIn(trigger, text)

    def test_declares_its_own_permissions(self):
        text = workflow()
        self.assertRegex(text, r"(?m)^permissions:\n  contents: write\n  issues: write\n  pull-requests: write\n")

    def test_every_script_it_runs_exists(self):
        scripts = re.findall(r"python3 (\.github/scripts/\w+\.py)", workflow())
        self.assertTrue(scripts)
        for script in scripts:
            self.assertTrue(os.path.exists(os.path.join(ROOT, script)), script)

    def test_the_preflight_runs_before_the_other_steps(self):
        text = workflow()
        main = text[text.index("\n  main:"):]
        self.assertLess(main.index("preflight.py"), main.index("bypass.py"))
        self.assertLess(main.index("bypass.py"), main.index("finalize.py"))
        self.assertLess(main.index("finalize.py"), main.index("bypass.py stale"))

    def test_uses_the_project_token_and_skips_its_own_commits(self):
        text = workflow()
        self.assertIn("secrets.PROJECT_TOKEN", text)
        self.assertIn("startsWith(github.event.head_commit.message, 'Finalize ')", text)
        self.assertIn("startsWith(github.event.head_commit.message, 'Flag bypass')", text)

    def test_the_commit_messages_it_skips_are_the_ones_the_scripts_write(self):
        import finalize
        import inspect
        self.assertIn('f"Finalize {version}', inspect.getsource(finalize.commit_heading))
        self.assertIn('f"Flag bypass (Alert', inspect.getsource(bypass.commit_entry))

    def test_branch_pushes_run_the_push_step_after_the_preflight(self):
        text = workflow()
        branch = text[text.index("  branch:"):text.index("  main:")]
        self.assertLess(branch.index("preflight.py"), branch.index("skipped_hooks.py"))
        self.assertLess(branch.index("skipped_hooks.py"), branch.index("push_step.py"))
        self.assertIn("AFTER_SHA=$(git rev-parse HEAD)", branch)  # the push step reads the repaired changelog
        self.assertIn("github.ref != 'refs/heads/main'", branch)
        self.assertIn("!github.event.deleted", branch)
        self.assertIn("- '**'", text)

    def test_the_main_job_only_runs_for_main(self):
        text = workflow()
        main = text[text.index("  main:"):]
        self.assertIn("github.ref == 'refs/heads/main'", main)

    def test_manual_runs_are_dry_runs_by_default(self):
        self.assertRegex(workflow(), r"dry_run:\n(?:.*\n)*?\s+default: true")


class FakeRepo:
    repo = "owner/repo"

    def __init__(self, planned):
        self.planned, self.created = planned, []

    def repo_path(self, path):
        return path

    def request(self, method, path, body=None):
        return self.planned

    def create_issue(self, title, body, issue_type=None, labels=(), assignees=()):
        self.created.append(title)
        return {"number": 1, "node_id": "N"}


class StaleCommandTests(unittest.TestCase):
    def run_command(self, changelog_text, planned):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "CHANGELOG.md"), "w", encoding="utf-8") as handle:
                handle.write(changelog_text)
            repo = FakeRepo(planned)
            return bypass.stale_command(folder, repo, None, None), repo

    def test_raises_the_alert_for_the_topmost_version(self):
        _, repo = self.run_command("# Changelog\n\n## V0.2.0 — 2026-10-05 21:24 UTC\n", [{"title": "Version 0.1.5", "number": 9}])
        self.assertEqual(repo.created, ["Stale planned Version tickets after V0.2.0"])

    def test_nothing_planned(self):
        _, repo = self.run_command("# Changelog\n\n## V0.2.0 — 2026-10-05 21:24 UTC\n", [])
        self.assertEqual(repo.created, [])

    def test_no_finalized_version(self):
        run, repo = self.run_command("# Changelog\n", [])
        self.assertEqual(run.log, ["no finalized version"])


if __name__ == "__main__":
    unittest.main()
