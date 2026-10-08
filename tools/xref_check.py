"""Check the cross-references between the guides.

A reference such as "the guide on project structure, section 4.3" or "(section 2.1)" must point at a section
that exists. This lists every reference that does not.

Usage:
    python tools/xref_check.py        print the sections found and any problems, exit 1 if there are problems
"""
import os
import re
import sys

GUIDES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guides")

FILES = {
    "01": "01-concepts-and-vocabulary.md",
    "02": "02-branching-and-merging-strategy.md",
    "03": "03-project-structure.md",
    "04": "04-starting-work.md",
    "05": "05-working-and-committing.md",
    "06": "06-syncing-and-merging.md",
    "07": "07-issues-and-the-board-in-practice.md",
    "08": "08-releases-hotfixes-and-retiring-branches.md",
    "09": "09-working-with-an-ai-assistant.md",
    "10": "10-new-project-bootstrap.md",
}

NAMES = [
    (r"branching and merging", "02"),
    (r"project structure", "03"),
    (r"starting work", "04"),
    (r"working and committing", "05"),
    (r"syncing and merging", "06"),
    (r"issues and the board in practice|issues and the board", "07"),
    (r"releases and hotfixes|releases, hotfixes and retiring branches", "08"),
    (r"working with an (?:AI )?assistant", "09"),
    (r"new-project bootstrap", "10"),
    (r"concepts", "01"),
]


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def load(base=GUIDES_DIR):
    return {k: read(os.path.join(base, v)) for k, v in FILES.items()}


def find_sections(text):
    sections = {}

    for k, t in text.items():
        found = set()
        in_code = False

        for line in t.splitlines():
            if line.startswith("```"):
                in_code = not in_code
                continue

            if in_code:
                continue

            m = re.match(r"^#{2,4} (\d+(?:\.\d+)?)[ .]", line)

            if m:
                found.add(m.group(1))

        sections[k] = found

    return sections


def check(base=GUIDES_DIR):
    """Return (sections, checked, problems)."""
    text = load(base)
    sections = find_sections(text)
    problems = []
    checked = 0

    for k, t in text.items():
        flat = re.sub(r"\s+", " ", t)

        # "<guide name> ... section N" in another guide
        for pat, tgt in NAMES:
            for m in re.finditer(r"(?:guide on |\*)?(?:" + pat + r")\*?[^.|()]{0,25}?sections? "
                                 r"(\d+(?:\.\d+)?(?: and \d+(?:\.\d+)?)*)", flat, re.I):
                for n in re.findall(r"\d+(?:\.\d+)?", m.group(1)):
                    checked += 1

                    if n not in sections[tgt]:
                        problems.append((k, tgt, n, m.group(0)[:90]))

        # "(section N)" inside the same guide, unless it follows "the guide on ..."
        for m in re.finditer(r"\(section (\d+(?:\.\d+)?)\)|section (\d+(?:\.\d+)?) of this guide"
                             r"|; section (\d+(?:\.\d+)?)", flat):
            before = flat[max(0, m.start() - 90):m.start()]

            if re.search(r"guide on [^.()]*$", before):
                continue

            n = next(g for g in m.groups() if g)
            checked += 1

            if n not in sections[k]:
                problems.append((k, k, n, m.group(0)))

    return sections, checked, problems


def main():
    sections, checked, problems = check()
    print("sections per guide:")

    for k in sorted(sections):
        print(k, sorted(sections[k], key=lambda s: [int(x) for x in s.split(".")]))

    print()
    print("checked", checked, "references; problems:", len(problems))

    for p in problems:
        print(p)

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
