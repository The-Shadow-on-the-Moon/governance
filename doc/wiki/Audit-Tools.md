# Audit tools

Scripts that look at an existing project and report which rules and recommendations of the guides it already
follows. They are a first step before adopting the standard: they show what differs, and change nothing.

They live in `tools/` of this repository and use only Python 3 and, for the GitHub parts, the
[`gh` command line tool](https://cli.github.com/) signed in to an account that can read the repository.

## Running them

```
python tools/audit.py <project-path>                  # all four audits
python tools/audit.py <project-path> --offline        # only the files and git audits (no gh, no network)
python tools/audit.py <project-path> --json audit.json
```

| Option | Meaning |
|---|---|
| `--offline` | Skip the GitHub and board audits. |
| `--repo owner/name` | The GitHub repository, when the project's `origin` remote is not it (or there is none). |
| `--board <number>` | The board, when the repository links more than one. The first one is used otherwise. |
| `--json <file>` | Also write the whole result to a JSON file. |

Each audit can also be run alone, with the same project path and the `--json` option:
`audit_files.py`, `audit_git.py`, `audit_github.py` (`--repo`) and `audit_board.py` (`--repo`, `--board`).

The exit code is `1` when a rule fails, `2` for bad arguments, and `0` otherwise. A failed recommendation, or a
check that could not be made, never fails the run.

## What each audit checks

| Audit | Looks at | Needs |
|---|---|---|
| **Files** (`audit_files.py`) | The places every project has (readme, `CHANGELOG.md`, `doc/wiki/`, `.githooks/`, `.github/`, `AGENTS.md`, `.gitignore`, `.gitattributes`, license); the `* text=auto eol=lf` line; the changelog (Unix line endings, no *Known bugs* or *Planned* sections, one open `WIP-Version` heading on top with a valid marker, version headings and their order, build and ticket headings); the hooks and whether they are active in the clone; the wiki (`Home.md`, page names); the workflow, pull request template, manifest and tests; that `AGENTS.md` points to the guides. | A clone. |
| **Git** (`audit_git.py`) | `main` exists and is the only integration line; branch names are kebab-case without `/` (or the hotfix form); tag names follow the namespaces; release tags are on `main` and name a changelog version; work reaches `main` through merge commits; no `fix:` or `feat:` subject prefix; no assistant co-author or "generated with" line. | A clone. Run `git fetch` first to include the remote branches. |
| **GitHub** (`audit_github.py`) | Merge methods, automatic branch deletion, default branch, issues, projects and wiki; that the owner is an organization; protection of `main` and the administrator bypass; Actions; the secret `PROJECT_TOKEN` and the variable `BOARD_NUMBER`; the labels (the 14 Area labels and `dummy`, described, standard colors); the eight issue types. | `gh`; administration access for protection and secrets. |
| **Board** (`audit_board.py`) | The board linked to the repository; every field with its kind, values and colors; the saved views against `.github/views.json`; the tickets (issue type, Size, Status against open or closed, Resolution, Origin and REF, the board form of Version, Version tickets, Alerts, Area labels). Throwaway (`dummy`) tickets and pull requests are skipped. | `gh` with the `project` scope (`gh auth refresh -s project`). |

The tables the audits compare with are not copied: the fields, their values and colors come from
`.github/scripts/preflight.py`, the views from `.github/views.json`, and the labels and issue types from
[Appendix C](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md),
so the audits follow the standard when it changes.

## Reading the report

Only checks that are not a pass are listed:

```
[FAIL] files.changelog.no-bug-plan-sections (rule, guide 03 section 7): the changelog has no 'Known bugs' or 'Planned' sections
    such a heading is on line(s) 12
    fix: move known bugs and planned work to tickets
```

- **pass, fail, not-checkable.** *Not-checkable* means the audit could not tell: `gh` is missing or not signed in, the
  data needs more access, or the project is not a clone. It is not a failure.
- **rule or recommendation** is the strength the guide gives the statement; the guide section is named so you can read
  the reason.
- The report ends with a total of rules and of recommendations, counted apart.

The JSON file holds the same: `summary` (counts by strength and result) and `audits`, each with its `area`, `counts`
and every check (`id`, `guide`, `strength`, `title`, `result`, `message`, `hint`). The ids are stable, so two runs can
be compared to follow progress.

## Limits

- The audits read facts. What needs judgment (is a ticket well written, is a changelog entry accurate, is the
  documentation current) is left to people.
- The history check looks at the first-parent line of `main`: commits made by the automation (`Finalize`, `Flag
  bypass`, `Fill in a build heading`) are allowed there.
- A project that adopts the standard late will fail rules about its past (old tags, old commit messages). The report
  says what, and the hint says what to do from now on; history is not rewritten.
