# Governance

The standard for how a small team works on a project that lives on GitHub: how to branch and merge, how
versions are numbered, how changes are recorded, how tickets and the board are used, how releases and
hotfixes are made, and how an AI assistant takes part. It is written for developers and for the assistants
that work with them, and it is meant to apply unchanged to any project.

## What is here

| Folder | What it holds |
|---|---|
| [`guides/`](guides/README.md) | The guides (01 to 10), the appendices (A to D) and a combined copy for reading in one place. Start with [`guides/README.md`](guides/README.md). |
| [`tools/`](tools/) | `combine.py` rebuilds the combined copy from the separate files. `xref_check.py` checks that every cross-reference between the guides points at a section that exists. |
| [`tests/`](tests/) | Tests for the tools. They also fail if the combined copy is out of date or a cross-reference is broken. |
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

## Status

This repository does not yet apply the standard to itself completely: the hooks and the versioning workflow are
not set up here. The guides describe the standard as it will be once they are.

See [`CHANGELOG.md`](CHANGELOG.md) for what has changed.

## Licence

Two licences, by the kind of file. The guides and other documentation are under
[CC BY 4.0](LICENSE-CC-BY-4.0.txt). The code (`tools/`, `tests/`, and the workflows, scripts and hooks) is under
the [MIT licence](LICENSE-MIT.txt). [`LICENSE`](LICENSE) lists which paths fall under which.
Copyright (c) 2026 The Shadow on the Moon, Inc.
