"""Audit the project board and its tickets against the guides.

Reads, through the `gh` command line tool, the board linked to the repository: its fields and their values, its saved
views (against `.github/views.json`) and every ticket on it (issue type, Size, Status against open or closed, Resolution,
Origin and REF, the form of Version, the Version and Alert tickets). Read-only. It needs `gh` signed in with the `project`
scope; what it cannot read is reported as not-checkable. Throwaway tickets (label `dummy`) and pull requests are skipped.

Usage:
    python tools/audit_board.py <project-path> [--repo owner/name] [--board <number>] [--json <file>]

The repository is the origin remote of the project unless --repo says otherwise; the board is the first one linked to
it unless --board says otherwise. Prints the checks that are not a pass and exits 1 when a rule fails.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", ".github", "scripts"))

from audit_common import Report, RULE, RECOMMENDATION, remote_repo, format_report  # noqa: E402
import preflight  # noqa: E402
import views  # noqa: E402

LIMIT = 5
WORK_EXEMPT = ("Version", "Alert")
BOARD_VERSION = re.compile(r"^V\d{3}\.\d{3}\.\d{3}(-HF\d)?$")
VERSION_TITLE = re.compile(r"^Version \d{3}\.\d{3}\.\d{3}(-HF\d)?$")
FINISHED = ("Completed", "Abandoned")
SELECTS = ("Status", "Size", "Resolution", "Delivery", "Origin", "Priority")
TEXTS = ("REF", "Version")

LINKED = ("query($o:String!,$n:String!){repository(owner:$o,name:$n){projectsV2(first:20){nodes{id number title}}}}")
FIELDS = ("query($id:ID!){node(id:$id){... on ProjectV2{fields(first:50){nodes{"
          "... on ProjectV2Field{name dataType} "
          "... on ProjectV2SingleSelectField{name dataType options{name color description}}}}}}}")
VIEWS = ("query($id:ID!){node(id:$id){... on ProjectV2{views(first:50){nodes{id number name layout filter "
         "groupByFields(first:5){nodes{... on ProjectV2FieldCommon{name}}} "
         "verticalGroupByFields(first:5){nodes{... on ProjectV2FieldCommon{name}}} "
         "sortByFields(first:5){nodes{field{... on ProjectV2FieldCommon{name}} direction}} "
         "visibleFields(first:50){nodes{... on ProjectV2FieldCommon{name}}}}}}}}")
ITEMS = ("query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){"
         "pageInfo{hasNextPage endCursor} nodes{content{__typename ... on Issue{number title state "
         "issueType{name} labels(first:20){nodes{name}}}} "
         + " ".join("{0}:fieldValueByName(name:\"{0}\"){{... on ProjectV2ItemFieldSingleSelectValue{{name}}}}".format(n)
                    for n in SELECTS) + " "
         + " ".join("{0}:fieldValueByName(name:\"{0}\"){{... on ProjectV2ItemFieldTextValue{{text}}}}".format(n)
                    for n in TEXTS) + "}}}}}")


def run_graphql(query, variables):
    """Call `gh api graphql`; return the `data` object, or None when it fails (no `gh`, not signed in, no scope)."""
    args = ["gh", "api", "graphql", "-f", "query=" + query]

    for key, value in variables.items():
        args += ["-f", "{}={}".format(key, value)]

    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        payload = json.loads(result.stdout) if result.returncode == 0 and result.stdout.strip() else None
    except (OSError, ValueError):
        return None

    return payload.get("data") if isinstance(payload, dict) and not payload.get("errors") else None


def audit(repo, board_number=None, graphql=run_graphql, definition=None):
    report = Report("board")
    owner, name = repo.split("/", 1)
    data = graphql(LINKED, {"o": owner, "n": name})

    if data is None:
        report.add("board.linked", "10 section 6.2", RULE, "the board linked to the repository can be read", None,
                   "could not read the repository's boards: `gh` missing, not signed in, or without the `project` scope",
                   "run `gh auth refresh -s project`")
        return report

    boards = data["repository"]["projectsV2"]["nodes"]
    board = next((b for b in boards if board_number is None or b["number"] == board_number), None)
    report.add("board.linked", "10 section 6.2", RULE, "a board is linked to the repository", board is not None,
               "no board is linked to {}".format(repo), "link the project to the repository")

    if board is None:
        return report

    fields = graphql(FIELDS, {"id": board["id"]})
    fields = {f["name"]: f for f in fields["node"]["fields"]["nodes"] if f and f.get("name")} if fields else None
    check_fields(report, fields)
    check_views(report, graphql(VIEWS, {"id": board["id"]}), definition)
    items = read_items(graphql, board["id"])

    if items is None:
        report.add("board.tickets", "03 section 4", RULE, "the tickets can be read", None, "the board's items could not be read", "")
    else:
        check_tickets(report, items)

    return report


def check_fields(report, fields):
    guide = "10 section 6.2"

    if fields is None:
        report.add("board.fields", guide, RULE, "the board's fields can be read", None, "the fields could not be read", "")
        return

    for field_name, (kind, values) in preflight.REQUIRED_FIELDS.items():
        found = fields.get(field_name)
        ident = "board.field." + field_name.lower().replace(" ", "-")

        if found is None:
            report.add(ident, guide, RULE, "the field {} exists".format(field_name), False,
                       "the board has no field {}".format(field_name), "create it (fields.py does)")
            continue

        report.add(ident + ".type", guide, RULE, "{} is of the kind {}".format(field_name, kind),
                   found.get("dataType") == kind, "it is {}".format(found.get("dataType")),
                   "recreate it with the right kind (Build must be text, not a number)")

        if values is None:
            continue

        have = [o["name"] for o in found.get("options") or []]
        missing = [v for v in values if v not in have]
        extra = [v for v in have if v not in values]
        report.add(ident + ".values", guide, RULE, "{} has exactly its values".format(field_name),
                   not missing and not extra,
                   "missing: {}; extra: {}".format(", ".join(missing) or "none", ", ".join(extra) or "none"),
                   "correct the values by hand")
        wrong = [o["name"] for o in found.get("options") or []
                 if o["name"] in preflight.OPTION_COLORS and o.get("color") != preflight.OPTION_COLORS[o["name"]]]
        report.add(ident + ".colors", "Appendix C", RECOMMENDATION, "{} values have the standard colors".format(field_name),
                   not wrong, "other color: {}".format(", ".join(wrong)), "use the colors of Appendix C")


def check_views(report, data, definition=None):
    guide = "10 section 6.2"

    if data is None:
        report.add("board.views", guide, RULE, "the board's views can be read", None, "the views could not be read", "")
        return

    try:
        wanted = definition if definition is not None else views.load_definition()
    except views.ViewsError as error:
        report.add("board.views", guide, RULE, "the definition of the views can be read", None, str(error), "")
        return

    current = {v["name"]: views.current_state(v) for v in data["node"]["views"]["nodes"] if v}
    entries = wanted["views"] if isinstance(wanted, dict) else wanted
    missing = [e["name"] for e in entries if e["name"] not in current]
    report.add("board.views.present", guide, RULE, "the saved views of views.json exist", not missing,
               "missing: {}".format(", ".join(missing)), "run views.py --apply")
    extra = sorted(set(current) - set(e["name"] for e in entries))
    report.add("board.views.no-extra", guide, RECOMMENDATION, "the board has no views besides those of views.json",
               not extra, "extra: {}".format(", ".join(extra)), "delete them, or add them to views.json")
    differing = []

    for entry in entries:
        if entry["name"] in current:
            keys = views.differences(views.desired_state(entry), current[entry["name"]])

            if keys:
                differing.append("{} ({})".format(entry["name"], ", ".join(keys)))

    report.add("board.views.match", guide, RULE, "each view matches views.json", not differing,
               "differs: {}".format("; ".join(differing)), "run views.py --apply, or correct views.json")


def read_items(graphql, board_id):
    items, after = [], None

    while True:
        variables = {"id": board_id}

        if after:
            variables["after"] = after

        data = graphql(ITEMS, variables)

        if data is None:
            return None

        page = data["node"]["items"]
        items += page["nodes"]

        if not page["pageInfo"]["hasNextPage"]:
            return items

        after = page["pageInfo"]["endCursor"]


def ticket(node):
    """A ticket as a plain dict, or None for a pull request, a draft or a throwaway ticket."""
    content = node.get("content") or {}

    if content.get("__typename") != "Issue":
        return None

    labels = [l["name"] for l in (content.get("labels") or {}).get("nodes", [])]

    if "dummy" in labels:
        return None

    value = lambda key: ((node.get(key) or {}).get("name") or (node.get(key) or {}).get("text") or "").strip()
    result = {"number": content["number"], "title": content["title"], "open": content["state"] == "OPEN",
              "type": (content.get("issueType") or {}).get("name", ""), "labels": labels}

    for key in SELECTS + TEXTS:
        result[key.lower()] = value(key)

    return result


def check_tickets(report, items):
    tickets = [t for t in (ticket(n) for n in items) if t]
    work = [t for t in tickets if t["type"] not in WORK_EXEMPT]

    def listing(found):
        return "{} ticket(s): {}".format(len(found), ", ".join("#{}".format(t["number"]) for t in found[:LIMIT]))

    def add(ident, guide, strength, title, bad, hint):
        report.add("board.ticket." + ident, guide, strength, title, not bad, listing(bad) if bad else "", hint)

    add("type", "03 section 4.3", RULE, "every ticket has an issue type", [t for t in tickets if not t["type"]],
        "set its Type")
    add("size", "03 section 3", RULE, "every work ticket has a Size", [t for t in work if not t["size"]],
        "estimate it and set the Size")
    add("closed-status", "03 section 4.3", RULE, "a closed work ticket is Completed or Abandoned",
        [t for t in work if not t["open"] and t["status"] not in FINISHED], "set the Status, or reopen the ticket")
    add("open-status", "03 section 4.3", RULE, "an open work ticket is not Completed or Abandoned",
        [t for t in work if t["open"] and t["status"] in FINISHED], "close the issue, or move the Status back")
    add("resolution", "03 section 4.3", RULE, "Resolution is set exactly when a work ticket is Completed or Abandoned",
        [t for t in work if bool(t["resolution"]) != (t["status"] in FINISHED)],
        "set Resolution on finished tickets and clear it on open ones")
    add("backfilled-ref", "03 section 4.3", RULE, "a Backfilled ticket records its REF",
        [t for t in work if t["origin"] == "Backfilled" and not t["ref"]], "set the REF field")
    add("version-form", "03 section 4.3", RECOMMENDATION, "Version is written in the board form (V000.010.001)",
        [t for t in tickets if t["version"] and not BOARD_VERSION.match(t["version"])],
        "the next scheduled run rewrites it; or type the three-digit form")
    add("version-title", "03 section 5.2", RULE, "a Version ticket is titled `Version 000.010.001`",
        [t for t in tickets if t["type"] == "Version" and not VERSION_TITLE.match(t["title"])],
        "retitle it in the board form")
    add("alert-priority", "03 section 5.3", RULE, "an Alert has Priority Critical",
        [t for t in tickets if t["type"] == "Alert" and t["priority"] != "Critical"], "set the Priority to Critical")
    add("area", "03 section 4.3", RECOMMENDATION, "a work ticket has at least one Area label",
        [t for t in work if not t["labels"]], "add an Area label")


def main(argv, graphql=run_graphql):
    args = argv[1:]
    options = {}

    for flag in ("--repo", "--board", "--json"):
        if flag in args:
            i = args.index(flag)
            options[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]

    if len(args) != 1 or not os.path.isdir(args[0]):
        print(__doc__)
        return 2

    repo = options.get("--repo") or remote_repo(args[0])

    if not repo:
        report = Report("board")
        report.add("board.remote", "03 section 1", RULE, "the project has a GitHub remote", None,
                   "no github.com origin remote; pass --repo owner/name", "")
    else:
        number = int(options["--board"]) if options.get("--board") else None
        report = audit(repo, number, graphql)

    print(format_report(report))

    if options.get("--json"):
        with open(options["--json"], "w", encoding="utf-8") as f:
            json.dump(report.as_dict(), f, indent=2)

    return 1 if report.failures(RULE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
