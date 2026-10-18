import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_common  # noqa: E402
import install  # noqa: E402
import kit_common  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402
from github_api import GitHubError  # noqa: E402

WANTED_LABELS, WANTED_TYPES = audit_common.appendix_c()


class FakeGitHub:
    """Stands for both clients: the repository, the organization, the variables and the board of a project."""

    repo = "owner/repo"

    def __init__(self, owner_type="Organization", labels=(), types=(), boards=(), variables=None, secrets=("PROJECT_TOKEN",)):
        self.owner_type = owner_type
        self.labels = [dict(label) for label in labels]
        self.types = [dict(item) for item in types]
        self.boards = list(boards)
        self.variables = dict(variables or {})
        self.secrets = list(secrets)
        self.calls, self.created_fields = [], []
        self.status_options = None

    def repo_path(self, path):
        return "/repos/owner/repo" + path

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        if method == "GET" and path == "/repos/owner/repo":
            return {"owner": {"login": "owner", "type": self.owner_type}}
        if method == "GET" and path.startswith("/repos/owner/repo/labels"):
            return list(self.labels)
        if method == "POST" and path == "/repos/owner/repo/labels":
            self.labels.append(dict(body))
            return body
        if method == "PATCH" and path.startswith("/repos/owner/repo/labels/"):
            name = path.rsplit("/", 1)[1].replace("%20", " ")
            next(l for l in self.labels if l["name"] == name).update(body)
            return body
        if method == "DELETE" and path.startswith("/repos/owner/repo/labels/"):
            name = path.rsplit("/", 1)[1].replace("%20", " ")
            self.labels = [l for l in self.labels if l["name"] != name]
            return None
        if method == "GET" and path.startswith("/orgs/owner/issue-types"):
            return list(self.types)
        if method == "POST" and path == "/orgs/owner/issue-types":
            self.types.append(dict(body, id=len(self.types) + 100))
            return body
        if method == "PUT" and path.startswith("/orgs/owner/issue-types/"):
            item = next(t for t in self.types if str(t["id"]) == path.rsplit("/", 1)[1])
            item.update(body)
            return body
        if method == "GET" and path == "/repos/owner/repo/actions/secrets":
            return {"secrets": [{"name": name} for name in self.secrets]}
        raise AssertionError((method, path))

    def get_variable(self, name):
        return self.variables.get(name)

    def set_variable(self, name, value):
        self.calls.append(("VARIABLE", name, value))
        self.variables[name] = value

    def graphql(self, query, variables=None):
        self.calls.append(("GRAPHQL", query.split("{")[0].strip()[:20], variables))
        if "projectsV2" in query:
            return {"repository": {"projectsV2": {"nodes": list(self.boards)}}}
        if "owner{id}" in query:
            return {"repository": {"id": "R1", "owner": {"id": "O1"}}}
        if "createProjectV2(" in query:
            board = {"id": "P1", "number": 7, "title": variables["t"]}
            self.pending = board
            return {"createProjectV2": {"projectV2": board}}
        if "linkProjectV2ToRepository" in query:
            self.boards.append(self.pending)
            return {"linkProjectV2ToRepository": {"repository": {"id": "R1"}}}
        if "field(name" in query:
            return {"node": {"field": {"id": "F-Status", "options": []}}}
        if "updateProjectV2Field" in query:
            self.status_options = [o["name"] for o in variables["o"]]
            return {"updateProjectV2Field": {}}
        raise AssertionError(query[:60])

    def create_field(self, project_id, name, data_type, options=()):
        self.created_fields.append(name)


def board(with_fields=False):
    fields = {}
    for name, (kind, values) in preflight.REQUIRED_FIELDS.items():
        if with_fields or name == "Status":
            fields[name] = {"id": "F-" + name, "type": kind, "options": {v: v for v in (values or [])}}
    return preflight.Board("P1", 7, "t", fields)


class Views:
    """Replaces views.sync, which reads and writes the board's views."""

    def __init__(self, test):
        self.calls = []
        self.original = install.views.sync
        install.views.sync = self.sync
        test.addCleanup(lambda: setattr(install.views, "sync", self.original))

    def sync(self, project_client, board, definition, dry_run=True, **kwargs):
        self.calls.append((board.number, [entry["name"] for entry in definition], dry_run))
        run = install.finalize.Runner(dry_run)
        run.do("views: create the {} views".format(len(definition)))
        return run


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.views = Views(self)

    def install(self, gh, dry_run=True, **kwargs):
        loader = kwargs.pop("load_board", lambda r, p, d: (board(), ticket_type.ISSUE_TYPE))
        return install.install(gh, gh, "owner/repo", dry_run, load_board=loader, **kwargs)

    def writes(self, gh):
        return [c for c in gh.calls if c[0] in ("POST", "PUT", "PATCH", "DELETE", "VARIABLE")
                or (c[0] == "GRAPHQL" and c[1].startswith("mutation"))]

    def test_a_dry_run_on_an_empty_organization_says_what_it_would_make_and_writes_nothing(self):
        gh = FakeGitHub()
        run = self.install(gh)
        self.assertEqual(self.writes(gh), [])
        text = "\n".join(run.log)
        self.assertEqual(sum(1 for line in run.log if line.startswith("create the label")), len(WANTED_LABELS))
        self.assertEqual(sum(1 for line in run.log if line.startswith("create the issue type")), 7)
        self.assertTrue(any(line.startswith("create the board") for line in run.log))
        self.assertIn("run this again", text)

    def test_apply_makes_the_labels_the_types_and_the_board(self):
        gh = FakeGitHub()
        run = self.install(gh, dry_run=False)
        self.assertEqual({label["name"] for label in gh.labels}, set(WANTED_LABELS))
        self.assertEqual(len(WANTED_LABELS), 15)
        first = next(iter(WANTED_LABELS))
        color, meaning = WANTED_LABELS[first]
        self.assertEqual(next(l for l in gh.labels if l["name"] == first), {"name": first, "color": color, "description": meaning})
        self.assertEqual([t["name"] for t in gh.types], ticket_type.VALUES)
        self.assertEqual(gh.types[0]["color"], WANTED_TYPES[ticket_type.VALUES[0]][0].lower())
        self.assertTrue(all(t["is_enabled"] for t in gh.types))
        self.assertEqual(gh.boards, [{"id": "P1", "number": 7, "title": "Project board (repo)"}])
        self.assertEqual(gh.status_options, preflight.REQUIRED_FIELDS["Status"][1])
        self.assertTrue(gh.created_fields)  # the fields the loaded board lacks
        self.assertEqual(self.views.calls[0][0], 7)

    def test_a_second_run_changes_nothing(self):
        gh = FakeGitHub()
        self.install(gh, dry_run=False)
        gh.calls.clear()
        gh.status_options = None
        run = self.install(gh, dry_run=False)
        self.assertEqual(self.writes(gh), [])
        self.assertFalse(any(line.startswith(("create the label", "create the issue type", "create the board")) for line in run.log))
        self.assertIsNone(gh.status_options)  # the board exists now: its Status options are not written again

    def test_an_existing_label_that_differs_is_corrected_and_the_others_are_kept(self):
        color, meaning = WANTED_LABELS["tool"]
        gh = FakeGitHub(labels=[{"name": "tool", "color": "FFFFFF", "description": "old"}, {"name": "good first issue", "color": "7057ff", "description": ""}])
        run = self.install(gh, dry_run=False)
        self.assertEqual(next(l for l in gh.labels if l["name"] == "tool")["color"], color)
        self.assertEqual(next(l for l in gh.labels if l["name"] == "tool")["description"], meaning)
        self.assertIn("good first issue", [l["name"] for l in gh.labels])
        self.assertTrue(any("good first issue is not on the list: kept" in line for line in run.log))

    def test_extra_labels_are_deleted_only_when_asked(self):
        gh = FakeGitHub(labels=[{"name": "good first issue", "color": "7057ff", "description": ""}, {"name": "bug", "color": "d73a4a", "description": ""}])
        self.install(gh, dry_run=False, delete_extra=True)
        self.assertEqual({l["name"] for l in gh.labels}, set(WANTED_LABELS))
        self.assertTrue(any(c[0] == "DELETE" and c[1].endswith("/good%20first%20issue") for c in gh.calls))

    def test_only_the_missing_issue_types_are_made_and_a_disabled_one_is_corrected(self):
        color, meaning = WANTED_TYPES["Task"]
        gh = FakeGitHub(types=[{"id": 1, "name": "Task", "description": meaning, "color": color.lower(), "is_enabled": True},
                               {"id": 2, "name": "Bug", "description": "x", "color": "red", "is_enabled": False},
                               {"id": 3, "name": "Version", "description": "legacy", "color": "gray", "is_enabled": True}])
        run = self.install(gh, dry_run=False)
        names = [t["name"] for t in gh.types]
        self.assertEqual(sorted(names), sorted(set(ticket_type.VALUES) | {"Version"}))
        self.assertEqual(len([c for c in gh.calls if c[0] == "POST" and c[1] == "/orgs/owner/issue-types"]), 5)
        self.assertFalse(next(t for t in gh.types if t["name"] == "Bug")["is_enabled"])  # an existing type is never changed
        self.assertTrue(any("Bug differs from Appendix C: kept" in line for line in run.log))
        self.assertTrue(any("Version" in line and "kept" in line for line in run.log))

    def test_a_personal_account_has_no_issue_types_and_gets_the_variable(self):
        gh = FakeGitHub(owner_type="User")
        self.install(gh, dry_run=False, load_board=lambda r, p, d: (board(), ticket_type.FIELD_SOURCE))
        self.assertEqual(gh.types, [])
        self.assertEqual(gh.variables[ticket_type.VARIABLE], ticket_type.FIELD_SOURCE)
        gh.calls.clear()
        self.install(gh, dry_run=False, load_board=lambda r, p, d: (board(), ticket_type.FIELD_SOURCE))
        self.assertNotIn(("VARIABLE", ticket_type.VARIABLE, ticket_type.FIELD_SOURCE), gh.calls)

    def test_several_linked_boards_are_a_refusal_that_names_them(self):
        gh = FakeGitHub(boards=[{"id": "A", "number": 1, "title": "One"}, {"id": "B", "number": 2, "title": "Two"}])
        with self.assertRaises(kit_common.KitError) as caught:
            self.install(gh)
        self.assertIn("#1 One, #2 Two", str(caught.exception))

    def test_an_existing_board_is_kept_and_its_status_options_are_not_rewritten(self):
        gh = FakeGitHub(boards=[{"id": "P1", "number": 7, "title": "Mine"}])
        run = self.install(gh, dry_run=False)
        self.assertIsNone(gh.status_options)
        self.assertFalse(any(c[0] == "GRAPHQL" and c[1].startswith("mutation") for c in gh.calls))
        self.assertTrue(any("the board #7 \"Mine\" is linked: kept" in line for line in run.log))

    def test_a_missing_secret_and_the_settings_are_listed_for_the_administrator(self):
        run = self.install(FakeGitHub(secrets=()))
        text = "\n".join(run.log)
        self.assertIn("Actions secret PROJECT_TOKEN", text)
        self.assertIn("repository settings of guide 10, section 3", text)
        run = self.install(FakeGitHub())
        self.assertNotIn("Actions secret PROJECT_TOKEN", "\n".join(run.log))

    def test_a_status_the_api_refuses_is_left_to_the_person(self):
        gh = FakeGitHub()
        original = gh.graphql

        def refusing(query, variables=None):
            if "updateProjectV2Field" in query:
                raise GitHubError(422, "not allowed")
            return original(query, variables)

        gh.graphql = refusing
        run = self.install(gh, dry_run=False)
        self.assertTrue(any("set the options of the field Status by hand" in line for line in run.log))

    def test_the_fields_a_board_lacks_are_created_and_the_views_follow(self):
        gh = FakeGitHub(boards=[{"id": "P1", "number": 7, "title": "Mine"}])
        self.install(gh, dry_run=False)
        self.assertIn("Fix", gh.created_fields)
        self.assertEqual(self.views.calls, [(7, [e["name"] for e in install.views.load_definition()], False)])

    def test_a_dry_run_passes_its_flag_to_the_views(self):
        gh = FakeGitHub(boards=[{"id": "P1", "number": 7, "title": "Mine"}])
        self.install(gh, dry_run=True)
        self.assertTrue(self.views.calls[0][2])


class MainTests(unittest.TestCase):
    def test_no_arguments_is_refused(self):
        self.assertEqual(install.main([]), 1)
        self.assertEqual(install.main(["--apply"]), 1)

    def test_a_folder_with_no_github_remote_needs_the_repository_named(self):
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(install.main([folder]), 1)


if __name__ == "__main__":
    unittest.main()
