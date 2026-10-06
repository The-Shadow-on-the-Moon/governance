"""Rebuild guides/Developer-Guides-Complete.md from the separate guide files.

The separate files are the source of truth. The combined file is a derived copy for reading in one place:
the README as front matter, a linked table of contents, guides 01 to 10 and appendices A to E, with every
heading demoted by one level.

Usage:
    python tools/combine.py           rewrite the combined file
    python tools/combine.py --check   exit 1 if the combined file is out of date, without changing it
"""
import os
import re
import sys

GUIDES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guides")
OUT_NAME = "Developer-Guides-Complete.md"

GUIDES = [
    ("01", "01-concepts-and-vocabulary.md"),
    ("02", "02-branching-and-merging-strategy.md"),
    ("03", "03-project-structure.md"),
    ("04", "04-starting-work.md"),
    ("05", "05-working-and-committing.md"),
    ("06", "06-syncing-and-merging.md"),
    ("07", "07-issues-and-the-board-in-practice.md"),
    ("08", "08-releases-hotfixes-and-retiring-branches.md"),
    ("09", "09-working-with-an-ai-assistant.md"),
    ("10", "10-new-project-bootstrap.md"),
]
APPENDICES = [
    "appendix-a-cheat-sheet-daily-flow.md",
    "appendix-b-cheat-sheet-if-then.md",
    "appendix-c-ticket-fields-reference.md",
    "appendix-d-ticket-examples.md",
    "appendix-e-ticket-model.md",
]


def read(name, base=GUIDES_DIR):
    with open(os.path.join(base, name), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def shift_headings(text):
    """Demote every heading by one level, outside code fences, and return the lines."""
    result = []
    in_code = False

    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            result.append(line)
            continue

        if not in_code:
            m = re.match(r"^(#{1,5}) (.*)$", line)

            if m:
                result.append("#" * (len(m.group(1)) + 1) + " " + m.group(2))
                continue

        result.append(line)

    return result


def split_title(text):
    """Return (title, rest), where the title is the first H1 line."""
    lines = text.strip("\n").split("\n")

    if not lines[0].startswith("# "):
        raise ValueError("a file does not start with a title line: " + lines[0][:60])

    return lines[0][2:].strip(), "\n".join(lines[1:]).strip("\n")


def slugger():
    seen = {}

    def slug(text):
        t = text.lower()
        t = re.sub(r"[`*_]", "", t)
        t = re.sub(r"[^\w\- ]", "", t, flags=re.UNICODE)
        t = t.strip().replace(" ", "-")
        n = seen.get(t, 0)
        seen[t] = n + 1
        return t if n == 0 else "{}-{}".format(t, n)

    return slug


def build(base=GUIDES_DIR):
    """Return the combined document as a string."""
    readme = read("README.md", base).strip("\n")

    if not readme.startswith("# ") or "\n" not in readme:
        raise ValueError("README.md must start with a title line and have a body")

    first, rest = readme.split("\n", 1)
    note = ("*This is a combined copy of the README, the guides and the appendices, for reading in one place. "
            "The separate files are the source of truth: make changes there.*")
    front = first + "\n\n" + note + "\n" + rest

    body = []

    for num, name in GUIDES:
        title, text = split_title(read(name, base))
        body.append("## Guide {}: {}\n\n".format(num, title) + "\n".join(shift_headings(text)))

    for name in APPENDICES:
        title, text = split_title(read(name, base))
        body.append("## {}\n\n".format(title) + "\n".join(shift_headings(text)))

    combined_body = "\n\n---\n\n".join(body)

    # the contents list is built from the headings of the whole document
    full_for_toc = front + "\n\n## Table of contents\n\n" + combined_body
    slug = slugger()
    toc = []
    in_code = False

    for line in full_for_toc.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            continue

        if in_code:
            continue

        m = re.match(r"^(#{1,6}) (.*)$", line)

        if not m:
            continue

        level, text = len(m.group(1)), m.group(2).strip()
        s = slug(text)

        if level == 2 and (text.startswith("Guide ") or text.startswith("Appendix ")):
            toc.append("- [{}](#{})".format(text, s))
        elif level == 3 and toc and re.match(r"^\d+\. ", text):
            toc.append("  - [{}](#{})".format(text, s))

    toc_text = "## Table of contents\n\n" + "\n".join(toc)
    return front + "\n\n---\n\n" + toc_text + "\n\n---\n\n" + combined_body + "\n"


def main(argv):
    document = build()
    path = os.path.join(GUIDES_DIR, OUT_NAME)

    if "--check" in argv:
        current = ""

        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                current = f.read().replace("\r\n", "\n")

        if current != document:
            print("{} is out of date: run python tools/combine.py".format(OUT_NAME))
            return 1

        print("{} is up to date".format(OUT_NAME))
        return 0

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(document)

    print("wrote {}: {} lines".format(OUT_NAME, document.count("\n")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
