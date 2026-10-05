# Developer Guides

A standard for how a small team works on a project that lives on GitHub: how to branch and merge, how
versions are numbered, how changes are recorded, how tickets and the board are used, and how releases and
hotfixes are made. It is written for developers and for the AI assistants that work with them, and it is
meant to apply unchanged to any project.

## How to read the guides

Each topic says what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

Every procedural guide ends with a checklist, and the appendices collect the flow and the common
situations on a page each.

## The guides

| Guide | What it covers | Read it when |
|---|---|---|
| **01 Concepts and vocabulary** | Version, build, compile stamp and release; the timestamp rule; the changelog, ticket, branch, role and automation words; the git and GitHub names used. | a word is unclear, or you are new |
| **02 Branching and merging strategy** | Branch types, naming, tags, where versions come from, keeping `main` clean, how a branch lands, and enforcement. | you need the rules and their reasons |
| **03 Project structure** | The pieces of a project and how they connect: the repository, tickets, fields, special tickets, pull requests, the changelog, documentation, and who sets what. | you need to know what something is |
| **04 Starting work** | From a task to the first push: setup, the ticket, the branch, the changelog entry. | you are starting a piece of work |
| **05 Working and committing** | The rhythm of work, writing changelog entries, what to update, building and testing, the commit, backfilling placeholders, keeping the ticket current. | you are working |
| **06 Syncing and merging** | Syncing `main`, getting ready to land, the pull request, the merge, what happens afterwards, and bypassing. | your work is ready to land |
| **07 Issues and the board in practice** | Triage, the daily board, review and verification, suspending and abandoning, Alerts, planning ahead, housekeeping. | you manage the board |
| **08 Releases, hotfixes and retiring branches** | Declaring a release, fixing a released version, and retiring a branch. | you release, hotfix or retire |
| **09 Working with an AI assistant** | What an assistant may do alone, what it must ask, how it handles tickets, the changelog and commits, and how a project instructs it. | an assistant works on the project |
| **10 New-project bootstrap** | Applying the standard to a new repository: structure, automation, settings, token, labels, board, first version, and a trial. | you start a project |

| Appendix | What it holds |
|---|---|
| **A Cheat sheet: the daily flow** | The whole flow on one page. |
| **B Cheat sheet: if this then that** | Common situations, what to do, and where to read more. |
| **C Ticket fields reference** | Every ticket field with its values, meanings and who sets them. |
| **D Ticket examples** | Example tickets for each Type, as full forms. |

## Where to start

- **New to a project:** 01, then 03, then 04, and keep appendix A at hand.
- **Starting a task:** 04, then 05.
- **Landing work:** 06.
- **Looking after the board:** 07, with appendix C.
- **Releasing or fixing a release:** 08.
- **Working with an assistant, or instructing one:** 09.
- **Starting a project:** 10.

## Ideas that run through the guides

- **Judgment belongs to people, facts belong to the automation.** What the automation can see (where the
  code is, which build, which dates), it records. What needs a person (is the work done, is it verified,
  how urgent) a person decides.
- **Where a rule can be checked, it is backed by a warning, a deliberate way around it, and an honest
  record.** The tooling warns and records. It does not block, and a bypass creates an Alert.
- **Evidence stays traceable.** Every change belongs to a ticket and a build, tested results name the build,
  and nothing that was tested is rewritten.
- **One ticket covers one thing,** and every stamp is UTC, as is everything the automation writes.
- **The standard is the same for every project,** so any developer can open any project and know where to
  look.

## Roles

Developer, project owner and administrator are roles, not people. One person may hold several, and in a
small team often does. Naming a role means that person is responsible; the step may be done by hand, by an
assistant, or by a script they run, and it is still that person's action. A small team can collapse the
roles (see *Project structure*, section 10.6).

## What the standard assumes

- The project is hosted on GitHub, in an organization, with issues, a project board and workflows.
- Compiling and testing are done by the developer, locally. There is no continuous integration.
- The local hooks and the workflow come with the standard, and the hooks need their runtime (Python 3).
- The tool-neutral text applies on any platform. The "In GitHub" blocks name the GitHub specifics.
