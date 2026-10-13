"""The check model shared by the audit scripts.

An audit script looks at an existing project and reports, for each rule or recommendation of the guides, whether
the project follows it. Nothing here changes the project that is audited.

A check has an id, the guide section it comes from, its strength (rule or recommendation), a result and, when the
result is not a pass, a message and a hint on how to fix it. It also keeps `details`: one line per item the check
looked at. On a fail or a not-checkable result they are the offenders, all of them; on a pass they are what was
examined and found right (shown only when the report is made verbose).

Results:
    pass          the project follows it
    fail          the project does not
    accepted      it fails, and the project recorded the deviation in its baseline (set by audit.py, never by a check)
    not-checkable the audit could not tell (the data was not reachable, or it needs a person's judgment)
"""
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".github", "scripts"))

import ticket_type  # noqa: E402

PASS = "pass"
FAIL = "fail"
ACCEPTED = "accepted"
NOT_CHECKABLE = "not-checkable"

RULE = "rule"
RECOMMENDATION = "recommendation"


@dataclass
class Check:
    id: str
    guide: str  # for example "03 section 2.2"
    strength: str  # RULE or RECOMMENDATION
    title: str
    result: str = PASS
    message: str = ""
    hint: str = ""
    details: list = field(default_factory=list)

    def as_dict(self):
        return asdict(self)


class Report:
    """The checks of one audit, in the order they were made."""

    def __init__(self, area):
        self.area = area
        self.checks = []

    def add(self, check_id, guide, strength, title, ok, message="", hint="", details=None):
        """Record a pass (ok True), a fail (ok False) or a check that could not be made (ok None). `details` are the
        items the check looked at, as text lines: the offenders when it did not pass, what was examined when it did."""
        result = NOT_CHECKABLE if ok is None else PASS if ok else FAIL
        self.checks.append(Check(check_id, guide, strength, title, result, "" if ok else message, "" if ok else hint,
                                 [str(d) for d in details or []]))

    def failures(self, strength=None):
        return [c for c in self.checks if c.result == FAIL and (strength is None or c.strength == strength)]

    def counts(self):
        counts = {PASS: 0, FAIL: 0, ACCEPTED: 0, NOT_CHECKABLE: 0}

        for check in self.checks:
            counts[check.result] += 1

        return counts

    def as_dict(self, verbose=False):
        """The report as plain data. The details of a passed check are left out unless `verbose`."""
        checks = [c.as_dict() for c in self.checks]

        for check in checks:
            if check["result"] == PASS and not verbose:
                check["details"] = []

        return {"area": self.area, "counts": self.counts(), "checks": checks}


def git(root, *args):
    """Run git in `root` and return (exit code, standard output without the final newline)."""
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout.rstrip("\n")


STANDARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def gh_api(*args):
    """Call `gh api` and return (status, data). Status is 200 on success, the HTTP status when GitHub refused, and 0
    when `gh` is missing or the call failed in another way (not signed in, no network)."""
    try:
        extra = ["--slurp"] if "--paginate" in args else []
        result = subprocess.run(["gh", "api", *args, *extra], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return 0, None

    if result.returncode != 0:
        found = re.search(r"HTTP (\d{3})", result.stderr)
        return (int(found.group(1)) if found else 0), None

    try:
        data = json.loads(result.stdout) if result.stdout.strip() else None
    except ValueError:
        return 0, None

    if extra and isinstance(data, list):
        data = [item for page in data for item in (page if isinstance(page, list) else [page])]

    return 200, data


class Variables:
    """The repository variables, read with `gh`, in the form ticket_type.source() asks for."""

    def __init__(self, repo, gh=gh_api):
        self.repo, self.gh = repo, gh

    def get_variable(self, name):
        status, data = self.gh("repos/{}/actions/variables/{}".format(self.repo, name))
        return data.get("value") if status == 200 and isinstance(data, dict) else None


def type_source(repo, gh=gh_api):
    """Where the Type of a ticket comes from for the repository: `issue-type` or `field` (guide 10, section 5.1)."""
    status, info = gh("repos/{}".format(repo))
    return ticket_type.source(info if status == 200 and isinstance(info, dict) else None, Variables(repo, gh))


def remote_repo(root):
    """`owner/name` of the origin remote of the project at `root`, or None."""
    code, url = git(root, "remote", "get-url", "origin")
    found = re.search(r"github\.com[:/]([^/\s]+)/([^/\s]+?)(?:\.git)?$", url) if code == 0 else None
    return "{}/{}".format(found.group(1), found.group(2)) if found else None


def appendix_c():
    """The label and issue type tables of the Ticket fields reference, read from the guides of this repository:
    ({label: (hex, meaning)}, {type: (color, meaning)})."""
    text = read(os.path.join(STANDARD, "guides", "appendix-c-ticket-fields-reference.md")) or ""
    labels, types = {}, {}

    for line in text.splitlines():
        label = re.match(r"^\| `([a-z]+)` \| ([0-9A-F]{6}) \| (.+) \|$", line)
        kind = re.match(r"^\| \*\*(Feature|Enhancement|Change|Bug|Refactor|Task|Version|Alert)\*\* \| ([A-Z]+) \| (.+?) \|", line)

        if label:
            labels[label.group(1)] = (label.group(2), label.group(3))
        elif kind:
            types[kind.group(1)] = (kind.group(2), kind.group(3))

    return labels, types


def read(path):
    """The text of a file, or None when it is missing or unreadable."""
    try:
        with open(path, encoding="utf-8", newline="") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return None


def format_report(report, verbose=False):
    """The report as text: one line per check that is not a pass (every pass too when `verbose`), each followed by its
    message, its detail lines and its fix hint, then the counts."""
    lines = ["== {} ==".format(report.area)]

    for check in report.checks:
        if check.result == PASS and not verbose:
            continue

        lines.append("[{}] {} ({}, guide {}): {}".format(check.result.upper(), check.id, check.strength, check.guide,
                                                          check.title))

        if check.message:
            lines.append("    {}".format(check.message))

        lines.extend("      - {}".format(d) for d in check.details)

        if check.hint:
            lines.append("    fix: {}".format(check.hint))

    counts = report.counts()
    lines.append("{} passed, {} failed, {} accepted, {} not checkable".format(
        counts[PASS], counts[FAIL], counts[ACCEPTED], counts[NOT_CHECKABLE]))
    return "\n".join(lines)
