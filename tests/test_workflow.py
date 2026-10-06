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

    def test_no_step_name_has_a_colon_followed_by_a_space(self):
        # An unquoted "key: value" inside a name makes the whole file invalid YAML (GitHub reports a workflow file issue).
        for number, line in enumerate(workflow().split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("- name:") or stripped.startswith("name:"):
                value = stripped.split("name:", 1)[1].strip()
                if not value.startswith(("'", '"')):
                    self.assertNotIn(": ", value, f"line {number}")

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
        self.assertLess(main.index("bypass.py stale"), main.index("dates.py"))
        self.assertLess(main.index("dates.py"), main.index("watch.py"))
        self.assertLess(main.index("watch.py"), main.index("field_rules.py"))

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

    def test_the_daily_job_is_scheduled_and_can_be_started_by_hand(self):
        text = workflow()
        self.assertRegex(text, r"schedule:\n    - cron: '\d+ \d+ \* \* \*'")
        self.assertIn("mode:", text)
        self.assertIn("- finalize", text)
        self.assertIn("- daily", text)
        daily = text[text.index("  daily:"):text.index("  release:")]
        self.assertIn("github.event_name == 'schedule'", daily)
        self.assertIn("inputs.mode == 'daily'", daily)

    def test_the_daily_job_runs_the_checks_in_order_and_never_commits(self):
        text = workflow()
        daily = text[text.index("  daily:"):text.index("  release:")]
        order = ["preflight.py", "implemented.py", "dates.py", "watch.py", "field_rules.py"]
        positions = [daily.index(name) for name in order]
        self.assertEqual(positions, sorted(positions))
        for forbidden in ("git push", "git commit", "finalize.py", "bypass.py"):
            self.assertNotIn(forbidden, daily)
        self.assertIn("--dry-run", daily)

    def test_the_finalize_job_only_runs_for_its_own_mode(self):
        text = workflow()
        main = text[text.index("  main:"):text.index("  daily:")]
        self.assertIn("inputs.mode == 'finalize'", main)

    def jobs(self):
        text = workflow()
        return (text[text.index("  release:"):text.index("  hotfix:")],
                text[text.index("  hotfix:"):text.index("  retire:")],
                text[text.index("  retire:"):])

    def test_release_hotfix_and_retire_are_modes_of_a_manual_start(self):
        text = workflow()
        for mode in ("release", "hotfix", "retire"):
            self.assertIn(f"          - {mode}", text)
        release, hotfix, retire = self.jobs()
        for job, mode in ((release, "release"), (hotfix, "hotfix"), (retire, "retire")):
            self.assertIn(f"github.event_name == 'workflow_dispatch' && inputs.mode == '{mode}'", job)
            self.assertLess(job.index("preflight.py"), job.index(f"{mode}.py"))
            self.assertIn("--dry-run", job)
            self.assertIn("DRY_RUN: ${{ inputs.dry_run }}", job)

    def test_the_inputs_of_the_three_steps_reach_their_scripts(self):
        release, hotfix, retire = self.jobs()
        self.assertIn("VERSION: ${{ inputs.version }}", release)
        self.assertIn("VERSION: ${{ inputs.version }}", hotfix)
        self.assertIn("BRANCH: ${{ github.ref_name }}", hotfix)  # a hotfix is finished from its own branch
        self.assertIn("github.ref_type == 'branch'", hotfix)
        for name in ("BRANCH: ${{ inputs.branch }}", "OUTCOME: ${{ inputs.outcome }}", "CONFIRM: ${{ inputs.confirm }}",
                     "COMMENT: ${{ inputs.comment }}"):
            self.assertIn(name, retire)

    def test_release_and_retire_use_the_ref_they_were_started_from_and_the_hotfix_its_branch_with_tags(self):
        release, hotfix, retire = self.jobs()
        for job in (release, retire):
            self.assertNotIn("ref:", job.split("steps:")[1])  # the default checkout: the ref of the manual start
        self.assertIn("ref: ${{ github.ref_name }}", hotfix)
        self.assertIn("fetch-tags: true", hotfix)
        for job in (release, hotfix, retire):
            self.assertIn("fetch-depth: 0", job)

    def test_only_the_hotfix_job_makes_a_commit_and_the_others_never_push_with_git(self):
        release, hotfix, retire = self.jobs()
        self.assertIn("git config user.name", hotfix)
        for job in (release, retire):
            self.assertNotIn("git config", job)
            self.assertNotIn("git push", job)

    def test_the_default_manual_start_is_still_a_dry_run_of_finalize(self):
        text = workflow()
        self.assertRegex(text, r"mode:\n(?:.*\n)*?\s+default: finalize")

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
