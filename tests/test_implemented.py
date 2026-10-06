import os
import sys
import unittest
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import finalize  # noqa: E402
import implemented  # noqa: E402
import preflight  # noqa: E402
from versions import Version  # noqa: E402

NOW = datetime(2026, 10, 6, 10, 0, 0, tzinfo=timezone.utc)
V = Version.parse


def node(number, delivery="Implemented", version="", parent=None, version_number=None, title=None):
    return {"id": f"I{number}", "content": {"number": number, "title": title or f"Ticket {number}", "parent": {"number": parent} if parent else None},
            "delivery": {"name": delivery} if delivery else None,
            "version": {"text": version} if version else None,
            "number": {"number": version_number} if version_number is not None else None}


class FakeProject:
    repo = "owner/repo"

    def __init__(self, nodes, per_page=100):
        self.nodes, self.per_page, self.sets, self.queries = nodes, per_page, [], 0

    def graphql(self, query, variables=None):
        start = int(variables["after"] or 0)
        page = self.nodes[start:start + self.per_page]
        end = start + self.per_page
        self.queries += 1
        return {"node": {"items": {"pageInfo": {"hasNextPage": end < len(self.nodes), "endCursor": str(end)}, "nodes": page}}}

    def set_project_field(self, project_id, item_id, field_id, value):
        self.sets.append((item_id, field_id, value))


class FakeRepo:
    repo = "owner/repo"

    def __init__(self, tickets):
        self.tickets, self.subs, self.comments = tickets, [], []

    def repo_path(self, path):
        return path

    def request(self, method, path, body=None):
        return self.tickets

    def add_sub_issue(self, parent, child):
        self.subs.append((parent, child))

    def comment(self, number, body):
        self.comments.append((number, body))


def board():
    fields = {name: {"id": f"F-{name}", "type": kind, "options": {v: f"{name}-{v}" for v in (values or [])}}
              for name, (kind, values) in preflight.REQUIRED_FIELDS.items()}
    return preflight.Board("P7", 7, "Governance", fields)


FINALIZED = {V("V0.3.0"), V("V0.3.1"), V("V0.4.0")}
OLD_TICKETS = [{"title": "Version 0.3.1", "state": "closed", "number": 27},
               {"title": "Version 0.5.0", "state": "open", "number": 31}]


def sweep(nodes, tickets=OLD_TICKETS, finalized=FINALIZED, dry_run=False):
    run = finalize.Runner(dry_run)
    project, repo = FakeProject(nodes), FakeRepo(tickets)
    added = implemented.sweep(run, repo, project, board(), finalized, (V("V0.4.0"), 30), NOW)
    return run, repo, project, added


class SweepTests(unittest.TestCase):
    def test_a_blank_version_gets_the_version_being_finalized(self):
        run, repo, project, _ = sweep([node(50)])
        self.assertEqual(repo.subs, [(30, 50)])
        sets = {(field): value for _, field, value in project.sets}
        self.assertEqual(sets["F-Version"], {"text": "V0.4.0"})
        self.assertEqual(sets["F-Version#"], {"number": 40000.0})

    def test_the_version_being_finalized_is_attached_and_kept(self):
        _, repo, project, _ = sweep([node(50, version="V0.4.0")])
        self.assertEqual(repo.subs, [(30, 50)])
        self.assertNotIn("F-Version", [field for _, field, _ in project.sets])

    def test_an_earlier_finalized_version_is_attached_to_its_own_ticket(self):
        run, repo, project, _ = sweep([node(50, version="V0.3.1")])
        self.assertEqual(repo.subs, [(27, 50)])
        self.assertEqual({field: value for _, field, value in project.sets}["F-Version#"], {"number": 30010.0})
        self.assertEqual(repo.comments[0][0], 27)

    def test_a_later_version_waits(self):
        run, repo, project, _ = sweep([node(50, version="V0.5.0")])
        self.assertEqual((repo.subs, project.sets), ([], []))
        self.assertIn("waits for V0.5.0", run.log[0])

    def test_already_attached_and_other_deliveries_are_left_alone(self):
        _, repo, project, _ = sweep([node(50, parent=27), node(51, delivery="Merged"), node(52, delivery=None)])
        self.assertEqual((repo.subs, project.sets, repo.comments), ([], [], []))

    def test_version_number_already_right_is_not_set_again(self):
        _, _, project, _ = sweep([node(50, version="V0.4.0", version_number=40000.0)])
        self.assertEqual(project.sets, [])

    def test_one_comment_per_version_ticket_lists_the_tickets(self):
        _, repo, _, _ = sweep([node(50, version="V0.3.1", title="A"), node(51, version="V0.3.1", title="B"), node(52, title="C")])
        self.assertEqual(sorted(number for number, _ in repo.comments), [27, 30])
        text = dict(repo.comments)[27]
        self.assertIn("#50 A; #51 B", text)
        self.assertIn("2026-10-06 10:00 UTC", text)

    def test_a_missing_or_open_version_ticket_is_left_alone(self):
        run, repo, _, _ = sweep([node(50, version="V0.3.0")], tickets=[{"title": "Version 0.3.0", "state": "open", "number": 25}])
        self.assertEqual(repo.subs, [])
        self.assertIn("no finalized Version ticket for V0.3.0", run.log[0])
        run, repo, _, _ = sweep([node(50, version="V0.3.0")], tickets=[])
        self.assertEqual(repo.subs, [])

    def test_something_that_is_not_a_version_is_left_alone(self):
        run, repo, _, _ = sweep([node(50, version="soon")])
        self.assertEqual(repo.subs, [])
        self.assertIn("is not a version", run.log[0])

    def test_dry_run_changes_nothing(self):
        run, repo, project, _ = sweep([node(50)], dry_run=True)
        self.assertEqual((repo.subs, project.sets, repo.comments), ([], [], []))
        self.assertTrue(any("attach to the Version ticket #30" in line for line in run.log))

    def test_every_page_of_the_board_is_read(self):
        project = FakeProject([node(n, delivery="Merged") for n in range(1, 230)] + [node(500)], per_page=100)
        found = implemented.unattached(project, board())
        self.assertEqual([t["number"] for t in found], [500])
        self.assertEqual(project.queries, 3)


class FinalizeIntegrationTests(unittest.TestCase):
    def test_finalize_runs_the_sweep_after_the_version_ticket(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            def git(*args):
                subprocess.run(["git", *args], cwd=folder, check=True, capture_output=True)
            git("init", "-q", "-b", "main")
            git("config", "user.name", "T")
            git("config", "user.email", "t@example.com")
            with open(os.path.join(folder, "CHANGELOG.md"), "w", encoding="utf-8", newline="") as handle:
                handle.write("# Changelog\n\n## V0.4.0 — 2026-10-06 00:47 UTC\n### Build 20261006004523 (branch b)\n#### #28 — Work\n- done.\n")
            git("add", "-A")
            git("commit", "-q", "-m", "x")

            class Repo(FakeRepo):
                def issue_type(self, number):
                    return "Enhancement"

            repo, project = Repo(OLD_TICKETS + [{"title": "Version 0.4.0", "state": "closed", "number": 30, "node_id": "N30"}]), FakeProject([node(50)])
            project.nodes = [node(50)]
            graphql = project.graphql

            def routed(query, variables=None):
                if "pageInfo" in query:
                    return graphql(query, variables)
                return {"repository": {"issue": {"id": "N28", "title": "t", "projectItems": {"nodes": []}}}}
            project.graphql = routed
            project.add_to_project = lambda project_id, content_id: "ITEM"
            run = finalize.finalize(folder, repo, project, board(), NOW, push=False)
            self.assertIn((30, 50), repo.subs)
            self.assertTrue(any("Version ticket #30: comment" in line for line in run.log))


if __name__ == "__main__":
    unittest.main()
