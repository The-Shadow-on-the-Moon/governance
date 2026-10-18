"""Convert the legacy Version tickets of a board (guide 03, section 5.2).

Earlier versions of the standard made a ticket per finalized version, with the version's tickets attached to it as
sub-issues. This tool turns each one into a closed history record, so that the sub-issue of every ticket is free and the
board lists no ticket of a type that is no longer made. For each Version ticket it:

1. checks that every sub-issue has the Version the ticket names (a ticket where one differs is reported and left alone);
2. writes a comment with the old title, type, labels, Size, Delivery, Version, Status, Resolution, dates and the child
   list, and the same in a restore file in the state folder of the project;
3. retitles it `Legacy Version 001.025.004`, makes it a Task with the label `process`, Size XS;
4. clears Delivery and Version, sets the dates it had (before the Status, which can fill them), Resolution
   Superseded and Status Abandoned, and closes the issue as not planned;
5. detaches its sub-issues.

A ticket already converted (its title starts with `Legacy Version `) is skipped. An open Version ticket that was still
planned (not Completed) is reported for a decision and left alone, unless `--include-open` says to convert it. A dry
run unless `--apply`; `--only 12,14` converts just those tickets.

    python tools/convert_legacy.py <project-path> [--repo owner/name] [--apply] [--only N,N] [--include-open]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kit_common  # noqa: E402
from kit_common import KitError, finalize  # noqa: E402

import audit_common  # noqa: E402
import conditions  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402
from github_api import GitHubError  # noqa: E402

PREFIX = "Legacy Version "
TRIPLE = re.compile(r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})")
DATES = "query($i:ID!){node(id:$i){... on ProjectV2Item{start:fieldValueByName(name:\"Start date\"){... on ProjectV2ItemFieldDateValue{date}} end:fieldValueByName(name:\"End date\"){... on ProjectV2ItemFieldDateValue{date}}}}}"


def triple(text):
    """(major, sub, mod) of a version text in any of the forms the standard used, or None."""
    found = TRIPLE.search(text or "")
    return tuple(int(part) for part in found.groups()) if found else None


def legacy_title(title, version=""):
    """`Legacy Version 001.025.004` from the old title or, failing that, the Version field."""
    numbers = triple(title) or triple(version)
    return None if numbers is None else "{}{:03d}.{:03d}.{:03d}".format(PREFIX, *numbers)


def children(repo_client, number):
    found, page = [], 1

    while True:
        batch = repo_client.request("GET", repo_client.repo_path("/issues/{}/sub_issues?per_page=100&page={}".format(number, page))) or []
        found += batch

        if len(batch) < 100:
            return found

        page += 1


def plan_one(parent, titles, by_number, kids):
    """What to do with one Version ticket: ("skip", reason), ("decide", reason) or ("convert", None)."""
    if titles[parent["number"]].startswith(PREFIX):
        return "skip", "already converted"

    numbers = triple(titles[parent["number"]]) or triple(parent["version"])

    if numbers is None:
        return "decide", "no version can be read from its title or its Version field"

    if parent["state"] == "OPEN" and parent["status"] != "Completed":
        return "decide", "it is open and not Completed: a planned version? decide whether to convert it"

    wrong = []

    for kid in kids:
        item = by_number.get(kid["number"])
        have = triple(item["version"]) if item else None

        if have != numbers:
            wrong.append("#{} has Version {}".format(kid["number"], (item or {}).get("version") or "none"))

    if wrong:
        return "decide", "its sub-issues do not all have its Version ({}): {}".format("{}.{}.{}".format(*numbers), "; ".join(wrong))

    return "convert", None


def option(board, field, name):
    return board.fields[field]["options"][name]


def convert_one(run, repo_client, project_client, board, parent, kids, title, dates, source, root):
    number = parent["number"]
    before = {"number": number, "title": parent["title"], "type": parent["type"], "status": parent["status"], "delivery": parent["delivery"],
              "version": parent["version"], "resolution": parent["resolution"], "state": parent["state"], "labels": parent["labels"],
              "start": dates["start"], "end": dates["end"], "children": [k["number"] for k in kids]}
    run.do("#{}: comment the old values and the sub-issues {}".format(number, before["children"] or "(none)"), repo_client.comment, number,
           "Converted to a legacy record (guide 03, section 5.2). Before: " + json.dumps(before, ensure_ascii=False) + "\n\n"
           "The sub-issues " + (", ".join("#{}".format(k["number"]) for k in kids) or "(none)") + " are detached.")

    if not run.dry_run:
        with open(kit_common.state_path(root, "convert-legacy-{}.json".format(number)), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(before, handle, indent=1)
            handle.write("\n")

    issue = {"title": title, "labels": sorted(set(parent["labels"]) | {"process"})}

    if source != ticket_type.FIELD_SOURCE:
        issue["type"] = "Task"

    run.do("#{}: retitle to \"{}\", make it a Task with the label process".format(number, title), repo_client.request, "PATCH",
           repo_client.repo_path("/issues/{}".format(number)), issue)

    if source == ticket_type.FIELD_SOURCE:
        ticket_type.set_kind(run, project_client, board, parent["item"], "Task", "#{}".format(number))

    item = parent["item"]
    set_choice = lambda field, value: run.do("#{}: set {} to {}".format(number, field, value), project_client.set_project_field,  # noqa: E731
                                              board.id, item, board.fields[field]["id"], {"singleSelectOptionId": option(board, field, value)})
    clear = lambda field: run.do("#{}: clear {}".format(number, field), project_client.clear_project_field, board.id, item,  # noqa: E731
                                 board.fields[field]["id"]) if parent[field.lower()] else None
    set_choice("Size", "XS")
    clear("Delivery")
    clear("Version")

    for field, key in (("Start date", "start"), ("End date", "end")):
        if dates[key] and field in board.fields:
            run.do("#{}: keep the {} {}".format(number, field.lower(), dates[key]), project_client.set_project_field, board.id, item,
                   board.fields[field]["id"], {"date": dates[key]})

    set_choice("Resolution", "Superseded")
    set_choice("Status", "Abandoned")

    if parent["state"] == "OPEN":
        run.do("#{}: close as not planned".format(number), repo_client.close_issue, number, "not_planned")

    for kid in kids:
        run.do("#{}: detach the sub-issue #{}".format(number, kid["number"]), repo_client.request, "DELETE",
               repo_client.repo_path("/issues/{}/sub_issue".format(number)), {"sub_issue_id": kid["id"]})


def read_dates(project_client, item):
    node = project_client.graphql(DATES, {"i": item})["node"]
    return {"start": (node.get("start") or {}).get("date"), "end": (node.get("end") or {}).get("date")}


def convert(repo_client, project_client, board, tickets, source, root, dry_run=True, only=None, include_open=False):
    """Convert the legacy Version tickets. Returns (Runner, decisions) where decisions lists the tickets left for the person."""
    run = finalize.Runner(dry_run)
    by_number = {t["number"]: t for t in tickets}
    decisions, converted = [], 0

    for parent in sorted((t for t in tickets if t["type"] == "Version"), key=lambda t: t["number"]):
        if only is not None and parent["number"] not in only:
            continue

        issue = repo_client.request("GET", repo_client.repo_path("/issues/{}".format(parent["number"])))
        parent = dict(parent, title=issue["title"], labels=[l["name"] for l in issue.get("labels", [])])
        kids = children(repo_client, parent["number"])
        verdict, reason = plan_one(parent, {parent["number"]: parent["title"]}, by_number, kids)

        if verdict == "decide" and include_open and reason.startswith("it is open"):
            verdict, reason = plan_one(dict(parent, state="CLOSED"), {parent["number"]: parent["title"]}, by_number, kids)

        if verdict == "skip":
            run.log.append("#{}: {}".format(parent["number"], reason))
        elif verdict == "decide":
            decisions.append({"number": parent["number"], "reason": reason})
            run.log.append("#{}: left alone, needs a decision: {}".format(parent["number"], reason))
        else:
            title = legacy_title(parent["title"], parent["version"])
            convert_one(run, repo_client, project_client, board, parent, kids, title, read_dates(project_client, parent["item"]), source, root)
            converted += 1

    run.log.append("{} ticket(s) converted, {} left for a decision".format(converted, len(decisions)))
    return run, decisions


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])

    try:
        if not args or args[0].startswith("--"):
            raise KitError("usage: python tools/convert_legacy.py <project-path> [--repo owner/name] [--apply] [--only N,N] [--include-open]")

        root = os.path.abspath(args[0])
        repo = kit_common.option(args, "--repo") or audit_common.remote_repo(root)

        if not repo:
            raise KitError("the origin remote of {} is not a GitHub repository: say it with --repo owner/name".format(root))

        only = kit_common.option(args, "--only")
        only = {int(n) for n in only.split(",")} if only else None
        repo_client, project_client = kit_common.connect(repo)
        report = preflight.run(repo_client, project_client, store=False)

        if report.board is None:
            raise KitError("no usable board: " + report.render().replace(chr(10), "; "))

        tickets = conditions.board_tickets(project_client, report.board)
        run, decisions = convert(repo_client, project_client, report.board, tickets, report.type_source, root, "--apply" not in args, only,
                                 "--include-open" in args)
    except (KitError, GitHubError, ValueError) as error:
        print("convert refused: {}".format(error))
        return 1

    kit_common.print_run(run)

    if not run.dry_run:
        print("log: {}".format(kit_common.save_log(root, "convert-legacy", run, {"decisions": decisions})))

    return 0


if __name__ == "__main__":
    sys.exit(main())
