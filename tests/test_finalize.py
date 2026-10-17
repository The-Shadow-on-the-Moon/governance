import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import finalize  # noqa: E402
import preflight  # noqa: E402
import versions  # noqa: E402
from github_api import GitHubError  # noqa: E402
from versions import Version  # noqa: E402

NOW = datetime(2026, 10, 6, 10, 0, 0, tzinfo=timezone.utc)

CHANGELOG = """# Changelog

## WIP-Version{marker}
### Build 20261006090000 (branch csv-export)
#### #201 — Add CSV export
- export: added.
#### #205 — Fix the totals
- totals: fixed.
### Build 20261006080000 (branch csv-export)
#### #201 — Add CSV export
- export: first draft.

## V0.2.0 — 2026-10-05 21:24 UTC
### Build 20261005211638 (branch other)
#### #4 — Earlier work
- done.
"""

FIRST = """# Changelog

## WIP-Version
### Build 20261005181657 (branch initial-structure)
#### #1 — Initial structure
- everything.
"""


class FakeRepo:
    repo = "owner/repo"

    def __init__(self, types, existing=()):
        self.types, self.existing, self.calls = types, list(existing), []

    def repo_path(self, path):
        return f"/repos/{self.repo}{path}"

    def issue_type(self, number):
        return self.types[number]

    def request(self, method, path, body=None):
        self.calls.append(("request", method, path, body))
        return self.existing if method == "GET" else {}

    def create_issue(self, title, body, issue_type=None, labels=(), assignees=()):
        self.calls.append(("create", title, body, issue_type))
        return {"number": 50, "node_id": "N50"}

    def add_sub_issue(self, parent, child):
        self.calls.append(("sub", parent, child))

    def close_issue(self, number, reason="completed"):
        self.calls.append(("close", number))

    def of(self, kind):
        return [c for c in self.calls if c[0] == kind]


def board():
    fields = {name: {"id": f"F-{name}", "type": kind, "options": {v: f"{name}-{v}" for v in (values or [])}}
              for name, (kind, values) in preflight.REQUIRED_FIELDS.items()}
    return preflight.Board("P7", 7, "Governance", fields)


class FakeProject:
    repo = "owner/repo"

    def __init__(self, items=None, fail=False):
        self.items, self.fail, self.sets, self.added = items or {}, fail, [], []

    def graphql(self, query, variables=None):
        if self.fail:
            raise GitHubError(502, "Bad gateway")
        if "pageInfo" in query:  # the sweep of Implemented tickets: none waiting
            return {"node": {"items": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": []}}}
        number = variables["num"]
        item = self.items.get(number, {"status": "ToDo"})
        node = None
        if item is not None:
            node = {"id": f"I{number}", "project": {"id": "P7"},
                    "status": {"name": item.get("status")} if item.get("status") else None,
                    "delivery": {"name": item["delivery"]} if item.get("delivery") else None,
                    "version": {"text": item["version"]} if item.get("version") else None,
                    "build": {"text": item["build"]} if item.get("build") else None,
                    "number": {"number": item["number"]} if item.get("number") else None}
        return {"repository": {"issue": {"id": f"N{number}", "title": "t", "projectItems": {"nodes": [node] if node else []}}}}

    def add_to_project(self, project_id, content_id):
        self.added.append(content_id)
        return f"I-{content_id}"

    def set_project_field(self, project_id, item_id, field_id, value):
        self.sets.append((item_id, field_id, value))


class Repo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.remote = os.path.join(self.tmp.name, "remote.git")
        self.dir = os.path.join(self.tmp.name, "work")
        os.makedirs(self.dir)
        subprocess.run(["git", "init", "-q", "--bare", self.remote], check=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Tester")
        self.git("config", "user.email", "t@example.com")
        self.git("remote", "add", "origin", self.remote)

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.dir, check=True, capture_output=True, text=True, encoding="utf-8").stdout

    def write(self, text):
        with open(os.path.join(self.dir, "CHANGELOG.md"), "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "merge")
        self.git("push", "-q", "-u", "origin", "main")

    def changelog(self):
        with open(os.path.join(self.dir, "CHANGELOG.md"), encoding="utf-8") as handle:
            return handle.read()


class FinalizeTests(Repo):
    TYPES = {201: "Feature", 205: "Bug", 4: "Task"}

    def test_the_whole_step(self):
        self.write(CHANGELOG.format(marker=""))
        repo, project = FakeRepo(self.TYPES), FakeProject({201: {"status": "InProgress"}, 205: {"status": "Completed"}})
        run = finalize.finalize(self.dir, repo, project, board(), NOW)
        self.assertIn("## V0.3.0 — 2026-10-06 10:00 UTC", self.changelog())
        self.assertNotIn("WIP-Version", self.changelog())
        self.assertEqual(self.git("log", "-1", "--format=%s"), "Finalize V0.3.0\n")
        self.assertEqual(self.git("rev-parse", "HEAD"), subprocess.run(
            ["git", "rev-parse", "main"], cwd=self.remote, capture_output=True, text=True).stdout)
        sets = {(item, field): value for item, field, value in project.sets}
        self.assertEqual(sets[("I201", "F-Version")], {"text": "V000.003.000"})
        self.assertEqual(sets[("I201", "F-Build")], {"text": "20261006090000"})
        self.assertNotIn(("I201", "F-Version#"), sets)
        self.assertEqual(sets[("I201", "F-Delivery")], {"singleSelectOptionId": "Delivery-Merged"})
        self.assertNotIn(("I201", "F-Status"), sets)  # already InProgress
        self.assertNotIn(("I205", "F-Status"), sets)  # a Completed ticket stays Completed
        self.assertEqual(repo.calls, [])  # no Version ticket, no sub-issue, nothing closed
        self.assertIn("V0.3.0: bump sub, from the Type of #201 (Feature)", run.log)

    def test_todo_and_ondeck_advance_to_inprogress(self):
        self.write(CHANGELOG.format(marker=""))
        project = FakeProject({201: {"status": "OnDeck"}, 205: {"status": "ToDo"}})
        finalize.finalize(self.dir, FakeRepo(self.TYPES), project, board(), NOW)
        advanced = [item for item, field, value in project.sets if field == "F-Status"]
        self.assertEqual(sorted(advanced), ["I201", "I205"])

    def test_a_ticket_not_on_the_board_is_added(self):
        self.write(CHANGELOG.format(marker=""))
        project = FakeProject({201: None, 205: {"status": "Review"}})
        finalize.finalize(self.dir, FakeRepo(self.TYPES), project, board(), NOW)
        self.assertEqual(project.added, ["N201"])

    def test_a_marker_forces_the_bump(self):
        self.write(CHANGELOG.format(marker=" +m"))
        run = finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        self.assertIn("## V0.2.1", self.changelog())
        self.assertTrue(any("bump mod, forced with the `+m` marker" in line for line in run.log))

    def test_the_first_version(self):
        self.write(FIRST)
        run = finalize.finalize(self.dir, FakeRepo({1: "Task"}), FakeProject(), board(), NOW)
        self.assertIn("## V0.1.0 — 2026-10-06 10:00 UTC", self.changelog())
        self.assertTrue(any("the first version is V0.1.0" in line for line in run.log))

    def test_dry_run_changes_nothing(self):
        self.write(CHANGELOG.format(marker=""))
        head = self.git("rev-parse", "HEAD")
        repo, project = FakeRepo(self.TYPES), FakeProject()
        run = finalize.finalize(self.dir, repo, project, board(), NOW, dry_run=True)
        self.assertIn("WIP-Version", self.changelog())
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(project.sets, [])
        self.assertEqual(repo.calls, [])
        self.assertTrue(any("V0.3.0" in line for line in run.log))

    def write_manifest(self, standard):
        import check_manifest
        os.makedirs(os.path.join(self.dir, ".github"), exist_ok=True)
        check_manifest.write(self.dir, {"standard": standard, "files": {}})
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "manifest")
        self.git("push", "-q", "origin", "main")

    def manifest_standard(self):
        import check_manifest
        return check_manifest.load(os.path.join(self.dir, check_manifest.MANIFEST))["standard"]

    def test_the_manifest_placeholder_becomes_the_version_in_the_same_commit(self):
        self.write(CHANGELOG.format(marker=""))
        self.write_manifest("WIP-Version")
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        self.assertEqual(self.manifest_standard(), "V0.3.0")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "Finalize V0.3.0\n")
        files = self.git("show", "--name-only", "--format=", "HEAD").split()
        self.assertEqual(sorted(files), [".github/automation-manifest.json", "CHANGELOG.md"])
        self.assertIn("Sets the standard of the automation manifest to V0.3.0", self.git("log", "-1", "--format=%b"))

    def test_a_manifest_with_a_real_version_is_left_alone(self):
        self.write(CHANGELOG.format(marker=""))
        self.write_manifest("V0.2.0")
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        self.assertEqual(self.manifest_standard(), "V0.2.0")
        self.assertEqual(self.git("show", "--name-only", "--format=", "HEAD").split(), ["CHANGELOG.md"])

    def test_a_dry_run_leaves_the_placeholder_and_says_so(self):
        self.write(CHANGELOG.format(marker=""))
        self.write_manifest("WIP-Version")
        run = finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW, dry_run=True)
        self.assertEqual(self.manifest_standard(), "WIP-Version")
        self.assertTrue(any("set the manifest standard to V0.3.0" in line for line in run.log))

    def test_running_again_skips_what_is_done(self):
        self.write(CHANGELOG.format(marker=""))
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        done = {201: {"status": "InProgress", "delivery": "Merged", "version": "V000.003.000", "build": "20261006090000"},
                205: {"status": "Completed", "delivery": "Merged", "version": "V000.003.000", "build": "20261006090000"}}
        repo, project = FakeRepo(self.TYPES), FakeProject(done)
        head = self.git("rev-parse", "HEAD")
        run = finalize.finalize(self.dir, repo, project, board(), NOW)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(project.sets, [])
        self.assertEqual(repo.calls, [])
        self.assertIn("no open WIP-Version heading: re-checking V0.3.0", run.log)

    def test_a_run_after_a_partial_one_completes_what_is_missing(self):
        self.write(CHANGELOG.format(marker=""))
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(fail=True), board(), NOW)  # the heading, no board update
        done = {201: {"status": "InProgress", "delivery": "Merged", "version": "V000.003.000", "build": "20261006090000"}}
        project = FakeProject(done)
        finalize.finalize(self.dir, FakeRepo(self.TYPES), project, board(), NOW)
        touched = {(item, field) for item, field, value in project.sets}
        self.assertNotIn(("I201", "F-Version"), touched)  # already right
        self.assertIn(("I205", "F-Version"), touched)  # was missed by the first run
        self.assertIn(("I205", "F-Delivery"), touched)

    def test_a_version_ticket_left_from_before_is_not_touched(self):
        self.write(CHANGELOG.format(marker=""))
        existing = [{"title": "Version 000.003.000", "state": "open", "number": 33, "node_id": "N33"}]
        repo = FakeRepo(self.TYPES, existing)
        finalize.finalize(self.dir, repo, FakeProject(), board(), NOW)
        self.assertEqual(repo.calls, [])

    def test_a_board_error_does_not_stop_the_version(self):
        self.write(CHANGELOG.format(marker=""))
        repo = FakeRepo(self.TYPES)
        run = finalize.finalize(self.dir, repo, FakeProject(fail=True), board(), NOW)
        self.assertIn("## V0.3.0", self.changelog())
        self.assertTrue(any("board update skipped" in line for line in run.log))
        self.assertEqual(repo.calls, [])

    def test_no_board_skips_the_board_steps(self):
        self.write(CHANGELOG.format(marker=""))
        run = finalize.finalize(self.dir, FakeRepo(self.TYPES), None, None, NOW)
        self.assertTrue(any("board steps skipped" in line for line in run.log))
        self.assertIn("## V0.3.0", self.changelog())

    def test_a_malformed_changelog_stops_before_any_change(self):
        self.write(CHANGELOG.format(marker=" soon"))
        repo = FakeRepo(self.TYPES)
        with self.assertRaises(Exception):
            finalize.finalize(self.dir, repo, FakeProject(), board(), NOW)
        self.assertEqual(repo.calls, [])

    def test_the_push_works_without_an_upstream_branch(self):
        self.write(CHANGELOG.format(marker=""))
        self.git("branch", "--unset-upstream")
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        remote_head = subprocess.run(["git", "log", "-1", "--format=%s", "main"], cwd=self.remote, capture_output=True, text=True).stdout
        self.assertEqual(remote_head, "Finalize V0.3.0\n")

    def test_checking_a_finalized_version_again_gives_the_real_bump(self):
        self.write(CHANGELOG.format(marker=""))
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        run = finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW)
        self.assertIn("V0.3.0: bump sub, from V0.2.0 to V0.3.0", run.log)

    def test_recorded_bump_of_the_first_version(self):
        import changelog
        sections = changelog.parse("# Changelog\n\n## V0.1.0 — 2026-10-05 18:22 UTC\n")
        self.assertEqual(finalize.recorded_bump(sections), "none, because it is the first version")

    def test_no_push_leaves_the_commit_local(self):
        self.write(CHANGELOG.format(marker=""))
        finalize.finalize(self.dir, FakeRepo(self.TYPES), FakeProject(), board(), NOW, push=False)
        remote_head = subprocess.run(["git", "log", "-1", "--format=%s", "main"], cwd=self.remote, capture_output=True, text=True).stdout
        self.assertEqual(remote_head, "merge\n")


class HelperTests(unittest.TestCase):
    def test_bump_reasons(self):
        self.assertEqual(finalize.bump_reason({1: "Task"}, "", False), "mod, from the ticket Types (no Feature or Enhancement)")
        self.assertEqual(finalize.bump_reason({1: "Task"}, "+s", False), "sub, forced with the `+s` marker")
        self.assertEqual(finalize.bump_reason({1: "Enhancement"}, "", False), "sub, from the Type of #1 (Enhancement)")

    def test_nothing_to_finalize(self):
        with tempfile.TemporaryDirectory() as folder:
            with open(os.path.join(folder, "CHANGELOG.md"), "w", encoding="utf-8") as handle:
                handle.write("# Changelog\n")
            run = finalize.finalize(folder, FakeRepo({}), None, None, NOW)
            self.assertEqual(run.log, ["nothing to finalize"])


if __name__ == "__main__":
    unittest.main()
