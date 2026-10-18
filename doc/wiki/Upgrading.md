# Upgrading a project to a newer version of the standard

How a project that already follows the standard (fully, partly, or from an older version) is brought to a newer
version, what the kit does, and what counts as a breaking change.

## The route

1. Copy `adoption/ADOPT-OR-UPDATE-GOVERNANCE.md` from a checkout of the standard into the root of the project and give
   it to an assistant with the starter prompt: *Follow ADOPT-OR-UPDATE-GOVERNANCE.md in this folder, phase by phase, and
   stop at every gate.* See [Adoption kit](Adoption-Kit).
2. The assistant surveys the project (`tools/survey.py`), plans, asks the decisions, and goes through the migration
   chain (`tools/upgrade.py`) one step at a time, each with a dry run first.
3. By hand, the same tools can be run from the checkout: `python -I <checkout>/tools/upgrade.py <project>` is a dry
   run; add `--apply` to apply, `--only <ID>` for one step.

The state decides, not the version label: a step is needed when the project lacks what it brings. Running the chain
again resumes it, because the survey is made again.

## The steps

| ID | Since | What | Needs a flag |
|---|---|---|---|
| A1 | V0.3.0 | The board, the labels and the issue types (the install module) | |
| A2 | V0.4.0 | The Delivery option *Implemented* (every ticket keeps its value) | |
| A4 | V0.7.0 | The labels of Appendix C, including `dummy` | |
| A6 | V0.10.0 | The field *Fix*, the values of Priority, Size and Risk, the field *Kind* | |
| F1 | V0.3.0 | The automation files of the standard (each replaced file is saved first) | `--overwrite-edited` for a file edited locally |
| M1 | V0.15.0 | The manifest names the real version, never the placeholder | |
| A5 | V0.8.0 | The saved views | `--with-views` |
| A7 | V0.11.0 | The Version of the tickets in the board form | |
| A7b | V0.11.0 | The removal of the field *Version#* (its values are saved first) | `--delete-version-number` |
| A8 | V0.13.0 | The Type source (`TYPE_SOURCE`) of a personal account | |
| L1 | V0.15.0 | The legacy Version tickets converted to closed records | `--convert-legacy` |

The inventory of what each version needs is `doc/migration-inventory.md`. A project older than V0.3.0 has no automation
to migrate: it is an adoption.

## What the first refresh does after an upgrade

The new files make the scheduled run judge the board with the rules of the new version. Expect, once:

- a **burst of Fix entries** and, after a wait, comments, for tickets that already broke a rule;
- **stale plans**: an unshipped ticket whose Version is at or below the highest finalized version;
- **Resolution *Done* filled** on Completed tickets that had no Resolution, and cleared on tickets that are not
  Completed. This is the rule of V0.15.0; it replaces a step a person did by hand.

The survey previews these numbers before anything is applied.

## What counts as breaking

A change is **breaking** when a project cannot get it by copying the automation files: a board field or option, a label,
an issue type, a repository or organization setting, a saved view, a conversion of data, a file the project edits that
is renamed or removed, or an input a rule starts to require. Everything else (a fix, a new rule that needs nothing new)
is not.

Until the standard reaches 1.0, a breaking change can come in any version, including a `s` or `m`. What it promises
instead: every breaking change has, in its changelog entry, a line

```
- Project action: A5, L1: the saved views and the legacy Version tickets
```

whose IDs are steps of `tools/migrations/`, and the step exists in the same release. A test fails for a marker that
names no step. A criterion for a stable 1.0 is left open on purpose.

## If something goes wrong

Every step that replaces or deletes keeps a restore file or a backup in the folder `.upgrade-state/` of the project, which git
ignores. The chain stops at the first step that does not leave the project as it should be; nothing after it runs. The
mirror backup of phase 0 and git history are the last resort. Settings are never changed by the kit: they are the
administrator's.
