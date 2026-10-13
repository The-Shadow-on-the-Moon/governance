import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import conditions  # noqa: E402
import dates  # noqa: E402
import fields  # noqa: E402
import finalize  # noqa: E402
import preflight  # noqa: E402
import release  # noqa: E402
import ticket_type  # noqa: E402
import version_format  # noqa: E402
import watch  # noqa: E402
from github_api import Client, GitHubError  # noqa: E402


class FakeVariables:
    repo = "owner/repo"
    token = "t"

    def __init__(self, value=None, error=None):
        self.value, self.error = value, error

    def get_variable(self, name):
        assert name == ticket_type.VARIABLE
        if self.error:
            raise self.error
        return self.value


class SourceTests(unittest.TestCase):
    ORG = {"owner": {"type": "Organization"}}
    USER = {"owner": {"type": "User"}}

    def test_an_organization_uses_the_issue_type_and_a_person_the_field(self):
        self.assertEqual(ticket_type.source(self.ORG, FakeVariables()), "issue-type")
        self.assertEqual(ticket_type.source(self.USER, FakeVariables()), "field")

    def test_the_variable_decides_when_it_is_valid(self):
        self.assertEqual(ticket_type.source(self.ORG, FakeVariables("field")), "field")
        self.assertEqual(ticket_type.source(self.USER, FakeVariables(" issue-type ")), "issue-type")

    def test_a_variable_that_is_not_valid_or_cannot_be_read_is_ignored(self):
        self.assertEqual(ticket_type.source(self.USER, FakeVariables("7")), "field")
        self.assertEqual(ticket_type.source(self.ORG, FakeVariables(error=GitHubError(403, "no"))), "issue-type")

    def test_nothing_known_means_an_organization(self):
        self.assertEqual(ticket_type.source(None, None), "issue-type")
        self.assertEqual(ticket_type.source({}, None), "issue-type")

    def test_the_field_is_required_only_for_the_field_source(self):
        self.assertEqual(ticket_type.required_fields("issue-type", "SINGLE_SELECT"), {})
        self.assertEqual(ticket_type.required_fields("field", "SINGLE_SELECT"), {"Kind": ("SINGLE_SELECT", ticket_type.VALUES)})

    def test_every_value_has_a_color_and_a_description(self):
        self.assertEqual(set(ticket_type.COLORS), set(ticket_type.VALUES))
        self.assertEqual(set(ticket_type.DESCRIPTIONS), set(ticket_type.VALUES))


class ReadingTests(unittest.TestCase):
    def test_a_board_item_has_its_issue_type_or_else_its_kind(self):
        self.assertEqual(ticket_type.of_node({"kind": {"name": "Bug"}}, {"issueType": {"name": "Feature"}}), "Feature")
        self.assertEqual(ticket_type.of_node({"kind": {"name": "Bug"}}, {"issueType": None}), "Bug")
        self.assertEqual(ticket_type.of_node({"kind": None}, {}), None)

    def test_the_reader_finds_the_kind_of_the_board_item_of_an_issue(self):
        asked = []

        class Project:
            repo = "owner/repo"

            def graphql(self, query, variables=None):
                asked.append(variables)
                return {"repository": {"issue": {"projectItems": {"nodes": [{"kind": None}, {"kind": {"name": "Feature"}}]}}}}

        self.assertEqual(ticket_type.reader(Project())(201), "Feature")
        self.assertEqual(asked, [{"o": "owner", "n": "repo", "i": 201}])

    def test_the_reader_returns_nothing_for_an_issue_without_a_kind(self):
        class Project:
            repo = "owner/repo"

            def graphql(self, query, variables=None):
                return {"repository": {"issue": {"projectItems": {"nodes": []}}}}

        self.assertIsNone(ticket_type.reader(Project())(5))

    def test_the_client_falls_back_to_the_kind_when_the_issue_has_no_type(self):
        client = Client("t", "owner/repo", transport=lambda *a: (200, '{"number": 3, "type": null}', {}))
        self.assertIsNone(client.issue_type(3))
        client.kind_reader = lambda number: "Task"
        self.assertEqual(client.issue_type(3), "Task")

    def test_the_issue_type_wins_over_the_reader(self):
        client = Client("t", "owner/repo", transport=lambda *a: (200, '{"number": 3, "type": {"name": "Bug"}}', {}))
        client.kind_reader = lambda number: "Task"
        self.assertEqual(client.issue_type(3), "Bug")

    def test_the_version_is_decided_from_the_kinds(self):
        class Repo:
            kind_reader = None

            def issue_type(self, number):
                return {1: "Feature", 2: "Bug"}[number]

        sections = finalize.changelog.parse(
            "# Changelog\n\n## WIP-Version\n### Build 20261006091200 (branch x)\n#### #1 — A\n- a.\n#### #2 — B\n- b.\n\n"
            "## V2.4.1 — 2026-10-05 16:41 UTC\n### Build 20261005143045 (branch y)\n#### #3 — C\n- c.\n")
        version, types, _ = finalize.decide(sections, Repo())
        self.assertEqual(str(version), "V2.5.0")
        self.assertEqual(types, {1: "Feature", 2: "Bug"})


class BoardQueryTests(unittest.TestCase):
    """Each script that reads the board's items gets the Type from the issue type or the field Kind."""

    def page(self, content_extra=None, node_extra=None, kind="Bug", issue_type=None):
        content = {"number": 7, "state": "OPEN", "updatedAt": "2026-10-01T00:00:00Z",
                   "issueType": {"name": issue_type} if issue_type else None, **(content_extra or {})}
        node = {"id": "I1", "updatedAt": "2026-10-01T00:00:00Z", "content": content, "kind": {"name": kind} if kind else None,
                **(node_extra or {})}
        return {"node": {"items": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [node]}}}

    def project(self, data):
        class Project:
            def graphql(self, query, variables=None):
                self.query = query
                return data

        return Project()

    class Board:
        id = "P1"

    def test_every_query_asks_for_the_kind(self):
        for module in (conditions, dates, release, version_format, watch):
            self.assertIn('kind:fieldValueByName(name:"Kind")', module.ITEMS, module.__name__)

    def test_conditions_read_the_kind(self):
        project = self.project(self.page())
        self.assertEqual(conditions.board_tickets(project, self.Board())[0]["type"], "Bug")
        project = self.project(self.page(issue_type="Feature"))
        self.assertEqual(conditions.board_tickets(project, self.Board())[0]["type"], "Feature")

    def test_dates_read_the_kind(self):
        self.assertEqual(dates.board_items(self.project(self.page()), self.Board())[0]["type"], "Bug")

    def test_version_format_reads_the_kind(self):
        self.assertEqual(version_format.board_items(self.project(self.page()), self.Board())[0]["type"], "Bug")

    def test_watch_reads_the_kind(self):
        self.assertEqual(watch.board_tickets(self.project(self.page()), self.Board())[0]["type"], "Bug")

    def test_release_skips_version_and_alert_tickets_by_their_kind(self):
        for kind, skipped in (("Version", True), ("Alert", True), ("Bug", False)):
            data = self.page(node_extra={"delivery": {"name": "Merged"}, "version": {"text": "V000.001.000"}}, kind=kind)
            found = release.releasable_tickets(self.project(data), self.Board(), release.Version.parse("V0.1.0"))
            self.assertEqual(not found, skipped, kind)


class PreflightTests(unittest.TestCase):
    def board_fields(self, with_kind):
        nodes = []
        for index, (name, (kind, values)) in enumerate(preflight.required_fields("field" if with_kind else "issue-type").items()):
            node = {"id": f"F{index}", "name": name, "dataType": kind}
            if kind == preflight.SELECT:
                node["options"] = [{"id": f"{name}-{v}", "name": v} for v in values]
            nodes.append(node)
        return nodes

    def clients(self, owner_type, with_kind, variable=None):
        class Repo:
            repo = "owner/repo"
            token = "t"
            kind_reader = None

            def request(self, method, path, body=None):
                return {"permissions": {"push": True}, "owner": {"type": owner_type}}

        fields_ = self.board_fields(with_kind)

        class Project:
            repo = "owner/repo"
            token = "p"

            def graphql(self, query, variables=None):
                if "viewer" in query:
                    return {"viewer": {"login": "admin"}}
                if "projectsV2" in query:
                    return {"repository": {"projectsV2": {"nodes": [{"id": "P7", "number": 7, "title": "B"}]}}}
                return {"node": {"fields": {"nodes": fields_}}}

            def request(self, method, path, body=None):
                return {"permissions": {"push": True}}

            def token_expiry(self):
                return None

            def get_variable(self, name):
                return variable if name == ticket_type.VARIABLE else "7"

            def set_variable(self, name, value):
                pass

        return Repo(), Project()

    def test_a_personal_account_needs_the_field_and_the_issue_type_reads_it(self):
        repo, project = self.clients("User", with_kind=True)
        report = preflight.run(repo, project, store=False)
        self.assertEqual(report.type_source, "field")
        self.assertIsNotNone(repo.kind_reader)
        self.assertTrue([c for c in report.checks if c.name == "board fields"][0].ok)

    def test_a_personal_account_without_the_field_fails_the_fields_check(self):
        repo, project = self.clients("User", with_kind=False)
        report = preflight.run(repo, project, store=False)
        check = [c for c in report.checks if c.name == "board fields"][0]
        self.assertFalse(check.ok)
        self.assertIn("missing field Kind", check.message)

    def test_a_personal_account_tells_the_project_client_to_use_the_users_paths(self):
        repo, project = self.clients("User", with_kind=True)
        preflight.run(repo, project, store=False)
        self.assertEqual(project.owner_kind, "users")

    def test_an_organization_keeps_the_orgs_paths(self):
        repo, project = self.clients("Organization", with_kind=False)
        project.owner_kind = "orgs"
        preflight.run(repo, project, store=False)
        self.assertEqual(project.owner_kind, "orgs")

    def test_an_organization_does_not_need_the_field(self):
        repo, project = self.clients("Organization", with_kind=False)
        report = preflight.run(repo, project, store=False)
        self.assertEqual(report.type_source, "issue-type")
        self.assertIsNone(repo.kind_reader)
        self.assertTrue([c for c in report.checks if c.name == "board fields"][0].ok)

    def test_the_variable_can_make_an_organization_use_the_field(self):
        repo, project = self.clients("Organization", with_kind=True, variable="field")
        report = preflight.run(repo, project, store=False)
        self.assertEqual(report.type_source, "field")


class FieldsTests(unittest.TestCase):
    class Board:
        def __init__(self, fields_):
            self.fields = fields_

    def test_the_field_is_created_only_for_the_field_source(self):
        board = self.Board({n: {"type": k, "options": {v: v for v in (vals or [])}} for n, (k, vals) in preflight.REQUIRED_FIELDS.items()})
        self.assertEqual(fields.plan(board), ([], []))
        missing, differing = fields.plan(board, preflight.required_fields("field"))
        self.assertEqual([m[0] for m in missing], ["Kind"])
        self.assertEqual(missing[0][2], ticket_type.VALUES)

    def test_the_options_of_kind_get_the_colors_and_descriptions_of_the_type(self):
        made = []

        class Run:
            def do(self, text, function, *args):
                made.append(args)

        class Project:
            def create_field(self, *args):
                pass

        fields.create(Run(), Project(), type("B", (), {"id": "P"})(), [("Kind", "SINGLE_SELECT", ticket_type.VALUES)])
        options = made[0][3]
        self.assertEqual(options[0], ("Feature", "PURPLE", ticket_type.DESCRIPTIONS["Feature"]))
        self.assertEqual(options[-1][:2], ("Alert", "RED"))


class WritingTests(unittest.TestCase):
    """The Version and Alert tickets get their Type from the issue type, or from Kind when there are no issue types."""

    class Run:
        dry_run = False

        def __init__(self):
            self.log = []

        def do(self, text, function, *args):
            self.log.append(text)
            return function(*args)

    class Repo:
        repo = "owner/repo"

        def __init__(self, kind_reader=None):
            self.kind_reader, self.created = kind_reader, []

        def repo_path(self, path):
            return f"/repos/{self.repo}{path}"

        def request(self, method, path, body=None):
            return [] if method == "GET" else {}

        def create_issue(self, title, body, issue_type=None, labels=(), assignees=()):
            self.created.append(issue_type)
            return {"number": 50, "node_id": "N50"}

        def add_sub_issue(self, parent, child):
            pass

        def close_issue(self, number, reason="completed"):
            pass

    class Project:
        def __init__(self):
            self.set = []

        def add_to_project(self, project_id, content_id):
            return "ITEM"

        def set_project_field(self, project_id, item_id, field_id, value):
            self.set.append((item_id, field_id, value))

    def board(self):
        fields_ = {name: {"id": f"F-{name}", "type": kind, "options": {v: f"{name}-{v}" for v in (values or [])}}
                   for name, (kind, values) in preflight.required_fields("field").items()}
        return preflight.Board("P7", 7, "Governance", fields_)

    def version_ticket(self, repo, project):
        return finalize.record_version_ticket(self.Run(), repo, project, self.board(), finalize.versions.Version(2, 5, 0),
                                              "2026-10-07 16:20", "sub", None, "20261006091200", [])

    def test_the_version_ticket_gets_its_issue_type_without_the_field(self):
        repo, project = self.Repo(), self.Project()
        self.version_ticket(repo, project)
        self.assertEqual(repo.created, ["Version"])
        self.assertNotIn(("ITEM", "F-Kind", {"singleSelectOptionId": "Kind-Version"}), project.set)

    def test_the_version_ticket_gets_its_kind_with_the_field(self):
        repo, project = self.Repo(kind_reader=lambda n: None), self.Project()
        self.version_ticket(repo, project)
        self.assertIn(("ITEM", "F-Kind", {"singleSelectOptionId": "Kind-Version"}), project.set)

    def test_the_alert_gets_its_kind_with_the_field(self):
        import alerts

        repo, project = self.Repo(kind_reader=lambda n: None), self.Project()
        alerts.create_alert(self.Run(), repo, project, self.board(), "T", "B")
        self.assertIn(("ITEM", "F-Kind", {"singleSelectOptionId": "Kind-Alert"}), project.set)

    def test_the_client_sends_no_issue_type_with_the_field(self):
        sent = []

        def transport(method, url, headers, body):
            sent.append(body)
            return 201, '{"number": 1}', {}

        client = Client("t", "owner/repo", transport=transport)
        client.create_issue("T", "B", "Alert")
        client.kind_reader = lambda number: None
        client.create_issue("T", "B", "Alert")
        self.assertIn(b'"type"', sent[0])
        self.assertNotIn(b'"type"', sent[1])


class LookupTests(unittest.TestCase):
    """The Version tickets are listed without the issue-type filter when there are no issue types."""

    class Repo:
        repo = "owner/repo"

        def __init__(self, kind_reader=None):
            self.kind_reader, self.paths = kind_reader, []

        def repo_path(self, path):
            return path

        def request(self, method, path, body=None):
            self.paths.append(path)
            return [{"number": 1, "title": "Not a version"}, {"number": 2, "title": "Version 000.002.000", "pull_request": {}},
                    {"number": 3, "title": "Version 000.002.000", "state": "closed"}]

    def test_the_filter_is_sent_with_issue_types_only(self):
        self.assertEqual(ticket_type.type_filter(self.Repo(), "Version"), "&type=Version")
        self.assertEqual(ticket_type.type_filter(self.Repo(kind_reader=lambda n: None), "Version"), "")
        self.assertEqual(ticket_type.type_filter(object(), "Version"), "&type=Version")

    def test_a_version_ticket_is_found_by_its_title_without_the_filter(self):
        import implemented

        repo = self.Repo(kind_reader=lambda n: None)
        found = implemented.version_ticket(repo, implemented.Version.parse("V0.2.0"))
        self.assertEqual(found["number"], 3)  # the pull request with the same title is skipped
        self.assertNotIn("type=", repo.paths[0])
        issue_repo = self.Repo()
        implemented.version_ticket(issue_repo, implemented.Version.parse("V0.2.0"))
        self.assertIn("type=Version", issue_repo.paths[0])

    def test_the_stale_planned_versions_are_listed_without_the_filter(self):
        import alerts

        class Open(self.Repo):
            def request(self, method, path, body=None):
                self.paths.append(path)
                return [{"number": 5, "title": "Version 0.1.0"}, {"number": 6, "title": "Version 0.1.0", "pull_request": {}}]

        repo = Open(kind_reader=lambda n: None)
        self.assertEqual(alerts.stale_planned(repo, alerts.Version.parse("V0.2.0")), [(5, "Version 0.1.0")])
        self.assertNotIn("type=", repo.paths[0])


if __name__ == "__main__":
    unittest.main()
