import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import convert_legacy  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402


class Fake:
    repo = "o/r"

    def __init__(self, issues, kids):
        self.issues, self.kids = issues, kids
        self.calls = []

    def repo_path(self, path):
        return "/repos/o/r" + path

    def request(self, method, path, body=None):
        self.calls.append((method, path, body))
        tail = path.split("/repos/o/r/issues/")[1] if "/repos/o/r/issues/" in path else ""
        number = int(tail.split("/")[0].split("?")[0]) if tail else None
        if method == "GET" and "/sub_issues" in path:
            return self.kids.get(number, [])
        if method == "GET":
            return self.issues[number]
        return None

    def comment(self, number, body):
        self.calls.append(("COMMENT", number, body))

    def close_issue(self, number, reason="completed"):
        self.calls.append(("CLOSE", number, reason))

    def set_project_field(self, *args):
        self.calls.append(("SET",) + args[2:])

    def clear_project_field(self, *args):
        self.calls.append(("CLEAR",) + args[2:])

    def graphql(self, query, variables=None):
        return {"node": {"start": {"date": "2025-01-02"}, "end": {"date": "2025-01-09"}}}


def board():
    fields = {n: {"id": "F" + n, "type": k, "options": {v: "O" + v for v in (vals or [])}} for n, (k, vals) in preflight.REQUIRED_FIELDS.items()}
    return preflight.Board("P", 1, "b", fields)


def ticket(number, **kw):
    base = {"number": number, "item": "I%d" % number, "state": "CLOSED", "type": "Feature", "status": "Completed", "delivery": "Released",
            "resolution": "Done", "version": "", "end": None}
    base.update(kw)
    return base


def issue(title, labels=()):
    return {"title": title, "labels": [{"name": l} for l in labels]}


class ConvertTests(unittest.TestCase):
    def run_(self, gh, tickets, source=ticket_type.ISSUE_TYPE, dry_run=False, **kw):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".git"))
            return convert_legacy.convert(gh, gh, board(), tickets, source, folder, dry_run, **kw)

    def good(self):
        gh = Fake({1: issue("Version 001.025.004", ["tool"])}, {1: [{"number": 2, "id": 902}, {"number": 3, "id": 903}]})
        tickets = [ticket(1, type="Version", version="V001.025.004", state="CLOSED"), ticket(2, version="V001.025.004"),
                   ticket(3, version="V001.025.004")]
        return gh, tickets

    def test_titles(self):
        self.assertEqual(convert_legacy.legacy_title("Version 1.25.4"), "Legacy Version 001.025.004")
        self.assertEqual(convert_legacy.legacy_title("Version", "V000.015.000"), "Legacy Version 000.015.000")
        self.assertIsNone(convert_legacy.legacy_title("Version"))

    def test_a_consistent_ticket_is_converted_in_order(self):
        gh, tickets = self.good()
        run, decisions = self.run_(gh, tickets)
        self.assertEqual(decisions, [])
        kinds = [c[0] for c in gh.calls if c[0] in ("COMMENT", "PATCH", "SET", "CLEAR", "DELETE")]
        self.assertEqual(kinds[0], "COMMENT")
        patch = next(c for c in gh.calls if c[0] == "PATCH")
        self.assertEqual(patch[2], {"title": "Legacy Version 001.025.004", "labels": ["process", "tool"], "type": "Task"})
        sets = [c for c in gh.calls if c[0] == "SET"]
        self.assertEqual([c[1] for c in sets], ["FSize", "FStart date", "FEnd date", "FResolution", "FStatus"])  # dates before Status
        self.assertEqual(sets[-1][2], {"singleSelectOptionId": "OAbandoned"})
        self.assertEqual(sets[-2][2], {"singleSelectOptionId": "OSuperseded"})
        self.assertEqual([c[1] for c in gh.calls if c[0] == "CLEAR"], ["FDelivery", "FVersion"])
        deletes = [c for c in gh.calls if c[0] == "DELETE"]
        self.assertEqual([d[2] for d in deletes], [{"sub_issue_id": 902}, {"sub_issue_id": 903}])
        self.assertEqual(max(i for i, c in enumerate(gh.calls) if c[0] == "DELETE"), len(gh.calls) - 1)  # detached last
        self.assertFalse(any(c[0] == "CLOSE" for c in gh.calls))  # already closed

    def test_a_dry_run_writes_nothing(self):
        gh, tickets = self.good()
        run, _ = self.run_(gh, tickets, dry_run=True)
        self.assertEqual([c for c in gh.calls if c[0] not in ("GET",)], [])
        self.assertTrue(any("detach the sub-issue #2" in line for line in run.log))

    def test_a_child_with_another_version_leaves_the_ticket_alone(self):
        gh, tickets = self.good()
        tickets[2]["version"] = "V001.025.005"
        run, decisions = self.run_(gh, tickets)
        self.assertEqual(decisions[0]["number"], 1)
        self.assertIn("#3 has Version V001.025.005", decisions[0]["reason"])
        self.assertEqual([c for c in gh.calls if c[0] in ("COMMENT", "PATCH", "SET", "DELETE")], [])

    def test_an_open_planned_version_ticket_needs_a_decision_unless_included(self):
        gh = Fake({1: issue("Version 001.026.000")}, {})
        tickets = [ticket(1, type="Version", state="OPEN", status="Todo", delivery="", version="V001.026.000")]
        _, decisions = self.run_(gh, tickets)
        self.assertEqual(len(decisions), 1)
        _, decisions = self.run_(gh, tickets, include_open=True)
        self.assertEqual(decisions, [])
        self.assertIn(("CLOSE", 1, "not_planned"), gh.calls)

    def test_a_converted_ticket_is_skipped(self):
        gh = Fake({1: issue("Legacy Version 001.025.004")}, {})
        run, decisions = self.run_(gh, [ticket(1, type="Version")])
        self.assertEqual(decisions, [])
        self.assertIn("#1: already converted", run.log)
        self.assertEqual([c for c in gh.calls if c[0] in ("COMMENT", "PATCH")], [])

    def test_only_limits_the_tickets(self):
        gh, tickets = self.good()
        self.run_(gh, tickets, only={99})
        self.assertEqual([c for c in gh.calls if c[0] in ("COMMENT", "PATCH")], [])

    def test_with_the_field_source_the_kind_is_set_not_the_issue_type(self):
        gh, tickets = self.good()
        fields = board().fields
        fields["Kind"] = {"id": "FKind", "type": "SINGLE_SELECT", "options": {"Task": "OTask"}}
        b = board()
        b.fields = fields
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".git"))
            convert_legacy.convert(gh, gh, b, tickets, ticket_type.FIELD_SOURCE, folder, False)
        patch = next(c for c in gh.calls if c[0] == "PATCH")
        self.assertNotIn("type", patch[2])
        self.assertIn(("SET", "FKind", {"singleSelectOptionId": "OTask"}), gh.calls)

    def test_main_needs_a_path(self):
        self.assertEqual(convert_legacy.main([]), 1)


if __name__ == "__main__":
    unittest.main()
