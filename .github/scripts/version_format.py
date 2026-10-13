"""The sweep for the board form of Version.

The board's Version field holds a version with three digits for each of V, s and m (`V000.010.001`), so that the
text sorts as the versions do, in a plain table, in a group and in the hierarchy. Everywhere else a version keeps
its short form (`V0.10.1`: the changelog, the tags, the branch names). A person may type a version in either form
into the field, and the finalize step writes the board form. So the scheduled run puts the board form into the
Version field of every ticket whose Version is a version and is written differently. It changes nothing else.
A Version that is not a version (any other text) is reported and skipped. Alert tickets are left alone; the
Version tickets are included, and so is their title's form, which the finalize step writes.

See appendix C and the guide on project structure (section 4.3). `--dry-run` only reports.
"""
import os
import sys

import finalize
import preflight
import failures
import ticket_type
from github_api import Client, GitHubError
from versions import Version, VersionError

SKIPPED_TYPES = ("Alert",)

ITEMS = ("query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){"
         "pageInfo{hasNextPage endCursor} nodes{id " + ticket_type.SELECTION + "content{... on Issue{number issueType{name}}} "
         "version:fieldValueByName(name:\"Version\"){... on ProjectV2ItemFieldTextValue{text}}}}}}}")


def board_items(project_client, board):
    """Every issue on the board with its Version (draft items and pull requests are skipped)."""
    found, after = [], None
    while True:
        page = project_client.graphql(ITEMS, {"id": board.id, "after": after})["node"]["items"]
        for node in page["nodes"]:
            content = node.get("content") or {}
            if not content.get("number"):
                continue
            found.append({"item": node["id"], "number": content["number"],
                          "type": ticket_type.of_node(node, content),
                          "version": ((node.get("version") or {}).get("text") or "").strip()})
        if not page["pageInfo"]["hasNextPage"]:
            return found
        after = page["pageInfo"]["endCursor"]


def sweep(run, project_client, board):
    """Put the Version of each ticket in the board form."""
    field = board.fields["Version"]["id"]
    for ticket in board_items(project_client, board):
        if ticket["type"] in SKIPPED_TYPES or not ticket["version"]:
            continue
        number = ticket["number"]
        try:
            wanted = Version.parse(ticket["version"]).board()
        except VersionError:
            run.log.append(f"#{number}: Version {ticket['version']!r} is not a version, so it was left as it is")
            continue
        if ticket["version"] != wanted:
            run.do(f"#{number}: set Version to {wanted} (was {ticket['version']})", project_client.set_project_field,
                   board.id, ticket["item"], field, {"text": wanted})
    return run


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
        print("Version-form sweep skipped: no board (the preflight did not identify one)")
        return 0
    run = finalize.Runner("--dry-run" in args)
    try:
        sweep(run, project_client, report.board)
    except GitHubError as error:
        run.log.append(f"Version-form sweep stopped: {error}")
        failures.record(f"Version-form sweep stopped: {error}")
    for line in run.log or ["no Version to put in the board form"]:
        print(line if "is not a version" in line else ("would: " if run.dry_run else "did: ") + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
