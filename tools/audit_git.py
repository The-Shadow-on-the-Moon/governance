"""Audit the local git history and names of an existing project against the guides.

Looks at the branches, the tags and the commits of a clone: branch and tag names, whether `main` is the only
integration line, how history reached `main`, the commit messages, and whether the released tags match the
changelog. Read-only; it never fetches, so run `git fetch` first to see the remote branches.

Usage:
    python tools/audit_git.py <project-path> [--json <file>]

Prints the checks that are not a pass and exits 1 when a rule fails.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (Report, RULE, RECOMMENDATION, git, read, format_report)  # noqa: E402

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
HOTFIX_BRANCH = re.compile(r"^hotfix-v\d+-\d+-\d+-[a-z0-9]+(-[a-z0-9]+)*$")
VERSION = r"V(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
DATE = r"\d{4}-\d\d-\d\d"
RETIRED_TAG = re.compile(r"^(?:test/)?(archived|suspended|abandoned)/{}_[a-z0-9]+(-[a-z0-9]+)*(_[a-z0-9]+(-[a-z0-9]+)*)?$"
                         .format(DATE))
RELEASED_TAG = re.compile(r"^(?:test/)?released/({})(-HF[1-9])?$".format(VERSION))
TYPE_PREFIX = re.compile(r"^(feat|fix|chore|docs|refactor|test|style|perf|build|ci)(\([^)]*\))?!?:\s", re.I)
ASSISTANT_TRAILER = re.compile(r"^co-authored-by:.*(claude|anthropic|codex|openai|copilot|gemini|cursor|chatgpt)",
                               re.I | re.M)
GENERATED_WITH = re.compile(r"generated (with|by)\b.*(claude|codex|copilot|gemini|chatgpt|ai\b)", re.I)
AUTOMATION_SUBJECT = re.compile(r"^(Finalize |Flag bypass|Fill in a build heading)")
CHANGELOG_VERSION = re.compile(r"^## ({}(?:-HF\d+)?) — ".format(VERSION), re.M)
LIMIT = 5


def audit(root):
    report = Report("git")
    code, _ = git(root, "rev-parse", "--git-dir")

    if code != 0:
        report.add("git.repository", "03 section 1", RULE, "the project is a git repository", False,
                   "{} is not a git repository".format(root), "run `git init` and make a first commit")
        return report

    check_branches(report, root)
    check_tags(report, root)
    check_history(report, root)
    check_messages(report, root)
    check_released_versions(report, root)
    return report


def names(root, *args):
    code, out = git(root, *args)
    return [n for n in out.split("\n") if n] if code == 0 else []


def branches(root):
    local = names(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    remote = [n.split("/", 1)[1] for n in names(root, "for-each-ref", "--format=%(refname:short)", "refs/remotes")
              if "/" in n and not n.endswith("/HEAD")]
    return sorted(set(local) | set(remote))


def check_branches(report, root):
    found = branches(root)
    report.add("git.branch.main", "02 section 1.1", RULE, "the branch `main` exists", "main" in found,
               "no `main` branch (found: {})".format(", ".join(found[:LIMIT]) or "none"),
               "name the integration branch `main`")
    long_lived = [b for b in found if b in ("develop", "development", "dev", "staging", "stage", "release")]
    report.add("git.branch.single-line", "02 section 1.1", RULE, "there is no long-lived develop or staging branch",
               not long_lived, "found: {}".format(", ".join(long_lived)), "merge it into `main` and retire it")
    slashed = [b for b in found if "/" in b]
    report.add("git.branch.no-slash", "02 section 2.1", RULE, "no branch name contains `/`", not slashed,
               "found: {}".format(", ".join(slashed[:LIMIT])), "rename the branch with hyphens")
    bad = [b for b in found if "/" not in b and b != "main" and not KEBAB.match(b) and not HOTFIX_BRANCH.match(b)]
    report.add("git.branch.kebab-case", "02 section 2.1", RULE, "branch names are kebab-case (or the hotfix form)",
               not bad, "found: {}".format(", ".join(bad[:LIMIT])), "rename them in lowercase words with hyphens")


def check_tags(report, root):
    tags = names(root, "tag", "--list")
    bad = [t for t in tags if not RETIRED_TAG.match(t) and not RELEASED_TAG.match(t)]
    report.add("git.tag.names", "02 section 2.2", RULE,
               "tags follow the namespaces (archived, suspended, abandoned, released, test/)", not bad,
               "{} tag(s) do not, for example {}".format(len(bad), ", ".join(bad[:LIMIT])),
               "retag as `released/V1.2.3` or `<archived|suspended|abandoned>/yyyy-mm-dd_<branch>`")

    if not names(root, "rev-parse", "--verify", "-q", "main"):
        return

    released = [t for t in tags if RELEASED_TAG.match(t) and not t.startswith("test/") and "-HF" not in t]
    off_main = [t for t in released if git(root, "merge-base", "--is-ancestor", t, "main")[0] != 0]
    report.add("git.tag.released-on-main", "02 section 1.1", RULE, "release tags are on `main`", not off_main,
               "not reachable from main: {}".format(", ".join(off_main[:LIMIT])),
               "a release is a tag placed on `main`")


def check_history(report, root):
    if not names(root, "rev-parse", "--verify", "-q", "main"):
        return

    commits = names(root, "log", "main", "--first-parent", "--format=%H%x09%P%x09%s")
    direct = []

    for line in commits:
        sha, parents, subject = (line.split("\t") + ["", ""])[:3]

        if len(parents.split()) == 1 and not AUTOMATION_SUBJECT.match(subject):
            direct.append("{} {}".format(sha[:7], subject[:50]))

    # the first commit has no parent and is never a violation
    direct = [d for d in direct if d.split(" ", 1)[0] != commits[-1].split("\t")[0][:7]] if commits else direct
    report.add("git.history.merge-commits", "06 section 4.1", RULE,
               "work reaches `main` through merge commits (no direct, squashed or rebased commits)", not direct,
               "{} commit(s) on main's first-parent line are not merges, for example {}".format(
                   len(direct), "; ".join(direct[:3])),
               "land work with a pull request and a merge commit")


def check_messages(report, root):
    raw = git(root, "log", "--all", "--format=%h%x1f%B%x1e")[1]
    prefixed = []
    attributed = []

    for entry in raw.split("\x1e"):
        entry = entry.strip("\n")

        if "\x1f" not in entry:
            continue

        sha, message = entry.split("\x1f", 1)
        subject = message.split("\n", 1)[0]

        if TYPE_PREFIX.match(subject):
            prefixed.append("{} {}".format(sha, subject[:40]))

        if ASSISTANT_TRAILER.search(message) or GENERATED_WITH.search(message):
            attributed.append("{} {}".format(sha, subject[:40]))

    report.add("git.message.no-type-prefix", "05 section 5.2", RULE, "commit subjects have no `fix:` or `feat:` prefix",
               not prefixed, "{} commit(s), for example {}".format(len(prefixed), "; ".join(prefixed[:3])),
               "write the ticket's title as the subject")
    report.add("git.message.no-assistant-attribution", "09 section 4.2", RULE,
               "commit messages carry no assistant co-author or 'generated with' line", not attributed,
               "{} commit(s), for example {}".format(len(attributed), "; ".join(attributed[:3])),
               "authorship belongs to the person; leave the line out of new commits")


def check_released_versions(report, root):
    text = read(os.path.join(root, "CHANGELOG.md"))
    tags = [t for t in names(root, "tag", "--list") if RELEASED_TAG.match(t) and not t.startswith("test/")]

    if text is None:
        report.add("git.tag.released-in-changelog", "03 section 7", RULE, "every released tag is a changelog version",
                   None, "", "")
        return

    versions = set(m.group(1) for m in CHANGELOG_VERSION.finditer(text))
    missing = []

    for tag in tags:
        match = RELEASED_TAG.match(tag)

        if match.group(1) + (match.group(5) or "") not in versions:
            missing.append(tag)

    report.add("git.tag.released-in-changelog", "03 section 7", RULE, "every released tag is a changelog version",
               not missing, "no changelog heading for: {}".format(", ".join(missing[:LIMIT])),
               "a release tag names a finalized version of the changelog")


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    json_path = argv[argv.index("--json") + 1] if "--json" in argv else None

    if json_path in args:
        args.remove(json_path)

    if len(args) != 1 or not os.path.isdir(args[0]):
        print(__doc__)
        return 2

    report = audit(os.path.abspath(args[0]))
    print(format_report(report))

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.as_dict(), f, indent=2)

    return 1 if report.failures(RULE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
