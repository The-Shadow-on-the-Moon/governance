"""The accepted deviations of an audited project: the baseline.

A project that adopts the standard has a past it cannot change (commits that are not merges, old tags) and may have
rules that do not apply to it. These are recorded in `.github/audit-baseline.json` in the audited project, so that the
audit shows them as *accepted* and not as failures:

    {"accepted": [
        {"check": "git.history.merge-commits",
         "reason": "history before the cut-over; it cannot be rewritten",
         "date": "2026-10-12",
         "agreed_by": "the project owner",
         "items": ["82e13d9"]}
    ]}

`check`, `reason`, `date` and `agreed_by` are required. `items` is optional: without it the entry accepts the whole
check; with it, only the detail lines of the check that start with one of the items (for example a commit hash, a
branch or tag name, or `line 12`). A check with items that are not all covered stays a failure for the rest.

An entry that no longer accepts anything (the check passes now, or the items are gone) is reported by the check
`baseline.stale`, a recommendation, so the file does not collect dead entries.
"""
import json
import os

from audit_common import ACCEPTED, FAIL, RECOMMENDATION, Report, read

PATH = os.path.join(".github", "audit-baseline.json")
REQUIRED = ("check", "reason", "date", "agreed_by")


class BaselineError(ValueError):
    pass


def load(path):
    """The entries of the baseline file, or [] when there is no such file. Raises BaselineError when it is invalid."""
    if not os.path.isfile(path):
        return []

    text = read(path)

    try:
        data = json.loads(text) if text is not None else None
    except ValueError as error:
        raise BaselineError("{} is not valid JSON: {}".format(path, error))

    entries = data.get("accepted") if isinstance(data, dict) else None

    if not isinstance(entries, list):
        raise BaselineError('{} must hold an object with a list named "accepted"'.format(path))

    for number, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            raise BaselineError("{}: entry {} is not an object".format(path, number))

        missing = [k for k in REQUIRED if not isinstance(entry.get(k), str) or not entry[k].strip()]
        items = entry.get("items", [])

        if missing:
            raise BaselineError("{}: entry {} lacks {}".format(path, number, ", ".join(missing)))

        if not isinstance(items, list) or not all(isinstance(i, str) and i for i in items):
            raise BaselineError("{}: entry {} has items that are not a list of texts".format(path, number))

    return entries


def note(entry):
    return "accepted: {} ({}, agreed by {})".format(entry["reason"], entry["date"], entry["agreed_by"])


def apply(reports, entries):
    """Turn the failures that the entries accept into *accepted*, in place. Returns the report `baseline` that lists
    the entries which accepted nothing, or None when there are no entries."""
    if not entries:
        return None

    used = set()

    for report in reports:
        for check in report.checks:
            if check.result != FAIL:
                continue

            mine = [(i, e) for i, e in enumerate(entries) if e["check"] == check.id]
            whole = next(((i, e) for i, e in mine if not e.get("items")), None)

            if whole:
                used.add(whole[0])
                check.result = ACCEPTED
                check.details.append(note(whole[1]))
                continue

            covered, rest, notes = [], [], []

            for line in check.details:
                hit = next(((i, e) for i, e in mine if any(line.startswith(item) for item in e["items"])), None)

                if hit:
                    used.add(hit[0])
                    covered.append(line)

                    if note(hit[1]) not in notes:
                        notes.append(note(hit[1]))

                else:
                    rest.append(line)

            if covered and not rest:
                check.result = ACCEPTED
                check.details = covered + notes
            elif covered:
                check.message = "{} item(s) are not covered by the baseline".format(len(rest))
                check.details = rest + ["{} item(s) accepted by the baseline".format(len(covered))]

    stale = [e for i, e in enumerate(entries) if i not in used]
    report = Report("baseline")
    report.add("baseline.stale", "11 section 3", RECOMMENDATION, "every accepted deviation still applies",
               not stale, "{} entry(ies) accept nothing now".format(len(stale)),
               "remove them from .github/audit-baseline.json",
               ["{}{}: {}".format(e["check"], " " + ", ".join(e["items"]) if e.get("items") else "", e["reason"])
                for e in stale] or ["{} accepted deviation(s) in use".format(len(entries))])
    return report
