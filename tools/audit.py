"""Audit an existing project against the guides: the files, the git history, the GitHub settings and the board.

Runs the four audits (audit_files.py, audit_git.py, audit_github.py and audit_board.py) on a project and prints one
report. Each check says whether the project follows a rule or a recommendation of the guides, with the guide section and
a hint. Rules that fail and recommendations that fail are counted apart. Nothing in the project is changed.

Usage:
    python tools/audit.py <project-path> [--offline] [--repo owner/name] [--board <number>] [--json <file>]

    --offline   run only the files and git audits (no `gh`, no network)
    --repo      the GitHub repository, when the project's origin remote is not it
    --board     the board number, when the repository links several
    --json      also write the whole result to this file

A check that could not be made (no `gh`, no access) is shown as not-checkable and is never a failure.
The exit code is 1 when a rule fails, 2 for bad arguments, and 0 otherwise.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import audit_board  # noqa: E402
import audit_files  # noqa: E402
import audit_git  # noqa: E402
import audit_github  # noqa: E402
from audit_common import (FAIL, NOT_CHECKABLE, PASS, RULE, RECOMMENDATION, Report, format_report,  # noqa: E402
                          remote_repo)


def audit(root, offline=False, repo=None, board=None, github=None, graphql=None):
    """The reports of every audit, in the order files, git, github, board."""
    reports = [audit_files.audit(root), audit_git.audit(root)]

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
    counts = {s: {PASS: 0, FAIL: 0, NOT_CHECKABLE: 0} for s in (RULE, RECOMMENDATION)}

    for report in reports:
        for check in report.checks:
            counts[check.strength][check.result] += 1

    return counts


def format_all(reports):
    lines = [format_report(r) for r in reports]
    counts = summary(reports)
    lines.append("== total ==")

    for strength, label in ((RULE, "rules"), (RECOMMENDATION, "recommendations")):
        c = counts[strength]
        lines.append("{}: {} passed, {} failed, {} not checkable".format(label, c[PASS], c[FAIL], c[NOT_CHECKABLE]))

    return "\n".join(lines)


def to_json(reports):
    return {"summary": summary(reports), "audits": [r.as_dict() for r in reports]}


def main(argv, github=None, graphql=None):
    args = argv[1:]
    options = {}
    offline = "--offline" in args

    if offline:
        args.remove("--offline")

    for flag in ("--repo", "--board", "--json"):
        if flag in args:
            i = args.index(flag)
            options[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]

    if len(args) != 1 or not os.path.isdir(args[0]) or (options.get("--board") or "0").isdigit() is False:
        print(__doc__)
        return 2

    number = int(options["--board"]) if options.get("--board") else None
    reports = audit(os.path.abspath(args[0]), offline, options.get("--repo"), number, github, graphql)
    print(format_all(reports))

    if options.get("--json"):
        with open(options["--json"], "w", encoding="utf-8") as f:
            json.dump(to_json(reports), f, indent=2)

    return 1 if any(r.failures(RULE) for r in reports) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
