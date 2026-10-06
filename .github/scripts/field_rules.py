"""The Caution flags for broken field rules.

The rules that span fields (guide on project structure, section 4.4) are checked on every run:

- *Completed* has Resolution *Done*, and *Abandoned* has one of the abandon reasons.
- A ticket that is open (*ToDo*, *OnDeck*, *InProgress*, *Review*, *Suspended*) has no Resolution and no End date.
- Waiting is only on open tickets.
- A Backfilled ticket has its REF.
- The issue is closed only at *Completed* or *Abandoned*, and open otherwise.

A broken rule raises *Caution*, with one comment, only if the ticket (its issue and its board fields) has not
changed for five minutes, because fixing one takes several edits. The flag is set only on a ticket that is
blank, *Fine*, *Acknowledged* or *Watch* (a higher level replaces a lower one, nothing is lowered). It is
raised when a rule becomes broken and not again while it stays broken: after a person closed it, it comes
back only when a rule that was not named in the last flag is broken. The rules named are kept in a hidden
marker in the comment. Version and Alert tickets have no Attention. Appendix C, section 4.3.
`--dry-run` only reports.
"""
import os
import re
import sys
from datetime import timedelta

import finalize
import preflight
import versions
from github_api import Client, GitHubError
from watch import FLAG_MARKER, NO_ATTENTION, parse_time

OPEN = ("ToDo", "OnDeck", "InProgress", "Review", "Suspended")
CLOSED = ("Completed", "Abandoned")
REASONS = ("Duplicate", "Invalid", "WontFix", "Superseded", "Obsolete")
QUIET = timedelta(minutes=5)
RULES_MARKER = re.compile(r"<!-- attention:caution rules=(\S*) -->")

ITEMS = ("query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){"
         "pageInfo{hasNextPage endCursor} nodes{id updatedAt "
         "content{... on Issue{number state updatedAt issueType{name} comments(last:30){nodes{body}}}} "
         "status:fieldValueByName(name:\"Status\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "resolution:fieldValueByName(name:\"Resolution\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "waiting:fieldValueByName(name:\"Waiting\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "origin:fieldValueByName(name:\"Origin\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "attention:fieldValueByName(name:\"Attention\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "ref:fieldValueByName(name:\"REF\"){... on ProjectV2ItemFieldTextValue{text}} "
         "end:fieldValueByName(name:\"End date\"){... on ProjectV2ItemFieldDateValue{date}}}}}}}")


def board_tickets(project_client, board):
    found, after = [], None
    while True:
        page = project_client.graphql(ITEMS, {"id": board.id, "after": after})["node"]["items"]
        for node in page["nodes"]:
            content = node.get("content") or {}
            if not content.get("number"):
                continue

            def name(key):
                return (node.get(key) or {}).get("name")

            found.append({"item": node["id"], "number": content["number"], "item_updated": node["updatedAt"],
                          "issue_updated": content["updatedAt"], "state": content["state"],
                          "type": (content.get("issueType") or {}).get("name"),
                          "comments": (content.get("comments") or {}).get("nodes") or [],
                          "status": name("status"), "resolution": name("resolution"), "waiting": name("waiting"),
                          "origin": name("origin"), "attention": name("attention"),
                          "ref": (node.get("ref") or {}).get("text") or "",
                          "end": (node.get("end") or {}).get("date")})
        if not page["pageInfo"]["hasNextPage"]:
            return found
        after = page["pageInfo"]["endCursor"]


def violations(ticket):
    """The broken rules of a ticket as {rule id: explanation}."""
    status, broken = ticket["status"], {}
    if not status:
        return broken
    if status == "Completed" and ticket["resolution"] != "Done":
        broken["completed-without-done"] = "it is Completed but its Resolution is not Done"
    if status == "Abandoned" and ticket["resolution"] not in REASONS:
        broken["abandoned-without-reason"] = "it is Abandoned but its Resolution is not one of the abandon reasons"
    if status in OPEN and ticket["resolution"]:
        broken["open-with-resolution"] = f"it is open ({status}) but has the Resolution {ticket['resolution']}"
    if status in OPEN and ticket["end"]:
        broken["open-with-end-date"] = f"it is open ({status}) but has the End date {ticket['end']}"
    if status in CLOSED and ticket["waiting"]:
        broken["waiting-on-closed"] = f"it is {status} but Waiting is still set"
    if ticket["origin"] == "Backfilled" and not ticket["ref"]:
        broken["backfilled-without-ref"] = "its Origin is Backfilled but its REF is blank"
    if status in CLOSED and ticket["state"] == "OPEN":
        broken["issue-open"] = f"it is {status} but its issue is still open"
    if status not in CLOSED and ticket["state"] == "CLOSED":
        broken["issue-closed"] = f"its issue is closed but it is {status}"
    return broken


def last_change(ticket):
    return max(parse_time(ticket["item_updated"]), parse_time(ticket["issue_updated"]))


def named_before(ticket):
    """The rules named in the latest Caution comment about field rules, or None if there was none."""
    latest = None
    for comment in ticket["comments"]:
        match = RULES_MARKER.search(comment.get("body") or "")
        if match:
            latest = set(filter(None, match.group(1).split(",")))
    return latest


def comment_text(broken):
    listing = "; ".join(broken.values())
    return (f"{FLAG_MARKER}caution rules={','.join(sorted(broken))} -->\n"
            f"Attention: Caution. A field rule is broken on this ticket: {listing}. Correct the field or the issue, "
            "then set Attention to Fine, or to Acknowledged if it is handled elsewhere, and say what you decided.")


def sweep(run, repo_client, project_client, board, now):
    """Raise the Caution flags that are due. Returns the numbers of the tickets flagged."""
    flagged = []
    field = board.fields["Attention"]
    for ticket in board_tickets(project_client, board):
        if ticket["type"] in NO_ATTENTION or ticket["attention"] in ("Caution", "AtRisk"):
            continue
        broken = violations(ticket)
        if not broken or now - last_change(ticket) < QUIET:
            continue
        before = named_before(ticket)
        if before is not None and set(broken) <= before:
            continue  # the same broken rules, already flagged once
        number = ticket["number"]
        run.do(f"#{number}: set Attention to Caution ({', '.join(sorted(broken))})", project_client.set_project_field,
               board.id, ticket["item"], field["id"], {"singleSelectOptionId": field["options"]["Caution"]})
        run.do(f"#{number}: comment on the broken rules", repo_client.comment, number, comment_text(broken))
        flagged.append(number)
    return flagged


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = argv if argv is not None else sys.argv[1:]
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        print("GITHUB_REPOSITORY is not set")
        return 1
    repo_client = Client(os.environ.get("GITHUB_TOKEN", ""), repo)
    project_client = Client(os.environ.get("PROJECT_TOKEN", ""), repo)
    report = preflight.run(repo_client, project_client, store=False)
    print(report.render())
    if report.board is None:
        print("field-rule flags skipped: no board (the preflight did not identify one)")
        return 0
    run = finalize.Runner("--dry-run" in args)
    try:
        sweep(run, repo_client, project_client, report.board, versions.utc_now())
    except GitHubError as error:
        run.log.append(f"field-rule sweep stopped: {error}")
    for line in run.log or ["no broken field rules to flag"]:
        print(("would: " if run.dry_run else "did: ") + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
