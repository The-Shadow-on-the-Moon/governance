"""The adoption plan: the open findings of an audit, grouped by the stage of guide 11 that deals with them.

The audit reports what differs; this says in what order to deal with it. The class, the stage, the role and whether
the change can be undone come from the tables of appendix G (the guide's own list of every finding), read from this
repository, so the plan and the guide cannot differ. A finding with no row there is listed under "no stage".

Only checks that failed are planned; the ones that could not be made are listed apart, as "to confirm". Accepted
deviations (the baseline) and passes are not part of the plan.
"""
import os
import re

from audit_common import FAIL, NOT_CHECKABLE, RULE, STANDARD, read

APPENDIX = os.path.join(STANDARD, "guides", "appendix-g-audit-findings-and-fixes.md")
ROW = re.compile(r"^\| `([^`]+)` \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| ([^|]+?) \| (.+) \|$")

# the headings of guide 11, section 4 (a test keeps them in step)
STAGES = {
    1: "GitHub settings",
    2: "the adoption branch, files and automation",
    3: "token, board and preflight",
    4: "git names, branches and tags",
    5: "the tickets",
    6: "land and prove",
    7: "keep it",
}
NO_STAGE = "not part of a stage"


def appendix_rows(path=APPENDIX):
    """The rows of appendix G: [(pattern for the id, class, stage or None, role, undo)]."""
    rows = []

    for line in (read(path) or "").splitlines():
        match = ROW.match(line)

        if not match:
            continue

        ident, kind, stage, role, undo, _ = match.groups()
        pattern = re.compile("^" + re.escape(ident).replace(re.escape("<field>"), "[^.]+") + "$")
        rows.append((pattern, kind, int(stage) if stage.isdigit() else None, role, undo))

    return rows


def plan(reports, rows=None):
    """The plan as [{stage, name, findings: [{id, title, strength, class, role, undo, count}]}], in stage order, with
    the group of findings that need no stage last and the checks to confirm in a group of their own ("to confirm")."""
    rows = appendix_rows() if rows is None else rows
    groups = {}
    confirm = []

    for report in reports:
        for check in report.checks:
            if check.result not in (FAIL, NOT_CHECKABLE):
                continue

            row = next((r for r in rows if r[0].match(check.id)), None)
            finding = {"id": check.id, "title": check.title, "strength": check.strength,
                       "class": row[1] if row else "", "role": row[3] if row else "", "undo": row[4] if row else "",
                       "count": len(check.details)}

            if check.result == NOT_CHECKABLE:
                confirm.append(finding)
            else:
                groups.setdefault(row[2] if row else None, []).append(finding)

    result = []

    for stage in sorted(s for s in groups if s is not None):
        result.append({"stage": stage, "name": STAGES.get(stage, ""), "findings": order(groups[stage])})

    if None in groups:
        result.append({"stage": None, "name": NO_STAGE, "findings": order(groups[None])})

    if confirm:
        result.append({"stage": None, "name": "to confirm (could not be checked)", "findings": order(confirm)})

    return result


def order(findings):
    """Rules before recommendations, the order of the report otherwise."""
    return sorted(findings, key=lambda f: f["strength"] != RULE)


def heading(group):
    return "Stage {}: {}".format(group["stage"], group["name"]) if group["stage"] else group["name"].capitalize()


def format_text(groups):
    """The plan as lines of text for the screen."""
    if not groups:
        return []

    lines = ["== adoption plan (guide 11, with appendix G) =="]

    for group in groups:
        lines.append(heading(group))

        for f in group["findings"]:
            lines.append("  - {} ({}{}{}{})".format(
                f["id"], f["strength"], ", " + f["class"] if f["class"] else "", ", " + f["role"] if f["role"] else "",
                ", undo: " + f["undo"] if f["undo"] else ""))

    return lines


def format_markdown(groups):
    """The plan as Markdown lines: a heading per stage, a table of its findings."""
    if not groups:
        return []

    lines = ["", "## Adoption plan", "",
             "The open findings in the order of the stages of guide 11. What to do about each is in appendix G."]

    for group in groups:
        lines += ["", "### " + heading(group), "", "| Id | Strength | Class | Role | Undo | Check |", "|---|---|---|---|---|---|"]
        lines += ["| `{}` | {} | {} | {} | {} | {} |".format(f["id"], f["strength"], f["class"], f["role"], f["undo"],
                                                          f["title"].replace("|", "\\|")) for f in group["findings"]]

    return lines
