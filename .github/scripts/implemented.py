"""Settle the tickets with Delivery "Implemented".

A ticket that changed no file has nothing in the changelog for the finalize step to find. A person
sets its Delivery to Implemented, with the Version it belongs to. At every finalize, at every scheduled
run and on a manual run, this sweep looks at the Implemented tickets:

- a blank Version gets the version being finalized (at a scheduled run, the latest finalized version);
- a Version that is already finalized is kept, put in the board form;
- a Version that is not finalized yet makes the ticket wait, quietly while a higher version is not finalized
  either; but when a higher version is already finalized, the aimed number was passed and can no longer
  happen, so the ticket would wait for ever: it gets Attention Caution and one comment, and a person decides
  (it is never moved by itself).

The ticket keeps Delivery Implemented and gets no Build; a release sets it to Released like a merged one.
Nothing is attached to anything: the Version field is the record. See the guide on project structure and
appendix C.
"""
import condition_comments
import failures
from versions import Version

ITEMS = ("query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){"
         "pageInfo{hasNextPage endCursor} nodes{id content{... on Issue{number title comments(last:30){nodes{body}}}} "
         "attention:fieldValueByName(name:\"Attention\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "delivery:fieldValueByName(name:\"Delivery\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "status:fieldValueByName(name:\"Status\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
         "version:fieldValueByName(name:\"Version\"){... on ProjectV2ItemFieldTextValue{text}}}}}}}")


def implemented_tickets(project_client, board):
    """The Implemented tickets on the board (an Abandoned ticket never shipped)."""
    found, after = [], None
    while True:
        page = project_client.graphql(ITEMS, {"id": board.id, "after": after})["node"]["items"]
        for node in page["nodes"]:
            content = node.get("content") or {}
            delivery = (node.get("delivery") or {}).get("name")
            status = (node.get("status") or {}).get("name")
            if delivery == "Implemented" and content.get("number") and status != "Abandoned":
                found.append({"item": node["id"], "number": content["number"], "title": content["title"],
                              "attention": (node.get("attention") or {}).get("name"),
                              "comments": [c.get("body") or "" for c in (content.get("comments") or {}).get("nodes") or []],
                              "version": (node.get("version") or {}).get("text") or ""})
        if not page["pageInfo"]["hasNextPage"]:
            return found
        after = page["pageInfo"]["endCursor"]


def flag_passed(run, repo_client, project_client, board, ticket, aimed, latest):
    """Raise Caution, once, on an Implemented ticket aimed at a version that was passed (it will never be finalized)."""
    number, marker = ticket["number"], f"<!-- attention:caution passed={aimed} -->"
    if ticket["attention"] in ("Caution", "AtRisk"):
        run.log.append(f"#{number}: waits for {aimed}, which was passed ({latest} is finalized); an Attention flag is already open")
        return
    if any(marker in body for body in ticket["comments"]):
        run.log.append(f"#{number}: waits for {aimed}, which was passed ({latest} is finalized); already flagged")
        return
    field = board.fields["Attention"]
    run.do(f"#{number}: waits for {aimed}, which was passed ({latest} is finalized): set Attention to Caution", project_client.set_project_field,
           board.id, ticket["item"], field["id"], {"singleSelectOptionId": field["options"]["Caution"]})
    run.do(f"#{number}: comment on the passed version", repo_client.comment, number,
           condition_comments.decorate(
               f"{marker}\nAttention: Caution. This ticket is Implemented and aimed at {aimed}, but {latest} is already finalized and {aimed} was "
               f"never released, so it can no longer happen and the ticket would wait for ever. Set its Version to the version it belongs to "
               f"(for example {latest}), or clear the Version: a blank Version gets the latest finalized version. The next scheduled run then "
               "settles it. Then tick a box below.", "passed-version"))


def sweep(run, repo_client, project_client, board, finalized, current_version, now):
    """Settle the Implemented tickets. `finalized` is the set of finalized Versions and `current_version` the version
    being finalized (or the latest, at a scheduled run). Returns the numbers of the tickets whose Version was set."""
    set_now = []
    for ticket in implemented_tickets(project_client, board):
        try:
            aimed = Version.parse(ticket["version"]) if ticket["version"] else current_version
        except ValueError:
            run.log.append(f"#{ticket['number']}: Version {ticket['version']!r} is not a version; left alone")
            continue
        if aimed not in finalized:
            latest = max(finalized, key=lambda v: v.number(), default=None)
            if latest is not None and latest.number() > aimed.number():
                flag_passed(run, repo_client, project_client, board, ticket, aimed, latest)
            else:
                run.log.append(f"#{ticket['number']}: waits for {aimed}, which is not finalized yet")
            continue
        if ticket["version"] != aimed.board():
            run.do(f"#{ticket['number']}: set Version to {aimed.board()}", project_client.set_project_field, board.id, ticket["item"],
                   board.fields["Version"]["id"], {"text": aimed.board()})
            set_now.append(ticket["number"])
    return set_now


def scheduled_sweep(root, repo_client, project_client, board, now, dry_run=False):
    """The scheduled run: settle the Implemented tickets without touching the changelog or main.

    The tickets are judged against the finalized versions in the changelog, and a blank Version gets the
    latest one, which is the version the work shipped with.
    """
    import changelog
    import finalize
    run = finalize.Runner(dry_run)
    with open(root + "/CHANGELOG.md", encoding="utf-8") as handle:
        finals = [s for s in changelog.parse(handle.read()) if s.kind == "final"]
    if not finals:
        run.log.append("no finalized version yet: nothing to settle")
        return run
    sweep(run, repo_client, project_client, board, {s.version for s in finals}, finals[0].version, now)
    return run


def main(argv=None):
    import os
    import sys
    import preflight
    import versions
    from github_api import Client, GitHubError
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
        print("Implemented sweep skipped: no board (the preflight did not identify one)")
        return 0
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    try:
        run = scheduled_sweep(root, repo_client, project_client, report.board, versions.utc_now(), "--dry-run" in args)
    except GitHubError as error:
        print(f"Implemented sweep stopped: {error}")
        failures.record(f"Implemented sweep stopped: {error}")
        return 0
    for line in run.log or ["no Implemented tickets waiting"]:
        print(("would: " if run.dry_run else "did: ") + line)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
