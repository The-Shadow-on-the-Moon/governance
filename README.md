# Governance

The standard for how a small team works on a project that lives on GitHub: how to branch and merge, how
versions are numbered, how changes are recorded, how tickets and the board are used, how releases and
hotfixes are made, and how an AI assistant takes part. It is written for developers and for the assistants
that work with them, and it is meant to apply unchanged to any project.

## What is here

| Folder | What it holds |
|---|---|
| [`guides/`](guides/README.md) | The guides (01 to 11), the appendices (A to G) and a combined copy for reading in one place. Start with [`guides/README.md`](guides/README.md). |
| [`adoption/`](adoption/) | `ADOPT-OR-UPDATE-GOVERNANCE.md`, the one file a person copies into the root of a project to have an assistant adopt the standard there or update it, using the tools of `tools/` (see the [adoption kit](doc/wiki/Adoption-Kit.md) and [upgrading](doc/wiki/Upgrading.md)). |
| [`.claude/commands/`](.claude/commands/) | The `gov-*` commands for the daily operations. |
| [`tools/`](tools/) | `combine.py` rebuilds the combined copy from the separate files. `xref_check.py` checks that every cross-reference between the guides points at a section that exists. `audit.py` (with `audit_files.py`, `audit_git.py`, `audit_github.py` and `audit_board.py`, the shared `audit_common.py`, and `audit_baseline.py` and `audit_plan.py`) reports which rules of the guides an existing project already follows, and what to do about each finding; see the [audit tools](doc/wiki/Audit-Tools.md). `install.py` makes the labels, the issue types and the board of a project that has none (a dry run until `--apply`); `survey.py` reads the real state of a project and changes nothing; `convert_legacy.py` converts the legacy Version tickets of a board (a dry run until `--apply`); `upgrade.py` brings a project to the version of the standard it runs from, step by step, with the modules of `tools/migrations/` (a dry run until `--apply`); `kit_common.py` holds what the tools of the adoption and upgrade kit share. `build_fingerprints.py` derives from the history of this repository the hash of each automation file at each version, and says which version(s) the automation files of a project come from (`--identify <project>`); see [`doc/migration-inventory.md`](doc/migration-inventory.md) for what a project must do besides copying files. |
| [`tests/`](tests/) | Tests for the tools and for the automation. They also fail if the combined copy is out of date, a cross-reference is broken, or an automation file differs from the manifest. |
| [`.githooks/`](.githooks/) | The local hooks: they stamp the build, draft the commit message and warn. |
| [`.github/`](.github/) | The versioning workflow and its scripts (`scripts/`), the manifest of the automation files, the wiki-sync workflow, the workflow that switches the schedule back on after GitHub disables it for inactivity, and the pull request template. |
| [`doc/wiki/`](doc/wiki/Home.md) | The wiki pages, copied to the repository's wiki by a workflow. |

## Working on the guides

The separate files in `guides/` are the source of truth. After changing any of them:

```
python tools/combine.py        # rebuild guides/Developer-Guides-Complete.md
python tools/xref_check.py     # check the cross-references
python -m unittest discover -s tests
```

`python tools/combine.py --check` only reports whether the combined copy is up to date.

The tools need Python 3 and nothing else.

## The automation

The hooks, the versioning workflow (the advisory check on pull requests, the push step and the fallback for
skipped hooks on branches, the finalize step and bypass detection on `main`, and a scheduled run for dates, stale
tickets and the Fix field that lists broken field rules), the steps a person starts by hand from the Actions tab (release, hotfix finish,
branch retire) and the check script are described on the [wiki](doc/wiki/Automation.md). The
automation files are covered by a manifest: after editing one, rewrite the manifest and run the tests.

```
python .github/scripts/check_manifest.py --update --pending      # in this repository; a project that uses the standard runs --update
python .github/scripts/check_manifest.py       # all files should be unchanged
```

## Setup

After cloning, activate the local hooks once (they stamp the build, draft the commit message and warn):

```
git config core.hooksPath .githooks
```

Check with `git config core.hooksPath`, which should print `.githooks`.

## Status

This repository applies the standard to itself, including all of its automation. Anything still open is
tracked in a ticket. The schedule runs from `main`.

See [`CHANGELOG.md`](CHANGELOG.md) for what has changed.

## License

Two licenses, by the kind of file. The guides and other documentation are under
[CC BY 4.0](LICENSE-CC-BY-4.0.txt). The code (`tools/`, `tests/`, the workflows, scripts and hooks, and the configuration files they read) is under
the [MIT license](LICENSE-MIT.txt). [`LICENSE`](LICENSE) lists which paths fall under which.
Copyright (c) 2026 The Shadow on the Moon, Inc.
