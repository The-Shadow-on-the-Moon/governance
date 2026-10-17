import copy
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_board  # noqa: E402
import audit_common  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402
import views  # noqa: E402


def board_fields():
    nodes = []

    for name, (kind, values) in preflight.REQUIRED_FIELDS.items():
        node = {"name": name, "dataType": kind}

        if values is not None:
            node["options"] = [{"name": v, "color": preflight.OPTION_COLORS.get(v, "GRAY"), "description": ""}
                               for v in values]

        nodes.append(node)

    return nodes


def view_nodes():
    nodes = []

    for entry in views.load_definition():
        state = views.desired_state(entry)
        nodes.append({"id": "V_" + entry["name"], "number": 1, "name": entry["name"],
                      "layout": views.LAYOUTS[entry["layout"]], "filter": state["filter"],
                      "groupByFields": {"nodes": [{"name": state["group_by"]}] if state["group_by"] else []},
                      "verticalGroupByFields": {"nodes": [{"name": state["vertical_group_by"]}]
                                                if state["vertical_group_by"] else []},
                      "sortByFields": {"nodes": [{"field": {"name": f}, "direction": d.upper()}
                                                 for f, d in state["sort_by"]]},
                      "visibleFields": {"nodes": [{"name": f} for f in state.get("visible_fields", [])]}})

    return nodes


def item(number, title="A ticket", state="OPEN", issue_type="Feature", labels=("tool",), kind=None, **fields):
    node = {"content": {"__typename": "Issue", "number": number, "title": title, "state": state,
                        "issueType": {"name": issue_type} if issue_type else None,
                        "labels": {"nodes": [{"name": l} for l in labels]}}}

    if kind:
        node["kind"] = {"name": kind}

    for key, value in fields.items():
        node[key] = {"text": value} if key in audit_board.TEXTS else {"name": value}

    return node


GOOD_ITEMS = [
    item(1, Status="InProgress", Size="M"),
    item(2, state="CLOSED", Status="Completed", Resolution="Done", Size="S", Version="V000.001.000"),
    item(3, title="Version 000.001.000", issue_type="Version", labels=(), Status="Completed", Resolution="Done"),
    item(4, issue_type="Alert", labels=(), Priority="Critical", Status="ToDo"),
]


class Fake:
    def __init__(self):
        self.boards = [{"id": "B1", "number": 7, "title": "Governance"}]
        self.fields = board_fields()
        self.views = view_nodes()
        self.items = copy.deepcopy(GOOD_ITEMS)
        self.down = set()

    def __call__(self, query, variables):
        for key, name in ((audit_board.LINKED, "linked"), (audit_board.FIELDS, "fields"),
                          (audit_board.VIEWS, "views"), (audit_board.ITEMS, "items")):
            if query == key:
                break
        else:
            raise AssertionError("unexpected query")

        if name in self.down:
            return None

        if name == "linked":
            return {"repository": {"projectsV2": {"nodes": self.boards}}}

        if name == "fields":
            return {"node": {"fields": {"nodes": self.fields}}}

        if name == "views":
            return {"node": {"views": {"nodes": self.views}}}

        return {"node": {"items": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": self.items}}}


def failed(report):
    return {c.id for c in report.checks if c.result == audit_common.FAIL}


class FieldSourceTests(unittest.TestCase):
    """A board whose Type lives in the field Kind (a personal account, which has no issue types)."""

    def setUp(self):
        self.fake = Fake()
        kind = {"name": "Kind", "dataType": "SINGLE_SELECT",
                "options": [{"name": v, "color": ticket_type.COLORS[v], "description": ""} for v in ticket_type.VALUES]}
        self.fake.fields = self.fake.fields + [kind]
        self.fake.views = []
        for entry in views.for_source(views.load_definition(), "field"):
            state = views.desired_state(entry)
            self.fake.views.append({
                "id": "V_" + entry["name"], "number": 1, "name": entry["name"], "layout": views.LAYOUTS[entry["layout"]],
                "filter": state["filter"],
                "groupByFields": {"nodes": [{"name": state["group_by"]}] if state["group_by"] else []},
                "verticalGroupByFields": {"nodes": [{"name": state["vertical_group_by"]}] if state["vertical_group_by"] else []},
                "sortByFields": {"nodes": [{"field": {"name": f}, "direction": d.upper()} for f, d in state["sort_by"]]},
                "visibleFields": {"nodes": [{"name": f} for f in state.get("visible_fields", [])]}})
        self.fake.items = [item(1, issue_type=None, kind="Feature", Status="InProgress", Size="M"),
                           item(3, title="Version 000.001.000", issue_type=None, kind="Version", labels=(),
                                Status="Completed", Resolution="Done"),
                           item(4, issue_type=None, kind="Alert", labels=(), Priority="Critical", Status="ToDo")]

    def audit(self):
        return audit_board.audit("org/proj", None, self.fake, None, "field")

    def test_a_conforming_board_passes(self):
        report = self.audit()
        self.assertEqual(failed(report), set())
        self.assertEqual(unknown(report), set())
        self.assertIn("board.field.kind.values", [c.id for c in report.checks])

    def test_the_issue_type_source_does_not_look_for_kind(self):
        ids = [c.id for c in audit_board.audit("org/proj", None, Fake()).checks]
        self.assertNotIn("board.field.kind", ids)

    def test_the_field_is_required(self):
        self.fake.fields = [f for f in self.fake.fields if f["name"] != "Kind"]
        self.assertIn("board.field.kind", failed(self.audit()))

    def test_the_values_and_colors_of_kind_are_checked(self):
        kind = [f for f in self.fake.fields if f["name"] == "Kind"][0]
        kind["options"] = kind["options"][:-1]
        self.assertIn("board.field.kind.values", failed(self.audit()))
        kind["options"] = [{"name": v, "color": "GRAY", "description": ""} for v in ticket_type.VALUES]
        self.assertIn("board.field.kind.colors", {c.id for c in self.audit().checks if c.result == audit_common.FAIL})

    def test_a_ticket_without_a_kind_has_no_type(self):
        self.fake.items.append(item(9, issue_type=None, Status="InProgress", Size="S"))
        self.assertIn("board.ticket.type", failed(self.audit()))

    def test_the_views_are_judged_with_kind(self):
        self.assertNotIn("board.views.match", failed(self.audit()))
        self.assertIn("board.views.match", failed(audit_board.audit("org/proj", None, self.fake, None, "issue-type")))


def unknown(report):
    return {c.id for c in report.checks if c.result == audit_common.NOT_CHECKABLE}


class AuditBoardTests(unittest.TestCase):
    def setUp(self):
        self.fake = Fake()

    def audit(self, number=None):
        return audit_board.audit("org/proj", number, self.fake)

    def test_a_conforming_board_passes(self):
        report = self.audit()
        self.assertEqual(failed(report), set())
        self.assertEqual(unknown(report), set())

    def test_board_cannot_be_read(self):
        self.fake.down.add("linked")
        self.assertEqual(unknown(self.audit()), {"board.linked"})

    def test_no_linked_board_or_wrong_number(self):
        self.fake.boards = []
        self.assertEqual(failed(self.audit()), {"board.linked"})
        self.fake.boards = [{"id": "B1", "number": 7, "title": "x"}]
        self.assertEqual(failed(self.audit(number=9)), {"board.linked"})

    def test_missing_field_wrong_kind_and_values(self):
        fields = {f["name"]: f for f in self.fake.fields}
        self.fake.fields = [f for f in self.fake.fields if f["name"] != "Fix"]
        fields["Build"]["dataType"] = "NUMBER"
        fields["Size"]["options"] = fields["Size"]["options"][:-1] + [{"name": "XXL", "color": "RED"}]
        fields["Risk"]["options"][0]["color"] = "PINK"
        bad = failed(self.audit())
        self.assertTrue({"board.field.fix", "board.field.build.type", "board.field.size.values",
                         "board.field.risk.colors"} <= bad)

    def test_views_missing_extra_and_different(self):
        removed = self.fake.views.pop(0)["name"]
        self.fake.views.append(dict(self.fake.views[0], name="Mine"))
        self.fake.views[1]["layout"] = "TABLE_LAYOUT" if self.fake.views[1]["layout"] != "TABLE_LAYOUT" else "BOARD_LAYOUT"
        bad = failed(self.audit())
        self.assertIn(removed, [e["name"] for e in views.load_definition()])
        self.assertTrue({"board.views.present", "board.views.no-extra", "board.views.match"} <= bad)

    def test_tickets_that_break_rules(self):
        self.fake.items += [
            item(10, issue_type=None, Size="S", Status="ToDo"),
            item(11, Status="ToDo"),
            item(12, state="CLOSED", Size="S", Status="Review"),
            item(13, Size="S", Status="Completed", Resolution="Done"),
            item(14, Size="S", Status="InProgress", Resolution="Done"),
            item(15, Size="S", Status="InProgress", Origin="Backfilled"),
            item(16, Size="S", Status="InProgress", Version="V0.1.0"),
            item(17, title="Version 0.1.0", issue_type="Version", labels=()),
            item(18, issue_type="Alert", labels=(), Priority="High"),
            item(19, labels=(), Size="S", Status="ToDo"),
        ]
        bad = failed(self.audit())
        self.assertEqual({i[len("board.ticket."):] for i in bad},
                         {"type", "size", "closed-status", "open-status", "resolution", "backfilled-ref",
                          "version-form", "alert-priority", "area"})

    def test_a_legacy_version_ticket_breaks_no_rule_whatever_its_title(self):
        self.fake.items += [item(30, title="Version 1.25.4", issue_type="Version", labels=(), Status="Completed", Resolution="Done"),
                            item(31, title="Version 000.001.001", issue_type="Version", labels=())]
        self.assertEqual(failed(self.audit()), set())

    def test_the_details_list_every_ticket(self):
        self.fake.items += [item(n, "Ticket %d" % n, Status="ToDo") for n in range(11, 19)]
        check = next(c for c in self.audit().checks if c.id == "board.ticket.size")
        self.assertEqual(check.message, "8 ticket(s)")
        self.assertEqual(check.details, ["#%d Ticket %d - no Size" % (n, n) for n in range(11, 19)])

    def test_a_passed_ticket_check_says_how_many_were_examined(self):
        check = next(c for c in self.audit().checks if c.id == "board.ticket.size")
        self.assertEqual(check.result, audit_common.PASS)
        self.assertRegex(check.details[0], r"^\d+ ticket\(s\) on the board checked$")

    def test_a_different_view_says_what_differs(self):
        view = next(v for v in self.fake.views if v["visibleFields"]["nodes"])
        removed = view["visibleFields"]["nodes"].pop()["name"]
        view["filter"] = "is:open"
        check = next(c for c in self.audit().checks if c.id == "board.views.match")
        mine = [d for d in check.details if d.startswith("view %s:" % view["name"])]
        self.assertIn("view %s: column %s is missing" % (view["name"], removed), mine)
        self.assertTrue(any("filter is 'is:open', views.json wants" in d for d in mine))

    def test_throwaway_tickets_and_pull_requests_are_skipped(self):
        self.fake.items.append(item(20, labels=("dummy",), Status="ToDo"))
        self.fake.items.append({"content": {"__typename": "PullRequest"}})
        self.fake.items.append({"content": None})
        self.assertEqual(failed(self.audit()), set())

    def test_items_that_cannot_be_read(self):
        self.fake.down.add("items")
        self.assertIn("board.tickets", unknown(self.audit()))

    def test_pagination(self):
        pages = [{"pageInfo": {"hasNextPage": True, "endCursor": "c1"}, "nodes": [item(1, Size="S", Status="ToDo")]},
                 {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": [item(2, Status="ToDo")]}]
        seen = []

        def graphql(query, variables):
            seen.append(variables.get("after"))
            return {"node": {"items": pages[len(seen) - 1]}}

        items = audit_board.read_items(graphql, "B1")
        self.assertEqual([i["content"]["number"] for i in items], [1, 2])
        self.assertEqual(seen, [None, "c1"])

    def test_main(self):
        self.assertEqual(audit_board.main(["audit_board.py"]), 2)
        self.assertEqual(audit_board.main(["audit_board.py", ROOT, "--repo", "org/proj", "--board", "7"], self.fake), 0)
        self.fake.items.append(item(11, Status="ToDo"))
        self.assertEqual(audit_board.main(["audit_board.py", ROOT, "--repo", "org/proj"], self.fake), 1)


if __name__ == "__main__":
    unittest.main()
