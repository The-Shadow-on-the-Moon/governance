import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_common  # noqa: E402
import audit_git  # noqa: E402


def run(root, *args):
    subprocess.run(["git", "-c", "user.name=T", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false", *args],
                   cwd=root, check=True, capture_output=True, text=True)


def commit(root, message, name="f.txt", text="x"):
    with open(os.path.join(root, name), "a", encoding="utf-8") as f:
        f.write(text + "\n")

    run(root, "add", "-A")
    run(root, "commit", "-m", message)


def failed(report):
    return {c.id for c in report.checks if c.result == audit_common.FAIL}


class AuditGitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        run(self.root, "init", "-b", "main")
        commit(self.root, "Start", "CHANGELOG.md", "## V1.0.0 — 2026-10-01 09:00 UTC")

    def tearDown(self):
        self.tmp.cleanup()

    def merge_branch(self, name="work-a"):
        run(self.root, "switch", "-c", name)
        commit(self.root, "Work on " + name, name + ".txt")
        run(self.root, "switch", "main")
        run(self.root, "merge", "--no-ff", "-m", "Merge " + name, name)

    def test_clean_history_passes(self):
        self.merge_branch()
        run(self.root, "tag", "released/V1.0.0")
        self.assertEqual(failed(audit_git.audit(self.root)), set())

    def test_not_a_repository(self):
        with tempfile.TemporaryDirectory() as empty:
            report = audit_git.audit(empty)

        self.assertEqual(failed(report), {"git.repository"})

    def test_branch_names(self):
        for name in ("Bad_Name", "feature/x", "develop", "ok-name"):
            run(self.root, "branch", name)

        bad = failed(audit_git.audit(self.root))
        self.assertTrue({"git.branch.kebab-case", "git.branch.no-slash", "git.branch.single-line"} <= bad)

    def test_hotfix_branch_name_is_accepted(self):
        run(self.root, "branch", "hotfix-v1-0-0-fix-timeout")
        self.assertNotIn("git.branch.kebab-case", failed(audit_git.audit(self.root)))

    def test_tag_names(self):
        run(self.root, "tag", "v1.0")
        self.assertIn("git.tag.names", failed(audit_git.audit(self.root)))

    def test_padded_version_tag(self):
        run(self.root, "tag", "released/V01.0.0")
        self.assertIn("git.tag.names", failed(audit_git.audit(self.root)))

    def test_valid_tags(self):
        for tag in ("released/V1.0.0", "released/V1.0.0-HF1", "archived/2026-10-05_some-branch_why",
                    "test/abandoned/2026-10-06_dummy-x"):
            run(self.root, "tag", tag)

        self.assertNotIn("git.tag.names", failed(audit_git.audit(self.root)))

    def test_release_tag_off_main(self):
        run(self.root, "switch", "-c", "side")
        commit(self.root, "Side")
        run(self.root, "tag", "released/V1.0.0")
        run(self.root, "switch", "main")
        self.assertIn("git.tag.released-on-main", failed(audit_git.audit(self.root)))

    def test_release_tag_without_changelog_version(self):
        run(self.root, "tag", "released/V2.0.0")
        self.assertIn("git.tag.released-in-changelog", failed(audit_git.audit(self.root)))

    def test_direct_commit_on_main(self):
        self.merge_branch()
        commit(self.root, "Straight onto main")
        self.assertIn("git.history.merge-commits", failed(audit_git.audit(self.root)))

    def test_automation_commits_on_main_are_allowed(self):
        self.merge_branch()
        commit(self.root, "Finalize V1.0.1")
        self.assertNotIn("git.history.merge-commits", failed(audit_git.audit(self.root)))

    def test_message_rules(self):
        commit(self.root, "feat: add thing")
        run(self.root, "commit", "--amend", "-m", "feat: add thing\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
        bad = failed(audit_git.audit(self.root))
        self.assertIn("git.message.no-type-prefix", bad)
        self.assertIn("git.message.no-assistant-attribution", bad)

    def test_a_human_co_author_is_fine(self):
        commit(self.root, "Pair work")
        run(self.root, "commit", "--amend", "-m", "Pair work\n\nCo-Authored-By: Pablo <p@example.com>")
        self.assertNotIn("git.message.no-assistant-attribution", failed(audit_git.audit(self.root)))

    def test_main_exit_codes(self):
        self.assertEqual(audit_git.main(["audit_git.py"]), 2)
        run(self.root, "branch", "Bad_Name")
        self.assertEqual(audit_git.main(["audit_git.py", self.root]), 1)


if __name__ == "__main__":
    unittest.main()
