"""Audit the local git history and names of an existing project against the guides.

Looks at the branches, the tags and the commits of a clone: branch and tag names, whether `main` is the only
integration line, how history reached `main`, the commit messages, and whether the released tags match the
changelog. Read-only; it never fetches, so run `git fetch` first to see the remote branches.

With --since the history is judged only from a cut-over: the commits made after a date (`2026-10-01`, or
`2026-10-01 14:30`, UTC) or after a commit (any revision, such as a hash or a tag). The merge commits, the commit
messages, and the tags that point at such commits are then checked; older ones are left out. Branch names are
the current state and are always checked.

Usage:
    python tools/audit_git.py <project-path> [--verbose] [--since <date or commit>] [--json <file>]

Prints the checks that are not a pass (every check with --verbose), each with all its detail lines, and exits 1 when
a rule fails.
"""
import json
import os
import re
import sys
from datetime import datetime

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


DATE_FORMATS = ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S")


def cutover(root, since):
    """The hashes of the commits made after the cut-over `since`, or None when the whole history is judged.
    `since` is a UTC date (`2026-10-01`, `2026-10-01 14:30`) or a revision; anything else raises ValueError."""
    if not since:
        return None

    for form in DATE_FORMATS:
        try:
            moment = datetime.strptime(since, form)
        except ValueError:
            continue

        return set(names(root, "rev-list", "--all", "--since=" + moment.strftime("%Y-%m-%d %H:%M:%S") + " +0000"))

    code, commit = git(root, "rev-parse", "--verify", "-q", since + "^{commit}")

    if code != 0:
        raise ValueError("--since is neither a UTC date nor a commit of the project: {}".format(since))

    return set(names(root, "rev-list", "--all", "^" + commit))


def scope(since, count):
    """The detail line that says which part of the history was judged."""
    return ["judged from {}: {} commit(s) in scope".format(since, count)] if since else []


def audit(root, since=None):
    report = Report("git")
    code, _ = git(root, "rev-parse", "--git-dir")

    if code != 0:
        report.add("git.repository", "03 section 1", RULE, "the project is a git repository", False,
                   "{} is not a git repository".format(root), "run `git init` and make a first commit",
                   [root])
        return report

    after = cutover(root, since)
    check_branches(report, root)
    check_tags(report, root, after, since)
    check_history(report, root, after, since)
    check_messages(report, root, after, since)
    check_released_versions(report, root, after, since)
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
               "no `main` branch", "name the integration branch `main`",
               ["branches: " + (", ".join(found) or "none")])
    long_lived = [b for b in found if b in ("develop", "development", "dev", "staging", "stage", "release")]
    report.add("git.branch.single-line", "02 section 1.1", RULE, "there is no long-lived develop or staging branch",
               not long_lived, "{} long-lived branch(es)".format(len(long_lived)),
               "merge it into `main` and retire it", long_lived or found)
    slashed = [b for b in found if "/" in b]
    report.add("git.branch.no-slash", "02 section 2.1", RULE, "no branch name contains `/`", not slashed,
               "{} branch(es) with `/`".format(len(slashed)), "rename the branch with hyphens", slashed or found)
    bad = [b for b in found if "/" not in b and b != "main" and not KEBAB.match(b) and not HOTFIX_BRANCH.match(b)]
    report.add("git.branch.kebab-case", "02 section 2.1", RULE, "branch names are kebab-case (or the hotfix form)",
               not bad, "{} branch(es) not in kebab-case".format(len(bad)),
               "rename them in lowercase words with hyphens", bad or found)


def tags_in_scope(root, after):
    """The tags, except those that point at a commit made before the cut-over (all of them when `after` is None)."""
    tags = names(root, "tag", "--list")

    if after is None:
        return tags

    return [t for t in tags if git(root, "rev-list", "-n", "1", t)[1] in after]


def check_tags(report, root, after=None, since=None):
    tags = tags_in_scope(root, after)
    bad = [t for t in tags if not RETIRED_TAG.match(t) and not RELEASED_TAG.match(t)]
    report.add("git.tag.names", "02 section 2.2", RULE,
               "tags follow the namespaces (archived, suspended, abandoned, released, test/)", not bad,
               "{} tag(s) do not follow them".format(len(bad)),
               "retag as `released/V1.2.3` or `<archived|suspended|abandoned>/yyyy-mm-dd_<branch>`",
               (bad or tags or ["no tags"]) + (["judged from {}: tags on older commits left out".format(since)]
                                               if since else []))

    if not names(root, "rev-parse", "--verify", "-q", "main"):
        return

    released = [t for t in tags if RELEASED_TAG.match(t) and not t.startswith("test/") and "-HF" not in t]
    off_main = [t for t in released if git(root, "merge-base", "--is-ancestor", t, "main")[0] != 0]
    report.add("git.tag.released-on-main", "02 section 1.1", RULE, "release tags are on `main`", not off_main,
               "{} release tag(s) not reachable from main".format(len(off_main)),
               "a release is a tag placed on `main`", off_main or released or ["no release tags"])


def check_history(report, root, after=None, since=None):
    if not names(root, "rev-parse", "--verify", "-q", "main"):
        return

    commits = names(root, "log", "main", "--first-parent", "--format=%H%x09%P%x09%s")
    first = commits[-1].split("\t")[0] if commits else None

    if after is not None:
        commits = [c for c in commits if c.split("\t")[0] in after]

    direct = []

    for line in commits:
        sha, parents, subject = (line.split("\t") + ["", ""])[:3]

        if len(parents.split()) == 1 and not AUTOMATION_SUBJECT.match(subject):
            direct.append((sha, subject))

    # the first commit has no parent and is never a violation
    direct = ["{} {}".format(sha, subject) for sha, subject in direct if sha != first]
    report.add("git.history.merge-commits", "06 section 4.1", RULE,
               "work reaches `main` through merge commits (no direct, squashed or rebased commits)", not direct,
               "{} commit(s) on main's first-parent line are not merges".format(len(direct)),
               "land work with a pull request and a merge commit",
               direct or ["{} commit(s) on main's first-parent line, all merges, the first commit or the "
                          "automation's".format(len(commits))] + scope(since, len(commits)))


def check_messages(report, root, after=None, since=None):
    raw = git(root, "log", "--all", "--format=%H%x1f%B%x1e")[1]
    prefixed = []
    attributed = []
    total = 0

    for entry in raw.split("\x1e"):
        entry = entry.strip("\n")

        if "\x1f" not in entry:
            continue

        total += 1
        sha, message = entry.split("\x1f", 1)

        if after is not None and sha not in after:
            total -= 1
            continue

        subject = message.split("\n", 1)[0]

        if TYPE_PREFIX.match(subject):
            prefixed.append("{} {}".format(sha, subject))

        if ASSISTANT_TRAILER.search(message) or GENERATED_WITH.search(message):
            attributed.append("{} {}".format(sha, subject))

    examined = ["{} commit(s) on all branches examined".format(total)] + scope(since, total)
    report.add("git.message.no-type-prefix", "05 section 5.2", RULE, "commit subjects have no `fix:` or `feat:` prefix",
               not prefixed, "{} commit(s) have a type prefix".format(len(prefixed)),
               "write the ticket's title as the subject", prefixed or examined)
    report.add("git.message.no-assistant-attribution", "09 section 4.2", RULE,
               "commit messages carry no assistant co-author or 'generated with' line", not attributed,
               "{} commit(s) carry an attribution".format(len(attributed)),
               "authorship belongs to the person; leave the line out of new commits", attributed or examined)


def check_released_versions(report, root, after=None, since=None):
    text = read(os.path.join(root, "CHANGELOG.md"))
    tags = [t for t in tags_in_scope(root, after) if RELEASED_TAG.match(t) and not t.startswith("test/")]

    if text is None:
        report.add("git.tag.released-in-changelog", "03 section 7", RULE, "every released tag is a changelog version",
                   None, "CHANGELOG.md cannot be read", "", ["CHANGELOG.md is missing or unreadable"])
        return

    versions = set(m.group(1) for m in CHANGELOG_VERSION.finditer(text))
    missing = []

    for tag in tags:
        match = RELEASED_TAG.match(tag)

        if match.group(1) + (match.group(5) or "") not in versions:
            missing.append(tag)

    report.add("git.tag.released-in-changelog", "03 section 7", RULE, "every released tag is a changelog version",
               not missing, "{} release tag(s) without a changelog heading".format(len(missing)),
               "a release tag names a finalized version of the changelog",
               missing or tags or ["no release tags"])


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in argv
    json_path = argv[argv.index("--json") + 1] if "--json" in argv else None
    since = argv[argv.index("--since") + 1] if "--since" in argv and argv.index("--since") + 1 < len(argv) else None

    for value in (json_path, since):
        if value in args:
            args.remove(value)

    if len(args) != 1 or not os.path.isdir(args[0]) or ("--since" in argv and since is None):
        print(__doc__)
        return 2

    try:
        report = audit(os.path.abspath(args[0]), since)
    except ValueError as error:
        print(error)
        return 2

    print(format_report(report, verbose))

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.as_dict(verbose), f, indent=2)

    return 1 if report.failures(RULE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
