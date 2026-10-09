"""The Caution flags for broken field rules.

The rules that span fields (guide on project structure, section 4.4) are checked on every run:

- *Completed* has Resolution *Done*, and *Abandoned* has one of the abandon reasons.
- A ticket that is open (*ToDo*, *OnDeck*, *InProgress*, *Review*, *Suspended*) has no Resolution and no End date.
- Waiting is only on open tickets.
- A Backfilled ticket has its REF.
- The issue is closed only at *Completed* or *Abandoned*, and open otherwise.
- A *Completed* work ticket has a Delivery (*Merged* if files changed, *Implemented* if none did); Version and
  Alert tickets are not work tickets.
- Shipped work (Delivery *Merged*, *Implemented* or *Released*) has a Version. The scheduled run gives a blank Version to an
  *Implemented* ticket and the finalize step to a *Merged* one, so a ticket still without one two hours later means a step
  failed. An *Abandoned* ticket never shipped and is left out.

A broken rule raises *Caution*, with one comment, only if the ticket (its issue and its board fields) has not
changed for five minutes, because fixing one takes several edits (two hours for the rules in `WAIT`, which a
person may be in the middle of completing). The flag is set only on a ticket that is
blank, *Fine*, *Acknowledged* or *Watch* (a higher level replaces a lower one, nothing is lowered). It is
raised when a rule becomes broken and not again while it stays broken: after a person closed it, it comes
back only when a rule that was not named in the last flag is broken. The rules named are kept in a hidden
marker in the comment. Version and Alert tickets have no Attention. Appendix C, section 4.3.
The rules themselves, and the Fix field that shows them live, are in `conditions.py`. `--dry-run` only reports.
"""
import os
import re
import sys
from datetime import timedelta

import finalize
import preflight
import versions
from conditions import (CLOSED, ITEMS, OPEN, REASONS, SHIPPED, board_tickets,  # noqa: F401 (re-exported: the rules live in conditions.py)
                        broken_rules as violations)
from github_api import Client, GitHubError
from watch import FLAG_MARKER, NO_ATTENTION, parse_time

QUIET = timedelta(minutes=5)
WAIT = {"completed-without-delivery": timedelta(hours=2), "shipped-without-version": timedelta(hours=2)}  # rules that wait longer than QUIET
RULES_MARKER = re.compile(r"<!-- attention:caution rules=(\S*) -->")


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
        idle = now - last_change(ticket)
        broken = {rule: why for rule, why in violations(ticket).items() if idle >= WAIT.get(rule, QUIET)}
        if not broken:
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
