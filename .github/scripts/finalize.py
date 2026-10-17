"""The finalize step: after a merge to main, number the version and record it.

It decides the bump, renames the open WIP-Version heading in a commit of its own, sets the
Delivery, Version, Build of each ticket on the board, and settles the Implemented tickets. It
creates no ticket for the version: the changelog entry, the Version field of the tickets and,
for a release, the tag are the record.

Safe to run again: every step sets a value only when it differs, so a run with no open heading
checks the last version again. A board problem does not stop the version from being finalized.
`--dry-run` only reports what it would do. See the guide on syncing and merging (section 5).
"""
import os
import subprocess
import sys

import changelog
import check_manifest
import implemented
import preflight
import versions
from versions import Version
import failures
from github_api import Client, GitHubError

CHANGELOG = "CHANGELOG.md"

ITEM_QUERY = ("query($o:String!,$n:String!,$num:Int!){repository(owner:$o,name:$n){issue(number:$num){"
              "id title projectItems(first:20){nodes{id project{id} "
              "status:fieldValueByName(name:\"Status\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
              "delivery:fieldValueByName(name:\"Delivery\"){... on ProjectV2ItemFieldSingleSelectValue{name}} "
              "version:fieldValueByName(name:\"Version\"){... on ProjectV2ItemFieldTextValue{text}} "
              "build:fieldValueByName(name:\"Build\"){... on ProjectV2ItemFieldTextValue{text}} "
              "attention:fieldValueByName(name:\"Attention\"){... on ProjectV2ItemFieldSingleSelectValue{name}}"
              "}}}}}")


class Runner:
    """Records every action and performs it unless this is a dry run."""

    def __init__(self, dry_run=False):
        self.dry_run, self.log = dry_run, []

    def do(self, text, function=None, *args):
        self.log.append(text)
        if not self.dry_run and function:
            return function(*args)
        return None


def bump_reason(types_by_ticket, marker, first):
    if first:
        return "none, because the changelog had no earlier version: the first version is V0.1.0 whatever the ticket Types"
    if marker:
        return f"{versions.MARKERS[marker]}, forced with the `{marker}` marker"
    drivers = [n for n, t in types_by_ticket.items() if t in versions.SUB_TYPES]
    if drivers:
        return "sub, from the Type of " + ", ".join(f"#{n} ({types_by_ticket[n]})" for n in drivers)
    return "mod, from the ticket Types (no Feature or Enhancement)"


def ticket_builds(section):
    """For each ticket, the latest build stamp among the builds that mention it."""
    latest = {}
    for build in section.builds:
        for block in build.blocks:
            if block.kind == "ticket" and build.stamp and build.stamp > latest.get(block.number, ""):
                latest[block.number] = build.stamp
    return latest


def decide(sections, repo_client):
    """The version the open section will get, the tickets' Types, and the reason for the bump."""
    wip = changelog.open_section(sections)
    previous = changelog.latest_final(sections)
    types = {n: repo_client.issue_type(n) for n in (wip.ticket_numbers() if wip else [])}
    marker = wip.marker if wip else ""
    version = versions.next_version(previous.version if previous else None, [t for t in types.values() if t], marker or None)
    return version, types, bump_reason(types, marker, previous is None)


def board_item(project_client, board, number):
    """The issue's node id and title, and its item on the board with the current values (or None)."""
    owner, name = project_client.repo.split("/", 1)
    issue = project_client.graphql(ITEM_QUERY, {"o": owner, "n": name, "num": number})["repository"]["issue"]
    item = next((i for i in issue["projectItems"]["nodes"] if i["project"]["id"] == board.id), None)
    return issue, item


def _value(item, key, attribute):
    found = item.get(key) if item else None
    return found.get(attribute) if found else None


def update_ticket(run, project_client, board, number, version, build, delivery="Merged"):
    issue, item = board_item(project_client, board, number)
    if item is None:
        item_id = run.do(f"#{number}: add to the board", project_client.add_to_project, board.id, issue["id"])
        item = {"id": item_id or "(new)"}
    fields = board.fields
    wanted = []
    if _value(item, "status", "name") in ("ToDo", "OnDeck"):
        wanted.append(("Status", "InProgress", {"singleSelectOptionId": fields["Status"]["options"]["InProgress"]}))
    if _value(item, "delivery", "name") != delivery:
        wanted.append(("Delivery", delivery, {"singleSelectOptionId": fields["Delivery"]["options"][delivery]}))
    if _value(item, "version", "text") != version.board():
        wanted.append(("Version", version.board(), {"text": version.board()}))
    if build and _value(item, "build", "text") != build:
        wanted.append(("Build", build, {"text": build}))
    for name, shown, value in wanted:
        run.do(f"#{number}: set {name} to {shown}", project_client.set_project_field, board.id, item["id"], fields[name]["id"], value)


def commit_heading(root, version, push, manifest=False):
    def git(*args):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

    git("add", CHANGELOG, *([check_manifest.MANIFEST] if manifest else []))
    git("commit", "-m", f"Finalize {version}\n\nRenames the open WIP-Version heading to {version}, "
        "as the versioning automation does when a branch is merged."
        + (f" Sets the standard of the automation manifest to {version}." if manifest else ""))
    if push:
        git("push", "origin", "HEAD")  # not a bare push: a clone may have no upstream set


def recorded_bump(sections):
    """The bump of the topmost finalized version, read from the version before it (its marker is gone)."""
    finals = [s for s in sections if s.kind == "final"]
    if len(finals) < 2:
        return "none, because it is the first version"
    new, old = finals[0].version, finals[1].version
    kind = "major" if new.major > old.major else "sub" if new.sub > old.sub else "mod"
    return f"{kind}, from {old} to {new}"


def finalize(root, repo_client, project_client=None, board=None, now=None, dry_run=False, push=True):
    """Finalize the version of the latest merge. Returns the Runner, whose log lists every action."""
    run = Runner(dry_run)
    now = now or versions.utc_now()
    path = os.path.join(root, CHANGELOG)
    with open(path, encoding="utf-8", newline="") as handle:
        text = handle.read()
    sections = changelog.parse(text)
    wip = changelog.open_section(sections)
    previous = next((s for s in sections if s.kind == "final"), None)
    if wip is None and previous is None:
        run.log.append("nothing to finalize")
        return run
    if wip is not None:
        target = wip
        version, _, bump = decide(sections, repo_client)
        tickets = target.ticket_numbers()
        when = versions.heading_time(now)
    else:
        target, version, when = previous, previous.version, previous.time
        tickets = target.ticket_numbers()
        bump = recorded_bump(sections)
        run.log.append(f"no open WIP-Version heading: re-checking {version}")
    run.log.append(f"{version}: bump {bump}")
    if wip is not None:
        stamp = check_manifest.stamp_pending(root)

        def rename():
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(changelog.rename_open_heading(text, version, when))
            if stamp:
                check_manifest.set_standard(root, version)
            commit_heading(root, version, push, stamp)
        run.do(f"rename the open WIP-Version heading to {version} — {when} UTC" +
               (f", set the manifest standard to {version}" if stamp else "") + " and commit it", rename)
    builds = ticket_builds(target)
    if board is None or project_client is None:
        run.log.append("board steps skipped: no board (the preflight did not identify one)")
    else:
        for number in tickets:
            try:
                update_ticket(run, project_client, board, number, version, builds.get(number))
            except GitHubError as error:
                run.log.append(f"#{number}: board update skipped: {error}")
                failures.record(f"#{number}: board update skipped: {error}")
    if board is not None and project_client is not None:
        try:
            finalized = {s.version for s in sections if s.kind == "final"} | {version}
            implemented.sweep(run, repo_client, project_client, board, finalized, version, now)
        except GitHubError as error:
            run.log.append(f"Implemented tickets: sweep skipped: {error}")
            failures.record(f"Implemented tickets: sweep skipped: {error}")
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
    report = preflight.run(repo_client, project_client, store="--dry-run" not in args)
    print(report.render())
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
    run = finalize(root, repo_client, project_client, report.board,
                   dry_run="--dry-run" in args, push="--no-push" not in args)
    prefix = "would: " if run.dry_run else "did: "
    for line in run.log:
        print(prefix + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
