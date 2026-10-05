import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import preflight  # noqa: E402
from github_api import GitHubError  # noqa: E402


def board_fields(missing=(), drop_value=None):
    nodes = []
    for index, (name, (kind, values)) in enumerate(preflight.REQUIRED_FIELDS.items()):
        if name in missing:
            continue
        node = {"id": f"F{index}", "name": name, "dataType": kind}
        if kind == preflight.SELECT:
            node["options"] = [{"id": f"{name}-{v}", "name": v} for v in values if v != drop_value]
        nodes.append(node)
    nodes.append({})  # a field type the query does not select comes back empty
    return nodes


class FakeRepoClient:
    repo = "owner/repo"
    token = "t"

    def __init__(self, info=None, error=None):
        self.info, self.error = info or {"permissions": {"push": True}}, error

    def request(self, method, path, body=None):
        if self.error:
            raise self.error
        return self.info


class FakeProjectClient:
    repo = "owner/repo"

    def __init__(self, token="p", boards=None, variable=None, fields=None, viewer_error=None, store_error=None, expiry=None):
        self.token, self.expiry = token, expiry
        self.boards = [{"id": "P7", "number": 7, "title": "Governance"}] if boards is None else boards
        self.variable, self.fields = variable, fields if fields is not None else board_fields()
        self.viewer_error, self.store_error = viewer_error, store_error
        self.stored = {}

    def graphql(self, query, variables=None):
        if "viewer" in query:
            if self.viewer_error:
                raise self.viewer_error
            return {"viewer": {"login": "admin"}}
        if "projectsV2" in query:
            return {"repository": {"projectsV2": {"nodes": self.boards}}}
        return {"node": {"fields": {"nodes": self.fields}}}

    def token_expiry(self):
        return self.expiry

    def get_variable(self, name):
        return self.variable

    def set_variable(self, name, value):
        if self.store_error:
            raise self.store_error
        self.stored[name] = value


class PreflightTests(unittest.TestCase):
    def test_everything_passes_and_the_board_number_is_stored(self):
        project = FakeProjectClient()
        report = preflight.run(FakeRepoClient(), project)
        self.assertTrue(report.ok, report.render())
        self.assertEqual(project.stored, {"BOARD_NUMBER": "7"})
        self.assertEqual(report.board.number, 7)
        self.assertEqual(report.board.fields["Status"]["options"]["Review"], "Status-Review")
        self.assertIn("preflight: passed", report.render())

    def test_a_token_close_to_expiry_gives_a_warning(self):
        soon = datetime.now(timezone.utc) + timedelta(days=5, hours=1)
        report = preflight.run(FakeRepoClient(), FakeProjectClient(expiry=soon))
        self.assertTrue(report.ok)
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("expires in 5 day(s)", report.warnings[0])
        self.assertIn("[warning]", report.render())

    def test_a_token_with_a_distant_expiry_gives_no_warning(self):
        later = datetime.now(timezone.utc) + timedelta(days=90)
        report = preflight.run(FakeRepoClient(), FakeProjectClient(expiry=later))
        self.assertEqual(report.warnings, [])
        self.assertIn("expires", report.checks[1].message)

    def test_a_token_with_no_expiry_gives_a_warning(self):
        report = preflight.run(FakeRepoClient(), FakeProjectClient())
        self.assertIn("no expiry date", report.warnings[0])

    def test_the_variable_is_not_rewritten_when_it_already_matches(self):
        project = FakeProjectClient(variable="7")
        preflight.run(FakeRepoClient(), project)
        self.assertEqual(project.stored, {})

    def test_no_store_leaves_the_variable_alone(self):
        project = FakeProjectClient()
        self.assertTrue(preflight.run(FakeRepoClient(), project, store=False).ok)
        self.assertEqual(project.stored, {})

    def test_repository_unreachable(self):
        report = preflight.run(FakeRepoClient(error=GitHubError(404, "Not Found")), FakeProjectClient())
        self.assertFalse(report.ok)
        self.assertIn("cannot reach owner/repo", report.checks[0].message)

    def test_repository_without_write_access(self):
        report = preflight.run(FakeRepoClient({"permissions": {"push": False}}), FakeProjectClient())
        self.assertIn("write access is needed", report.checks[0].message)

    def test_missing_token_skips_the_board_checks(self):
        report = preflight.run(FakeRepoClient(), FakeProjectClient(token=""))
        self.assertEqual([c.skipped for c in report.checks], [False, False, True, True])
        self.assertIn("PROJECT_TOKEN is not set", report.checks[1].message)
        self.assertIsNone(report.board)

    def test_token_that_does_not_work(self):
        project = FakeProjectClient(viewer_error=GitHubError(401, "Bad credentials"))
        report = preflight.run(FakeRepoClient(), project)
        self.assertIn("Bad credentials", report.checks[1].message)
        self.assertTrue(report.checks[2].skipped)

    def test_no_board_stops_at_the_board_step(self):
        report = preflight.run(FakeRepoClient(), FakeProjectClient(boards=[]))
        self.assertIn("no linked board", report.checks[2].message)
        self.assertTrue(report.checks[3].skipped)

    def test_two_boards_ask_the_administrator(self):
        boards = [{"id": "A", "number": 3, "title": "One"}, {"id": "B", "number": 7, "title": "Two"}]
        report = preflight.run(FakeRepoClient(), FakeProjectClient(boards=boards))
        message = report.checks[2].message
        self.assertIn("2 linked boards", message)
        self.assertIn("BOARD_NUMBER", message)
        self.assertTrue(report.checks[3].skipped)

    def test_two_boards_with_the_variable_set_use_that_one(self):
        boards = [{"id": "A", "number": 3, "title": "One"}, {"id": "B", "number": 7, "title": "Two"}]
        report = preflight.run(FakeRepoClient(), FakeProjectClient(boards=boards, variable="7"))
        self.assertTrue(report.ok, report.render())
        self.assertEqual(report.board.id, "B")

    def test_storing_the_variable_can_fail(self):
        project = FakeProjectClient(store_error=GitHubError(403, "Resource not accessible"))
        report = preflight.run(FakeRepoClient(), project)
        self.assertIn("could not store BOARD_NUMBER", report.checks[2].message)

    def test_missing_field_and_value_are_named(self):
        report = preflight.run(FakeRepoClient(), FakeProjectClient(fields=board_fields(missing=["Attention"], drop_value="Merged")))
        message = report.checks[-1].message
        self.assertIn("missing field Attention", message)
        self.assertIn("field Delivery lacks the values Merged", message)
        self.assertIsNone(report.board)

    def test_wrong_field_type_is_named(self):
        fields = board_fields()
        for node in fields:
            if node.get("name") == "Build":
                node["dataType"] = preflight.NUMBER
        report = preflight.run(FakeRepoClient(), FakeProjectClient(fields=fields))
        self.assertIn("field Build is NUMBER, expected TEXT", report.checks[-1].message)

    def test_main_needs_the_repository(self):
        saved = os.environ.pop("GITHUB_REPOSITORY", None)
        try:
            self.assertEqual(preflight.main([]), 1)
        finally:
            if saved is not None:
                os.environ["GITHUB_REPOSITORY"] = saved


if __name__ == "__main__":
    unittest.main()
