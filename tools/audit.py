"""Audit an existing project against the guides: the files, the git history, the GitHub settings and the board.

Runs the four audits (audit_files.py, audit_git.py, audit_github.py and audit_board.py) on a project and prints one
report. Each check says whether the project follows a rule or a recommendation of the guides, with the guide section and
a hint. Rules that fail and recommendations that fail are counted apart. Nothing in the project is changed.

The same report is also written as a Markdown file with every check, passes included: `audit-report.md` in the current
directory (not in the audited project), or the file given with --md. An existing file is overwritten.

After the checks the report gives an adoption plan: the open findings grouped by the stage of guide 11 that deals with
them, with their class, role and whether the change can be undone (read from appendix G).

A check that fails or could not be made lists every item behind it (every commit, branch, ticket, view column ...), one
per line. With --verbose the checks that passed list what they examined too; without it they show no detail.

Usage:
    python tools/audit.py <project-path> [--offline] [--verbose] [--since <date or commit>] [--baseline <file>]
                          [--repo owner/name] [--board <number>] [--md <file>] [--json <file>]

    --offline   run only the files and git audits (no `gh`, no network)
    --verbose   also detail the checks that passed, on the screen and in the Markdown and JSON files
    --since     judge the history only from a cut-over: the commits made after this UTC date (`2026-10-01`) or after
                this commit (a hash or a tag). Applies to the merge commits on main, the commit messages, and the
                tags on such commits; the other checks look at the present state
    --baseline  the file of accepted deviations, instead of .github/audit-baseline.json in the project. A failed check
                that the file accepts is shown as accepted and is not a failure (see audit_baseline.py)
    --repo      the GitHub repository, when the project's origin remote is not it
    --board     the board number, when the repository links several
    --md        write the Markdown report to this file instead of audit-report.md
    --json      also write the whole result to this file

A check that could not be made (no `gh`, no access) is shown as not-checkable and is never a failure.
The exit code is 1 when a rule fails, 2 for bad arguments, and 0 otherwise.
"""
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit_board  # noqa: E402
import audit_files  # noqa: E402
import audit_git  # noqa: E402
import audit_github  # noqa: E402
import audit_baseline  # noqa: E402
import audit_plan  # noqa: E402
from audit_common import (ACCEPTED, FAIL, NOT_CHECKABLE, PASS, RULE, RECOMMENDATION, Report, format_report,  # noqa: E402
                          remote_repo)


APPENDIX_G = "guides/appendix-g-audit-findings-and-fixes.md"


def audit(root, offline=False, repo=None, board=None, github=None, graphql=None, since=None):
    """The reports of every audit, in the order files, git, github, board. `since` is the cut-over for the history."""
    reports = [audit_files.audit(root), audit_git.audit(root, since)]

    if offline:
        return reports

    repo = repo or remote_repo(root)

    if not repo:
        missing = Report("github")
        missing.add("github.remote", "03 section 1", RULE, "the project has a GitHub remote", None,
                    "no github.com origin remote; pass --repo owner/name", "")
        return reports + [missing]

    reports.append((github or audit_github.audit)(repo))
    reports.append(audit_board.audit(repo, board, graphql or audit_board.run_graphql))
    return reports


def summary(reports):
    """Counts over all reports: {strength: {result: n}}."""
    counts = {s: {PASS: 0, FAIL: 0, ACCEPTED: 0, NOT_CHECKABLE: 0} for s in (RULE, RECOMMENDATION)}

    for report in reports:
        for check in report.checks:
            counts[check.strength][check.result] += 1

    return counts


def format_all(reports, verbose=False, plan=None):
    lines = [format_report(r, verbose) for r in reports]
    lines += audit_plan.format_text(plan)
    counts = summary(reports)
    lines.append("== total ==")

    for strength, label in ((RULE, "rules"), (RECOMMENDATION, "recommendations")):
        c = counts[strength]
        lines.append("{}: {} passed, {} failed, {} accepted, {} not checkable".format(
            label, c[PASS], c[FAIL], c[ACCEPTED], c[NOT_CHECKABLE]))

    lines.append("What to do about each finding: appendix G of the guides ({}).".format(APPENDIX_G))
    return "\n".join(lines)


def cell(text):
    """Text safe inside a Markdown table cell."""
    return str(text).replace("|", "\\|").replace("\n", " ")


def format_markdown(reports, project, now=None, verbose=False, since=None, plan=None):
    """The whole result as Markdown: the totals, then for each audit one table with every check, passes included, and
    under it the detail lines of each check that failed or could not be made (of every check when `verbose`)."""
    now = now or datetime.now(timezone.utc)
    counts = summary(reports)
    lines = ["# Audit report", "",
             "- **Project:** `{}`".format(project),
             "- **Date:** {} UTC".format(now.strftime("%Y-%m-%d %H:%M"))]

    if since:
        lines.append("- **History judged from:** {}".format(since))

    lines.append("- **What to do about each finding:** appendix G of the guides (`{}`)".format(APPENDIX_G))

    lines += ["",
             "## Totals", "",
             "| | Passed | Failed | Accepted | Not checkable |", "|---|---|---|---|---|"]

    for strength, label in ((RULE, "Rules"), (RECOMMENDATION, "Recommendations")):
        c = counts[strength]
        lines.append("| {} | {} | {} | {} | {} |".format(label, c[PASS], c[FAIL], c[ACCEPTED], c[NOT_CHECKABLE]))

    lines += audit_plan.format_markdown(plan)

    for report in reports:
        c = report.counts()
        lines += ["", "## {}".format(report.area.capitalize()), "",
                  "{} passed, {} failed, {} accepted, {} not checkable.".format(
                      c[PASS], c[FAIL], c[ACCEPTED], c[NOT_CHECKABLE]), "",
                  "| Result | Id | Strength | Guide | Check | Detail and fix |", "|---|---|---|---|---|---|"]

        for check in report.checks:
            detail = " ".join(part for part in (check.message, "Fix: " + check.hint if check.hint else "") if part)
            lines.append("| {} | `{}` | {} | {} | {} | {} |".format(
                check.result.upper(), check.id, check.strength, check.guide, cell(check.title), cell(detail)))

        shown = [ch for ch in report.checks if ch.details and (verbose or ch.result != PASS)]

        for check in shown:
            lines += ["", "**`{}`** ({})".format(check.id, check.result), ""]
            lines += ["- {}".format(cell(d)) for d in check.details]

    return "\n".join(lines) + "\n"


def to_json(reports, verbose=False, since=None, plan=None):
    """The summary, the plan and every audit; the details of a passed check only when `verbose`. `since` is the
    cut-over."""
    return {"since": since, "summary": summary(reports), "plan": plan or [],
            "audits": [r.as_dict(verbose) for r in reports]}


def main(argv, github=None, graphql=None):
    args = argv[1:]
    options = {}
    offline = "--offline" in args
    verbose = "--verbose" in args

    for flag in ("--offline", "--verbose"):
        if flag in args:
            args.remove(flag)

    for flag in ("--repo", "--board", "--md", "--json", "--since", "--baseline"):
        if flag in args:
            i = args.index(flag)
            options[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]

    if len(args) != 1 or not os.path.isdir(args[0]) or (options.get("--board") or "0").isdigit() is False:
        print(__doc__)
        return 2

    number = int(options["--board"]) if options.get("--board") else None
    since = options.get("--since")

    if "--since" in options and not since:
        print(__doc__)
        return 2

    try:
        reports = audit(os.path.abspath(args[0]), offline, options.get("--repo"), number, github, graphql, since)
    except ValueError as error:
        print(error)
        return 2

    baseline_path = options.get("--baseline") or os.path.join(os.path.abspath(args[0]), audit_baseline.PATH)

    if "--baseline" in options and not os.path.isfile(baseline_path):
        print("the baseline file {} does not exist".format(baseline_path))
        return 2

    try:
        stale = audit_baseline.apply(reports, audit_baseline.load(baseline_path))
    except audit_baseline.BaselineError as error:
        print(error)
        return 2

    if stale:
        reports.append(stale)

    plan = audit_plan.plan(reports)
    print(format_all(reports, verbose, plan))
    md_path = options.get("--md") or "audit-report.md"

    with open(md_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(format_markdown(reports, os.path.abspath(args[0]), verbose=verbose, since=since, plan=plan))

    print("report written to {}".format(os.path.abspath(md_path)))

    if options.get("--json"):
        with open(options["--json"], "w", encoding="utf-8") as f:
            json.dump(to_json(reports, verbose, since, plan), f, indent=2)

    return 1 if any(r.failures(RULE) for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
