"""Audit the files of an existing project against the guides.

Looks at what is in the working tree: the places every project has, the changelog and its structure, the line
endings file, the hooks, the wiki and the files of the automation. Read-only.

Usage:
    python tools/audit_files.py <project-path> [--verbose] [--json <file>]

Prints the checks that are not a pass (every check with --verbose), each with all its detail lines, and exits 1 when
a rule fails.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (Report, RULE, RECOMMENDATION, git, read, format_report)  # noqa: E402

HOOKS = ("pre-commit", "pre-push", "prepare-commit-msg")
LOCATIONS = (
    ("README.md", "file", RECOMMENDATION, "the readme"),
    ("CHANGELOG.md", "file", RULE, "the changelog"),
    ("doc", "dir", RULE, "the doc/ folder"),
    ("doc/wiki", "dir", RULE, "the doc/wiki/ folder"),
    (".githooks", "dir", RULE, "the .githooks/ folder"),
    (".github", "dir", RULE, "the .github/ folder"),
    ("AGENTS.md", "file", RULE, "the shared assistant instructions"),
    (".gitignore", "file", RECOMMENDATION, "the ignore file"),
    (".gitattributes", "file", RULE, "the line endings file"),
)

WIP = re.compile(r"^## WIP-Version(?: (\+[Vsm]))?$")
WIP_ANY = re.compile(r"^## WIP-Version")
FINAL = re.compile(r"^## (V(\d+)\.(\d+)\.(\d+)(-HF\d+)?) — (\d{4}-\d\d-\d\d \d\d:\d\d) UTC$")
FINAL_ANY = re.compile(r"^## V\d")
BUILD = re.compile(r"^### Build (\d{14}) \(branch ([^\s,)]+)(?:, commit ([0-9a-f]{7,40}))?\)$")
TICKET = re.compile(r"^#### #(\d+) — (.+)$")
REF = re.compile(r"^#### REF (\d{14}) — (.+)$")
AUTO_REF = re.compile(r"^#### AUTO-REF (\d{14}) \(tracked as #(\d+)\)$")
BANNED_SECTIONS = re.compile(r"^#{2,4} (known bugs|planned)\b", re.I)


def audit(root):
    report = Report("files")
    check_locations(report, root)
    check_gitattributes(report, root)
    changelog = read(os.path.join(root, "CHANGELOG.md"))
    check_changelog(report, changelog)
    check_hooks(report, root)
    check_wiki(report, root)
    check_automation(report, root)
    check_instructions(report, root)
    return report


def check_locations(report, root):
    for name, kind, strength, label in LOCATIONS:
        path = os.path.join(root, name)
        ok = os.path.isdir(path) if kind == "dir" else os.path.isfile(path)
        report.add("files.location." + name.strip(".").replace("/", "."), "03 section 2.1", strength,
                   "{} exists at {}".format(label, name), ok, "{} is missing".format(name),
                   "create {}".format(name), [name])

    licenses = [n for n in os.listdir(root) if re.match(r"(?i)licen[cs]e", n)] if os.path.isdir(root) else []
    report.add("files.location.license", "03 section 2.1", RECOMMENDATION, "a license file exists", bool(licenses),
               "no LICENSE file in the root", "add the project's license, when it has one", licenses or ["LICENSE"])


def check_gitattributes(report, root):
    text = read(os.path.join(root, ".gitattributes"))
    ok = None if text is None else "* text=auto eol=lf" in text.splitlines()
    report.add("files.gitattributes.eol", "03 section 2.2", RULE, ".gitattributes holds `* text=auto eol=lf`", ok,
               "the line is missing", "add the line `* text=auto eol=lf` to .gitattributes",
               ["line found: * text=auto eol=lf"] if ok else
               ["lines in the file: " + (" | ".join(l for l in text.splitlines() if l.strip()) or "none")
                if text is not None else ".gitattributes cannot be read"])


def check_changelog(report, text):
    guide = "03 section 7"

    if text is None:
        report.add("files.changelog.readable", guide, RULE, "CHANGELOG.md can be read", False, "no CHANGELOG.md",
                   "create CHANGELOG.md")
        return

    lines = text.split("\n")

    def at(numbers):
        """One detail line per line number: the number and the heading's text."""
        return ["line {}: {}".format(n, lines[n - 1].rstrip()) for n in numbers]

    crlf = sum(1 for line in lines if line.endswith("\r"))
    report.add("files.changelog.eol", "03 section 2.2", RULE, "CHANGELOG.md uses Unix line endings",
               "\r" not in text, "the file has carriage returns",
               "convert it to LF line endings (and add .gitattributes)",
               ["{} of {} lines end with a carriage return".format(crlf, len(lines))])

    banned = [i + 1 for i, line in enumerate(lines) if BANNED_SECTIONS.match(line)]
    report.add("files.changelog.no-bug-plan-sections", guide, RULE,
               "the changelog has no 'Known bugs' or 'Planned' sections", not banned,
               "{} such heading(s)".format(len(banned)),
               "move known bugs and planned work to tickets",
               at(banned) or ["{} lines searched, no such heading".format(len(lines))])

    wip = [i for i, line in enumerate(lines) if WIP_ANY.match(line)]
    bad_wip = [i + 1 for i in wip if not WIP.match(lines[i])]
    report.add("files.changelog.wip-heading", "02 section 3", RULE,
               "a WIP-Version heading carries nothing but a +V, +s or +m marker", not bad_wip,
               "{} WIP-Version heading(s) have other text".format(len(bad_wip)),
               "write `## WIP-Version` with at most one marker",
               at(bad_wip) or at([i + 1 for i in wip]) or ["no WIP-Version heading"])
    report.add("files.changelog.one-wip", "04 section 4.1", RULE, "at most one open WIP-Version heading",
               len(wip) <= 1, "{} WIP-Version headings".format(len(wip)), "keep a single open heading",
               at([i + 1 for i in wip]) or ["no WIP-Version heading"])

    finals = []
    bad_finals = []

    for i, line in enumerate(lines):
        match = FINAL.match(line)

        if match:
            finals.append((int(match.group(2)), int(match.group(3)), int(match.group(4)), bool(match.group(5)), i))
        elif FINAL_ANY.match(line):
            bad_finals.append(i + 1)

    report.add("files.changelog.version-heading", guide, RULE,
               "finalized headings read `## V<V>.<s>.<m> — yyyy-mm-dd hh:mm UTC`", not bad_finals,
               "{} version heading(s) of another form".format(len(bad_finals)),
               "rewrite them as `## V1.2.3 — 2026-10-05 14:32 UTC`",
               at(bad_finals) or ["{} finalized heading(s) read correctly".format(len(finals))])
    report.add("files.changelog.has-version", "02 section 3", RULE, "the changelog has a finalized version",
               bool(finals), "no finalized version heading", "finalize the first version (V0.1.0)",
               at([f[4] + 1 for f in finals]) or ["no heading of the form `## V<V>.<s>.<m> — …`"])

    main_line = [f for f in finals if not f[3]]
    unordered = ["line {}: V{}.{}.{} is listed above the newer V{}.{}.{} (line {})".format(
        a[4] + 1, *a[:3], *b[:3], b[4] + 1) for a, b in zip(main_line, main_line[1:]) if a[:3] < b[:3]]
    report.add("files.changelog.newest-first", guide, RULE, "the versions are listed newest first",
               not unordered, "{} version(s) out of order".format(len(unordered)),
               "order the finalized versions from the newest down",
               unordered or ["{} versions, newest first".format(len(main_line))])

    top = next((i for i, line in enumerate(lines) if WIP.match(line) or FINAL_ANY.match(line)), None)
    report.add("files.changelog.wip-on-top", "04 section 4.1", RULE, "the open WIP-Version heading is first",
               not wip or wip[0] == top, "a finalized version comes above the WIP-Version heading",
               "move the WIP-Version heading to the top",
               ["WIP-Version heading on line {}; the first version heading is on line {}".format(
                   wip[0] + 1, (top or 0) + 1)] if wip else ["no WIP-Version heading"])

    block_problems = []
    checked = 0
    in_version = False

    for i, line in enumerate(lines):
        if line.startswith("## "):
            in_version = True
        elif line.startswith("### ") and in_version:
            checked += 1

            if line != "### WIP-Build" and not BUILD.match(line):
                block_problems.append(i + 1)
        elif line.startswith("#### ") and in_version:
            checked += 1

            if not (TICKET.match(line) or REF.match(line) or AUTO_REF.match(line)):
                block_problems.append(i + 1)

    report.add("files.changelog.headings", guide, RULE,
               "build and ticket headings follow the forms of the guide", not block_problems,
               "{} heading(s) do not".format(len(block_problems)),
               "use `### Build <stamp> (branch <name>)` and `#### #123 — <title>` or `#### REF <token> — <reason>`",
               at(block_problems) or ["{} build and ticket headings checked".format(checked)])


def check_hooks(report, root):
    present = [h for h in HOOKS if os.path.isfile(os.path.join(root, ".githooks", h))]
    report.add("files.hooks.present", "03 section 2.2", RULE, "the three hooks are in .githooks/",
               len(present) == len(HOOKS),
               "missing: {}".format(", ".join(h for h in HOOKS if h not in present)),
               "add the hooks of the standard",
               ["{}: {}".format(h, "found" if h in present else "missing") for h in HOOKS])
    code, value = git(root, "config", "core.hooksPath")
    ok = None if not os.path.isdir(os.path.join(root, ".git")) else (code == 0 and value == ".githooks")
    report.add("files.hooks.active", "04 section 1", RULE, "this clone has the hooks activated", ok,
               "core.hooksPath is {!r}".format(value if code == 0 else ""),
               "run `git config core.hooksPath .githooks`",
               ["core.hooksPath = {}".format(value if code == 0 else "(not set)")])


def check_wiki(report, root):
    wiki = os.path.join(root, "doc", "wiki")

    if not os.path.isdir(wiki):
        report.add("files.wiki.home", "03 section 9.2", RULE, "the wiki has a Home page", False,
                   "no doc/wiki folder", "create doc/wiki/Home.md", ["doc/wiki is not a folder"])
        return

    names = os.listdir(wiki)
    report.add("files.wiki.home", "03 section 9.2", RULE, "the wiki has a Home page", "Home.md" in names,
               "no Home.md", "add Home.md as the index",
               ["{} file(s) in doc/wiki".format(len(names)), "Home.md: " + ("found" if "Home.md" in names else "missing")])
    bad = [n for n in names if os.path.isfile(os.path.join(wiki, n))
           and (not n.endswith(".md") or " " in n or "_" in n)]
    report.add("files.wiki.names", "03 section 9.2", RULE,
               "wiki pages are markdown files named by title with hyphens", not bad,
               "{} unfit name(s)".format(len(bad)), "rename them like `Getting-Started.md`",
               bad or [n for n in names if os.path.isfile(os.path.join(wiki, n))] or ["no pages"])


def check_automation(report, root):
    github = os.path.join(root, ".github")
    workflows = os.path.join(github, "workflows")
    found = [n for n in os.listdir(workflows) if n.endswith((".yml", ".yaml"))] if os.path.isdir(workflows) else []
    has_workflow = bool(found)
    report.add("files.automation.workflow", "03 section 2.2", RULE, "a workflow file exists in .github/workflows",
               has_workflow, "no workflow", "add the workflow of the standard",
               [".github/workflows/" + n for n in found] or [".github/workflows has no .yml or .yaml file"])
    report.add("files.automation.pr-template", "06 section 3", RECOMMENDATION, "the pull request template exists",
               os.path.isfile(os.path.join(github, "pull_request_template.md")), "no template",
               "add .github/pull_request_template.md", [".github/pull_request_template.md"])
    report.add("files.automation.manifest", "03 section 2.2", RECOMMENDATION,
               "the automation manifest exists", os.path.isfile(os.path.join(github, "automation-manifest.json")),
               "no .github/automation-manifest.json", "generate it with check_manifest.py --update",
               [".github/automation-manifest.json"])

    own_code = os.path.isdir(os.path.join(github, "scripts"))
    tests = os.path.isdir(os.path.join(root, "tests"))
    report.add("files.automation.tests", "03 section 2.2", RULE, "the automation's logic has tests",
               tests if own_code else True, "scripts exist but there is no tests/ folder", "add tests/",
               ["tests/ folder: " + ("found" if tests else "missing"),
                ".github/scripts: " + ("found" if own_code else "none, so no tests are needed")])


def check_instructions(report, root):
    text = read(os.path.join(root, "AGENTS.md"))
    ok = None if text is None else ("guides" in text.lower())
    report.add("files.agents.guides", "09 section 6", RULE, "AGENTS.md points the assistant to the guides", ok,
               "AGENTS.md does not mention the guides", "say that the assistant follows the guides' checklists",
               ["AGENTS.md: " + ("cannot be read" if text is None else "the word 'guides' is " +
                                 ("present" if ok else "absent"))])


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    verbose = "--verbose" in argv
    json_path = argv[argv.index("--json") + 1] if "--json" in argv else None

    if json_path in args:
        args.remove(json_path)

    if len(args) != 1 or not os.path.isdir(args[0]):
        print(__doc__)
        return 2

    report = audit(os.path.abspath(args[0]))
    print(format_report(report, verbose))

    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report.as_dict(verbose), f, indent=2)

    return 1 if report.failures(RULE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
