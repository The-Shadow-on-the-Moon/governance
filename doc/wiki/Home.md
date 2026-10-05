# Governance

The standard for how a small team works on a project that lives on GitHub: branching and merging,
versioning, the changelog, tickets and the board, releases and hotfixes, and working with an AI assistant.
It is written for developers and for the assistants that work with them, and it is meant to apply unchanged
to any project.

## The guides

The guides are kept in the repository, and this page only points to them.

| Guide | What it covers |
|---|---|
| [Start here: the guide index](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/README.md) | The reading order, the ideas that run through the guides, the roles, and what the standard assumes. |
| [All guides in one file](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/Developer-Guides-Complete.md) | The README, guides 01 to 10 and appendices A to D, for reading in one place. |
| [Appendix A: the daily flow](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-a-cheat-sheet-daily-flow.md) | The whole flow on one page. |
| [Appendix B: if this then that](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-b-cheat-sheet-if-then.md) | Common situations, what to do, and where to read more. |
| [Appendix C: ticket fields](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md) | Every ticket field with its values and who sets them. |

## Working on the guides

The separate files in `guides/` are the source of truth, and the combined file is rebuilt from them with
`python tools/combine.py`. See the repository's readme.

## Licence

The guides and other documentation are under CC BY 4.0. The code (`tools/`, `tests/`, and the workflows, scripts and hooks) is under the MIT licence. See the [licence file](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/LICENSE) for which paths fall under which. Copyright (c) 2026 The Shadow on the Moon, Inc.

## Roles and board

- [Roles and access](Roles-and-Access)
- [Board views](Board-Views)
