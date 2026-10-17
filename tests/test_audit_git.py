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


def commit_at(root, message, date, name="f.txt", text="x", merge=None, committed=None):
    """A commit (or, with `merge`, a no-fast-forward merge of that branch) authored at `date` and committed at `committed`
    (the same by default; later when the commit was rebased or cherry-picked)."""
    env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=committed or date)
    base = ["git", "-c", "user.name=T", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false"]

    if merge:
        subprocess.run([*base, "merge", "--no-ff", "-m", message, merge], cwd=root, check=True, capture_output=True, text=True, env=env)
        return

    with open(os.path.join(root, name), "a", encoding="utf-8") as f:
        f.write(text + "\n")

    subprocess.run([*base, "add", "-A"], cwd=root, check=True, capture_output=True, text=True, env=env)
    subprocess.run([*base, "commit", "-m", message], cwd=root, check=True, capture_output=True, text=True, env=env)


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

    def test_every_direct_commit_is_listed_with_its_full_hash_and_subject(self):
        self.merge_branch()

        for n in range(7):
            commit(self.root, "Direct %d" % n)

        check = next(c for c in audit_git.audit(self.root).checks if c.id == "git.history.merge-commits")
        self.assertEqual(check.message, "7 commit(s) on main's first-parent line are not merges")
        self.assertEqual(len(check.details), 7)
        self.assertTrue(all(len(d.split(" ", 1)[0]) == 40 for d in check.details))
        self.assertIn("Direct 0", check.details[-1])
        self.assertIn("Direct 6", check.details[0])

    def test_every_prefixed_subject_is_listed(self):
        for n in range(6):
            commit(self.root, "fix: thing %d" % n)

        check = next(c for c in audit_git.audit(self.root).checks if c.id == "git.message.no-type-prefix")
        self.assertEqual(len(check.details), 6)

    def test_a_passed_check_says_what_was_examined(self):
        self.merge_branch()
        check = next(c for c in audit_git.audit(self.root).checks if c.id == "git.message.no-type-prefix")
        self.assertEqual(check.result, audit_common.PASS)
        self.assertEqual(check.details, ["3 commit(s) on all branches examined"])

    def old_history_then_a_cutover(self):
        """A direct commit with a prefix and a stray tag before the cut-over; returns the cut-over commit."""
        commit(self.root, "fix: old direct commit")
        run(self.root, "tag", "v1.0")
        cut = audit_git.git(self.root, "rev-parse", "HEAD")[1]
        self.merge_branch()
        return cut

    def test_the_whole_history_is_judged_without_since(self):
        self.old_history_then_a_cutover()
        bad = failed(audit_git.audit(self.root))
        self.assertTrue({"git.history.merge-commits", "git.message.no-type-prefix", "git.tag.names"} <= bad)

    def test_since_a_commit_leaves_the_older_history_out(self):
        cut = self.old_history_then_a_cutover()
        report = audit_git.audit(self.root, cut)
        self.assertEqual(failed(report), set())
        check = next(c for c in report.checks if c.id == "git.history.merge-commits")
        self.assertIn("judged from " + cut, check.details[-1])

    def test_since_a_commit_still_judges_what_comes_after(self):
        cut = self.old_history_then_a_cutover()
        commit(self.root, "fix: new direct commit")
        run(self.root, "tag", "v2.0")
        bad = failed(audit_git.audit(self.root, cut))
        self.assertTrue({"git.history.merge-commits", "git.message.no-type-prefix", "git.tag.names"} <= bad)

    def test_since_a_date(self):
        self.old_history_then_a_cutover()
        self.assertEqual(failed(audit_git.audit(self.root, "2099-01-01")), set())
        self.assertIn("git.history.merge-commits", failed(audit_git.audit(self.root, "2000-01-01 00:00")))

    def old_branch_merged_after_the_cutover(self):
        """A branch with an old-style commit authored in January (committed in July, as after a rebase), a cut-over in June, the branch merged in July and a
        direct old-style commit in August; returns the cut-over commit."""
        run(self.root, "switch", "-c", "old-work")
        commit_at(self.root, "fix: old branch work", "2026-01-10T10:00:00+0000", "old.txt", committed="2026-07-15T10:00:00+0000")
        run(self.root, "switch", "main")
        commit_at(self.root, "Adopt the standard", "2026-06-01T10:00:00+0000", "adopt.txt")
        cut = audit_git.git(self.root, "rev-parse", "HEAD")[1]
        commit_at(self.root, "Merge old-work", "2026-07-01T10:00:00+0000", merge="old-work")
        commit_at(self.root, "fix: new direct commit", "2026-08-01T10:00:00+0000", "new.txt")
        return cut

    def prefixed(self, report):
        check = next(c for c in report.checks if c.id == "git.message.no-type-prefix")
        return " ".join(check.details)

    def test_work_made_before_the_cutover_is_history_wherever_it_lands(self):
        cut = self.old_branch_merged_after_the_cutover()
        whole = self.prefixed(audit_git.audit(self.root))
        self.assertIn("old branch work", whole)
        scoped = self.prefixed(audit_git.audit(self.root, cut))
        self.assertNotIn("old branch work", scoped)
        self.assertIn("new direct commit", scoped)

    def test_the_merge_that_lands_old_work_is_judged_like_any_other(self):
        cut = self.old_branch_merged_after_the_cutover()
        report = audit_git.audit(self.root, cut)
        check = next(c for c in report.checks if c.id == "git.history.merge-commits")
        self.assertEqual(check.message, "1 commit(s) on main's first-parent line are not merges")
        self.assertIn("new direct commit", " ".join(check.details))

    def test_a_date_judges_by_the_author_date(self):
        self.old_branch_merged_after_the_cutover()
        scoped = self.prefixed(audit_git.audit(self.root, "2026-06-01"))
        self.assertNotIn("old branch work", scoped)
        self.assertIn("new direct commit", scoped)

    def test_the_cutover_commit_and_what_it_reaches_are_history(self):
        cut = self.old_branch_merged_after_the_cutover()
        scoped = self.prefixed(audit_git.audit(self.root, cut))
        self.assertNotIn("Adopt the standard", scoped)
        self.assertNotIn("Start", scoped)

    def test_since_that_is_neither_a_date_nor_a_commit(self):
        with self.assertRaises(ValueError):
            audit_git.audit(self.root, "not-a-commit")

        self.assertEqual(audit_git.main(["audit_git.py", self.root, "--since", "not-a-commit"]), 2)
        self.assertEqual(audit_git.main(["audit_git.py", self.root, "--since"]), 2)

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
