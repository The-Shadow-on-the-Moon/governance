import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import field_rules  # noqa: E402
import finalize  # noqa: E402
import preflight  # noqa: E402

NOW = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)


def ago(minutes):
    return (NOW - timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def ticket(number, status, resolution=None, state=None, waiting=None, origin=None, ref=None, end=None, attention=None,
           kind="Task", quiet=60, comments=(), issue_quiet=None):
    if state is None:
        state = "CLOSED" if status in ("Completed", "Abandoned") else "OPEN"
    pick = lambda value: {"name": value} if value else None  # noqa: E731
    return {"id": f"I{number}", "updatedAt": ago(quiet),
            "content": {"number": number, "state": state, "updatedAt": ago(quiet if issue_quiet is None else issue_quiet),
                        "issueType": pick(kind), "comments": {"nodes": [{"body": b} for b in comments]}},
            "status": pick(status), "resolution": pick(resolution), "waiting": pick(waiting), "origin": pick(origin),
            "attention": pick(attention), "ref": {"text": ref} if ref else None, "end": {"date": end} if end else None}


class FakeProject:
    repo = "owner/repo"

    def __init__(self, nodes, per_page=100):
        self.nodes, self.per_page, self.sets = nodes, per_page, []

    def graphql(self, query, variables=None):
        start = int(variables["after"] or 0)
        end = start + self.per_page
        return {"node": {"items": {"pageInfo": {"hasNextPage": end < len(self.nodes), "endCursor": str(end)},
                                   "nodes": self.nodes[start:end]}}}

    def set_project_field(self, project_id, item_id, field_id, value):
        self.sets.append((item_id, field_id, value["singleSelectOptionId"]))


class FakeRepo:
    repo = "owner/repo"

    def __init__(self):
        self.comments = []

    def comment(self, number, body):
        self.comments.append((number, body))


def board():
    fields = {name: {"id": f"F-{name}", "type": kind, "options": {v: f"{name}-{v}" for v in (values or [])}}
              for name, (kind, values) in preflight.REQUIRED_FIELDS.items()}
    return preflight.Board("P7", 7, "Governance", fields)


def sweep(nodes, dry_run=False):
    run, repo, project = finalize.Runner(dry_run), FakeRepo(), FakeProject(nodes)
    flagged = field_rules.sweep(run, repo, project, board(), NOW)
    return run, repo, project, flagged


def rules(**kwargs):
    return sorted(field_rules.violations(field_rules.board_tickets(FakeProject([ticket(1, **kwargs)]), board())[0]))


class RuleTests(unittest.TestCase):
    def test_a_consistent_ticket_breaks_nothing(self):
        for fields in (dict(status="ToDo"), dict(status="InProgress"), dict(status="Review"),
                       dict(status="Completed", resolution="Done"), dict(status="Abandoned", resolution="Obsolete"),
                       dict(status="Suspended"), dict(status="Review", waiting="Needs input"),
                       dict(status="InProgress", origin="Backfilled", ref="20261006091500")):
            self.assertEqual(rules(**fields), [], fields)

    def test_completed_needs_done(self):
        self.assertEqual(rules(status="Completed"), ["completed-without-done"])
        self.assertEqual(rules(status="Completed", resolution="Duplicate"), ["completed-without-done"])

    def test_abandoned_needs_a_reason(self):
        self.assertEqual(rules(status="Abandoned"), ["abandoned-without-reason"])
        self.assertEqual(rules(status="Abandoned", resolution="Done"), ["abandoned-without-reason"])
        for reason in field_rules.REASONS:
            self.assertEqual(rules(status="Abandoned", resolution=reason), [])

    def test_open_tickets_have_no_resolution_or_end_date(self):
        for status in field_rules.OPEN:
            self.assertEqual(rules(status=status, resolution="Done"), ["open-with-resolution"])
            self.assertEqual(rules(status=status, end="2026-10-01"), ["open-with-end-date"])

    def test_waiting_only_on_open_tickets(self):
        self.assertEqual(rules(status="Completed", resolution="Done", waiting="Needs input"), ["waiting-on-closed"])
        self.assertEqual(rules(status="Abandoned", resolution="Invalid", waiting="Needs input"), ["waiting-on-closed"])

    def test_a_backfilled_ticket_needs_its_ref(self):
        self.assertEqual(rules(status="InProgress", origin="Backfilled"), ["backfilled-without-ref"])
        self.assertEqual(rules(status="InProgress", origin="Backdated"), [])

    def test_the_issue_is_closed_only_when_the_ticket_is(self):
        self.assertEqual(rules(status="Completed", resolution="Done", state="OPEN"), ["issue-open"])
        self.assertEqual(rules(status="Abandoned", resolution="WontFix", state="OPEN"), ["issue-open"])
        self.assertEqual(rules(status="Review", state="CLOSED"), ["issue-closed"])

    def test_a_ticket_with_no_progress_has_no_rules_to_break(self):
        self.assertEqual(rules(status=None, resolution="Done"), [])

    def test_several_rules_at_once(self):
        self.assertEqual(rules(status="Completed", state="OPEN"), ["completed-without-done", "issue-open"])


class SweepTests(unittest.TestCase):
    def test_a_broken_rule_raises_caution_with_one_comment(self):
        _, repo, project, flagged = sweep([ticket(1, "Completed", state="OPEN")])
        self.assertEqual(flagged, [1])
        self.assertEqual(project.sets, [("I1", "F-Attention", "Attention-Caution")])
        text = repo.comments[0][1]
        self.assertTrue(text.startswith("<!-- attention:caution rules=completed-without-done,issue-open -->\n"))
        self.assertIn("it is Completed but its Resolution is not Done; it is Completed but its issue is still open", text)

    def test_nothing_while_the_ticket_is_still_being_edited(self):
        self.assertEqual(sweep([ticket(1, "Completed", quiet=4)])[3], [])
        self.assertEqual(sweep([ticket(1, "Completed", quiet=60, issue_quiet=2)])[3], [])
        self.assertEqual(sweep([ticket(1, "Completed", quiet=5)])[3], [1])

    def test_a_flag_that_is_open_is_not_raised_again(self):
        for attention in ("Caution", "AtRisk"):
            self.assertEqual(sweep([ticket(1, "Completed", attention=attention)])[3], [], attention)

    def test_caution_replaces_a_lower_flag_and_a_closed_one(self):
        for attention in (None, "Fine", "Acknowledged", "Watch"):
            self.assertEqual(sweep([ticket(1, "Completed", attention=attention)])[3], [1], attention)

    def test_not_raised_again_for_the_same_rules_after_a_person_closed_it(self):
        earlier = ["<!-- attention:caution rules=completed-without-done,issue-open -->\nAttention: Caution. ..."]
        stuck = ticket(1, "Completed", state="OPEN", attention="Fine", comments=earlier)
        self.assertEqual(sweep([stuck])[3], [])
        fewer = ticket(1, "Completed", state="CLOSED", attention="Fine", comments=earlier)  # one of them put right
        self.assertEqual(sweep([fewer])[3], [])

    def test_raised_again_when_a_different_rule_is_broken(self):
        earlier = ["<!-- attention:caution rules=completed-without-done -->\nAttention: Caution. ..."]
        worse = ticket(1, "Completed", waiting="Needs input", attention="Acknowledged", comments=earlier)
        run, repo, _, flagged = sweep([worse])
        self.assertEqual(flagged, [1])
        self.assertIn("rules=completed-without-done,waiting-on-closed", repo.comments[0][1])

    def test_the_push_steps_caution_comment_is_not_a_rules_comment(self):
        push_comment = ["<!-- attention:caution -->\nAttention: Caution. New work arrived on this ticket."]
        self.assertEqual(sweep([ticket(1, "Completed", attention="Fine", comments=push_comment)])[3], [1])

    def test_version_and_alert_tickets_are_skipped(self):
        self.assertEqual(sweep([ticket(1, "Completed", kind="Version"), ticket(2, "Review", kind="Alert", state="CLOSED")])[3], [])

    def test_dry_run_changes_nothing(self):
        run, repo, project, _ = sweep([ticket(1, "Completed")], dry_run=True)
        self.assertEqual((repo.comments, project.sets), ([], []))
        self.assertEqual(len(run.log), 2)

    def test_every_page_is_read_and_draft_items_skipped(self):
        nodes = [ticket(n, "ToDo") for n in range(1, 230)] + [ticket(500, "Completed"), {"id": "D", "updatedAt": ago(60), "content": {}}]
        self.assertEqual(sweep(nodes)[3], [500])


if __name__ == "__main__":
    unittest.main()
