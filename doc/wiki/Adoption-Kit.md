# Adoption kit

The tools, the instruction file and the commands that take a project to the standard, or to a newer version of it,
without assuming anything about the project. The route is in [Adopting the standard](Adopting-the-Standard) and
[Upgrading](Upgrading); this page says what is in the kit.

## The instruction file

`adoption/ADOPT-OR-UPDATE-GOVERNANCE.md` is the one file a person copies into the root of the target project (not
committed there) and gives to an assistant. It has nine standing rules and ten phases (0 preconditions, 1 survey,
2 plan, 3 decisions, 4 settings, 5 files, 6 board and tickets, 7 land, 8 prove, 9 report), each ending in a gate where
the assistant stops. Where it differs from the guides, the guides win.

## The tools (in `tools/`, run from a checkout of the standard with its full history)

| Tool | What it does |
|---|---|
| `survey.py` | Reads the real state of a project and changes nothing: repository, files (which version each automation file comes from), settings, organization, board; names the state, the gaps and the blockers; previews what the first refresh would do. |
| `install.py` | For a project with none of it: labels, issue types (or the field Kind), the board with fields and views. Creates only what is missing. |
| `upgrade.py` | The migration chain (`tools/migrations/`): the steps a project needs, one at a time, each checked afterwards. |
| `convert_legacy.py` | Converts the legacy Version tickets of a board into closed records. |
| `build_fingerprints.py` | Builds, from the standard's own history, the hash of each automation file at each version; the survey uses it to tell which version a file is from. |

All of them are a dry run until `--apply`, run as `python -I <checkout>/tools/<tool>.py <project>` (never from inside
the project), and keep their notes, restore files and backups in `.upgrade-state/` of the project, which git
ignores through `.git/info/exclude`.

## The commands (in `.claude/commands/`)

Sixteen thin commands for the daily operations, copied to a project with the automation files: `gov-status`,
`gov-ticket`, `gov-start`, `gov-changelog`, `gov-commit`, `gov-review`, `gov-sync`, `gov-pr`, `gov-after-merge`,
`gov-plan`, `gov-fix`, `gov-release`, `gov-hotfix`, `gov-retire`, `gov-audit`, `gov-upgrade`. Each names the guide
section and the tool to follow; none commits, pushes, merges, releases or completes a ticket by itself.

## What the kit never does

It does not change repository, organization or board settings, create a release, close a ticket as Completed, or
delete anything that is not in its log and its restore files.
