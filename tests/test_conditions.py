import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import conditions  # noqa: E402
import finalize  # noqa: E402
import preflight  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from versions import Version  # noqa: E402

HIGHEST = Version(0, 2, 0)  # the highest finalized version of the tickets below

FIX_IDS = ["completed-without-done", "abandoned-without-reason", "open-with-resolution", "open-with-end-date",
           "waiting-on-closed", "backfilled-without-ref", "completed-without-delivery", "shipped-without-version",
           "stale-plan", "issue-open", "issue-closed"]


def ticket(status="InProgress", **kwargs):
    """A ticket as board_tickets returns it, consistent unless a keyword breaks it."""
    base = {"item": "I1", "number": 1, "item_updated": "2026-10-01T00:00:00Z", "issue_updated": "2026-10-01T00:00:00Z",
            "state": "CLOSED" if status in ("Completed", "Abandoned") else "OPEN", "type": "Task", "comments": [],
            "status": status, "delivery": None, "resolution": None, "waiting": None, "origin": None, "attention": None,
            "ref": "", "version": "", "fix": "", "end": None}
    if status == "Completed":
        base.update(resolution="Done", delivery="Merged", version="V0.1.0")
    if status == "Abandoned":
        base.update(resolution="Invalid")
    base.update(kwargs)
    return base


class RegistryTests(unittest.TestCase):
    def test_ids_are_unique_and_the_fix_rules_are_the_eleven_of_the_guide_in_order(self):
        ids = [c.id for c in conditions.CONDITIONS]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual([c.id for c in conditions.FIX_RULES], FIX_IDS)

    def test_only_a_fix_rule_has_a_detector_and_every_condition_has_a_nature_and_text(self):
        for c in conditions.CONDITIONS:
            self.assertIn(c.nature, (conditions.DECIDE, conditions.FOLLOW_UP, conditions.FIX), c.id)
            self.assertEqual(c.detect is not None, c.nature == conditions.FIX, c.id)
            self.assertTrue(c.name and c.summary and c.detected_by and c.cleared_by, c.id)

    def test_a_decide_condition_has_an_attention_level_unless_it_is_an_alert(self):
        for c in conditions.CONDITIONS:
            if c.nature == conditions.DECIDE and c.id != "open-alert":
                self.assertIn(c.level, ("Watch", "Caution"), c.id)

    def test_the_three_natures_are_all_used(self):
        self.assertEqual({c.nature for c in conditions.CONDITIONS}, {"decide", "follow-up", "fix"})

    def test_the_lookup_by_id(self):
        self.assertIs(conditions.BY_ID["issue-open"], conditions.FIX_RULES[9])


class RuleTests(unittest.TestCase):
    def broken(self, **kwargs):
        return sorted(conditions.broken_rules(ticket(**kwargs), HIGHEST), key=FIX_IDS.index)

    def test_a_consistent_ticket_breaks_nothing(self):
        for status in ("ToDo", "OnDeck", "InProgress", "Review", "Suspended", "Completed", "Abandoned"):
            self.assertEqual(self.broken(status=status), [], status)

    def test_completed_needs_done_and_abandoned_needs_a_reason(self):
        self.assertEqual(self.broken(status="Completed", resolution=None), ["completed-without-done"])
        self.assertEqual(self.broken(status="Completed", resolution="Invalid"), ["completed-without-done"])
        self.assertEqual(self.broken(status="Abandoned", resolution=None), ["abandoned-without-reason"])
        self.assertEqual(self.broken(status="Abandoned", resolution="Done"), ["abandoned-without-reason"])

    def test_an_open_ticket_has_no_resolution_and_no_end_date(self):
        for status in conditions.OPEN:
            self.assertEqual(self.broken(status=status, resolution="Done"), ["open-with-resolution"], status)
            self.assertEqual(self.broken(status=status, end="2026-10-01"), ["open-with-end-date"], status)

    def test_waiting_only_on_open_tickets(self):
        self.assertEqual(self.broken(status="Completed", waiting="Needs input"), ["waiting-on-closed"])
        self.assertEqual(self.broken(status="Review", waiting="Needs input"), [])

    def test_a_backfilled_ticket_needs_its_ref(self):
        self.assertEqual(self.broken(origin="Backfilled"), ["backfilled-without-ref"])
        self.assertEqual(self.broken(origin="Backfilled", ref="20261001000000"), [])
        self.assertEqual(self.broken(origin="Backdated"), [])

    def test_completed_work_needs_a_delivery_but_bookkeeping_tickets_do_not(self):
        self.assertEqual(self.broken(status="Completed", delivery=None, version=""), ["completed-without-delivery"])
        self.assertEqual(self.broken(status="Completed", delivery=None, version="", type="Alert"), [])
        self.assertEqual(self.broken(status="Completed", delivery="Implemented", version="V0.1.0"), [])

    def test_shipped_work_needs_a_version_but_an_abandoned_ticket_is_left_out(self):
        for delivery in conditions.SHIPPED:
            self.assertEqual(self.broken(delivery=delivery, version=""), ["shipped-without-version"], delivery)
            self.assertEqual(self.broken(delivery=delivery, version="  "), ["shipped-without-version"], delivery)
        self.assertEqual(self.broken(status="Abandoned", delivery="Merged", version=""), [])
        self.assertEqual(self.broken(delivery="Merged", version="", type="Version"), [])
        self.assertEqual(self.broken(delivery="Pushed", version=""), [])

    def test_the_issue_is_closed_only_at_completed_or_abandoned(self):
        self.assertEqual(self.broken(status="Completed", state="OPEN"), ["issue-open"])
        self.assertEqual(self.broken(status="Abandoned", state="OPEN"), ["issue-open"])
        self.assertEqual(self.broken(status="Review", state="CLOSED"), ["issue-closed"])
        self.assertEqual(self.broken(status="ToDo", state="CLOSED"), ["issue-closed"])

    def test_two_broken_rules_are_both_reported_in_the_registry_order(self):
        self.assertEqual(self.broken(status="Completed", resolution=None, state="OPEN", delivery=None, version=""),
                         ["completed-without-done", "completed-without-delivery", "issue-open"])

    def test_a_ticket_without_progress_is_a_version_ticket_and_breaks_nothing(self):
        self.assertEqual(conditions.broken_rules(ticket(status=None, state="CLOSED", delivery="Merged", version="")), {})

    def test_an_alert_is_checked_like_any_ticket_except_for_the_delivery_rules(self):
        self.assertEqual(self.broken(status="Completed", type="Alert", resolution=None, delivery=None), ["completed-without-done"])

    def test_the_explanations_say_what_is_wrong(self):
        why = conditions.broken_rules(ticket(status="Review", resolution="Done"))["open-with-resolution"]
        self.assertIn("Review", why)
        self.assertIn("Done", why)

    def test_a_stale_plan_is_an_open_unshipped_ticket_with_a_version_at_or_below_the_highest_finalized(self):
        for version in ("V0.1.0", "V0.2.0", "V000.002.000", "V0.1.9-HF1"):
            self.assertEqual(self.broken(status="InProgress", version=version), ["stale-plan"], version)

    def test_a_version_above_the_highest_or_none_is_a_plan_that_can_still_happen(self):
        for version in ("V0.2.1", "V0.3.0", "V1.0.0", "V0.2.0-HF1", ""):
            self.assertEqual(self.broken(status="InProgress", version=version), [], version)

    def test_every_open_status_can_hold_a_stale_plan_and_a_closed_one_cannot(self):
        for status in ("ToDo", "OnDeck", "InProgress", "Review", "Suspended"):
            self.assertEqual(self.broken(status=status, version="V0.1.0"), ["stale-plan"], status)
        self.assertEqual(self.broken(status="Abandoned", version="V0.1.0"), [])
        self.assertEqual(self.broken(status="Completed", version="V0.1.0"), [])

    def test_shipped_work_is_not_a_plan_but_every_other_delivery_is(self):
        for delivery in ("Merged", "Implemented", "Released"):
            self.assertEqual(self.broken(status="Review", version="V0.1.0", delivery=delivery), [], delivery)
        for delivery in (None, "Committed", "Pushed", "Dropped"):
            self.assertEqual(self.broken(status="Review", version="V0.1.0", delivery=delivery), ["stale-plan"], delivery)

    def test_an_alert_and_a_legacy_version_ticket_are_not_plans(self):
        self.assertEqual(self.broken(status="InProgress", type="Alert", version="V0.1.0"), [])
        self.assertEqual(self.broken(status="InProgress", type="Version", version="V0.1.0"), [])

    def test_a_text_that_is_not_a_version_is_not_a_stale_plan(self):
        self.assertEqual(self.broken(status="InProgress", version="soon"), [])

    def test_without_the_highest_version_the_rule_is_skipped(self):
        self.assertEqual(conditions.broken_rules(ticket(status="InProgress", version="V0.1.0")), {})

    def test_a_plan_below_a_version_reached_by_a_major_marker_is_stale(self):
        found = conditions.broken_rules(ticket(status="InProgress", version="V0.16.0"), Version(1, 0, 0))
        self.assertEqual(list(found), ["stale-plan"])
        self.assertIn("V000.016.000", found["stale-plan"])
        self.assertIn("V001.000.000", found["stale-plan"])
        self.assertIn("clear the Version", found["stale-plan"])

    def test_the_stale_plan_gets_no_comment_and_a_commented_rule_does(self):
        class Repo:
            def __init__(self):
                self.posted = []

            def list_comments(self, number):
                return []

            def comment(self, number, body):
                self.posted.append(body)

        now = datetime(2026, 10, 17, tzinfo=timezone.utc)
        repo = Repo()
        conditions.sync_comments(finalize.Runner(), repo, ticket(status="InProgress", version="V0.1.0"), {"stale-plan": "x"}, now)
        self.assertEqual(repo.posted, [])
        conditions.sync_comments(finalize.Runner(), repo, ticket(status="Review", resolution="Done"), {"open-with-resolution": "y"}, now)
        self.assertEqual(len(repo.posted), 1)

    def test_comments_are_read_only_for_rules_that_can_have_one(self):
        self.assertFalse(conditions.needs_comments(ticket(fix="stale-plan"), {"stale-plan": "x"}))
        self.assertTrue(conditions.needs_comments(ticket(fix="stale-plan issue-open"), {"stale-plan": "x"}))
        self.assertTrue(conditions.needs_comments(ticket(), {"issue-open": "y"}))

    def test_the_highest_finalized_version_is_read_from_the_changelog(self):
        import tempfile

        def highest(text):
            with tempfile.TemporaryDirectory() as folder:
                if text is not None:
                    with open(os.path.join(folder, "CHANGELOG.md"), "w", encoding="utf-8", newline="") as handle:
                        handle.write(text)
                return conditions.highest_finalized(folder)

        entries = "## V0.2.0 — 2026-10-05 21:24 UTC\n### Build 20261005211638 (branch a)\n#### #4 — T\n- x.\n\n"
        older = "## V0.10.0 — 2026-10-09 08:30 UTC\n### Build 20261009083000 (branch a)\n#### #5 — T\n- x.\n"
        self.assertEqual(highest("# Changelog\n\n## WIP-Version\n### WIP-Build\n#### #9 — W\n- w.\n\n" + entries), Version(0, 2, 0))
        self.assertEqual(highest("# Changelog\n\n" + entries + older), Version(0, 10, 0))  # the highest, not the first
        self.assertIsNone(highest("# Changelog\n"))
        self.assertIsNone(highest(None))
        self.assertIsNone(highest("# Changelog\n\n## WIP-Version soon\n"))

    def test_the_fix_value_is_the_ids_in_registry_order_or_nothing(self):
        self.assertEqual(conditions.fix_value({}), "")
        self.assertEqual(conditions.fix_value({"issue-open": "x", "completed-without-done": "y"}), "completed-without-done issue-open")


def node(t):
    """The GraphQL item board_tickets reads, from a ticket dict."""
    pick = lambda value: {"name": value} if value else None  # noqa: E731
    text = lambda value: {"text": value} if value else None  # noqa: E731
    return {"id": t["item"], "updatedAt": t["item_updated"],
            "content": {"number": t["number"], "state": t["state"], "updatedAt": t["issue_updated"], "issueType": pick(t["type"]),
                        "comments": {"nodes": []}},
            "status": pick(t["status"]), "delivery": pick(t["delivery"]), "resolution": pick(t["resolution"]),
            "waiting": pick(t["waiting"]), "origin": pick(t["origin"]), "attention": pick(t["attention"]),
            "ref": text(t["ref"]), "version": text(t["version"]), "fix": text(t["fix"]),
            "end": {"date": t["end"]} if t["end"] else None}


class FakeProject:
    repo = "owner/repo"

    def __init__(self, tickets, page=100):
        self.nodes, self.page, self.sets, self.clears = [node(t) for t in tickets], page, [], []

    def graphql(self, query, variables=None):
        start = int(variables["after"] or 0)
        chunk = self.nodes[start:start + self.page]
        more = start + self.page < len(self.nodes)
        return {"node": {"items": {"pageInfo": {"hasNextPage": more, "endCursor": str(start + self.page)}, "nodes": chunk}}}

    def set_project_field(self, project_id, item_id, field_id, value):
        self.sets.append((item_id, field_id, value))

    def clear_project_field(self, project_id, item_id, field_id):
        self.clears.append((item_id, field_id))


def board(with_fix=True, with_resolution=False):
    fields = {"Fix": {"id": "FX", "type": "TEXT", "options": {}}} if with_fix else {}
    if with_resolution:
        fields["Resolution"] = {"id": "RS", "type": "SELECT", "options": {name: f"R-{name}" for name in ("Done", "Invalid", "Superseded")}}
    return preflight.Board("P7", 7, "Governance", fields)


class ResolutionTests(unittest.TestCase):
    """Resolution Done follows Status Completed: the refresh fills and clears it before the rules are judged."""

    def refresh(self, tickets, dry=False, with_resolution=True):
        project = FakeProject(tickets)
        run = finalize.Runner(dry)
        conditions.refresh(run, project, board(with_resolution=with_resolution), highest=HIGHEST)
        return project, run

    def test_a_completed_ticket_with_no_resolution_gets_done_and_no_flag(self):
        project, run = self.refresh([ticket(number=7, status="Completed", resolution=None)])
        self.assertEqual(project.sets, [("I1", "RS", {"singleSelectOptionId": "R-Done"})])
        self.assertEqual(project.clears, [])  # and nothing for the Fix field: the rule is judged after the fill
        self.assertIn("#7: set Resolution to Done (it is Completed)", run.log)

    def test_a_ticket_sent_back_loses_done_and_gets_no_flag(self):
        project, run = self.refresh([ticket(number=8, status="InProgress", resolution="Done")])
        self.assertEqual((project.sets, project.clears), ([], [("I1", "RS")]))
        self.assertIn("#8: clear Resolution (Done goes only with Completed, and it is InProgress)", run.log)

    def test_every_open_status_loses_a_done_set_by_hand(self):
        for status in ("ToDo", "OnDeck", "InProgress", "Review", "Suspended"):
            project, _ = self.refresh([ticket(status=status, resolution="Done")])
            self.assertEqual(project.clears, [("I1", "RS")], status)

    def test_a_completed_ticket_with_done_is_left_alone(self):
        project, run = self.refresh([ticket(status="Completed")])
        self.assertEqual((project.sets, project.clears, run.log), ([], [], []))

    def test_another_value_on_a_completed_ticket_is_not_replaced_but_flagged(self):
        project, _ = self.refresh([ticket(status="Completed", resolution="Invalid")])
        self.assertEqual(project.sets, [("I1", "FX", {"text": "completed-without-done"})])
        self.assertEqual(project.clears, [])

    def test_the_reason_of_an_abandoned_ticket_is_never_filled_or_cleared(self):
        project, _ = self.refresh([ticket(status="Abandoned", resolution="Superseded")])
        self.assertEqual((project.sets, project.clears), ([], []))
        project, _ = self.refresh([ticket(status="Abandoned", resolution=None)])
        self.assertEqual(project.sets, [("I1", "FX", {"text": "abandoned-without-reason"})])  # a person chooses the reason

    def test_done_on_an_abandoned_ticket_is_cleared_and_the_missing_reason_flagged(self):
        project, _ = self.refresh([ticket(status="Abandoned", resolution="Done")])
        self.assertEqual(project.clears, [("I1", "RS")])
        self.assertEqual(project.sets, [("I1", "FX", {"text": "abandoned-without-reason"})])

    def test_a_ticket_with_no_progress_is_left_alone(self):
        project, run = self.refresh([ticket(status=None, state="CLOSED", resolution="Done", delivery="Merged")])
        self.assertEqual((project.sets, project.clears, run.log), ([], [], []))

    def test_a_board_without_the_field_or_the_option_is_left_to_the_rules(self):
        project, _ = self.refresh([ticket(status="Completed", resolution=None)], with_resolution=False)
        self.assertEqual(project.sets, [("I1", "FX", {"text": "completed-without-done"})])

        class NoDone(FakeProject):
            pass

        project = NoDone([ticket(status="Completed", resolution=None)])
        no_done = board(with_resolution=True)
        del no_done.fields["Resolution"]["options"]["Done"]
        conditions.refresh(finalize.Runner(), project, no_done, highest=HIGHEST)
        self.assertEqual(project.sets, [("I1", "FX", {"text": "completed-without-done"})])

    def test_a_dry_run_reports_the_fill_and_writes_nothing(self):
        project, run = self.refresh([ticket(number=9, status="Completed", resolution=None)], dry=True)
        self.assertEqual((project.sets, project.clears), ([], []))
        self.assertIn("#9: set Resolution to Done (it is Completed)", run.log)

    def test_the_fill_and_the_flag_clear_do_not_disturb_the_fix_field_already_empty(self):
        project, _ = self.refresh([ticket(number=7, status="Completed", resolution=None, fix="")])
        self.assertEqual([call for call in project.sets if call[1] == "FX"], [])

    def test_a_fix_field_left_by_the_old_flag_is_cleared_once_the_resolution_is_filled(self):
        project, _ = self.refresh([ticket(number=7, status="Completed", resolution=None, fix="completed-without-done")])
        self.assertEqual(project.clears, [("I1", "FX")])
        self.assertEqual(project.sets, [("I1", "RS", {"singleSelectOptionId": "R-Done"})])


class RefreshTests(unittest.TestCase):
    def refresh(self, tickets, dry=False, with_fix=True, page=100, highest=HIGHEST):
        project = FakeProject(tickets, page)
        run = finalize.Runner(dry)
        changed = conditions.refresh(run, project, board(with_fix), highest=highest)
        return project, run, changed

    def test_a_stale_plan_is_written_to_the_fix_field(self):
        project, _, changed = self.refresh([ticket(number=7, status="InProgress", version="V0.1.0")])
        self.assertEqual((changed, project.sets), ([7], [("I1", "FX", {"text": "stale-plan"})]))

    def test_without_the_highest_version_no_plan_is_flagged(self):
        project, run, changed = self.refresh([ticket(number=7, status="InProgress", version="V0.1.0")], highest=None)
        self.assertEqual((changed, project.sets, run.log), ([], [], []))

    def test_a_plan_put_right_clears_the_field(self):
        project, _, changed = self.refresh([ticket(number=7, status="InProgress", version="V0.3.0", fix="stale-plan")])
        self.assertEqual((changed, project.clears), ([7], [("I1", "FX")]))

    def test_a_broken_ticket_gets_its_rules_in_the_fix_field(self):
        project, run, changed = self.refresh([ticket(number=5, status="Completed", resolution=None, state="OPEN")])
        self.assertEqual(changed, [5])
        self.assertEqual(project.sets, [("I1", "FX", {"text": "completed-without-done issue-open"})])
        self.assertEqual(project.clears, [])

    def test_a_fixed_ticket_is_cleared(self):
        project, run, changed = self.refresh([ticket(number=6, fix="issue-open")])
        self.assertEqual(changed, [6])
        self.assertEqual(project.clears, [("I1", "FX")])
        self.assertIn("clear Fix (was issue-open)", run.log[0])

    def test_nothing_is_written_when_the_field_already_says_it(self):
        project, run, changed = self.refresh([ticket(number=1, fix=""), ticket(number=2, status="Review", resolution="Done", fix="open-with-resolution")])
        self.assertEqual(changed, [])
        self.assertEqual((project.sets, project.clears, run.log), ([], [], []))

    def test_one_rule_put_right_and_another_still_broken_keeps_the_field_until_both_are(self):
        broken_two = ticket(number=3, status="Review", resolution="Done", end="2026-10-01", fix="open-with-resolution open-with-end-date")
        project, _, changed = self.refresh([dict(broken_two, resolution=None)])
        self.assertEqual(changed, [3])
        self.assertEqual(project.sets, [("I1", "FX", {"text": "open-with-end-date"})])
        project, _, changed = self.refresh([dict(broken_two, resolution=None, end=None)])
        self.assertEqual(project.clears, [("I1", "FX")])

    def test_a_dry_run_reports_and_writes_nothing(self):
        project, run, changed = self.refresh([ticket(number=5, status="Completed", resolution=None)], dry=True)
        self.assertEqual(changed, [5])
        self.assertEqual((project.sets, project.clears), ([], []))
        self.assertTrue(run.log[0].startswith("#5: set Fix to completed-without-done"))

    def test_without_the_field_nothing_is_written_and_the_log_says_how_to_create_it(self):
        project, run, changed = self.refresh([ticket(status="Completed", resolution=None)], with_fix=False)
        self.assertEqual((changed, project.sets), ([], []))
        self.assertIn("fields.py --apply", run.log[0])

    def test_version_tickets_are_left_alone_and_every_page_is_read(self):
        tickets = [ticket(number=n, item=f"I{n}", status="Review", resolution="Done") for n in range(1, 6)]
        tickets.append(ticket(number=9, item="I9", status=None, state="CLOSED", delivery="Merged", version=""))
        project, _, changed = self.refresh(tickets, page=2)
        self.assertEqual(changed, [1, 2, 3, 4, 5])
        self.assertEqual(len(project.sets), 5)

    def test_board_tickets_reads_the_current_fix_text_and_skips_items_that_are_not_issues(self):
        project = FakeProject([ticket(number=4, fix="issue-open")])
        project.nodes.append({"id": "PR", "updatedAt": "2026-10-01T00:00:00Z", "content": {}})
        tickets = conditions.board_tickets(project, board())
        self.assertEqual([(t["number"], t["fix"]) for t in tickets], [(4, "issue-open")])

    def test_main_needs_the_repository(self):
        saved = os.environ.pop("GITHUB_REPOSITORY", None)
        try:
            self.assertEqual(conditions.main([]), 1)
        finally:
            if saved is not None:
                os.environ["GITHUB_REPOSITORY"] = saved


if __name__ == "__main__":
    unittest.main()
