"""The check model shared by the audit scripts.

An audit script looks at an existing project and reports, for each rule or recommendation of the guides, whether
the project follows it. Nothing here changes the project that is audited.

A check has an id, the guide section it comes from, its strength (rule or recommendation), a result and, when the
result is not a pass, a message and a hint on how to fix it.

Results:
    pass          the project follows it
    fail          the project does not
    not-checkable the audit could not tell (the data was not reachable, or it needs a person's judgment)
"""
import json
import os
import re
import subprocess
from dataclasses import dataclass, asdict

PASS = "pass"
FAIL = "fail"
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

    def as_dict(self):
        return asdict(self)


class Report:
    """The checks of one audit, in the order they were made."""

    def __init__(self, area):
        self.area = area
        self.checks = []

    def add(self, check_id, guide, strength, title, ok, message="", hint=""):
        """Record a pass (ok True), a fail (ok False) or a check that could not be made (ok None)."""
        result = NOT_CHECKABLE if ok is None else PASS if ok else FAIL
        self.checks.append(Check(check_id, guide, strength, title, result, "" if ok else message, "" if ok else hint))

    def failures(self, strength=None):
        return [c for c in self.checks if c.result == FAIL and (strength is None or c.strength == strength)]

    def counts(self):
        counts = {PASS: 0, FAIL: 0, NOT_CHECKABLE: 0}

        for check in self.checks:
            counts[check.result] += 1

        return counts

    def as_dict(self):
        return {"area": self.area, "counts": self.counts(), "checks": [c.as_dict() for c in self.checks]}


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


def format_report(report):
    """The report as text: one line per check that is not a pass, then the counts."""
    lines = ["== {} ==".format(report.area)]

    for check in report.checks:
        if check.result == PASS:
            continue

        lines.append("[{}] {} ({}, guide {}): {}".format(check.result.upper(), check.id, check.strength, check.guide,
                                                          check.title))

        if check.message:
            lines.append("    {}".format(check.message))

        if check.hint:
            lines.append("    fix: {}".format(check.hint))

    counts = report.counts()
    lines.append("{} passed, {} failed, {} not checkable".format(counts[PASS], counts[FAIL], counts[NOT_CHECKABLE]))
    return "\n".join(lines)
