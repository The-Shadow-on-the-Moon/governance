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
| [All guides in one file](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/Developer-Guides-Complete.md) | The README, guides 01 to 10 and appendices A to E, for reading in one place. |
| [Appendix A: the daily flow](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-a-cheat-sheet-daily-flow.md) | The whole flow on one page. |
| [Appendix B: if this then that](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-b-cheat-sheet-if-then.md) | Common situations, what to do, and where to read more. |
| [Appendix E: ticket model](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-e-ticket-model.md) | The design of a ticket as a whole, and its life from creation to release. |
| [Appendix C: ticket fields](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md) | Every ticket field with its values and who sets them. |
| [Appendix D: ticket examples](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-d-ticket-examples.md) | Example tickets for each Type, as full forms. |

The ten guides:
[01 Concepts and vocabulary](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/01-concepts-and-vocabulary.md),
[02 Branching and merging strategy](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/02-branching-and-merging-strategy.md),
[03 Project structure](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/03-project-structure.md),
[04 Starting work](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/04-starting-work.md),
[05 Working and committing](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/05-working-and-committing.md),
[06 Syncing and merging](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/06-syncing-and-merging.md),
[07 Issues and the board in practice](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/07-issues-and-the-board-in-practice.md),
[08 Releases, hotfixes and retiring branches](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/08-releases-hotfixes-and-retiring-branches.md),
[09 Working with an AI assistant](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/09-working-with-an-ai-assistant.md),
[10 New-project bootstrap](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/10-new-project-bootstrap.md).

## Working on the guides

The separate files in `guides/` are the source of truth, and the combined file is rebuilt from them with
`python tools/combine.py`. See the repository's readme.

## Licence

The guides and other documentation are under CC BY 4.0. The code (`tools/`, `tests/`, and the workflows, scripts and hooks) is under the MIT licence. See the [licence file](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/LICENSE) for which paths fall under which. Copyright (c) 2026 The Shadow on the Moon, Inc.

## Roles and board

- [Ticket model](Ticket-Model)
- [Automation](Automation)
- [Roles and access](Roles-and-Access)
- [Board views](Board-Views)
