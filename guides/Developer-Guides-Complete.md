# Developer Guides

*This is a combined copy of the README, the guides and the appendices, for reading in one place. The separate files are the source of truth: make changes there.*

A standard for how a small team works on a project that lives on GitHub: how to branch and merge, how
versions are numbered, how changes are recorded, how tickets and the board are used, and how releases and
hotfixes are made. It is written for developers and for the AI assistants that work with them, and it is
meant to apply unchanged to any project.

## How to read the guides

Each topic says what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
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
| **E Ticket model** | The design of a ticket as a whole: the questions it answers, why each has its own field, and its life from creation to release. |

## Where to start

- **New to a project:** 01, then 03, then 04, and keep appendix A at hand.
- **Starting a task:** 04, then 05.
- **Landing work:** 06.
- **Understanding the ticket model:** appendix E, then appendix C for the values.
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

## Where a rule lives

Each rule is set out in one place. Everywhere else only summarizes it and points there, so a rule is changed
in one place. Checklists and cheat sheets add no rules.

| The rule about | Lives in |
|---|---|
| Branch types, names, tags | *Branching and merging*, sections 1 and 2 |
| How the version number is decided | *Branching and merging*, section 3.3 |
| Syncing, landing, bypass and enforcement | *Branching and merging*, sections 4 to 6 |
| Ticket fields: the rules, Attention causes, idle times and waits | *Project structure*, section 4 |
| Version and Alert tickets | *Project structure*, section 5 |
| The scheduled run | *Project structure*, section 2.3 |
| The changelog's structure | *Project structure*, section 7 |
| The value of every field and who sets it | *Appendix C* |
| Who is responsible for what | *Project structure*, section 10 |
| Test results | *Working and committing*, section 4 |
| What an assistant may do | *Working with an AI assistant* |
| Setting up a project | *New-project bootstrap* |

The automation's own values (idle times, waits, Alert kinds, labels) are checked against these places by the
tests in `tests/test_tools.py`.

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

---

## Table of contents

- [Guide 01: Concepts and Vocabulary](#guide-01-concepts-and-vocabulary)
  - [1. Version, build, compile stamp and release](#1-version-build-compile-stamp-and-release)
  - [2. Timestamps and the UTC rule](#2-timestamps-and-the-utc-rule)
  - [3. The changelog's words](#3-the-changelogs-words)
  - [4. Tickets and the board's words](#4-tickets-and-the-boards-words)
  - [5. The words for branches and tags](#5-the-words-for-branches-and-tags)
  - [6. Roles and automation's words](#6-roles-and-automations-words)
  - [7. Git: names and concepts used](#7-git-names-and-concepts-used)
  - [8. GitHub: names used](#8-github-names-used)
- [Guide 02: Branching and Merging Strategy](#guide-02-branching-and-merging-strategy)
  - [1. Branch types](#1-branch-types)
  - [2. Naming](#2-naming)
  - [3. Where versions come from](#3-where-versions-come-from)
  - [4. Keeping `main` clean](#4-keeping-main-clean)
  - [5. How a branch lands](#5-how-a-branch-lands)
  - [6. Enforcement](#6-enforcement)
- [Guide 03: Project Structure](#guide-03-project-structure)
  - [1. The map](#1-the-map)
  - [2. The repository](#2-the-repository)
  - [3. Tickets](#3-tickets)
  - [4. Ticket fields](#4-ticket-fields)
  - [5. Special tickets](#5-special-tickets)
  - [6. Pull requests](#6-pull-requests)
  - [7. The changelog](#7-the-changelog)
  - [8. Branches and tags](#8-branches-and-tags)
  - [9. Documentation](#9-documentation)
  - [10. Who sets what](#10-who-sets-what)
- [Guide 04: Starting Work](#guide-04-starting-work)
  - [1. Before you start](#1-before-you-start)
  - [2. Get a ticket, or a REF](#2-get-a-ticket-or-a-ref)
  - [3. Create the branch](#3-create-the-branch)
  - [4. Open the changelog entry](#4-open-the-changelog-entry)
  - [5. First commit and push](#5-first-commit-and-push)
  - [6. Checklist](#6-checklist)
- [Guide 05: Working and Committing](#guide-05-working-and-committing)
  - [1. The rhythm of work](#1-the-rhythm-of-work)
  - [2. Writing changelog entries](#2-writing-changelog-entries)
  - [3. What to update as you go](#3-what-to-update-as-you-go)
  - [4. Building and testing](#4-building-and-testing)
  - [5. The commit](#5-the-commit)
  - [6. Placeholders and backfill](#6-placeholders-and-backfill)
  - [7. Keeping the ticket current](#7-keeping-the-ticket-current)
  - [8. Checklist](#8-checklist)
- [Guide 06: Syncing and Merging](#guide-06-syncing-and-merging)
  - [1. Sync `main` into your branch](#1-sync-main-into-your-branch)
  - [2. Get ready to land](#2-get-ready-to-land)
  - [3. Open the pull request](#3-open-the-pull-request)
  - [4. Merge](#4-merge)
  - [5. After the merge](#5-after-the-merge)
  - [6. If you need to bypass](#6-if-you-need-to-bypass)
  - [7. The branch after the merge](#7-the-branch-after-the-merge)
  - [8. Checklist](#8-checklist-1)
- [Guide 07: Issues and the Board in Practice](#guide-07-issues-and-the-board-in-practice)
  - [1. Triage and planning](#1-triage-and-planning)
  - [2. Working the board](#2-working-the-board)
  - [3. Review and verification](#3-review-and-verification)
  - [4. Suspending, abandoning and reopening](#4-suspending-abandoning-and-reopening)
  - [5. Alerts](#5-alerts)
  - [6. Planning ahead with versions](#6-planning-ahead-with-versions)
  - [7. Housekeeping](#7-housekeeping)
  - [8. Checklist](#8-checklist-2)
- [Guide 08: Releases, Hotfixes and Retiring Branches](#guide-08-releases-hotfixes-and-retiring-branches)
  - [1. Cut a release](#1-cut-a-release)
  - [2. Hotfix](#2-hotfix)
  - [3. Retire a branch](#3-retire-a-branch)
  - [4. Checklist](#4-checklist)
- [Guide 09: Working with an AI Assistant](#guide-09-working-with-an-ai-assistant)
  - [1. What an assistant is in this process](#1-what-an-assistant-is-in-this-process)
  - [2. What an assistant does without asking](#2-what-an-assistant-does-without-asking)
  - [3. What an assistant asks about first](#3-what-an-assistant-asks-about-first)
  - [4. Tickets and the board](#4-tickets-and-the-board)
  - [5. The changelog, commits and documentation](#5-the-changelog-commits-and-documentation)
  - [6. Instructing an assistant](#6-instructing-an-assistant)
  - [7. Checklist](#7-checklist)
- [Guide 10: New-Project Bootstrap](#guide-10-new-project-bootstrap)
  - [1. Create the repository and its structure](#1-create-the-repository-and-its-structure)
  - [2. Install the automation](#2-install-the-automation)
  - [3. Repository settings](#3-repository-settings)
  - [4. The project token](#4-the-project-token)
  - [5. Issue types and labels](#5-issue-types-and-labels)
  - [6. The board](#6-the-board)
  - [7. The first version and the roles](#7-the-first-version-and-the-roles)
  - [8. Prove the setup](#8-prove-the-setup)
  - [9. Checklist](#9-checklist)
- [Appendix A: Cheat sheet, the daily flow](#appendix-a-cheat-sheet-the-daily-flow)
- [Appendix B: Cheat sheet, if this then that](#appendix-b-cheat-sheet-if-this-then-that)
- [Appendix C: Ticket fields reference](#appendix-c-ticket-fields-reference)
- [Appendix D: Ticket examples](#appendix-d-ticket-examples)
- [Appendix E: Ticket model](#appendix-e-ticket-model)
  - [1. The idea](#1-the-idea)
  - [2. Why each space is separate](#2-why-each-space-is-separate)
  - [3. The life of a work ticket](#3-the-life-of-a-work-ticket)
  - [4. How the fields hold together](#4-how-the-fields-hold-together)
  - [5. Special tickets](#5-special-tickets-1)
  - [6. How the model drives the automation](#6-how-the-model-drives-the-automation)
  - [7. Where each part is defined](#7-where-each-part-is-defined)

---

## Guide 01: Concepts and Vocabulary

This guide defines the words the other guides use, and the git and GitHub names they rely on. Read it first,
or come back to it when a word is unclear. The rules that use these words are in the other guides.

**How to read it.** Each topic states what something is. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

---

### 1. Version, build, compile stamp and release

Four words that are easy to confuse. Each answers a different question.

| | What it is | Assigned | Lives in | Identifies |
|---|---|---|---|---|
| **Version** | `V<major>.<sub>.<mod>`, with `-HF<n>` added for a hotfix | when a branch merges into `main`; for a hotfix, when it is finished | the topmost finalized heading of the changelog | a position in the history |
| **Build** | a UTC timestamp, `yyyymmddhhmmss` | when a commit is made, by the local hook | a build heading in the changelog | one commit's worth of changes |
| **Compile stamp** | a UTC timestamp, `yyyymmddhhmmss` | every time the product is compiled | inside the compiled product | exactly what was compiled |
| **Release** | a version declared a release | deliberately, after verifying it | a tag `released/V…` | a version that is fit to be used |

- A version cannot be known while a branch is being written, because it depends on what else has landed on
  `main`. A build can, because it is stamped at the commit. A release is a decision, and many versions are
  never one.
- **Rule:** a product that is compiled carries a compile stamp, generated afresh on every compile and
  embedded in the product itself. It is a UTC timestamp and needs no lookup and no git command. It is
  unique in practice, even for repeated compiles of the same commit, though its resolution is one second.
- A recorded test result names the build, and the compile stamp where there is one, of what was tested
  (the guide on working and committing, section 4.3, sets this out).
- **Rule:** the `V` is part of a version wherever it is written as a version: the changelog heading, the
  Version field and the release tag (`V2.4.1`, `released/V2.4.1`). A Version ticket's title is the one
  exception and has no `V` (`Version 2.4.1`).
- A *release* is a version that has been declared one, and the tag marks it; a version that was not declared a
  release is simply a version. A stamp embedded at compile time is a *compile stamp*.

**Why.** The version says where in the history something is, the build says which commit, and the compile
stamp says which binary. Only the last one can tell you, when a device or a deployed copy misbehaves, exactly
what is running on it. A timestamp is practically unique without any state to check, and always UTC so that stamps from
different machines and places order correctly.

This section does not apply to a product that is never compiled.


---

### 2. Timestamps and the UTC rule

#### 2.1 The formats

There are three formats, and the year always has four digits: a **stamp**, a **date and time**, and a
**date**.

| Where | Format | Zone | Example |
|---|---|---|---|
| Build heading | `yyyymmddhhmmss` | UTC | `20261005143045` |
| Compile stamp | `yyyymmddhhmmss` | UTC | `20261005143045` |
| `REF` token, written by hand | `yyyymmddhhmmss` | UTC | `20261005180000` |
| `AUTO-REF` token, written by the automation | `yyyymmddhhmmss` | UTC | `20261005164000` |
| Finalized version heading, and the times the automation writes in tickets and comments | `yyyy-mm-dd hh:mm`, then ` UTC` | UTC | `2026-10-05 14:32 UTC` |
| Tag date, and the Start and End dates | `yyyy-mm-dd` | UTC | `2026-10-05` |
| A date or time a person writes (a record's file name, a note in a comment) | `yyyy-mm-dd` or `yyyy-mm-dd hh:mm`, and optionally a zone after a space | the writer's local time | `2026-10-05`, `2026-10-05 10:32 ET` |

#### 2.2 The rules

- **Rule:** every stamp (`yyyymmddhhmmss`) is UTC, wherever it is written.
- **Rule:** everything the automation writes is UTC. Where the format has room, " UTC" follows it, as in
  the finalized version heading. A tag date and the Start and End dates have no room for it, and are UTC
  too.
- **Rule:** a date or time that a person writes by hand is in that person's own local time. Writing the
  zone after a space is optional and may take any form. No tool reads or checks it, so it is for reference
  only.

**Why.** Stamps are what get ordered and compared: commits made in different time zones carry different
offsets, and mixing them makes it unreliable to rebuild a timeline of what happened when. UTC is the same
everywhere, so stamps made on different machines, in different places, sort and compare correctly. Local
time also shifts with daylight saving, which can make two stamps appear to run backwards. A date or time
that a person writes is only there to be read, and never used to order or decide anything, so it can be in
whatever time the writer is in. What the automation writes carries its zone, because nobody is there to
say.

> **In GitHub.** A UTC stamp from a shell is `date -u +%Y%m%d%H%M%S`. In PowerShell it is
> `Get-Date -AsUTC -Format yyyyMMddHHmmss`. The hooks and the workflow state UTC explicitly instead of
> relying on the machine's setting.


---

### 3. The changelog's words

The terms below are in the order they appear in the file, from the top of the structure down. Each ends
with where it is explained. Nothing here is new: it collects what the other guides define.

| Term | What it means | See |
|---|---|---|
| **Changelog** | The file in the repository that records every change to files, grouped by version, then build, then ticket. | project structure, section 7 |
| **Open version** | The `## WIP-Version` heading on a branch: the version being worked on. It has no number until the branch merges. | starting work, section 4 |
| **Marker** | `+V`, `+s` or `+m` written after `WIP-Version`, to force a major, sub or mod bump for that one version. | branching and merging, section 3.3 |
| **Finalized version** | A `## V2.4.1 — 2026-10-05 14:32 UTC` heading: a version that has been merged, with its UTC date and time. | syncing and merging, section 5 |
| **`WIP-Build`** | The placeholder build heading for the commit being made. The local hook replaces it at commit time. | starting work, section 5 |
| **Build heading** | `### Build 20261005143045 (branch <name>)`: one commit's worth of changes, stamped with the UTC time of the commit. If a commit was made without the hook, the automation writes a form that also carries the commit's hash. | project structure, section 7 |
| **Ticket block** | `#### #123 — title` with the bullets under it: the changes belonging to one ticket. | working and committing, section 2 |
| **Bullet** | One concrete change, starting with the file or component. | working and committing, section 2 |
| **`REF`** | A placeholder block for a change made without a ticket, named by a token and a short reason. | project structure, section 7.4 |
| **Backfill** | Replacing a `REF` with a real ticket afterwards. The ticket gets Origin *Backfilled* and the token in its REF field. | working and committing, section 6 |
| **`AUTO-REF`** | A placeholder block the automation writes when it detects a bypass or a change with no entries. It points at an Alert. | branching and merging, section 6 |
| **Safety net** | What the automation does when a change reaches `main` with no entries: it writes the missing version, build and `AUTO-REF` entries itself. | project structure, section 7.3 |
| **Correction** | A change to an earlier entry, made only when the entry is critically wrong, through a set procedure. | working and committing, section 2.5 |



---

### 4. Tickets and the board's words

"Fields reference" below means the *Ticket fields reference* appendix; the *Ticket model* appendix gives the
design of a ticket as a whole. Nothing here is new: it collects what the other guides define.

| Term | What it means | See |
|---|---|---|
| **Ticket** | A unit of tracked work, or a bookkeeping record. GitHub calls it an *issue*. | project structure, section 3 |
| **Board** | The view of all tickets and their fields. GitHub calls it a *project*. | project structure, section 4 |
| **Work ticket** | An ordinary ticket for work a person does. | project structure, section 3 |
| **Type** | What sort of ticket it is and why the change is made: Feature, Enhancement, Change, Bug, Refactor, Task, Version or Alert. | fields reference |
| **Area** | The kinds of work a ticket involves, from a fixed list of labels. | fields reference |
| **Origin** | Whether a ticket was created late: blank, *Backfilled* (after the work, to replace a `REF`) or *Backdated* (to document history from before the process). | fields reference |
| **REF** (field) | The placeholder token or tokens a backfilled ticket replaces. | working and committing, section 6 |
| **Progress** | Where the work is: *ToDo*, *OnDeck*, *InProgress*, *Review*, *Completed*, *Suspended* or *Abandoned*. On the board it is the Status field. | fields reference |
| **Review** | The work is done and awaits verification, which may be a real review or a formality. | issues and the board, section 3 |
| **Verification** | A person checking the result, after which the ticket is *Completed* with Resolution *Done*. | issues and the board, section 3 |
| **Waiting** | A flag that an open ticket is waiting for someone's input. | fields reference |
| **Attention** | A field saying whether a ticket's state has been looked at and is sound: blank, *Fine*, *Acknowledged*, *Watch*, *Caution* or *AtRisk*. The automation raises the last three, and a person closes the flag with *Fine* or *Acknowledged*. | project structure, section 4.3 |
| **Resolution** | How a ticket ended: *Done*, or a reason for abandoning it. | fields reference |
| **Delivery** | Where the ticket's delivered work is: *Committed*, *Pushed*, *Merged*, *Implemented*, *Released* or *Dropped*. | fields reference |
| **Priority, Size, Risk** | How urgent, how big in effort, and how likely to go wrong. | fields reference |
| **Version, Build, Version#** | The version and build a ticket belongs to, and a number used only to sort versions. | fields reference |
| **Start date, End date** | The dates the automation noticed the work start and end. | fields reference |
| **Version ticket** | A bookkeeping record for one version, created by the automation and closed at finalize. | project structure, section 5 |
| **Alert** | A ticket the automation raises when a person must review something, such as a bypass. | project structure, section 5 |
| **Sub-issue** | A ticket attached to another. The automation attaches a version's tickets to its Version ticket. | project structure, section 5 |
| **Triage** | Looking at a new ticket, completing it, setting its priority and deciding where it goes. | issues and the board, section 1 |



---

### 5. The words for branches and tags

"Branching and merging" below means the guide on branching and merging. Nothing here is new: it collects
what the other guides define.

| Term | What it means | See |
|---|---|---|
| **`main`** | The single integration line. Every merge into it produces a version. | branching and merging, section 1.1 |
| **Work branch** | A branch that starts from `main` and is merged back, holding one feature or a set of related changes. | branching and merging, section 1.2 |
| **Hotfix branch** | A branch that starts from a release tag and is never merged into `main`, used to fix a released version. | branching and merging, section 1.3 |
| **Parked branch** | Finished or substantial work kept off `main` on purpose, expected to be merged eventually. | branching and merging, section 1.4 |
| **Sync** | Merging `main` into a branch to bring it up to date. Never a rebase. | branching and merging, section 4 |
| **Land** | Merge a branch into `main` through a pull request. | branching and merging, section 5 |
| **Staged merge** | Merging a branch more than once, delivering and testing the work in stages. | branching and merging, section 1.2 |
| **Forward-port** | Reintroducing a hotfix's fix into `main` as an ordinary change with its own ticket. | releases and hotfixes, section 2 |
| **Retire** | Recording where a branch ended up with a tag, then deleting the branch. A finished hotfix branch is simply deleted, because its release tag already records it. | branching and merging, section 1.5 |
| **Archived** | The retirement outcome for a branch whose work is done and merged. | branching and merging, section 1.5 |
| **Suspended** | The outcome for a branch set aside to be picked up later. It can be recovered from its tag. | branching and merging, section 1.5 |
| **Abandoned** | The outcome for a branch whose work is discarded. It too can be recovered from its tag. | branching and merging, section 1.5 |
| **Recover** | Recreating a suspended or abandoned branch from its tag. The tag stays as history. | starting work, section 3.4 |
| **Tag namespaces** | `archived/`, `suspended/`, `abandoned/` and `released/`, each with a fixed format. | branching and merging, section 2.2 |
| **Release tag** | A `released/V…` tag on a version declared a release. It only indicates the version, and a mistaken one can be removed. | releases and hotfixes, section 1 |
| **Hotfix version** | A version with `-HF<n>` after it, such as `V1.25.0-HF1`, counted separately for each released version. | branching and merging, section 1.3 |



---

### 6. Roles and automation's words

Nothing here is new: it collects what the other guides define.

| Term | What it means | See |
|---|---|---|
| **Developer** | A role: a person doing the project's work. | project structure, section 10 |
| **Project owner** | A role: the person responsible for the project's direction and priorities, who triages the board. | project structure, section 10 |
| **Administrator** | A role: the person who manages the repository's settings, secrets and board configuration. | project structure, section 10.4 |
| **Role** | One person may hold several roles, and in a small team often does. A role names a responsibility, not a person. | project structure, section 10 |
| **Responsible, not necessarily manual** | Naming a role means that person is accountable. The step may be done by hand, by an assistant, or by a script they run. | project structure, section 10 |
| **Assistant** | An AI that works for a person and does steps on their behalf, under the same rules. | working with an assistant |
| **Durable authorization** | An approval for a kind of action that is recorded in the shared instructions file, so the assistant need not ask each time. | working with an assistant, section 3 |
| **Local automation** | The git hooks and scripts that run on a developer's machine. | project structure, section 10 |
| **Remote automation** | The workflow that runs on the hosting service. | project structure, section 10 |
| **Scheduled run** | The workflow's runs on a timer (three a day) and on request. It sweeps the board for what no event announces: dates, stale and waiting tickets, broken field rules, Version# and *Implemented* tickets. A small workflow switches the schedule back on if GitHub turns it off for inactivity. | project structure, section 2.3 |
| **Hook** | A small script git runs at a set moment, such as before a commit. The hooks stamp the build, draft the message and warn. | working and committing, section 5 |
| **Workflow** | The hosting service's automation. It finalizes versions, tags, updates the board and raises Alerts. | new-project bootstrap, section 2 |
| **Finalize** | The automation's step at merge: it renames the open version to the real one, updates the tickets and creates the Version ticket. | syncing and merging, section 5 |
| **Preflight** | The automation's first step: it checks it can reach the repository and the board, identifies the board, and checks the settings and fields. | new-project bootstrap, section 2.3 |
| **Advisory** | A check or warning that tells you something and never blocks you. | branching and merging, section 6 |
| **Fail open** | When a check cannot run or hits an error, work continues and the check says so. | branching and merging, section 6 |
| **Bypass** | Going around a rule on purpose. It is allowed, and it is detected and recorded afterwards as an Alert. | branching and merging, section 6 |
| **Dry run** | Running a step so that it prints every write it would make, without making any. | new-project bootstrap, section 8 |
| **Project token** | The credential, stored as a secret, that lets the automation write to the board. | new-project bootstrap, section 4 |
| **Manifest** | The file that lists the version of the standard a project follows and a hash of each automation file. | new-project bootstrap, section 2.4 |



---

### 7. Git: names and concepts used

#### 7.1 Concepts

| Term | What it means | Why it matters here |
|---|---|---|
| **Repository** | The project's files with their complete history. | Everything the process records lives in it. |
| **Clone** | Your own copy of a repository. | Hooks have to be activated once per clone. |
| **Remote**, `origin` | The shared copy on the hosting service, usually named `origin`. | Pushing sends your work there. |
| **Working tree** | The files as they are on your machine right now. | Where you make changes. |
| **Staging area** | The set of changes chosen for the next commit. | The hook stamps the staged changelog. |
| **Commit** | A saved set of changes with a message, identified by a hash. | The unit that the build stamp and test results refer to. |
| **Hash** | The unique identifier of a commit. | A rebase or an amend gives a commit a new one. |
| **Branch** | A named line of commits. | Work happens on branches. |
| **`HEAD`** | The commit you are currently on. | Used in commands such as `git log HEAD..origin/main`. |
| **Tag** | A fixed name for one commit. A *lightweight* tag is just the name; an *annotated* tag also carries a message. | Releases and retired branches are tags. |
| **Merge** | Combining the work of two branches. | How branches land, and how `main` is synced into them. |
| **Merge commit** | The commit a merge creates, with two parents. | The only merge method the process uses. |
| **Fast-forward** | A merge where nothing new has to be combined: the branch pointer simply moves ahead. | No sync is needed when `main` has not moved. |
| **Conflict** | Two changes to the same lines that git cannot combine by itself. | Resolved on the branch, as an ordinary commit. |
| **Rebase** | Replaying a branch's commits on top of another as new commits. | Forbidden: the tested commits would no longer exist. |
| **Squash** | Combining several commits into one. | Forbidden for the same reason. |
| **Amend** | Replacing the last commit with a changed one. | Allowed before pushing, but discouraged. |
| **Reachable** | A commit is reachable from a branch if you can get to it by following parents. | "All its commits are reachable from `main`" means the branch is merged. |
| **Hook** | A script git runs at a set moment. | The local automation. |
| **Ignore file** | A list of files git leaves out. | Keeps personal and generated files out of the repository. |

#### 7.2 Commands and flags the guides use

| Command | What it does |
|---|---|
| `git fetch` | Brings in what is new on the remote without changing your files. |
| `git pull` | Fetches and merges the remote's changes into your current branch. |
| `git switch <branch>` | Moves to a branch. `-c <name> [<start>]` creates it from a starting point such as `main` or a tag. |
| `git branch -a`, `git branch -d` | Lists all branches, or deletes a local one. |
| `git merge origin/main` | Merges the remote `main` into your current branch (a sync). |
| `git log HEAD..origin/main` | Lists what `main` has that your branch lacks. Empty means up to date. |
| `git add`, `git commit` | Stages changes and saves them as a commit. `-m` gives the message directly and skips the drafted one. |
| `git commit --amend` | Amends the last commit. |
| `git push`, `git push -u origin <branch>` | Sends commits to the remote. `-u` also links the branch to it. |
| `git push --force-with-lease` | Overwrites the remote branch, but only if nobody else has pushed to it. |
| `git push origin --delete <name>` | Deletes a branch or tag on the remote. |
| `git tag`, `git tag -a`, `git tag -l`, `git tag -d` | Creates a tag, creates an annotated one, lists tags, deletes one locally. |
| `--no-verify` | Skips the hooks for a commit or push. |
| `git config core.hooksPath` | Tells git where the hooks are. |
| `git config user.name`, `user.email` | Sets who commits are attributed to. |
| `git fetch --prune --prune-tags` | Drops local copies of branches and tags that were removed on the remote. |



---

### 8. GitHub: names used

These are the names the guides use for GitHub's own features. Nothing here is new: it collects what the
other guides define.

| Term | What it means | See |
|---|---|---|
| **Organization** | The account that owns the repository and the board. The standard needs one, because issue types are an organization feature. | new-project bootstrap, section 5 |
| **Issue** | A ticket. | project structure, section 3 |
| **Issue type** | The native single value on an issue that says what sort of ticket it is. It carries the Type. | fields reference |
| **Label** | A tag on an issue. The only labels are the 14 Area labels and the marker label `dummy`. | fields reference |
| **Sub-issue** | An issue attached to another, which has one parent. | project structure, section 5 |
| **Closing keyword** | A word such as *Closes*, *Fixes* or *Resolves* followed by a ticket number, which closes the ticket automatically when the pull request merges. The process never uses one. | syncing and merging, section 3 |
| **Pull request** | The proposal to merge a branch into `main`. | project structure, section 6 |
| **Check** | A status shown on a pull request. The advisory check says whether the branch is behind `main`. | syncing and merging, section 4 |
| **"Update branch" button** | A button on a pull request that merges `main` into the branch on the server. | syncing and merging, section 1 |
| **Project (board)** | The board of all tickets, with its fields and saved views, linked to the repository. | project structure, section 4 |
| **Field** | A column of the board: single select, text, number or date. | new-project bootstrap, section 6 |
| **View** | A saved way of looking at the board, with a filter, grouping and sorting, such as Board or Health. | issues and the board, section 2 |
| **Actions, workflow** | The hosting service's automation, run on a push, on a pull request or on request. | new-project bootstrap, section 2 |
| **Secret** | A stored value a workflow can use but nobody can read back, such as the project token. | new-project bootstrap, section 4 |
| **Repository variable** | A stored non-secret value a workflow can read, such as the board's number. | new-project bootstrap, section 2.3 |
| **Personal access token** | A credential that stands for a person's account, used here as the project token. | new-project bootstrap, section 4 |
| **Branch protection** | Repository rules on `main`, such as requiring a pull request. The administrator bypass is left open. | new-project bootstrap, section 3 |
| **Wiki** | The repository's own wiki, fed from the `doc/wiki/` folder where it is available. | project structure, section 9 |
| **Tags and releases page** | Where the repository lists its tags, including the `released/` ones. | branching and merging, section 2.2 |

---

## Guide 02: Branching and Merging Strategy

This guide explains how branches are used, named and retired, and why. It is the reference the
procedural guides (starting work, syncing, merging, releases) point back to.

**How to read it.** Each topic states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides. Departing from it is
  legitimate when there is a reason.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

---

### 1. Branch types

#### 1.1 `main`

- **Rule:** `main` is the single integration line. There is no long-lived `develop` or staging
  branch.
- **Rule:** every merge into `main` produces a new version. When a merge lands without changelog
  entries, the automation records that itself and still assigns a version (see section 6).
- **Rule:** a release is a tag placed on `main`, never a branch.

**Why.** One line of history keeps the order of changes unambiguous. Because versions are assigned at
merge time (see *Concepts*), that order is also the order of the versions. Keeping releases as tags
means a release can be chosen after the fact from versions that already exist, without a second
long-lived line to keep in step.

#### 1.2 Work branch

- **Rule:** a work branch starts from `main` and is merged back into `main`.
- **Recommendation:** keep a branch *functional*: one feature, or a set of related changes or
  enhancements that belong together. The number of tickets on it does not matter, and neither does
  whether it is one or many. How to group work is the developer's judgment.
- **Recommendation:** be willing to merge a branch more than once. Typical reasons are delivering
  and testing in stages, planned follow-up enhancements to the same feature, and an expected
  follow-up fix. Each merge gets its own version.

**Why.** A branch lands as one merge and receives one version, so what it holds should read as one
coherent change in the history. A branch that mixes unrelated work produces a version that cannot be
described in a sentence. Allowing repeated merges lets work reach `main` early and be exercised
there, which is safer than one large merge at the end.

> **In GitHub.** A branch that continues after a merge needs a new in-progress version entry at the
> top of `CHANGELOG.md` (a `## WIP-Version` heading and a `### WIP-Build` block) before its next
> logged change, because finalizing a version does not leave an empty one behind. See *Starting work*.

#### 1.3 Hotfix branch

- **Rule:** a hotfix branch starts from a release tag, not from `main`. A further hotfix for the same
  release starts from the tag of the latest hotfix of that release, so that it includes the earlier fixes.
- **Rule:** a hotfix branch is never merged into `main`.
- **Rule:** a hotfix has its own version in a separate lineage:
  `V<major>.<sub>.<mod>-HF<n>` (for example `V1.25.0-HF1`).
- **Rule:** the same fix reaches `main` separately, through the normal work-branch flow, and gets
  whatever version `main` is at when that happens.
- **Rule:** a finished hotfix branch is deleted without a retirement tag, because its release tag already
  keeps its history. A hotfix that was never finished is suspended or abandoned like any other branch.

**Why.** A hotfix patches exactly what was released, which may be far behind `main`. Branching from
the tag keeps unrelated changes out. A separate numbering lineage means the hotfix can never collide
with a version `main` has already produced or will produce.

Details of cutting and finishing a hotfix are in *Releases, hotfixes and retiring branches*.

#### 1.4 Parked branch

A parked branch holds finished or substantial work that is deliberately kept off `main` and is
expected to be merged eventually. It still exists as a branch. It is not the same as an abandoned
branch, where the work has been discarded.

- **Recommendation:** sync a parked branch from `main` periodically.
- **Recommendation:** if a branch has been parked for about a month, decide whether to suspend it
  (section 1.5) or abandon it, instead of leaving it open indefinitely.

**Why.** The longer a branch lags behind `main`, the larger and riskier the eventual conflicts, and
the more likely they are resolved under time pressure and without testing. Periodic syncing keeps the
cost of the final merge small. A branch nobody touches for a long time also hides an unmade
decision: suspending or abandoning it turns that into a visible, recorded choice.

#### 1.5 Retiring a branch: archived, suspended, abandoned

*Retiring* means recording where a branch ended up with a tag and then deleting the branch. There
are three outcomes, each with its own tag namespace (section 2.2):

| Outcome | Meaning | Work merged? |
|---|---|---|
| **archived** | The work is done and merged. | Yes |
| **suspended** | The work is not going to be addressed soon, but is expected to be picked up eventually. | Not fully |
| **abandoned** | The work is discarded and not expected to return. | No |

- **Rule:** tag first, delete second. The tag is what keeps the branch's history reachable.
- **Recommendation:** do not wait too long to retire a branch once its work is merged. What counts
  as too long depends on the team's pace; for a small team that does not work on the project full
  time, anything from a week or two up to about a month is reasonable. Keeping it longer is a
  legitimate choice when the developer expects to continue the same feature, expects a follow-up
  fix, or is merging the work in stages.
- **Rule:** recovering a suspended or abandoned branch means recreating it from its tag. The tag
  stays as history, so a branch suspended twice simply has two dated tags.
- **Recommendation:** after recovering a branch, sync it from `main` before doing anything else,
  because it has been standing still while `main` moved.

**Why.** Deleting a branch without a record loses where the work ended up and why. Three outcomes,
not one, because each answers a different later question: "was this ever merged", "can we pick this
back up", and "did we consciously drop this". A tag costs nothing to keep and makes every one of
those answers a lookup.

> **In GitHub.** A merged branch whose commits are reachable from `main` is archived. List what has
> been set aside with `git tag -l 'suspended/*'`, and recover with
> `git switch -c <branch-name> <tag-name>`. Deleting the remote branch afterwards is
> `git push origin --delete <branch-name>`.
>
> On the board, suspending a branch normally goes with moving its tickets to `Suspended`, and
> abandoning a branch sets the Delivery of its tickets to `Dropped`.

---

### 2. Naming

#### 2.1 Branch names

- **Rule:** a branch is named `main` or uses `kebab-case`: lowercase words separated by hyphens.
- **Rule:** a branch name never contains `/`.
- **Rule:** a hotfix branch is named `hotfix-v<major>-<sub>-<mod>-<description>`, with the version's
  dots written as hyphens (for example `hotfix-v1-25-0-fix-sensor-timeout`).

**Why.** Branch names are embedded in tag names (section 2.2), where `/` already separates the
namespace from the rest. A `/` in a branch name would make the tag ambiguous and nest tag paths
unpredictably. One style also makes names predictable, searchable and easy to type, and the dots in a
version would break pure kebab-case, hence the hyphens.

#### 2.2 Tag names

| Namespace | Format | Applied when |
|---|---|---|
| `archived/` | `archived/<yyyy-mm-dd>_<branch>[_<comment>]` | a merged branch is retired |
| `suspended/` | `suspended/<yyyy-mm-dd>_<branch>[_<comment>]` | a branch is set aside to resume later |
| `abandoned/` | `abandoned/<yyyy-mm-dd>_<branch>[_<comment>]` | a branch is discarded |
| `released/` | `released/V<major>.<sub>.<mod>` | a version on `main` is deliberately declared a release |
| `released/` | `released/V<major>.<sub>.<mod>-HF<n>` | a hotfix is finished |

Where:

- `<yyyy-mm-dd>` is the UTC date of the **last commit on the branch** at the moment it is tagged.
- `<branch>` is the branch's name in kebab-case.
- `<comment>` is optional and kebab-case. Keep it very short. For a longer note, make the tag an
  annotated tag and put the note in its message.
- Versions are written without padding: `V2.0.0`, not `V02.00.00`.
- The hotfix number `<n>` is a single digit, starting at 1, counted separately for each released
  version being fixed: `V1.25.0-HF1`, `V1.25.0-HF2`, and independently `V1.26.0-HF1`. If a release would
  need a tenth hotfix, the fix is finished on `main` and that version is released instead. This is
  deliberate: a release that needs that many fixes should be replaced by a newer one, not patched
  further.

Examples:

```
archived/2026-03-14_user-login-rework
suspended/2026-03-14_offline-sync_waiting-on-api
abandoned/2026-03-14_dark-theme_dropped-for-redesign
released/V2.4.0
released/V2.4.0-HF1
```

**Why.**

- *Separate namespaces* let a single prefix query answer a question ("everything abandoned") and
  keep the three retirement outcomes from blending into one list.
- *The date comes first* so each namespace lists in chronological order with no extra sorting, and
  the *last commit's* date (not the day the tag happened to be made) says when the work really
  stopped.
- *The comment is optional and short* so a tag stays readable in a list; anything longer belongs in
  an annotated tag's message, where it can be as long as it needs to be.
- *Two tags for the same branch on the same day* would collide. When that happens (for example, a
  branch suspended, recovered and suspended again within a day) the short comment tells them apart, and the retire step refuses a name that already exists.
- *`released/` is separate from the version itself* because not every version is a release. A
  version is created by every merge; a release is a deliberate decision about which versions
  actually shipped.
- *The hotfix number is one digit* because no release is expected to need more than nine hotfixes,
  and a fixed width keeps version numbers easy to encode and sort.

> **In GitHub.** Tags appear under *Releases / Tags* and can be filtered by typing the prefix. From
> the command line, `git tag -l 'archived/*'` lists a namespace. Create an annotated tag with
> `git tag -a <tag-name> -m "<long note>"`. Push tags explicitly: `git push origin <tag-name>`.

---

### 3. Where versions come from

#### 3.1 When a version is assigned

- **Rule:** a version is assigned only when work lands on `main`. A branch has no version of its own;
  it carries a placeholder (`WIP-Version`) until it merges.
- **Rule:** versions are written `V<major>.<sub>.<mod>`, without padding (`V2.0.0`).
- **Rule:** the topmost finalized version heading in the changelog is the single source of truth.
  There is no separate version file to keep in step.

**Why.** The next version depends on what else has already landed on `main`, which cannot be known
while a branch is still being written. Assigning it at merge also means the code being compiled on a
branch never needs to know its own version in advance. Keeping the changelog as the only source avoids
two records of the same fact drifting apart. (The distinction between a version, a build and a release
is defined in *Concepts*.)

#### 3.2 What each part means

| Part | Meaning |
|---|---|
| **major** | A large redesign or a major new capability. |
| **sub** | A new feature, smaller than a major. |
| **mod** | A bug fix or a small change. |

#### 3.3 How the bump is decided

- **Rule (default, automatic):** the bump comes from the Type of the tickets in the version being
  finalized (the ticket Types are defined in the project structure guide). When tickets differ, the
  highest-impact Type wins, so a feature outweighs a fix. A version with no typed tickets (for example
  only changes made without a ticket) is a **mod**.

  | Ticket Type | Bump |
  |---|---|
  | Feature, Enhancement | sub |
  | Change, Bug, Refactor, Task | mod |
  | Version, Alert | none (ignored) |

- **Rule (override):** the developer can force the result with a marker written after
  `WIP-Version` in the heading:

  | Heading | Result |
  |---|---|
  | `## WIP-Version +V` | major bump |
  | `## WIP-Version +s` | sub bump |
  | `## WIP-Version +m` | mod bump |

- **Rule:** a major bump is never automatic. Only `+V` produces one.
- **Rule:** a marker applies to that one version only. The next `WIP-Version` heading is plain
  again unless it carries a marker of its own.
- **Rule:** any other text after `WIP-Version` is an error, never guessed at. A changelog with such an
  error, or with two open headings, that reaches `main` stops the run without a version and raises a
  *Critical* Alert saying what is wrong. The developer corrects the changelog by hand, and the version is
  then finalized by running the finalize step again.
- **Rule:** markers are not allowed on a hotfix branch. A hotfix version is stated explicitly when
  the hotfix is finished (`V1.25.0-HF1`), so there is nothing to compute or force.
- **Rule:** a revert gets no special handling. It is a change like any other: the developer chooses the
  Type of its ticket, and may force the bump with a marker if the Type gives the wrong size.
- **Rule:** a marker overrides the automatic result in either direction, including a smaller bump than the
  tickets would give. Use it deliberately.
- **Rule:** when the changelog has no finalized version yet, the first version is `V0.1.0`, whatever the
  Types of the tickets.

**Why.**

- *Tickets, not the pull request,* carry the bump because the tickets are where the nature of each
  change is already recorded, as a Type. A branch may hold a feature and a fix together (see
  section 1.2), which a single label on the pull request cannot express.
- *The highest Type wins* so that a feature never ends up hidden inside what looks like a fix.
- *The default is mod* because the safest assumption about a change with no Type is that it is small.
- *Major is only ever human-declared* because "this is a redesign" is a judgment about meaning, not
  something a ticket's Type can express.
- *An override exists* because automatic rules are right most of the time, and the developer should be
  able to correct them in the place where the version is being decided, in plain sight in the
  changelog, instead of editing tickets after the fact.
- *Reverts need no special case* because the history is easier to read when every change, including
  an undo, follows the same rules.

A version is not a release. Every merge creates a version; declaring one of them a release is a
separate, deliberate step (section 2.2).

> **In GitHub.** The Type is the issue's native Issue Type. A `## WIP-Version` heading with a marker
> sits at the top of `CHANGELOG.md`. The finalizing job reads the ticket numbers listed in that
> section, looks up each issue's Type, applies any marker, and renames the heading to the resulting
> version on merge.

---

### 4. Keeping `main` clean

#### 4.1 The principle

A merge into `main` should look exactly like the branch, plus the version bookkeeping on top. The
result of the merge is identical to the branch's final state.

**Why.** If `main` has moved while a branch was away, merging the branch back becomes a real
three-way merge. Any conflict is then resolved for the first time on the shared line, at the moment
of landing, and untested. Everything below exists to move that work onto the branch, where it can be
done deliberately and checked before it reaches `main`.

#### 4.2 Sync before merging

- **Rule:** a branch is brought up to date with `main` before it is merged, whether or not git
  reports a conflict.

**Why.** A conflict-free merge is only a textual statement. It says nothing about whether the
combined code behaves correctly. Changes that look unrelated can still interact through shared
resources: memory, peripherals, timing, voltage levels on a line, power draw, and similar. Nothing in
the text of the changes will show that. This matters more for software that runs unattended, as
firmware does: nobody is there to notice a fault or restart the device, so it has to work correctly
the first time, and anything that removes risk before a change lands on `main` is worth its cost.

#### 4.3 Sync by merging, never by rebasing

- **Rule:** sync a branch by merging `main` into it. Never rebase the branch onto `main`.

**Why.** Every test result and every build entry refers to specific commits. A rebase replays those
commits as new ones, with different identities and sometimes different content, so the exact code
that was tested no longer exists anywhere in the history. Nobody can then be confident that what
reached `main` is what was tested, and that is the question that matters when a problem appears
later. A build stamp and the commit it points to are the evidence for recreating what was tested;
merging keeps them intact. A rebase also resolves conflicts one replayed commit at a time, so there
is never a single point where the combined result is built and tested.

This rule rests on discipline and on the reasoning above: a rebase cannot be reliably detected
afterwards.

#### 4.4 Resolve conflicts on the branch

- **Rule:** a conflict found while syncing is resolved as an ordinary commit on the branch. It is
  built, tested and logged there, before the branch reaches `main`. By the final merge there is
  nothing left to resolve.
- **Rule:** if `main` moves again between the sync and the merge, sync again. A conflict can then
  only ever appear at a sync, never at the final merge.
- **Rule:** if the sync involved a manual conflict resolution, or any adjustment you had to make that
  git did not flag as a conflict, document it: log it in the changelog under the ticket you are working
  on and put the details in a comment on that ticket (a `REF` if there is none). A significant one may
  deserve a ticket of its own.

**Why.** A resolution is a decision about which of two behaviours survives, and it is easy to get
wrong. Making it on the branch, as its own commit, means it is visible, testable and reversible.
Documenting it matters for the same reason as the build stamps: when a problem appears later, the
conflict resolution is one of the first places to look, and it should not have to be reconstructed
from the diff.

**Tree-clean is not the same as correct.** A merge can be identical to its branch and still contain a
bad resolution that was made earlier on the branch. Keeping the resolution as a separate, built and
tested commit is what protects against that.

#### 4.5 After a sync: recompile, and retest in proportion

- **Rule:** after a sync that brought changes in from `main`, recompile before going further.
- **Strong recommendation:** retest in proportion to what came in. The developer judges how
  different the incoming changes are from what the branch started with: a changed log message is not
  a change to a module the branch also touches. When in doubt, even a small doubt, retest.

**Why.** A clean merge is not proof that the code still builds, and the sync is what creates the
combined code: only building and running it on the branch verifies what will land on `main`.
Compilation is done locally by the developer and nothing else compiles the code, so skipping it
leaves no other check.

#### 4.6 Enforcement

These rules are checked and warned about, not enforced. Merging despite a warning is allowed, and it is
detected afterwards as a bypass. See section 6 for why, and for what happens when one is bypassed.

> **In GitHub.** An advisory check on the pull request fails and comments once when the branch is
> behind `main`; the merge button still works, and the failed check is the warning. The same comment
> lists any merge in the branch that carries a manual conflict resolution, as a reminder to confirm it
> was built and tested. The local commit and push hooks give the same warnings, and also remind you to
> recompile whenever a merge brings in commits from `main`, and to build and test after a manually
> resolved conflict. A project can make the check mandatory with
> branch protection ("require branches to be up to date before merging") where the hosting plan
> allows it. Squash and rebase merging are disabled in the repository settings, so merge commits are
> the only merge method.
>
> To sync, merge `main` into the branch (`git merge main`, or the "Update branch" button set to
> merge). No CI runs in this setup, so the developer's own local build is the only compile.

---

### 5. How a branch lands

#### 5.1 Through a pull request

- **Rule:** a branch lands on `main` through a pull request (a reviewable merge request), not by
  pushing directly to `main`.
- **Rule:** the pull request title states the branch's functional purpose, the way a version heading
  would. The description contains the changelog entries of the open version, copied as they are (at a
  minimum the ticket numbers the branch covers).
- **Rule:** reference tickets in a pull request by plain number (`#123`). Never use a closing keyword
  (such as "Closes" or "Fixes"), because it would close the ticket automatically when the branch
  merges.
- **Rule:** a branch that is merged more than once (section 1.2) goes through its own pull request
  each time.

**Why.** The pull request is the one place that carries a branch's checks and warnings, and it is the
lasting record of what landed and why. A direct push skips both. It is not forbidden, but it is a
bypass: it is detected and logged afterwards (see section 6).

Closing a work ticket automatically on merge would contradict how work is verified. Merging puts work
on `main`; it does not show that the work is right. The move from *review* to *completed* is a manual
step by a person who has checked the result, and nothing about a merge should do it for them (see the
guide on issues and the board in practice for the full status path). Bookkeeping tickets for a version have nothing to
verify; the automation closes those itself when the version is finalized.

Labels on the pull request play no part in versioning. The bump comes from the Types of the tickets (section 3.3).

#### 5.2 Merge commits only

- **Rule:** a branch is merged with a merge commit. Squash merging and rebase merging are not used.

**Why.** This is the same reasoning as for never rebasing (section 4.3). Every commit on the branch
carries its build stamp and the tests that were run against it. A squash replaces all of them with one
new commit that was never built or tested as such. A rebase merge rewrites them with new identities.
A merge commit keeps every tested commit exactly as it was, so what reached `main` is what was tested.

#### 5.3 What the merge looks like

Because of the sync rules (section 4), the result of the merge is identical to the branch's final
state. The only thing added on top is the version bookkeeping that follows the merge: the in-progress
version heading is renamed to the version that was assigned (section 3).

After the merge, retiring the branch is the developer's choice (section 1.5).

> **In GitHub.** Squash and rebase merging are disabled in the repository settings, so the merge
> button offers only a merge commit. The title and description are set when the pull request is
> opened; to link a ticket without closing it, write `#123` on its own, never `Closes #123`,
> `Fixes #123` or `Resolves #123`. The advisory check described in section 4.6 runs on every pull
> request into `main`.

---

### 6. Enforcement

#### 6.1 The principle

- **Rule:** where a rule can be checked, it is backed by a warning, a deliberate way around it, and an
  honest record when it is used. The tooling warns and records. It does not block. Some rules rest on
  discipline alone (section 6.4).
- **Rule:** where a platform can enforce a rule by blocking (for example, requiring a branch to be up to
  date before it can merge), leave an administrator bypass open anyway.

**Why.**

- *A wall gets forced through anyway.* Under real pressure a hard block is bypassed by whatever means
  exist, and then leaves no trace of what happened or why. Admitting that a rule will sometimes be
  bypassed, and having a way to recover afterwards, is more reliable than assuming it never will be.
- *A small team cannot absorb the friction.* Being blocked from working efficiently, even when the
  block is technically correct, builds frustration the team has no slack to spend.
- *A visible record is worth more than a prevented mistake nobody learns from.* Every bypass that is
  recorded can be reviewed, explained and, if needed, repaired.

#### 6.2 Three layers

1. **Warn.** Checks and local reminders say when a rule is about to be broken. They never block, and a
   missing tool or an error in a check lets the work continue.
2. **Bypass.** The developer may go around a warning on purpose: merge anyway, push straight to `main`,
   or skip the local checks.
3. **Record.** The more serious bypasses are detected automatically afterwards and logged, so that a
   person reviews them.

#### 6.3 What is detected and recorded

On every change that lands on `main`, the automation looks for these shapes:

- **A direct push**, with no pull request.
- **A merge that is not identical to its branch's final state**: the branch was not synced first, or a
  conflict was resolved during the merge itself.
- **A merge that differs from both of its parents**: a conflict resolution nobody verified.
- **File changes with no changelog entries**: no in-progress version heading, or an empty one, for
  example a reused branch whose heading was forgotten, a forgotten changelog, or a direct push.

The response is the same for all of them, and it never blocks the person who needed the bypass:

- **An Alert ticket** is created automatically: Priority `Critical`, Progress `ToDo`, Area `process`.
- **An `AUTO-REF` entry** is added to the changelog, pointing at that ticket. It is easy to tell from a
  developer's own `REF` entry (a change made without a ticket) because the system wrote it.
- **If the change carried no changelog entries at all**, the automation also writes the missing version
  and build entries itself and finalizes the version with a mod bump, so the merge still produces a
  version. The `AUTO-REF` entry stands in for the description nobody wrote.
- **One push is one version,** one Alert and one `AUTO-REF` entry, which lists every commit that was
  flagged.

What the developer does afterwards:

- **Recommendation:** triage the Alert promptly. Confirm that the result was built and tested, document
  what changed, either by replacing the generated note in the changelog or, preferably, by describing
  it in a new block in the current version.
- Every move of the Alert after creation is manual: a person starts it (`InProgress`), says they believe
  it is handled (`Review`), and a human verifies it (`Completed`). Shipping a version never moves it.

**Why.** A bypass is not a failure to be hidden; it is a decision that needs follow-up. Creating the
ticket at the moment of the event means the follow-up exists even if the person who bypassed is too busy
to remember it, which is exactly when bypasses happen.

#### 6.4 What cannot be checked

Some rules rest on discipline and on the reasoning given with them, because nothing can reliably detect
a breach:

- Rebasing instead of merging (section 4.3).
- Recompiling and retesting after a sync (section 4.5).

Skipped local checks are only partly detectable. If a commit made on a developer's machine changed the
changelog but still has its build placeholder when it is pushed, the local checks were skipped, and the
automation adds a note to that changelog entry. A skipped check on a commit that did not touch the
changelog leaves nothing behind to detect.

**Why say so.** A guide that implied every rule was checked would make the unchecked ones look optional.
Naming them tells the developer where the safeguard is their own care.

#### 6.5 When you need to bypass

- **Recommendation:** a bypass is legitimate when there is a reason. Do it deliberately, say why in the
  commit or ticket, and expect the Alert. Treat the Alert as the other half of the decision, not as a
  penalty.
- **Recommendation:** never hide a bypass, for example by editing history. The record is what makes it
  recoverable.

> **In GitHub.** The warnings are the advisory check on the pull request and the local git hooks, which
> fail open and are skipped with `--no-verify`. The detection runs from the automation on every push to
> `main` and opens an issue of type Alert with Priority `Critical` and the `process` label. A generated
> changelog entry looks like this:
>
> ```
> #### AUTO-REF 20261005164000 (tracked as #187)
> - **Auto-flagged: this merge's result is not identical to the source branch's tip.** The sync-first
>   rule was not followed, or a conflict was resolved during the merge itself rather than beforehand on
>   the branch. Issue #187 opened automatically for review: document the change once triaged.
> ```
>
> The administrator bypass of branch protection, where the hosting plan offers it, is deliberately left
> available (do not tick "do not allow bypassing the above settings").

---

## Guide 03: Project Structure

This guide explains the pieces a project is made of, what each one means, how they connect and how they
are created. It is the reference the procedural guides (starting work, committing, merging, issues and
the board) point back to. The values of every ticket field are in the *Ticket fields reference*
appendix, and the design of a ticket as a whole, with its life from creation to release, is in the
*Ticket model* appendix.

**How to read it.** Each topic states what something is and why it exists. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Vocabulary.** This guide says *ticket* for a unit of tracked work. GitHub calls it an *issue*; the
two words mean the same thing here.

---

### 1. The map

#### 1.1 The pieces

| Piece | What it is |
|---|---|
| **Repository** | The code and documentation, with their full history. |
| **Branch** | A line of work. `main` is the one integration line. |
| **Tag** | A named point in history: a release, or a retired branch. |
| **Changelog** | A file in the repository that records every change, grouped by version and build. |
| **Ticket** | A unit of tracked work, or a bookkeeping record such as a version. Its details are held in fields on the board. |
| **Pull request** | The proposal to merge a branch into `main`. |
| **Board** | The view of all tickets and their fields. |
| **Documentation** | The folder of project documents, the wiki and the readme. |
| **Automation** | The local hooks on each developer's machine and the server-side job that stamps builds, assigns versions, detects bypasses and updates the board. |

#### 1.2 How they connect

```
ticket ──▶ branch ──▶ commits ──▶ pull request ──▶ main ──▶ version ──▶ release tag
  ▲           │           │                                     │
  │           └───────────┴──▶ changelog entries ◀──────────────┘
  └───────────── board fields, set by people and automation
```

Reading the diagram from the left: work starts from a ticket (or, when there is none yet, from a
placeholder reference). It happens on a branch, in commits. Each commit records what it changed in the
changelog. The branch lands on `main` through a pull request, which gives the changes a version, and a
version may later be declared a release with a tag. Along the way, the board shows where each ticket
stands, set partly by people and partly by the automation.

The links that matter:

- A changelog entry names its ticket (`#123`), or a `REF` placeholder if there is no ticket yet.
- A pull request lists the tickets it covers.
- A ticket's *Version* field names the version it shipped in.
- A *Version ticket* groups the tickets of one version.
- A tag names a branch (when it is retired) or a version (when it is released).
- The automation reads the changelog and the tickets, and writes the changelog and the board.

**Why this matters.** Each piece answers a different question: the branch says *where the work is*, the
changelog says *what changed*, the ticket says *why and how it stands*, the pull request says *what is
landing*, and the tag says *what the history means*. The links are what let you start from any one of
them and reach the rest. For example, from a problem found on a device you can follow the version to its
changelog entries, from the entries to their tickets, and from the tickets to the pull request and the
branch they came through.

> **In GitHub.** The repository is a GitHub repository. Branches and tags are git branches and tags. The
> changelog is a `CHANGELOG.md` file at the repository root. A ticket is a GitHub *issue*, and its fields
> are on a *project board* (a GitHub Project). A pull request is a GitHub pull request. Documentation is
> a `doc/` folder in the repository, the repository's wiki and the readme. The automation is a set of
> git hooks kept in the repository and enabled once per clone, plus a GitHub Actions workflow that runs
> on pushes to branches and to `main`, on pull requests, and on request.

---

### 2. The repository

#### 2.1 What lives where

| Location | Holds |
|---|---|
| **readme** (root) | What the project is, how to build and use it. |
| **`CHANGELOG.md`** (root) | The changelog (structure in section 7). |
| **Source folders** | The project's own code. Project-specific, so this guide says nothing about them. |
| **`tests/`** | Automated tests, for the product and for the automation scripts, and any recorded test results in `tests/results/`. Present when the project has code or scripts of its own. |
| **`doc/`** | Project documentation other than the readme and the changelog. |
| **`doc/wiki/`** | The wiki pages, one markdown file per page. |
| **`.githooks/`** | The local git hooks. |
| **`.github/`** | Server-side workflows and their scripts, and the pull request template. |
| **`AGENTS.md`** (root) | The shared instructions for AI assistants (see the guide on working with an assistant). |
| **Ignore file** (`.gitignore`) | What stays out of the repository. |
| **`.gitattributes`** (root) | Line-ending settings: the line `* text=auto eol=lf`. |
| **Licence files** (root) | The project's licence, when it has one. |

#### 2.2 Rules

- **Rule:** these locations exist in every project, under these names, and hold only what the table
  lists. The exception is `tests/`, which is needed only when the project has code or scripts of its
  own.
- **Rule:** the hooks and the automation are part of the repository. They are versioned and changed
  through the same flow as code, and their logic has tests.
- **Rule:** the hooks are activated once per clone, with one command. A fresh clone has no hooks until
  that step is done. (The procedure is in the guide on starting work; this guide only states that the
  step exists.)
- **Rule:** `.gitattributes` contains the line `* text=auto eol=lf`, so the changelog, the hooks and the
  scripts keep Unix line endings on every platform.
- **Recommendation:** keep personal and generated files out of the repository through the ignore file,
  so nobody commits the state of their own machine.

**Why.**

- *Line endings* because the hooks and the automation read the changelog byte for byte. A changelog saved
  with Windows line endings once broke both, and rewrote the whole file on the next commit.
- *Fixed names* mean any developer can open any project and know where to look, and tooling and guides
  can refer to a location without asking.
- *The hooks and automation live in the repository* because the project's rules are only as reliable as
  the tooling that supports them. Versioned and tested, they change deliberately and travel with the
  code, instead of living on one person's machine.
- *Activation is a separate, explicit step* because a hook can only run on a machine that has been told
  to use it. Saying so plainly stops a fresh clone from being mistaken for a protected one.

> **In GitHub.** Hooks are activated with `git config core.hooksPath .githooks`, stored in the clone's
> own configuration, so each fresh clone needs it once. Server-side workflows are in
> `.github/workflows/` and their scripts in `.github/scripts/`; the pull request template is a file in
> `.github/`. The wiki pages in `doc/wiki/` are copied to the repository's own wiki by a workflow where
> a wiki is available (a wiki must first be initialized by creating a first page, and it may not be
> offered for private repositories on every plan). Where it is not, `doc/wiki/` simply remains the
> readable source in the repository.

#### 2.3 The scheduled run

Most of the automation reacts to an event: a push, a pull request, a merge. Some things are not events.
Nothing is sent when a person changes a field on the board, and nothing happens when a ticket simply goes
quiet. The *scheduled run* covers them: the workflow also starts on a timer, three times a day, and on
request. Each run sweeps the board and does the following, and the other guides refer to it by this name:

- sets the Start and End dates of tickets that have started or ended;
- raises *Watch* on tickets that have gone quiet or have waited too long, and *Caution* on tickets that
  break a field rule (section 4.3);
- sets Version# on every ticket that has a Version, including one that is only aimed at a version;
- attaches the tickets with Delivery *Implemented* to their Version tickets (section 5.2).

- **Rule:** the project keeps the schedule enabled.
- **Rule:** the step that runs after a merge into `main` makes the same sweeps (finalizing attaches the
  *Implemented* tickets), so a version that has just been finalized does not wait for the next run, and the
  two never run at the same time: the second waits for the first.

**Why.** Facts that no event announces are still facts the board depends on. A timer finds them without
asking a person to remember, and without a person's edit having to trigger anything.

> **In GitHub.** The schedule is the workflow's `schedule` trigger (three cron times a day, in UTC, which
> cannot follow daylight saving). GitHub switches a scheduled workflow off after 60 days without activity
> in the repository, so the project also has a small workflow with no schedule of its own that switches it
> back on at the next push to any branch, or on request. It leaves a workflow that a person disabled by
> hand alone.

---

### 3. Tickets

#### 3.1 What each part of a ticket means

| Part | Meaning |
|---|---|
| **Number** | A permanent, unique identifier given automatically at creation and never reused. Everything refers to the ticket by it: changelog entries, pull requests, commits. |
| **Title** | One line saying what the ticket is about. It appears in the changelog heading and becomes the summary line of the drafted commit message. |
| **Description** | What and why: the problem or purpose, the expected result, and how to tell it is done. |
| **Comments** | The running record: decisions, findings, questions, and verification results. |
| **Assignee** | Who owns the ticket. |
| **Links** | The pull requests that carry its work, the Version ticket that groups it, and related tickets, mostly through plain `#123` mentions. |
| **Fields** | The board fields (section 4). |

#### 3.2 Creating a ticket

- **Who:** a developer or an assistant creates work tickets. The automation creates Version and Alert
  tickets (section 5).
- **When:** the recommendation is to create the ticket before starting the work. Work may also start
  without one, as a `REF` placeholder, and the ticket is backfilled afterwards (see the guide on working
  and committing).
- **Rule:** one ticket covers one thing. Independent changes never share a ticket. Related parts of one
  change (a bug fix with its documentation and extra diagnostics) may share one ticket, with one Type.
- **Rule:** every work ticket gets a Size when it is created. Tickets created by the automation are the
  exception.
- **Rule:** every change can be traced to a ticket, or to a `REF` that becomes one.
- **Recommendation:** assign the ticket to the person who starts the work. More people can be added as
  the team grows.

**Why.** One ticket per thing keeps each version describable and each ticket verifiable by itself.
Requiring a Size at creation means every ticket carries an estimate from the start, instead of the
estimate being forgotten. Tracing every change to a ticket is what lets a problem found later be followed
back to why the change was made.

#### 3.3 Titles, descriptions and comments

- **Title (recommended):** short and specific, stating the problem or the outcome. No prefix such as
  `[bug]`, because the Type already says that. Settle it early: if the ticket is renamed after changelog
  entries were written, those entries keep the old title.
- **Description (recommended):** the problem or the need, in as much detail as is useful, written for
  someone who was not there. Include the background, who is affected and how, the expected result,
  constraints, and what "done" looks like. For a bug, add how to reproduce it, what was expected versus
  what happened, and the version or build it was found on. **The more detail the better**: a ticket that
  can be understood without asking anyone saves more time than it costs to write. The solution and the
  discussion that leads to it belong in the comments. A suggested implementation may go in the
  description, but only when it is clearly labelled as a proposal.
- **Comments:** keep the record in comments, not in side channels.
  - When setting *Waiting*, say what is needed and from whom.
  - When abandoning a ticket, say why and link the related ticket.
  - When moving a ticket to *Review*, a comment saying what was done and on which build it was tested is
    optional but recommended when a real review takes place. *Review* is sometimes a true review and
    sometimes a holding place for work already known to be done; the comment is for the first case.

#### 3.4 When a review fails

A review can fail before or after the merge, because a ticket may be moved to *Review* either way. Two
cases:

- **The ticket's own work is wrong or incomplete.** The ticket goes back to *InProgress*, even if it is
  already merged or released, with a comment saying what failed. The fix goes on a branch as more work on
  the same ticket, and the delivery state follows the code by itself. The changelog keeps both entries,
  one under each version, so the history stays complete.
- **A separate problem, or one found after the ticket is completed.** A new Bug ticket is created for
  it. Its description mentions the original ("introduced by #123"). The original proceeds if its own
  scope was met.

**Why.** Sending the original back keeps one ticket as the record of one piece of work until it is right.
A separate Bug keeps a finished ticket finished, and the mention keeps the link, which is enough to trace
where a problem came from, or to count how often problems slip through, without an extra field.

#### 3.5 Examples

Two typical tickets, shown as full forms with their critical fields, to show how much detail a ticket
should carry. The examples are generic, not taken from any one product. The descriptions state the
problem or the need in detail; the solution is worked out in the comments, except where a description
labels a suggestion as a proposed implementation.

More examples, covering every Type, are in appendix D (*Ticket examples*).

##### Feature: "Add CSV export to the reports page"

| Field | Value |
|---|---|
| **Title** | Add CSV export to the reports page |
| **Type** | Feature |
| **Area** | requirements, design, implementation, testing, documentation |
| **Priority** | Normal |
| **Size** | M |
| **Risk** | 2 (Low) |
| **Assignee** | Sam |

> **Purpose.** Users currently select the report table by hand and paste it into a spreadsheet. Support
> has had three requests this quarter for a way to take the data out directly, and two customers use the
> pasted tables in monthly reviews.
>
> **Who is affected.** Anyone who reads reports and needs to analyse or share them: mostly finance users,
> typically once a month, with reports of up to a few thousand rows.
>
> **What is wanted.** An *Export* button on the reports page that downloads the report currently shown
> as a CSV file. The file has one header row, the same columns in the same order as the page, values
> without display formatting (plain numbers, dates as `yyyy-mm-dd`), UTF-8 encoding, and a file name made
> of the report name and the date.
>
> **Out of scope.** Other formats (Excel, PDF), scheduled exports, and exporting reports that are not
> currently shown.
>
> **Done when.** The CSV opens correctly in two common spreadsheet programs with accented characters
> intact, matches what the page shows for at least three different reports, and the user guide describes
> the export. Behaviour with an empty report is defined and tested (header row only).
>
> **Notes.** The layout was agreed in #210. Reports above 50,000 rows are not expected; if one is found
> in practice, raise a separate ticket.
>
> **Proposed implementation** *(a suggestion, open to change in the comments).* Reuse the existing report
> query and write rows as they are read, instead of building the whole file in memory.

##### Bug: "Report totals ignore the last day of the month"

| Field | Value |
|---|---|
| **Title** | Report totals ignore the last day of the month |
| **Type** | Bug |
| **Area** | debugging, testing |
| **Priority** | High |
| **Size** | S |
| **Risk** | 2 (Low) |
| **Assignee** | Sam |

> **Problem.** The monthly report total leaves out entries dated on the last day of the month.
>
> **How to reproduce.**
> 1. Create an entry dated the 31st of a month with an amount of 100.
> 2. Open the monthly report for that month.
> 3. Note the total, then compare it with the sum of the entries listed.
>
> **Expected.** The total includes the entry from the 31st.
>
> **Actual.** The total is 100 lower than the sum of the entries. The entry is listed in the table but not
> counted. It happens for months of 28, 30 and 31 days alike: always the last day.
>
> **Found on.** Version 2.3.1, build 20260301120000, in the production data and in a clean test setup, so
> it does not depend on the data.
>
> **Impact.** Every monthly total is understated whenever the last day of the month has any entries.
> Users have been checking totals by hand. A workaround exists (run the report for a range ending on the
> first of the next month).
>
> **Done when.** Totals include every day of the month for months of 28, 29, 30 and 31 days, and an
> automated test covers the month boundary so it cannot return.

> **In GitHub.** The number appears as `#123`. The title is used in the changelog heading
> (`#### #123 — <title>`) and in the drafted commit message. A pull request that mentions `#123` shows up
> in the ticket's linked pull requests, and a plain mention creates a link without closing the ticket.
> A Version ticket groups a version's tickets as sub-issues. Comments are the issue comments; the
> assignee is the issue's assignee.

---

### 4. Ticket fields

A ticket's details are held in fields. This section explains the idea behind each one and the rules that
tie them together. The values of every field, with their meanings, are in the *Ticket fields reference*
appendix. The *Ticket model* appendix shows how the fields work together over a ticket's life.

#### 4.1 One question per field

Each field answers one question about a ticket, and the fields are kept separate on purpose. Mixing two
questions in one field is how a single value ends up meaning two things: "in progress" cannot also say
whether the code has shipped, and "closed" cannot also say whether the work was done or dropped.

#### 4.2 The fields at a glance

| Field | Question it answers | Values | Set by |
|---|---|---|---|
| **Type** | What sort of ticket is this, and why is the change being made? | one | a person (the automation for Version and Alert tickets) |
| **Area** | What kind of work does it involve? | several | a person |
| **Origin**, **REF** | Was the ticket created after the work, and which placeholder did it replace? | one; text | a person |
| **Progress** | Where is the work? | one | a person; the automation only advances *ToDo* and *OnDeck* to *InProgress* |
| **Waiting** | Is it waiting for someone's input? | one | a person |
| **Attention** | Has the ticket's state been looked at, and is it sound? | one | the automation raises *Watch*, *Caution* and *AtRisk*; a person sets *Fine* or *Acknowledged* |
| **Resolution** | How did it end? | one | a person |
| **Delivery** | Where is the delivered work? | one | the automation (apart from the optional *Committed* marker, *Implemented*, and *Dropped* on a planned Version ticket, which a person sets) |
| **Priority**, **Size**, **Risk** | How urgent, how big, how risky? | one each | a person |
| **Version**, **Build**, **Version#** | Which version and build? | text, text, number | a person may aim it; the automation sets the real values |
| **Start date**, **End date** | When did the work actually start and end? | dates | the automation |

#### 4.3 The idea of each field

**Type.**

- **Rule:** every ticket has exactly one Type: Feature, Enhancement, Change, Bug, Refactor, Task, Version
  or Alert.
- **Rule:** the Type of the tickets in a version decides how the version number moves (see the guide on
  branching and merging).

*Why.* Exactly one value keeps the ticket's main reason for existing unambiguous, and it is the one fact
the automation needs in order to number versions. A ticket that bundles related parts, such as a bug fix
with its documentation, has the Type of its main reason, and the other parts are recorded as Area.

**Area.**

- **Rule:** Area is descriptive only. It never affects version numbers or any automation.
- **Recommendation:** give a work ticket at least one Area. A ticket with none is allowed, but it cannot
  be filtered by activity.

*Why.* Area says what work a ticket takes (design, implementation, testing, documentation, and so on),
which is true whatever the product is: software, hardware and mechanical work go through the same
activities. Several values are allowed because one ticket often involves several activities.

**Origin and REF.**

- **Rule:** Origin is blank for a ticket created in the normal flow, *Backfilled* for a ticket created
  after the work to replace a ticket-less placeholder, and *Backdated* for a ticket written to document
  history from before the process existed.
- **Rule:** a Backfilled ticket also records the placeholder it replaces, in REF.

*Why.* Tickets made late have less to say about how the work was planned, and anyone reading the history
should be able to tell. REF is the link back to the changelog entries the placeholder was used in, and it lets the
automation set the ticket's Version and Delivery from where the placeholder appears.

**Progress.**

- **Rule:** the path is *ToDo, OnDeck, InProgress, Review, Completed*, with *Suspended* and *Abandoned*
  as exits from any open state. A reviewer may send work back from *Review* to *InProgress*.
- **Rule:** *Review* and *Completed* are set by people. *Review* means the work is done and awaits
  verification, which may be a real review or a formality; *Completed* means a human verified it.
- **Rule:** a ticket with code on the hosting service is at least *InProgress*: when a push (or, failing
  that, a merge) brings code for a ticket still at *ToDo* or *OnDeck*, the automation advances it. That
  is the only change it makes to Progress. It never sets *Review* or *Completed*, and never moves a ticket out of *Review*,
  *Completed*, *Abandoned* or *Suspended*: when something looks wrong there, it raises Attention (below)
  and a person decides.
- **Rule:** the GitHub issue is closed only when a ticket is *Completed* or *Abandoned*, by a person,
  never by a closing keyword.

*Why.* Progress is a judgment, so people make it. Only the developer knows whether work is finished: a
ticket may be committed, pushed or even merged in several steps, and the board may be updated later. The
one thing that is certain is that a ticket with code is not *ToDo* or *OnDeck*, so that is the only
thing the automation corrects. Keeping *Completed* manual, in both directions, means "verified" always
means a person looked, and a ticket verified before its merge is never undone by the merge.

**Waiting.**

- **Rule:** Waiting marks an open ticket as waiting for someone's input. A comment says what is needed
  and from whom; the field only flags it.
- **Rule:** it is cleared when the answer arrives, and always when the ticket becomes *Completed* or
  *Abandoned*.

*Why.* A ticket can wait in any open state. If waiting were a Progress value it would replace the real
state and lose where the ticket was.

**Attention.**

- **Rule:** Attention says whether a work ticket's state has been looked at and is sound. Its values are
  blank (the default: nothing has affected it), *Fine*, *Acknowledged*, *Watch*, *Caution* and *AtRisk*.
  Setting it never changes anything else: not Progress, Resolution, the End date or the issue.
- **Rule:** *Watch*, *Caution* and *AtRisk* are the open flags, in rising severity, raised by the
  automation. A level records how serious something looks, not what it is: the comment the automation
  adds says why, so new causes can be added without new values. *AtRisk* is reserved, and no rule uses
  it yet.
- **Rule:** *Fine* and *Acknowledged* close a flag, and are set by a person after looking. *Fine* means
  nothing is wrong, or it has been put right. *Acknowledged* means something has to be done and it is
  handled elsewhere: in another ticket, or on this one, moved back to *ToDo*, *OnDeck*, *InProgress* or
  *Suspended*. A comment says what was decided and, for *Acknowledged*, where it is handled.
- **Rule:** these are the causes the automation uses today, with the level each starts at:
  - *Caution:* new work arrives on a ticket that is *Completed*, *Abandoned*, *Review* or *Suspended* and
    whose earlier work was already pushed or delivered (Delivery is *Pushed*, *Merged*, *Implemented*,
    *Released* or *Dropped*), or a rule in section 4.4 is broken (for example *Completed* without
    Resolution *Done*, or without a Delivery). Earlier work is recognised by the ticket's recorded Build: a Build older than the
    one being pushed (or, for *Implemented*, which has no file change and no Build, the Delivery itself). A
    Delivery with no such Build, for example one set by hand, does not count. The first push of a ticket
    never raises it: a ticket moved to *Review* before its first push has no earlier work. A *Caution* is also
    raised on an *Implemented* ticket whose Version is a version that was passed: it is not finalized and a
    higher version is, so it can never be attached and would wait for ever.
  - *Watch:* a ticket looks out of date: no activity at *Review* for a week, at *OnDeck* or
    *InProgress* for a month, or at *Suspended* for six months, or a ticket that has been waiting for
    input for two weeks. Activity means a comment, a change to a field, or a new build that mentions the
    ticket; the automation's own flag comments do not count.
- **Rule:** a broken rule is raised only if the ticket, meaning its issue or its board fields, has not
  changed for five minutes. Fixing a ticket takes several edits (for example *Completed*, *Done* and
  closing the issue), and a ticket in the middle of them is not yet wrong. The two rules about Delivery and
  Version (section 4.4) wait two hours, because a person may be in the middle of completing the ticket.
- **Rule:** the automation sets an open flag only on a ticket that is blank, *Fine* or *Acknowledged*, or
  that has a lower open flag, and a higher level replaces a lower one. It never sets *Fine* or
  *Acknowledged*, and never lowers a level. A person may set any value by hand.
- **Rule:** each time it raises a flag, the automation adds one comment saying why and, for new work,
  which build.
- **Rule:** a flag is raised when a situation begins, and not again while the same situation goes on,
  however long that is. Time alone never raises it a second time. After a person closed a flag, it is
  raised again only if the situation reappears: new work arrives (a later build); or the ticket changes
  Progress and then becomes stale there; or a broken rule is put right and then broken again.

*Why.* The automation can see that something does not add up, but only a person knows what is true, so it
asks instead of guessing, and the answer is recorded in the field. Because the closing values are
values and not a blank, the field itself remembers that someone looked, and that is what keeps a
decided ticket quiet. Keeping the cause in the comment and only the severity in the field means the
list of causes can grow. Raising a flag when a situation begins, and not again while it goes on, keeps the
flag useful: one that keeps coming back gets ignored. An Alert is different: it says a rule was bypassed and gets its
own ticket and an assignee. Attention says that a ticket's own state needs a look.

**Resolution.**

- **Rule:** blank while a ticket is open. *Done* when it becomes *Completed*. One of the reasons
  (*Duplicate*, *Invalid*, *WontFix*, *Superseded*, *Obsolete*) when it becomes *Abandoned*, together
  with a comment linking any related ticket.
- **Rule:** cleared when a ticket leaves *Completed* or *Abandoned* and becomes open again.

*Why.* "How did it end" is a different question from "where is it", and the reasons for dropping work
are worth keeping: they answer later questions such as "did we already decide not to do this".

**Delivery.**

- **Rule:** Delivery says where a ticket's delivered work is: *Committed* (an optional personal marker, set by
  hand), *Pushed*, *Merged*, *Implemented* (the work is in effect and involved no file change, set by a
  person), *Released*, or *Dropped*. Apart from *Committed*, *Implemented* and *Dropped* on a planned Version
  ticket (which a person marks, section 5.2) it is set by the automation, and people only correct a mistake.
- **Rule:** *Implemented* is for a ticket that changed no file (a setting, a secret, a check that was run). A
  person sets it, together with Version, when the work is in effect. A ticket with changelog entries never
  needs it, because the automation sets *Merged*.
- **Rule:** Delivery depends only on the work, never on Progress or Resolution. It can move back: new work
  pushed on a ticket that is already *Merged*, *Implemented*, *Released* or *Dropped* returns it to *Pushed*.
- **Rule:** *Committed* is never required, and the next push overwrites it with *Pushed*; nobody else can
  see a local commit, so the team cannot rely on it. A suspended branch is not dropped, because its code is
  kept: *Pushed* stays, and only an abandoned branch sets *Dropped*.
- **Rule:** a hotfix ticket skips *Merged* and goes straight to *Released* when the hotfix is finished, and
  a release marks the tickets as *Released* as set out in the guide on releases and hotfixes, section 1.1.

*Why.* Where the code is, is a fact the automation can see, and mixing it with anyone's judgment would
make it unreliable. A ticket whose code has shipped but is not yet verified is *Merged* or *Released* and
*Review* at the same time, and both are true. *Implemented* is the one value a person sets, because
nothing in the repository shows that a secret was stored or a setting changed.

**Planning fields.**

- **Rule:** Priority says how urgent a ticket is, by consequence rather than by deadline. Size is the
  estimated developer effort, not calendar time. Risk, from 1 to 5, says how likely the work is to go
  badly wrong (a failure, a major delay, or not being feasible). Size assumes the work succeeds; Risk
  says how likely that estimate is to be wrong.
- **Rule:** every work ticket gets a Size at creation. Priority defaults to *Normal*. Risk is proposed by
  the creator and revised by the developer before the ticket moves to *Review*. Risk is informational and
  drives nothing.
- **Rule:** Version is a single field for the version a ticket is aimed at and, once it ships, the
  version it really shipped in: a person may set it ahead of time, and the automation overwrites it with
  the real version. Build holds the ticket's latest build (the most recent build stamp among the build blocks that
  mention it), and Version# is derived from Version only to sort versions. The automation sets it, not only
  when a version ships but on every scheduled run for any ticket that has a Version, so a ticket that is only aimed at a
  version sorts among the others.
- **Rule:** Start date and End date are the dates the automation noticed the ticket start and end. A
  person may correct one by hand. The automation clears the End date when it sees the ticket open again.

*Why.* Keeping urgency, effort and risk in separate fields lets them disagree, which they do: a small
change can be risky, and a large one can wait. One Version field that the automation corrects means a
ticket planned for a later version that ships earlier fixes itself.

#### 4.4 Rules that span fields

| When | Then |
|---|---|
| Progress is *Completed* | Resolution is *Done*; both are set together by the person. |
| Progress is *Abandoned* | Resolution is one of the reasons; both are set together by the person. |
| Progress is *ToDo*, *OnDeck*, *InProgress*, *Review* or *Suspended* | Resolution and End date are blank. |
| A ticket becomes *Completed* or *Abandoned* | Waiting is cleared. |
| A ticket leaves *Completed* or *Abandoned* | The person clears Resolution; the automation clears the End date. |
| Origin is *Backfilled* | REF names the placeholder it replaced. |
| Code is merged or released | Delivery says so, whatever Progress and Resolution are. |
| A ticket has no file change and its work is in effect | Delivery is *Implemented* and Version names the version it belongs to. Pure analysis, a setting or a check that was run counts: the Delivery is never left blank. |
| A work ticket is *Completed* | Delivery is set: *Merged* if files changed, *Implemented* if none did. (A ticket that came to nothing is *Abandoned*, not *Completed*. Version and Alert tickets are not work tickets.) |
| Delivery is *Merged*, *Implemented* or *Released* | Version is set. The automation sets it (the finalize step for *Merged*, the next scheduled run for *Implemented*); a ticket still without one two hours after its last change is flagged. |
| A ticket is *Completed* or *Abandoned* | The GitHub issue is closed, by a person. |
| A ticket is a Version ticket | Only the version and Delivery fields apply (see the special tickets section). |
| A work ticket breaks one of these rules | The automation raises *Caution* in Attention, with a comment. |

> **In GitHub.** Type is the native issue type. Area is a set of labels. The other fields are board
> fields: Progress is the board's *Status* field, Delivery is a single-select field, and Start
> date and End date are date fields. The automation reads Type from the issue and writes the other fields
> to the board.


---

### 5. Special tickets

#### 5.1 What makes them special

Version and Alert tickets are created by the automation, not planned by people. They do not follow the
work-ticket rules: they are exempt from the rule that every ticket gets a Size at creation, and only
some fields apply to them (the *Ticket fields reference* appendix has the table).

#### 5.2 Version tickets

A Version ticket is a bookkeeping record for one version, titled `Version X.Y.Z` (without the `V`), or
`Version X.Y.Z-HFn` for a hotfix. The work tickets of the version point to it through their Version
field, and the automation attaches them as sub-issues of the Version ticket, so the board shows how many
of them are complete. A Version ticket does no work and is never verified.

| Stage | What happens | Delivery | Issue |
|---|---|---|---|
| **Planned** (optional, not recommended) | A person creates it ahead of time for a future version. | blank | open |
| **Finalized** | The automation creates it, or reuses the planned one with the same title, when the version is finalized. | Merged | closed by the automation |
| **Released** | A release is cut on that version. The automation posts a comment with the date and the tag name. | Released | stays closed |
| **Planned, then dropped** | The version never happened under that number. A person marks it. | Dropped | closed, with a comment saying what replaced it |

- **Rule:** the automation writes the description at finalize: the date (UTC), the bump and why (which
  ticket gave it, or the marker that forced it), the pull request, and the tickets with their Type.
  Build holds the last build of the version.
- **Rule:** at every finalize, and on a manual run, the automation also attaches the tickets with Delivery
  *Implemented* that are not yet sub-issues of any Version ticket, by their Version: a blank Version gets
  the version being finalized (at a scheduled run, the latest finalized version), an already finalized version is kept and the ticket is attached to that
  version's ticket, and a later version makes the ticket wait. Such a ticket keeps Delivery *Implemented*
  and gets no Build. A comment on the Version ticket says which tickets were added, because its description
  is written once.
- **Rule:** a hotfix version goes straight from planned or created to *Released* when the hotfix is
  finished, because a hotfix is never merged into `main`.
- **Rule:** when a version is finalized, any planned Version ticket with a lower number can no longer
  happen under that number. The automation raises one Alert listing them (section 5.3). Hotfix versions
  do not run this check.
- **Recommendation:** do not create Version tickets ahead of time. Aim tickets at a version with their
  Version field instead (the guide on issues and the board in practice, section 6): the automation creates the
  Version ticket when the version is finalized, so the Version tickets are in the order the versions shipped,
  which the *Versions* view relies on. If you do plan one and the number turns out wrong, the alert above is
  how the mismatch is cleaned up.

*Why.* Delivery already describes a version's life (planned, merged, released, dropped), so a Version
ticket needs no Progress. One ticket per version gives a single place to see what shipped in it and how
much of it has been verified. Closing it at finalize keeps bookkeeping records from crowding the open
tickets that need attention.

#### 5.3 Alert tickets

An Alert is a real check that a person must do. The automation raises one when something needs a person
to review it: a detected bypass, a merge that landed without changelog entries, a changelog it cannot read
(so no version was finalized), or planned versions that can no longer happen. It is not the same as the Attention flag: an Alert is about a rule that was bypassed
and is a ticket of its own, while Attention is a flag on a work ticket whose own state needs a look.

- **Rule:** an Alert has Priority *Critical*, Area `process` and Progress *ToDo* when it is created. Size
  and Risk are blank until the person who takes it triages it.
- **Rule:** every move of an Alert after creation is manual: *InProgress* when someone starts, *Review*
  when they believe it is handled, *Completed* when a human verifies it. Shipping a version never moves
  it. A person closes it.
- **Rule:** an Alert for a bypass, for a merge without changelog entries or for a changelog that could not
  be read is assigned to the person who pushed, because they know the context. An Alert for stale planned
  versions is unassigned until someone takes it.
- For a bypass, the changelog also gets an entry that points at the Alert. What the person does with it
  is described in the guide on branching and merging, in the section on enforcement.

*Why.* A bypass is a decision that needs follow-up, and the follow-up must exist even when the person who
bypassed is too busy to remember it. An Alert makes the follow-up a ticket at the top of the queue,
instead of a note someone has to remember.

#### 5.4 Examples

The automation generates these texts. The names, numbers and dates are invented for illustration.

##### Version ticket: "Version 2.4.1"

| Field | Value |
|---|---|
| **Title** | Version 2.4.1 |
| **Type** | Version |
| **Delivery** | Merged |
| **Version** | V2.4.1 |
| **Build** | 20261005143045 |
| **Sub-issues** | #201, #204, #205 |
| **Progress, Priority, Size, Risk, Area** | none |

> Finalized 2026-10-05 14:32 UTC from pull request #187. Bump: sub, because #201 is a Feature. Last
> build: 20261005143045.
>
> Tickets:
> - #201 Add CSV export to the reports page (Feature)
> - #204 Report totals ignore the last day of the month (Bug)
> - #205 Write the user guide for the export feature (Task)

When a release is cut on this version, the automation sets Delivery to *Released* and adds a comment:
"Released 2026-10-12 09:15 UTC. Tag: `released/V2.4.1`."

##### Alert ticket for a bypass: "Merge to main not identical to its branch (V2.4.1)"

| Field | Value |
|---|---|
| **Title** | Merge to main not identical to its branch (V2.4.1) |
| **Type** | Alert |
| **Area** | process |
| **Priority** | Critical |
| **Progress** | ToDo |
| **Size, Risk** | blank until triaged |
| **Assignee** | Sam (the person who pushed) |
| **Version** | V2.4.1 |

> Detected on the push of 2026-10-05 16:40 UTC to `main` (commit `abc1234`): this merge's result is not
> identical to its branch's final state. The branch was not synced first, or a conflict was resolved
> during the merge itself.
>
> **To do.** Confirm that the merged result was built and tested, document anything that changed in the
> changelog (in the entry for V2.4.1 that points at this ticket, or in a new block in the current
> version).

##### Alert ticket for stale planned versions: "Stale planned Version tickets after V2.4.1"

| Field | Value |
|---|---|
| **Title** | Stale planned Version tickets after V2.4.1 |
| **Type** | Alert |
| **Area** | process |
| **Priority** | Critical |
| **Progress** | ToDo |
| **Size, Risk** | blank until triaged |
| **Assignee** | none until someone takes it |

> Version 2.4.1 was finalized. These planned Version tickets have a lower number and cannot happen under
> it: #130 Version 2.4.0.
>
> **To do.** For each one, set Delivery to *Dropped* and close it with a comment saying what replaced it,
> or correct the number if it was a mistake.

A third kind of Alert, for a merge that landed without changelog entries, reads like the bypass Alert: it
says that file changes reached `main` with no changelog entries, that the automation created the version
and the changelog entry itself, and asks the person who pushed to document what changed.

A fourth kind, for a changelog the automation could not read, is titled "Changelog error on main: no
version finalized". It names the push and quotes the error (for example two open `WIP-Version` headings,
or text after the heading that is not a marker), and asks the person who pushed to correct `CHANGELOG.md`
by hand and then run the finalize step again.


---

### 6. Pull requests

#### 6.1 What a pull request is

A pull request is the proposal to merge a branch into `main`. It is the place where the branch's checks
run, where discussion about the change happens, and where the lasting record of what landed stays. The
rules for using one (it is required, how it is titled, how tickets are referenced, how it is merged) are
in the guide on branching and merging; this section only defines it and says what it carries.

#### 6.2 What it carries

| Part | Meaning |
|---|---|
| **Number** | A permanent identifier, shared with tickets. |
| **Source and target** | The branch being merged and the branch it lands on, always `main`. |
| **Title** | The branch's functional purpose. |
| **Description** | What the person merging, and anyone reading the history later, needs to know (section 6.3). |
| **Commits** | Every commit of the branch, each with its build stamp in the changelog. |
| **Checks** | The advisory check that warns when the branch is behind `main`. |
| **Discussion** | Comments about the change. |
| **Merge method** | A merge commit, nothing else. |

Ticket fields (Type, Area, Priority and the rest) do not apply to a pull request, and labels on it play no
part in versioning: the version number comes from the tickets.

A pull request shares its number with the tickets, so the numbers of the pull requests would be missing from the
board's *All* view. The automation therefore puts each pull request on the board as an item when it is opened,
and sets no field on it. The other views leave pull requests out (their filters end with `is:issue`), and the
automation's sweeps skip them, because a pull request is not a ticket.

#### 6.3 Creating and ending one

- **Rule:** the description contains, at a minimum, what the pull request changes and every ticket it
  covers: the changelog entries of the open version, copied as they are (the ticket headings with their
  bullets). If they are too long, the ticket numbers alone are enough. The pull request itself
  identifies the branch it comes from.
- **Recommendation:** also say which build was tested, whether `main` was synced into the branch and
  when, and where any conflict resolution was documented.
- **Recommendation:** open the pull request when the branch is ready to land: committed, synced with
  `main`, built and tested.
- **Recommendation:** if the branch is suspended or abandoned instead of merged, close its pull request
  with a comment saying why, then retire the branch as usual.

**Why.** The description is where the changes and the ticket numbers meet, which is exactly the connection
needed when a problem appears later: from a version you find its pull request, and from the pull request
the tickets. The changelog entries are copied as they are, because they are already written and
checked, and rewriting the spirit of a change in new words is more likely to introduce an error than to
add clarity. The build, the sync and the conflict notes are the evidence behind the rules about testing
and syncing, so they are worth recording whenever there is something to say.

#### 6.4 Example

##### Pull request: "Add CSV export to the reports page"

| Field | Value |
|---|---|
| **Title** | Add CSV export to the reports page |
| **Source and target** | `csv-export` into `main` |
| **Tickets** | #201, #205 |

> #### #201 — Add CSV export to the reports page
> - reports page: added an Export button that downloads the current report as CSV (this change also
>   covers #205).
> - tests: added a test that compares the exported file with the page for three reports.
> #### #205 — Write the user guide for the export feature
> - Covered by the change described under #201.
>
> **Tested on build** 20261004101530. `main` was merged into the branch on 2026-10-04 with no conflicts, and
> the branch was rebuilt and retested afterwards.

> **In GitHub.** The source and target branches and the commits appear automatically in the pull request.
> The description is set when the pull request is opened and can be edited afterwards. The advisory check
> appears among the pull request's checks. Squash and rebase merging are disabled in the repository
> settings, so the merge button offers a merge commit only. A pull request template in `.github/` can
> pre-fill the description.


---

### 7. The changelog

#### 7.1 What it is

The changelog is a running record of every change to files, grouped by version, then by build (one per
commit), then by ticket. It is also the source the automation reads to number versions, to draft commit
messages and to update the board. How to write entries is in the guide on working and committing; this
section describes what the file contains and how it is structured.

#### 7.2 The structure

```
## WIP-Version                         the open version, on a branch (a marker may follow: +V, +s, +m)
### WIP-Build                          placeholder for the commit being made
### Build 20261005143045 (branch <name>)  stamped at commit time, one per commit that logs a change
### Build 20261005143045 (branch <name>, commit 1a2b3c4)   filled in by the automation when the hooks were skipped
#### #201 — <ticket title>             one block per ticket
- what changed
#### REF 20261005180000 — <reason>     a change with no ticket yet
#### AUTO-REF 20261005164000 (tracked as #187)   written by the automation
## V2.4.1 — 2026-10-05 14:32 UTC       a finalized version (UTC date and time)
```

| Heading | Meaning |
|---|---|
| `## WIP-Version` | The version being worked on. It has no number until it merges. |
| `### Build <timestamp> (branch <name>)` | One commit's worth of changes. The local hook stamps it with the UTC time of the commit. |
| `### Build <timestamp> (branch <name>, commit <hash>)` | The same, filled in by the automation for a commit made without the hooks. It carries the commit's UTC time and the start of its hash, and a note in the first entry says why it looks different. |
| `#### #123 — title` | The changes belonging to one ticket. |
| `#### REF <token> — reason` | Changes made without a ticket yet: a placeholder to be backfilled. |
| `#### AUTO-REF … (tracked as #N)` | An entry the automation wrote, pointing at an Alert. |
| `## V2.4.1 — date time UTC` | A finalized version. Newest first. |

#### 7.3 Rules

- **Rule:** the changelog records changes to files and nothing else. Repository settings, tags, branches,
  secrets and git configuration are tracked in tickets, and so are known bugs and planned work. There
  are no "Known bugs" or "Planned" sections.
- **Rule:** every commit that changes files adds a build block with at least one ticket block or `REF`
  block.
- **Rule:** the newest version comes first, and within a version the newest build comes first: the hook
  stamps a `### WIP-Build` placeholder where it stands, so it is added above the earlier builds. Stamps and
  everything the automation writes are UTC (see the guide on concepts, section 2).
- **Rule:** the topmost finalized version heading is the single source of truth for the version (see the
  guide on branching and merging).
- **Rule:** entries of commits already made are not edited (the two exceptions, a placeholder replaced
  and a critical correction, are in the guide on working and committing, sections 2.3 and 2.5).
- **Rule:** the commit message is drafted from the entries just written, so each ticket's title and
  bullets are written once.
- **Rule:** a hotfix version's heading lives only on its hotfix branch. The link between a hotfix and
  the fix later reintroduced into `main` is kept in the tickets, not in the changelog.
- **Safety net, not a way of working:** if a change reaches `main` with no changelog entries, the
  automation creates the missing version and an `AUTO-REF` entry itself. It exists so that nothing is
  silently lost; relying on it leaves a generated note where a real description should be.

**Why.** One record of what changed, written when it changed and tied to a ticket and a build, is what
lets anyone trace a problem back to a commit and its reason. Keeping everything else (settings, plans,
known bugs) in tickets stops the changelog drifting out of step with the board.

#### 7.4 Placeholder entries: REF and AUTO-REF

Both kinds of entry are temporary. They record that a change happened before its proper description
or ticket existed.

- **`REF`** is a developer's own placeholder for a change made without a ticket. Its token is the UTC
  timestamp of when it was written (`yyyymmddhhmmss`), and the reason says briefly why there is no ticket
  yet. Nothing blocks work on having a ticket first. The ticket is created afterwards, with its Origin
  set to *Backfilled* and its REF field holding the token. The change is then documented under the real
  ticket, either by replacing the placeholder in place or, preferably, by describing it in a new block in
  the current version.
- **`AUTO-REF`** is written by the automation when it detects a bypass or a change with no entries. It
  points at the Alert ticket that was opened for it. The person triaging the Alert documents the
  change, either by replacing the generated note in place or, preferably, by describing it in a new block
  in the current version.

When the change is described in a new block, the placeholder, a `REF` or an `AUTO-REF`, stays where it is:
it is the record of how the change first appeared, and the new block is the description.

The procedure for backfilling a `REF` is in the guide on working and committing, and the procedure for
triaging an Alert, including its `AUTO-REF`, is in the guide on issues and the board.

#### 7.5 Example

```
## WIP-Version
### Build 20261006091200 (branch csv-export)
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
- tests: added a test that compares the exported file with the page for three reports.
#### REF 20261006091500 — no ticket yet (typo in the settings help text)
- settings help text: fixed the spelling of "authentication".

## V2.4.1 — 2026-10-05 14:32 UTC
### Build 20261005143045 (branch report-fixes)
#### #204 — Report totals ignore the last day of the month
- report totals: the last day of the month is now included in the sum.
- tests: added a test for months of 28, 29, 30 and 31 days.
#### AUTO-REF 20261005164000 (tracked as #187)
- Auto-flagged: this merge's result is not identical to its branch's final state. Issue #187 opened
  automatically for review: document the change once triaged.
```

> **In GitHub.** The changelog is a `CHANGELOG.md` file at the repository root. The local hooks replace
> `### WIP-Build` with the stamped build heading when a commit is made and draft the commit message from
> the entries. The automation renames `## WIP-Version` to the finalized version when a branch merges, and
> writes the `AUTO-REF` entries and, as a safety net, the missing version and build entries.


---

### 8. Branches and tags

A short recap, with no new rules. The full rules and their reasons are in the guide on branching and
merging; if the two ever differ, that guide is the reference.

#### 8.1 Branches

- `main` is the one integration line. Every other branch is named in kebab-case, with no `/`.
- A branch is a **work branch** (starts from `main` and merges back), a **hotfix branch** (starts from a
  release tag and never merges), or a **parked branch** (finished work deliberately kept off `main`).

#### 8.2 Tags

A tag is in one of four namespaces: `archived/`, `suspended/` and `abandoned/` for a branch that is
retired, and `released/` for a version, or a finished hotfix, declared a release. The formats, with their
reasons, are in the guide on branching and merging, section 2.2.

#### 8.3 How they fit in the map

- A branch's name appears in the changelog's build headings and in the pull request description. A tag
  records where a retired branch ended up, or which version was released.
- To find things, list a namespace: everything suspended, everything released, everything abandoned.

> **In GitHub.** Branches and tags are git branches and tags, and the tags show under the repository's
> tags and releases. `git tag -l 'suspended/*'` lists a namespace.


---

### 9. Documentation

#### 9.1 The three places

Documentation lives in three places, and each answers a different question.

| Place | Holds | Kept up to date? |
|---|---|---|
| **Readme** (root) | What the project is, its requirements, and how to build and use it. The entry point: kept short, and linking to the wiki for detail. | Yes |
| **Wiki** (`doc/wiki/`) | Current-state reference pages: how the project works now. One topic per page, with a `Home` page as the index. | Yes, whenever what a page describes changes |
| **Records** (`doc/`, outside the wiki) | Point-in-time documents: design records (why something was decided), analyses and investigations, measurements. | No: dated, and not rewritten afterwards |

#### 9.2 Rules

- **Rule:** when a change alters what the readme or a wiki page describes, the same change updates that
  page. Documentation travels with the change and is merged in the same pull request.
- **Rule:** wiki pages are one markdown file per page, named by page title with hyphens
  (`Getting-Started.md`) and linked with `[[Page Name]]` or relative links, so the folder can be
  published to the hosting wiki as it is.
- **Recommendation:** put a date in the file name of a record (`2026-09-18_sensor-conflict-analysis.md`), in
  your own local time,
  and do not edit it afterwards to reflect later changes. When a record is superseded, say so at the top
  and point to its replacement.
- **Recommendation:** do not repeat the same content in the readme and the wiki. Keep one and link to it.
- **Recommendation:** a wiki page of known issues lists only the critical or very important limitations,
  as a summary. The ticket that tracks each one is the source of truth and holds the detail.
- **Relation to the changelog:** the changelog says *what changed*, the wiki says *how things are*, and a
  record says *why something was decided or found*.
- **The process guides** (this set) are published separately. The project's wiki links to them and may
  keep a one-page summary.

**Why.** Readers have different questions at different times: "how do I start", "how does this work
today", and "why was it done this way". Separating the places lets each be answered without one
document trying to be all three. A wiki updated in the same change as the code cannot quietly go stale.
Leaving records unedited preserves what people knew when they decided, which is what makes them useful
later, and a date in the name tells a reader at a glance how old the reasoning is.

What to update as you work, and when, is a checklist in the guide on working and committing.

> **In GitHub.** The readme is the repository's readme file. The wiki pages are in `doc/wiki/` and are
> copied to the repository's own wiki by a workflow where a wiki is available. Records are plain markdown
> files in `doc/`.


---

### 10. Who sets what

A lookup table of who is responsible for each thing. It adds no new rules.

#### 10.1 The actors

| Actor | Who or what it is |
|---|---|
| **Developer** | A person doing the project's work. |
| **Project owner** | The person responsible for the project's direction and priorities (also called the manager). |
| **Administrator** | The person who manages the repository's settings, secrets and the board's configuration. |
| **Local automation** | The git hooks and scripts that run on a developer's machine. |
| **Remote automation** | The workflows that run on the hosting service. |

**Responsible, not necessarily manual.** Naming a developer, the project owner or the administrator means
that person is responsible. It does not mean the step is done by hand. Anything a person is responsible for can be done
by an assistant or by a script or command the person runs, and it is still that person's action. Scripts
and commands exist for some steps; the procedural guides give the steps, and the guide on working with an
assistant covers what an assistant may do. One thing cannot be delegated: *Completed* and *Done* mean that
a person has verified the result, so an assistant never decides them.

**The principle.** Judgment belongs to people and facts belong to the automation. Where something is a
fact the automation can see (where the code is, which build, which dates), the automation sets it. Where
it is a judgment (is the work done, is it verified, how urgent is it), a person does.

#### 10.2 Ticket fields

| Field | Developer | Project owner | Local automation | Remote automation |
|---|---|---|---|---|
| Type, Area, Origin, REF, Waiting, Size, Risk | sets | may change | | sets Type on Version and Alert tickets |
| Attention | sets *Fine* or *Acknowledged*, after deciding | sets *Fine* or *Acknowledged*, after deciding | | raises *Watch*, *Caution* and *AtRisk*, with a comment |
| Priority | proposes | sets | | |
| Progress up to *Review* | sets | may change | | advances *ToDo* and *OnDeck* to *InProgress* when code for the ticket is pushed |
| *Completed* and *Done* | sets, after verifying | sets, after verifying | | |
| *Abandoned*, *Suspended* and the abandon reasons | proposes | decides | | |
| Version (the target) | | sets | | overwrites it with the real version |
| Delivery (except *Committed*, *Implemented* and *Dropped* on a planned Version ticket), Build, Version#, Start and End dates | | | | sets |
| Delivery *Implemented*, with its Version | sets | may change | | attaches the ticket to its Version ticket |

*Completed* and *Done* may be set by the developer or the project owner, whoever verified the result. The
developer may also set the optional *Committed* marker in Delivery.

#### 10.3 Everything else

| Item | Developer | Project owner | Local automation | Remote automation |
|---|---|---|---|---|
| Branches, pull requests, merges | does | | | |
| Retiring a branch | does | | | carries it out |
| Planned Version tickets, and *Dropped* on them | | does | | |
| Cutting a release | decides | told | | carries it out |
| Starting and finishing a hotfix | does | told | | carries out the finish |
| Forcing the version bump (`+V`, `+s`, `+m`) | decides | | | |
| Changelog entries | writes | | stamps the build time | renames the version, writes `AUTO-REF` entries, adds missing entries as a safety net |
| Commit message | confirms | | drafts it | |
| Version and Alert tickets | triages Alerts | | | creates them |
| Closing a ticket | at *Completed* or *Abandoned* | at *Completed* or *Abandoned* | | closes Version tickets |

#### 10.4 Administration

| Item | Who does it |
|---|---|
| Repository settings, branch protection and its bypass | the administrator |
| Issue types, labels, and the board's fields and views (the views are created from a file by a script) | the administrator |
| The project token and other secrets | the administrator holds and renews them |
| Installing and updating the automation | the administrator |

The settings are listed in the new-project bootstrap guide. One person may be administrator and developer
at once.

#### 10.5 Where the steps are

This guide says who is responsible. The steps, commands and scripts for doing each thing are in the
procedural guides: starting work, working and committing, syncing and merging, issues and the board, and
releases and hotfixes.

> **In GitHub.** The local automation is the git hooks kept in the repository and any scripts run on a
> developer's machine. The remote automation is the repository's workflow, which runs on pushes, on pull
> requests and on request.


#### 10.6 A small team

One person may hold every role. In a team of one or two people who trust each other, the roles collapse:

- **"Proposes" and "tells the project owner" steps** become a comment on the ticket or the pull request, or
  nothing at all when the same person holds both roles. Nobody waits for anyone.
- **"Decides" steps** are decided by whoever is doing the work. That includes suspending or abandoning,
  releases, hotfixes and the version bump.
- **Triage and the board review** are done by whoever is working on the board.
- **The author may verify their own work,** though a second pair of eyes is better.

What stays, whatever the team size:

- the evidence rules: every change belongs to a ticket and a build, results name the build, and nothing that
  was tested is rewritten;
- the Alerts for a bypass;
- verification by a person, and the field rules;
- the tooling.

- **Rule:** collapsing the roles is not a bypass and raises no Alert. The "who" statements in the guides are
  the default for a team that has the roles split.
- **Recommendation:** keep the roles named in the shared instructions file (see the guide on working with an
  assistant, section 6), even in a team of one, so that they can be split when the team grows. When a second
  person joins, the proposing, telling and deciding steps become real again.

**Why.** A process built for a team should not slow a team of two. The safeguards that matter protect the
record, which is the evidence and the history, and not a chain of approvals.

---

## Guide 04: Starting Work

This guide covers the steps from "I am going to work on something" to the first push: getting a ticket,
creating the branch, opening the changelog entry, and making the first commit. It is a procedure: each
step says what to do and why, and the commands are in the "In GitHub" blocks. The pieces it refers to
(tickets, fields, the changelog, branches and tags) are defined in the guide on project structure, and the
rules about branches in the guide on branching and merging.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

### 1. Before you start

- **Rule:** every clone is set up once before work starts: clone the repository, follow the readme's
  setup for the project's tools, and activate the hooks.
- **Recommendation:** check that the hooks are active.
- **Recommendation:** make sure git knows who you are (name and email), so commits are attributed
  correctly.

**Why.** A clone without the hooks is not protected. Nothing stamps the build time, drafts the commit
message or warns about being behind `main`, and the first sign of the problem is a changelog entry with an
unresolved placeholder. The hooks also need their runtime installed, and on Linux their scripts must keep
their executable bit or git ignores them. The readme gives the project's exact setup command; this guide
only states that the step exists.

> **In GitHub.** Clone the repository, then run the project's setup command, which also activates the
> hooks (`git config core.hooksPath .githooks`). Check with `git config core.hooksPath`, which should print
> `.githooks`. Check your identity with `git config user.name` and `git config user.email`.


---

### 2. Get a ticket, or a REF

The steps:

1. **Check for an existing ticket.** Search the open and closed tickets for the same thing before
   creating one.
2. **If there is none, create it.** Fill in what the guide on project structure says a ticket needs, and
   assign it to yourself.
3. **Or start with a `REF`.** For a small or urgent change, or exploratory work, you may start without a
   ticket. Every `REF` is backfilled later (see the guide on working and committing).
4. **Mark it started.** Set Progress to *InProgress*. The Start date is filled in by the automation.
5. **If you need input before starting,** set Waiting, with a comment saying what is needed and from whom.

#### 2.1 Rules

- **Rule:** check for an existing ticket before creating one.
- **Rule:** a new ticket has at least a Title, a Type, a Description and a Size. Area, Priority and Risk
  are suggested.
- **Recommendation:** create the ticket first. A `REF` is legitimate for a small, urgent or exploratory
  change, and judgment decides which those are, but it is a loan and not a way of working: every `REF`
  is backfilled, with Origin set to *Backfilled*.
- **Rule:** when you start the work, set Progress to *InProgress* and assign the ticket to yourself.
- **Rule:** one ticket covers one thing. If the work turns out to be several independent changes, split
  them into separate tickets. They may still share a branch.

**Why.**

- *Search first* because a duplicate splits the history of one piece of work, and a closed ticket may be
  the right one to reopen. For example, a failed review sends a ticket back to *InProgress* instead of
  creating a new one (see the guide on project structure, section 3.4).
- *A minimum set of fields at creation* so that every ticket is understandable and estimated from the
  start, which is cheaper than reconstructing it later.
- *Ticket first* because writing down what and why before starting makes the work clearer, and gives the
  changelog a ticket to refer to. A `REF` keeps small work from being slowed down, at the price of a
  backfill.
- *Mark it started* because the board should show what is being worked on, and the dates and the safety
  net for tickets whose code is already pushed depend on an accurate Progress.
- *One ticket per thing* so that each can be verified and described by itself.

> **In GitHub.** Create the issue from the repository's Issues tab (or with `gh issue create`). Set its
> Type, then the Area labels, the board fields (Progress, Priority, Size, Risk) and the assignee. A `REF`
> has no ticket, so there is nothing to create; the placeholder is written into the changelog when you
> log the first change (section 4).


---

### 3. Create the branch

#### 3.1 A new work branch

1. **Update `main`.** Fetch and bring your local `main` up to date.
2. **Check that no branch already exists for this work.** If one does, use section 3.3 instead.
3. **Create the branch from `main`,** named for what it does.

- **Rule:** a work branch starts from an up-to-date `main`.
- **Rule:** the branch name is kebab-case, never contains `/`, and says what the branch is for, such as
  `csv-export` or `settings-module-split`. It does not carry a ticket number: a branch can cover several
  tickets, and the pull request lists them.
- **Recommendation:** one branch per functional unit (see the guide on branching and merging, section
  1.2).

**Why.** Starting from an out-of-date `main` means paying for the lag later, as conflicts. A name that says
what the branch does is useful to everyone who sees it in a list, in a build heading or in a pull
request, and unlike a ticket number it stays true however many tickets the branch ends up carrying.

> **In GitHub.** `git fetch`, `git switch main`, `git pull`, then `git switch -c <branch-name>`. List
> existing branches with `git branch -a`.

#### 3.2 A hotfix branch

- **Rule:** a hotfix branch starts from the release tag being patched, not from `main`. A further
  hotfix for the same release starts from the tag of the latest hotfix, so that it includes the earlier
  fixes.
- **Rule:** it is named as set out in the guide on branching and merging, section 2.1 (for example
  `hotfix-v1-25-0-fix-sensor-timeout`).

The details of finishing a hotfix are in the guide on releases and hotfixes.

**Why.** A hotfix patches exactly what was released, so it must start from exactly that, and not from a
`main` that has moved on.

> **In GitHub.** `git switch -c hotfix-v1-25-0-fix-sensor-timeout released/V1.25.0`.

#### 3.3 Continue on an existing branch

When the branch still exists and the new work belongs with it (a follow-up, the next stage of the same
feature, or a fix to what it delivered):

- **Rule:** bring `main` into the branch first (see the guide on branching and merging, section 4). If
  the branch was merged before, this brings in the automation's commit that renamed the version
  heading.
- **Rule:** if the branch was merged before, add a new `WIP-Version` heading before the next logged change
  (section 4 of this guide), after that sync, because finalizing a version leaves no empty heading
  behind.

#### 3.4 Recover a suspended or abandoned branch

- **Rule:** recreate the branch from its tag. The tag stays as history.
- **Recommendation:** bring `main` into it before doing anything else, since it stood still while `main`
  moved.
- **Rule:** the ticket goes from *Suspended* or *Abandoned* back to *InProgress*, and its Resolution is
  cleared.
- If the branch's changelog already has an open `WIP-Version`, continue it. Do not open a second heading.

> **In GitHub.** `git switch -c <branch-name> suspended/<date>_<branch-name>`, or use the `abandoned/`
> tag for an abandoned branch.


---

### 4. Open the changelog entry

The steps:

1. **Check for an open `WIP-Version` heading.** If the branch already has one, continue it. Do not open a
   second.
2. **Add `## WIP-Version`** at the top of `CHANGELOG.md`, above the latest finalized version. Add a
   marker (`+V`, `+s` or `+m`) only if you want to force the version bump.
3. **Add a `### WIP-Build` placeholder** under it. The hook turns it into a stamped build heading when you
   commit.
4. **Add the ticket block:** `#### #123 — <ticket title>`, using the ticket's number and its exact title.
   For a change without a ticket, add `#### REF <token> — <reason>` instead, where the token is the
   current UTC time (`yyyymmddhhmmss`) and the reason is brief.
5. **Write the bullets** for what changed as you make the changes. How to write them is in the guide on
   working and committing.

#### 4.1 Rules

- **Rule:** a branch has at most one open `WIP-Version` heading, at the top of the changelog.
- **Rule:** a marker is only for forcing the version bump. It applies to that one version, and it is not
  allowed on a hotfix branch.
- **Rule:** the ticket heading uses the ticket's number and its exact title.
- **Recommendation:** open the entry when you start the work, not at the end.

**Why.**

- *One open heading* because finalizing renames it to the real version, and two would leave the
  automation guessing which to rename.
- *Markers only to force* because the bump is normally decided from the tickets' Types, and a marker is
  the developer's way of overriding that in plain sight.
- *The exact ticket title* because the commit message summary is drafted from it, and the automation finds
  the ticket by its number.
- *Open it at the start* because the changelog is written as the work happens, and a version can only be
  finalized if there is something to finalize. The automation renames an existing heading but does not
  create one, except as the safety net for a change that arrived without entries.

#### 4.2 Example

When you start the work, before any change is logged:

```
## WIP-Version
### WIP-Build
#### #201 — Add CSV export to the reports page
```

After the first change is logged and committed, the hook has stamped the build:

```
## WIP-Version
### Build 20261006091200 (branch csv-export)
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
```

The same start for a change without a ticket:

```
## WIP-Version
### WIP-Build
#### REF 20261006091500 — no ticket yet (typo in the settings help text)
```

> **In GitHub.** Edit `CHANGELOG.md` at the repository root. To produce a `REF` token, run
> `date -u +%Y%m%d%H%M%S`. The `pre-commit` hook replaces `### WIP-Build` with
> `### Build <timestamp> (branch <name>)` in the staged changelog.


---

### 5. First commit and push

The rhythm of later commits is in the guide on working and committing. This section covers the first
commit and what happens around it.

The steps:

1. **Stage the change and its changelog entry together.** They go in the same commit.
2. **Commit with the editor,** not with `-m`. The hooks do two things: they stamp the build in the staged
   changelog, and they draft the commit message from the entries you wrote.
3. **Check the result.** The build heading is stamped (no `WIP-Build` is left), and the drafted message
   reads right: the ticket's title as the summary for one ticket, "Multiple tickets" for several, or the
   first bullet if there is only a `REF`.
4. **Push the branch.** The remote automation sets Delivery to *Pushed* on the tickets in your changelog
   entries, and moves a ticket still at *ToDo* or *OnDeck* to *InProgress*. If new work arrives on a ticket
   that looked finished, it also raises *Caution* in Attention, with a comment; the first push of a ticket
   raises nothing. When exactly it does this is in the guide on project structure, section 4.3.
5. **Check the ticket.** Delivery shows *Pushed*. The Start date appears after the automation's next
   sweep.

#### 5.1 Rules

- **Rule:** the change and its changelog entry go in the same commit.
- **Rule:** build the change locally before committing. Compiling is done by the developer, once, before
  the commit exists, and nothing else compiles it.
- **Recommendation:** commit through the editor, not with `-m`, and read the drafted message before
  confirming it.
- **If the hooks were skipped,** the remote automation fills in the build heading itself, with the
  commit's hash in it, and adds a note to the entry.

**Why.**

- *Same commit* because the build stamp ties the entry to that commit, and the hook stamps only what is
  staged.
- *Build first* because there is no other check: a commit that does not compile reaches the branch
  exactly as it is.
- *The editor, not `-m`* because `-m` skips the draft, so the message would be written twice.
- *The fallback and its note* because a commit made without the hook has an unresolved placeholder, and
  the note tells a later reader why that heading looks different.

> **In GitHub.** `git add <files> CHANGELOG.md`, then `git commit` (no `-m`). The first push is
> `git push -u origin <branch-name>`; later pushes are plain `git push`.


---

### 6. Checklist

A one-page summary of the guide. It adds no new rules, and it can be copied into a ticket or a pull
request description.

**Before the first time**

- [ ] The clone is set up and the hooks are active (section 1).

**For each piece of work**

- [ ] I searched for an existing ticket (section 2).
- [ ] A ticket exists with a Title, Type, Description and Size, or I have decided to start with a `REF`.
- [ ] The ticket is assigned to me and Progress is *InProgress*. Waiting is set if I need input.
- [ ] `main` is up to date, and no existing branch already covers this work (section 3).
- [ ] The branch is created: kebab-case, no `/`, from `main`. A hotfix starts from its release tag and is
      named `hotfix-v…`.
- [ ] If I am continuing or recovering a branch: `main` was merged into it first; a new `WIP-Version`
      heading was added if it had merged before; and the ticket is back to *InProgress* with its
      Resolution cleared.
- [ ] `CHANGELOG.md` has one `## WIP-Version` heading at the top. A marker is used only to force the
      bump, and never on a hotfix (section 4).
- [ ] It has a `### WIP-Build` placeholder and a ticket block with the ticket's exact title, or a `REF`
      block with a UTC token.
- [ ] I built the change locally (section 5).
- [ ] The change and the changelog entry are staged together, I committed through the editor, and I
      checked the drafted message.
- [ ] I pushed, and the ticket's Delivery shows *Pushed*.

**In one line:** ticket, branch, changelog entry, build, commit, push.

---

## Guide 05: Working and Committing

This guide covers the work itself, once a branch exists: the rhythm of working, how to write the changelog,
which documentation to update as you go, how to build and test, how to commit, how to turn a placeholder
into a real ticket, and how to keep the ticket current. The pieces it refers to (tickets, fields, the
changelog) are defined in the guide on project structure, and the steps for starting a branch are in the
guide on starting work.

**How to read it.** Each topic states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

### 1. The rhythm of work

Work goes in small logical steps. Each step has the same shape: change, build, test in proportion, log the
change in the changelog, commit.

- **Rule:** every commit builds. Compiling is done locally by the developer, and nothing else compiles
  the code.
- **Rule:** every commit that changes files adds a build block to the changelog, with at least one ticket
  block or `REF` block (the changelog's rules are in the guide on project structure, section 7.3).
- **Recommendation:** commit when a logical step is complete and verified, not only at the end of the day.
- **Recommendation:** do not mix unrelated changes in one commit.

**Why.** Each commit is a point you can return to, and its build stamp is the evidence of what was tested.
Small commits make a failure traceable to the step that caused it. A commit that mixes unrelated changes
is hard to trace and hard to undo.


---

### 2. Writing changelog entries

#### 2.1 What an entry is

An entry describes the changes to files made in this commit, one block per ticket. The ticket says *why*
the work exists, and the entry says *what changed in the files*.

#### 2.2 How to word a bullet

- Each bullet is one concrete change. It starts with the file or component, then says what changed.
- Add what it was before when that clarifies ("Previously …"), and the reason when it is not obvious from
  the ticket.
- Code, tests and documentation get their own bullets, so a reader can see that all three were handled.

#### 2.3 Rules

- **Rule:** an entry describes changes to files in this commit and nothing else. Settings, tags, branches
  and plans are tracked in tickets.
- **Rule:** each bullet names the file or component and says what changed. "Fixed the bug" and "updated
  files" do not qualify.
- **Rule:** do not repeat the ticket's description in the entry. The ticket says why, and the entry says
  what changed.
- **Rule:** entries of commits already made are not edited, except to replace a placeholder (section 6)
  or to make a critical correction (section 2.5).
- **Recommendation:** write the entry as you make each change, not at commit time.
- **Recommendation:** list code, tests and documentation as separate bullets.
- **Recommendation:** include the previous behaviour when it helps a reader.

**Why.** The changelog is the record someone reads when a problem appears. A specific entry lets them find
the change and see its effect without reading the diff. Leaving earlier entries untouched keeps it a
record of what was written at the time, which is what makes it trustworthy.

**Weak:**

```
#### #204 — Report totals ignore the last day of the month
- Fixed the bug.
- Updated tests.
```

**Good:**

```
#### #204 — Report totals ignore the last day of the month
- report totals: the last day of the month is now included in the sum. Previously entries dated on that
  day were listed but not counted.
- tests: added a test for months of 28, 29, 30 and 31 days.
- user guide: the report totals section now states that the whole month is included.
```

#### 2.4 A change that serves several tickets

- **Rule:** the change is described in full under one ticket, with the others mentioned by number.
- **Rule:** each of the other tickets gets its own block with no details, referring to the one that has
  them.

```
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV (this change also
  covers #205).
#### #205 — Write the user guide for the export feature
- Covered by the change described under #201.
```

**Why.** Each ticket should show up in the changelog, so that it can be traced to a commit, but the change
itself should be written once, so that the entries cannot disagree.

#### 2.5 Correcting an earlier entry

An earlier entry is corrected only when it is critical: it says something wrong, or leaves out something
important, and a reader would be misled. The procedure:

1. **Create a ticket for the correction.** Type *Task*, Area `documentation`. The description says which
   entry is wrong (the version, the build and the ticket), what it says, what is true, why it matters, and
   the exact corrected wording.
2. **Log the correction in the current version.** A new block in the open `WIP-Version` records that a
   correction was made to ticket X in version X, with the details.
3. **Comment on the original ticket,** linking the correction ticket and saying in one line what was wrong.
4. **Correct the old entry,** and include in it a note that it was corrected, naming the correction
   ticket and the date. The corrected block keeps its build stamp but is no longer a verbatim record of
   that commit; the note is what tells a reader so.

The new block in the current version:

```
#### #231 — Correct the changelog entry for #204 in V2.4.1
- Corrected the entry for #204 in V2.4.1 (build 20261005143045): it said the month-end fix covers all
  report types; it covers only the monthly report. The quarterly report problem is tracked in #232.
```

The corrected old entry:

```
#### #204 — Report totals ignore the last day of the month
- report totals: the last day of the month is now included in the sum of the monthly report.
  (Corrected on 2026-10-12 per #231; the original entry said all report types.)
```

The comment on #204:

> The changelog entry for this ticket in V2.4.1 overstated its scope. Corrected in #231 (see the current
> version's entry). The quarterly report problem is tracked in #232.

**Why.** A silent edit would make the record untrustworthy, because a reader could not tell what had been
changed or why. Putting the correction in a ticket, in the current version and in a comment on the
original ticket means it can be found from all three directions, and the note in the old entry tells
anyone who reads only that entry that it was corrected. A correction of the code's behaviour is a Bug, not
a changelog correction.


---

### 3. What to update as you go

#### 3.1 The principle

- **Rule:** the documentation a change affects is updated in the same change, and merged in the same pull
  request.
- **Rule:** new logic comes with tests, written alongside it and not afterwards.
- **Recommendation:** update documentation as you make the change, not at the end.

**Why.** A wiki or readme that is changed together with the code cannot quietly go stale, and tests
written with the logic describe what it was meant to do.

#### 3.2 The checklist

Go through your commit change by change. Each change has one row, and the row lists everything to update
for it. A commit with several changes uses several rows. Items in italics are conditional, and the
condition is given.

| What you changed | Update |
|---|---|
| **Product** (code, design files, product settings) | ☐ Changelog bullet for each file<br>☐ Tests (new or changed logic)<br>☐ Build locally<br>☐ Ticket<br>☐ Wiki page *(if behaviour it describes changed)*<br>☐ Readme *(if setup, build or use changed)*<br>☐ Code comment *(if what it describes changed)*<br>☐ User docs *(if users can see the change)*<br>☐ Dated record in `doc/` *(if it rests on a decision or investigation worth keeping)*<br>☐ Known-limitation ticket *(if one is created or removed)*<br>☐ Wiki known-issues page *(if the limitation is critical or very important)* |
| **Tests** | ☐ Changelog bullet<br>☐ Build and run<br>☐ Ticket<br>☐ Test procedure document *(if what it describes changed)* |
| **Documentation** (readme, wiki, records, comments) | ☐ Changelog bullet<br>☐ Ticket<br>☐ Wiki `Home` and links *(if a page is added, renamed or removed)*<br>☐ Date in the file name *(if it is a record)* |
| **Build, tooling, config files** | ☐ Changelog bullet<br>☐ Build locally<br>☐ Ticket<br>☐ Tests *(if scripts have logic)*<br>☐ Readme *(if setup or build changed)*<br>☐ Readme and wiki variable list *(if people must apply new settings)* |
| **Hooks, automation, process rules** | ☐ Changelog bullet<br>☐ Tests for the scripts<br>☐ Build locally<br>☐ Ticket<br>☐ Try it with a throwaway ticket and branch *(if it writes to the board, the tags or the repository; section 4.4)*<br>☐ Every page that states a changed rule *(if a rule changed)*<br>☐ Readme setup text *(if hook setup changed)*<br>☐ Guides and board setup *(if what the automation reads or writes changed)* |
| **Settings** (repository or board, no file changes) | ☐ Ticket records it, not the changelog<br>☐ Delivery *Implemented* and Version, when the work is in effect<br>☐ The page that states the rule *(if a documented rule changed)* |

The wiki's known-issues page lists only the critical or very important limitations, as a summary. The
ticket is the source of truth and holds every detail. "Ticket" means keeping the ticket current: Progress, comments, and the Size and Risk if they turned out
wrong (see the section on keeping the ticket current). Documentation that you update is itself a change
to a file, so it gets its own bullet in the changelog entry.

**Why.** The list is organised by what you changed, not by what to update, because you know what you
changed and do not yet know what else it affects. One row per change means you never have to combine
rows, and a short checklist is one that gets used.


---

### 4. Building and testing

#### 4.1 Before a commit

- **Rule:** build locally before every commit, and every commit builds. Compiling is done by the
  developer, once, before the commit exists, and nothing else compiles it. For a project with nothing to
  compile, "build" means whatever check shows that the change works, such as a lint, a site build or a
  test run.
- **Rule:** run the existing tests before considering a change done. They must pass.
- **Rule:** new or changed logic comes with tests (section 3).
- **If an existing test fails:** the recommendation is to fix it before committing when your change
  caused it. When it did not, raise a Bug ticket, mention it in your ticket, and do not hide or delete
  the test.

**Why.** There is no continuous integration, so your build and your test run are the only checks the
commit gets.

#### 4.2 Testing

Testing helps, and the higher the risk of a change, the more it helps. How much to test is the
developer's judgment, and recording results is a strong recommendation (section 4.3). After a sync that
brought in changes, recompiling is a rule and retesting is a strong recommendation (see the guide on
branching and merging, section 4.5).

#### 4.3 Recording results

A *recorded result* is the outcome of a test run that you write down: what was run, on which build, and
whether it passed. The routine run before each commit (section 4.1) is not one unless you write it down.

- **Strong recommendation:** record the results of a test run that matters: a review, a verification, a
  regression run for a release, or a run that found a problem. Keep each one in the ticket, as a comment,
  and also store it in the repository. Do not throw a recorded result away.
- **Strong recommendation:** a recorded result names the build it applies to and, where the product has
  one, the compile stamp of what was tested. The build named is the one the tests ran against, which always
  comes before the commit that stores the result.
- **Recommendation:** store each result as a markdown file under `tests/results/`, named
  `<date>_<build>_<subject>.md`, with the date in your own local time (for example `2026-10-06_20261006091200_csv-export.md`), so the files sort
  by date and show the build at a glance.
- **Recommendation:** when a ticket moves to *Review* after a real review, say what was tested and on
  which build.

**Why.** A result with no build cannot be recreated or trusted when a problem appears later. A copy in the
repository outlives the ticket's comments and travels with the code, and you never know in advance which
result will be needed, so none is discarded.

> **In GitHub.** Ticket comments are the issue comments. The result files are ordinary markdown files in
> `tests/results/`, committed like any other change, so they appear in the changelog entry as their own
> bullet.

#### 4.4 Trying an automation change

A change to the hooks, the workflow or a rule the automation applies can only be proved for real by
running it against the board, the tags and the repository. Do that with throwaway material, so that no
real ticket, version or tag is touched.

The steps:

1. **Create a throwaway ticket** titled `DUMMY ...` (what is being tried), with the label `dummy` and a
   Size. The saved views leave it out, so it never mixes with real work.
2. **Work on a throwaway branch** named `dummy-...`, started from the branch under test. It is never
   merged into `main`. If the trial needs a pull request, title it `DUMMY ...` and close it unmerged.
3. **Run the trial** and check what the automation did: the build heading, the ticket's fields, the
   comments, the Alerts.
4. **Close it down.** Close the ticket as *Abandoned* with Resolution *Invalid* and a comment saying what
   was proved. Close any pull request. Retire the branch as abandoned, tagging it first (a short comment in
   the tag such as `dummy-test`). Mark any Version ticket the trial made as *Dropped*, and delete any
   release tag it made.

- **Rule:** a trial uses throwaway tickets, branches and tags only, and never merges into `main`.
- **Recommendation:** leave nothing behind: the trial's tickets are closed, its branches are retired and
  its tags are removed or are the retirement tags of step 4.

**Why.** An automation that writes to shared records has to be tried on shared records, and a mistake
there is visible to everyone. The `dummy` label and the retirement tags keep the trial out of the working
views while leaving a record of what was tried.


---

### 5. The commit

#### 5.1 Staging and the hooks

Stage by logical change, with each change's changelog entry in the same commit. When you commit, two
hooks run: one stamps the build in the staged changelog, and one drafts the commit message from the
entries you wrote.

The hook stamps a `### WIP-Build` placeholder that is already there; it does not add one. So before each
commit that logs a change, put a fresh `### WIP-Build` heading directly under the open `## WIP-Version`
heading, above the builds already stamped, and write that commit's ticket blocks under it. The first
commit of a branch uses the placeholder opened in the guide on starting work; every later commit needs its
own.

The new commit's entries go under the new placeholder, above the build that is already stamped:

```
## WIP-Version
### WIP-Build
#### #201 — Add CSV export to the reports page
- reports page: the Export button now keeps the report's column order.
### Build 20261006091200 (branch csv-export)
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
```

#### 5.2 The message

- **Rule:** no type prefix such as `fix:` or `feat:`.
- **Rule:** the summary line is the ticket's title if the commit covers one ticket, "Multiple tickets" if
  it covers several, or the first bullet (shortened) if it has only a `REF`.
- **Rule:** the body has one block per ticket: a line `Ticket #123 — <title>` followed by its bullets,
  and `REF …` blocks written the same way. The line starts with the word *Ticket*, because git drops any
  line that starts with `#`.
- **Recommendation:** read the draft in the editor. You may reword it and add detail, but the message
  must still name every ticket the commit covers.

**Why.** The content is written once, in the changelog, and the message is generated from it, so the two
cannot disagree. Keeping every ticket named in the message means a commit can be found from its ticket
in the history as well as in the changelog.

One ticket:

```
Report totals ignore the last day of the month

Ticket #204 — Report totals ignore the last day of the month
- report totals: the last day of the month is now included in the sum. Previously entries dated on
  that day were listed but not counted.
- tests: added a test for months of 28, 29, 30 and 31 days.
```

A `REF` only:

```
settings help text: fixed the spelling of "authentication".

REF 20261006091500 — no ticket yet (typo in the settings help text)
- settings help text: fixed the spelling of "authentication".
```

#### 5.3 What not to rewrite

- **Rule:** never squash commits. That includes squashing your own commits before pushing.
- **Rule:** never rebase, including to reorder or rewrite your own commits (see the guide on branching
  and merging, section 4.3).
- **Amending before pushing:** allowed, but the recommendation is to avoid it.
- **Amending after pushing:** allowed, but not recommended, and only if nothing else has built on the
  commit: it has not been merged into `main` or into another branch, `main` has not been merged into your
  branch since, and no new branch has been created from it.
- **Rule:** if you amend, rebuild and retest.

**Why.**

- *No squashing* because every commit carries its build stamp and the tests run against it, and a squash
  replaces them with a commit that was never built or tested as such.
- *No rebasing* for the same reason, and because it rewrites history that others may have built on.
- *Amending is discouraged* because an amended commit has different content from the one that was built
  and tested, while the build stamp keeps the time of the original commit. That is why you rebuild and
  retest if you do it.
- *The limit on amending after a push* because a merge, or a branch created from the commit, still points
  at the old version, so rewriting it leaves those places pointing at a commit that no longer exists on
  your branch.

> **In GitHub.** `git commit` runs the hooks. `git commit --amend` amends the last commit. An amended
> commit that was already pushed needs `git push --force-with-lease`, on your own branch only and never on
> `main`. Squash merging and rebase merging are disabled in the repository settings.


---

### 6. Placeholders and backfill

A placeholder entry (`REF`, or `AUTO-REF` written by the automation) records that a change happened before
its ticket or description existed. It is a loan, and this section is how it is repaid.

#### 6.1 Backfilling a REF

1. **Create the ticket.** Set Type, Description, Size and Area as for any ticket. Origin is *Backfilled*,
   and REF holds the token (or tokens, separated by commas, if one ticket replaces several entries).
2. **Document the change under the ticket,** in one of two ways. Both are allowed.
   - **In place:** replace the placeholder heading in the changelog with `#### #123 — <title>`, keeping
     its bullets.
   - **In a new block (preferred):** add `#### #123 — <title>` to the current version, with a bullet
     `Documents REF <token>: <what changed>`. The old placeholder stays as the honest record that the
     change first appeared without a ticket.
3. **Comment on the ticket** with the token and the version and build where the change happened.
4. **Set Progress to what is true.** Version and Delivery are set by the automation from the REF: it takes
   the version in which the placeholder appears, not the version in which the backfill is documented.

The placeholder in a finalized version:

```
#### REF 20261006091500 — no ticket yet (typo in the settings help text)
- settings help text: fixed the spelling of "authentication".
```

Replaced in place:

```
#### #233 — Fix the spelling of "authentication" in the settings help text
- settings help text: fixed the spelling of "authentication".
```

Or documented in a new block in the current version, leaving the placeholder as it was:

```
#### #233 — Fix the spelling of "authentication" in the settings help text
- Documents REF 20261006091500 (V2.4.1): fixed the spelling of "authentication" in the settings help text.
```

#### 6.2 Triaging an Alert and its AUTO-REF

1. Confirm that the merged result was built and tested.
2. Document what changed, in place or in a new block under the Alert's ticket, as above.
3. Comment on the Alert with what you found.
4. Move it to *Review*; a human completes it.

#### 6.3 Rules

- **Rule:** every `REF` is backfilled.
- **Strong recommendation:** backfill before you open the pull request. Otherwise do it as soon as you
  notice it.
- **Rule:** a backfilled ticket has Origin *Backfilled* and its REF set, so the placeholder can always be
  found from the ticket.
- **Rule:** the automation sets Version and Delivery of a backfilled ticket from its REF, so documenting
  the change in a later version does not give the ticket the wrong version.
- **Rule:** a `REF` counts toward the bump as a change with no Type, so as a mod. If the change is really
  a Feature or an Enhancement, add the `+s` marker to the `WIP-Version` heading when you write it.

**Why.** A placeholder keeps small or urgent work from being slowed down, at the price of a backfill.
Backfilling keeps the history traceable to a real ticket, and the REF field is the link back to what was
written at the time. Backfilling before the pull request means the ticket is documented while the work is
still fresh and before anyone has to ask. Taking Version and Delivery from the REF means the ticket shows
where the work actually shipped, instead of when someone got round to documenting it.


---

### 7. Keeping the ticket current

#### 7.1 What to keep current

| Item | What to do |
|---|---|
| **Progress** | *InProgress* while you work. *Review* when the work is done and ready to merge. Back to *InProgress* if a review fails. You propose *Suspended* or *Abandoned*, and the project owner decides. A human who verified the result sets *Completed*. |
| **Waiting** | Set it when you need someone's input, with a comment saying what is needed and from whom. Clear it when the answer arrives. |
| **Attention** | If the automation raised it on your ticket, read its comment, decide what is true (reopen, leave as it is, correct a field, or abandon), act, and then set *Fine*, or *Acknowledged* if it is handled elsewhere. |
| **Comments** | Record decisions, findings and changes of scope as they happen. The solution and its discussion belong here. |
| **Size** | Correct it when you learn the work is bigger or smaller, and say why in a comment. |
| **Risk** | Revise it before moving the ticket to *Review*. |
| **Work that splits** | If it turns out to be several independent changes, split them into separate tickets. |

#### 7.2 Rules and recommendations

- **Rule:** set Waiting together with a comment, and clear it when answered.
- **Rule:** revise Risk before moving to *Review*.
- **Rule:** *Completed* is set only by a human who verified the result.
- **Recommendation:** update the ticket whenever its state changes, so it tells the truth when you stop
  for the day.
- **Recommendation:** move a ticket to *Review* before the merge, once the work is done and ready to merge.
  The automation then has nothing to change when the version is finalized.
- **Recommendation:** deal with an Attention flag on your ticket when you see it, as set out in the guide
  on issues and the board in practice, section 2.4.
- **Recommendation:** comment on decisions and scope changes as they happen, not afterwards.
- **Recommendation:** when you correct a Size, say why.

**Why.** The board and the tickets are how the team sees the project. A ticket that says "in progress"
when the work is finished, or that hides a decision made in a conversation, makes the next person start
from zero. Moving to *Review* before the merge keeps the order of events simple: the ticket says the work
is done, the pull request lands it, and the version records it.

#### 7.3 Before moving a ticket to Review

- ☐ The changelog entries are complete.
- ☐ The tests that matter and their results are recorded, naming the build (section 4; a strong
  recommendation).
- ☐ The documentation the change affects is updated (section 3).
- ☐ Risk is revised.


---

### 8. Checklist

A one-page summary of the guide. It adds no new rules, and it can be copied into a ticket or a pull
request description. The pull request steps (syncing, the description, merging) are in the guide on
syncing and merging.

**For each commit**

- [ ] Each change in the commit has its row in the "what to update" table, and everything that row lists
      is done (section 3).
- [ ] Changelog entries are specific bullets, one block per ticket. A change serving several tickets is
      described once and referenced from the others (section 2).
- [ ] Earlier entries are untouched, except a placeholder replaced or a critical correction made by the
      procedure (sections 2.5 and 6).
- [ ] Built locally, and the existing tests pass (section 4).
- [ ] Any test result worth keeping is recorded in the ticket and in `tests/results/`, naming the build
      (section 4; a strong recommendation).
- [ ] A fresh `### WIP-Build` was added under the open `## WIP-Version` for this commit's entries.
- [ ] The change and its entry are staged together, committed through the editor, and the drafted message
      names every ticket (section 5).
- [ ] No squash and no rebase. Any amend was allowed under the rule (section 5).

**Before moving a ticket to Review**

- [ ] The changelog entries are complete, the results worth keeping are recorded, the documentation is
      updated, and Risk is revised (section 7).
- [ ] Waiting is set, with a comment, if I need input. Size is corrected if it was wrong.

**Before opening the pull request**

- [ ] Every `REF` is backfilled (section 6).

**In one line:** change, build, test, log, commit, and keep the ticket current.

---

## Guide 06: Syncing and Merging

This guide covers the steps from "my work is done" to "it is on `main`": syncing `main` into your branch,
getting ready to land, opening the pull request, merging, and what happens afterwards. It is a procedure:
each step says what to do and why, and the commands are in the "In GitHub" blocks. The rules and their
reasons are in the guide on branching and merging; the pieces it refers to (tickets, the changelog, pull
requests) are defined in the guide on project structure.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

### 1. Sync `main` into your branch

The steps:

1. **Fetch** and look at what came in from `main`.
2. **Merge `main` into your branch.** Never rebase.
3. **If there are conflicts,** resolve them as an ordinary commit on the branch.
4. **Recompile.** Retest in proportion.
5. **Push.**

#### 1.1 When to sync

- **Rule:** sync before the branch is merged, whether or not git reports a conflict (see the guide on
  branching and merging, section 4.2).
- **No sync is needed when `main` has not moved.** If `main` has no commits your branch lacks, the branch
  is already up to date. Merging it would be a fast-forward in git terms, and there is nothing to bring
  in. Check by fetching and listing what `main` has that your branch does not: if the list is empty, skip
  the sync.
- **Recommendation:** also sync regularly during long work, and periodically for a parked branch.

**Why.** A clean merge only means git found no overlapping text. It does not mean the combined result is
correct. Your branch may rely on something as it stood at your last sync (a value, a setting, how a
function behaves, a resource another part now uses), while `main` has since changed it somewhere else.
Nothing overlaps, so git reports no conflict, yet your code now assumes something that is no longer true.
Syncing before the merge, and rebuilding, brings such mismatches to the surface while you can still fix
them on the branch. This is only one way it can happen; there are others.

#### 1.2 Conflicts and adjustments

- **Rule:** a conflict is resolved on the branch, as an ordinary commit, then built, tested and logged
  there, before the branch reaches `main`.
- **Rule:** if the sync needed a manual resolution, or any adjustment that git did not flag as a
  conflict, log it in the changelog under the ticket you are working on, and put the details in a
  comment on that ticket. With no ticket, use a `REF`. If the branch has no open `WIP-Version` heading at
  that moment (it was merged before), add the heading and a build block in the same commit.
- **Rule:** if `main` moves again after your sync, sync again.
- **Note:** if the ticket has already been pushed and is at *Review* (or *Completed*) when you sync again and log an adjustment, the
  automation sees new work on it and raises *Caution*. That is expected: confirm it was only the sync, and
  set *Fine* (see the guide on issues and the board in practice, section 2.4).
- **Recommendation:** in the entry, say what conflicted and how you resolved it. If it is easy to see what
  came from `main` (a ticket number in the log), name it, but do not go looking for it.

**Why.**

- *On the branch* so the resolution is a deliberate, visible, tested step, and not something done for the
  first time at the moment of landing.
- *Logged* because a resolution changes files, so it needs an entry like any other change, and a problem
  found later often leads back to one.
- *Under the ticket you are working on* because the resolution is a change you made while doing that work,
  and finding which ticket on `main` caused the conflict could take far longer than the resolution did.
  The merge commit points to both parents, so the cause can still be found when it is needed.
- *Sync again if `main` moves* so that a conflict can only appear at a sync, never at the final merge.

```
#### #201 — Add CSV export to the reports page
- Merged `main` into `csv-export` and resolved a conflict in the report query: `main` had renamed the date
  column, and the export now uses the new name. Rebuilt and retested.
```

A sync with no conflict and nothing adjusted needs no entry, because you made no change of your own.

#### 1.3 After syncing

- **Rule:** recompile after a sync that brought in changes.
- **Strong recommendation:** retest in proportion to what came in. When in doubt, even a small doubt,
  retest (see the guide on branching and merging, section 4.5).
- Then push the branch.

> **In GitHub.** `git fetch`, then `git log HEAD..origin/main` to see what came in. If it prints nothing,
> the branch is up to date and the advisory check on the pull request is green. Otherwise
> `git merge origin/main`. The "Update branch" button on a pull request, set to merge, does the same on
> the server; pull the result afterwards. The hooks remind you to recompile when a merge brings in changes
> and to build and test after a manual conflict resolution. Even when git could fast-forward, the
> repository's merge setting still creates a merge commit when the pull request is merged, so the history
> looks the same as for any other merge.

#### 1.4 When a push is rejected

When two people work on the same branch, a push can be rejected because the other person pushed first.

- **Rule:** fetch, merge the remote branch into yours (`origin/<branch>`), and push again. Never rebase and
  never force the push.
- **Rule:** a conflict in that merge is resolved on the branch as in section 1.2, then built and tested
  before the push.
- **Recommendation:** recompile after the merge, and retest in proportion to what the other person
  changed.

**Why.** Rebasing or forcing would rewrite commits the other person has already built on and tested (see
the guide on branching and merging, section 4.3), and would leave their work pointing at commits that no
longer exist.

> **In GitHub.** `git fetch`, then `git merge origin/<branch-name>`. A plain `git pull` does the same
> when git is set to merge on pull (`git config pull.rebase false`).


---

### 2. Get ready to land

#### 2.1 Before you open the pull request

- ☐ **All the work is pushed,** and every commit builds (see the guide on working and committing,
  section 4).
- ☐ **The branch is synced with `main`,** and rebuilt and retested afterwards (section 1). If `main`
  had nothing to bring in, no sync is needed.
- ☐ **The changelog is complete:** one open `WIP-Version` heading, no unstamped `WIP-Build` left, and
  every change logged under a ticket or a `REF`.
- ☐ **Every `REF` is backfilled** (a strong recommendation; guide on working and committing, section 6).
- ☐ **The documentation your changes affect is updated** (guide on working and committing, section 3).
- ☐ **Test results worth keeping are recorded** in the ticket and in `tests/results/`, naming the build
  (a strong recommendation; guide on working and committing, section 4).
- ☐ **The tickets are at *Review*** (or already *Completed*) and their Risk is revised (a
  recommendation; guide on working and committing, section 7).
- ☐ **The Type of each ticket is right.**
- ☐ **The bump marker is deliberate.** The `WIP-Version` heading carries a marker (`+V`, `+s`, `+m`) only
  if you mean to force the bump.

#### 2.2 Rules

- **Rule:** open the pull request only when the branch is ready to land: committed, pushed, synced, built
  and tested.
- **Rule:** the developer decides whether to force the bump, including a major bump (`+V`).

**Why.**

- *Ready first* because the pull request is where the checks and the record are. Opened early, it gives
  them nothing to report on, and a pull request that is open gets read as ready.
- *The Type of each ticket* because the version number is derived from the tickets' Types, so a Feature
  recorded as a Task would be numbered as a small change.
- *A deliberate marker* because a marker overrides the automatic bump for that one version. A major
  version is a judgment about meaning (a redesign or a major capability), and in a small team that trusts
  its developers the person who did the work is best placed to make it.


---

### 3. Open the pull request

The steps:

1. **Open the pull request** from your branch into `main`.
2. **Write the title:** the branch's functional purpose, the way a version heading would read.
3. **Write the description:** paste the changelog entries of the open version, as they are, and add the
   tested build and the sync status.
4. **Check the pasted text** for closing keywords.
5. **Look at the checks.** The advisory check says whether the branch is behind `main`. If it is, go back
   to section 1.

#### 3.1 The description

The description is the changelog entries of the open `WIP-Version`, copied as they are: the ticket headings
with their bullets, details included. Add two lines under them:

- which build was tested, taken from the latest build heading if that is the build you tested, and
- whether and when `main` was synced into the branch, and where any conflict resolution is documented.

```
<paste the open WIP-Version section of the changelog: the ticket headings and their bullets>

**Tested on build** <build>. `main` was merged into the branch on <date>, <with no conflicts / the conflict
is documented in #<number>>.
```

- **Rule:** the description contains the changelog entries copied as they are. If they are too long, the
  ticket numbers alone are the minimum.
- **Rule:** reference tickets by plain number (`#123`). Before opening, check the pasted text for the
  words *Closes*, *Fixes* or *Resolves* followed by a ticket number, and reword them.
- **Rule:** a branch that is merged more than once gets a new pull request each time (see the guide on
  branching and merging, section 5.1).
- **Recommendation:** also state the tested build and the sync, as above.

**Why.**

- *Copy, do not rewrite* because the entries are already written and checked, and rewriting the spirit of
  a change in new words is more likely to introduce an error than to add clarity. The details stay.
- *The tickets are in it* because the headings are the ticket numbers and titles, which is the connection
  needed when a problem appears later: from a version you find its pull request, and from the pull
  request the tickets.
- *No closing keywords* because a closing keyword would close a ticket on merge, and closing is a
  person's step after verification. Pasted bullets can contain such words without anyone meaning them.
- *The build and the sync* because they are the evidence behind the rules about testing and syncing.

A script or an assistant can draft the description the same way: read the open `WIP-Version` section,
paste it, and add the build and sync lines for the developer to review.

> **In GitHub.** Open the pull request from the branch's page or with `gh pr create`. The branch, the
> commits and the checks appear in the pull request automatically, so the branch needs no mention in the
> description. A pull request template in `.github/` can pre-fill the description.


---

### 4. Merge

The steps:

1. **Read the checks.** The advisory check is green when the branch is up to date with `main`. If it is
   red, `main` has moved: go back to section 1 and sync again. If its comment lists a merge in your branch
   with a manual conflict resolution, confirm that the result was built and tested.
2. **Merge with a merge commit.** It is the only method available.
3. **Do not delete the branch from the merge screen.** Retire it later, tagging it first (see the guide on
   releases and hotfixes).
4. **Do not close the tickets.** Closing is a person's step after verification.

#### 4.1 Rules

- **Rule:** if the advisory check is red because the branch is behind `main`, sync again before merging.
- **Rule:** merge with a merge commit. Squash and rebase merging are not used.
- **Rule:** the developer who opened the pull request merges it.
- **Rule:** do not delete the branch when merging. Tag it first, then delete it, when you retire it.

**Why.**

- *A red check means sync again* because it is the warning for the case where `main` moved and something may
  no longer fit. Merging anyway is a bypass: it is allowed, but it is detected and logged as an Alert
  (see the guide on branching and merging, section 6).
- *A merge commit* because it keeps every tested commit as it was.
- *Do not delete the branch at merge* because that would skip the tag, and the tag is what keeps the
  branch's history reachable. You may also not be done with the branch: staged merges and follow-up work
  are normal.
- *Do not close the tickets* because merging puts work on `main` but does not show that it is right.

> **In GitHub.** Use the "Create a merge commit" button, the only one enabled. Leave alone the "Delete
> branch" button that appears after the merge. The repository setting "Automatically delete head
> branches" should be off, so that a merge never removes the branch on its own.


---

### 5. After the merge

#### 5.1 What the automation does

After a merge to `main`, the automation:

- decides the bump from the Types of the tickets, or from the marker if there is one, and renames the open
  `WIP-Version` heading to the real version (with its UTC date and time) in a commit of its own on top of
  the merge;
- for each ticket in the version: advances it to *InProgress* if it was somehow still *ToDo* or *OnDeck* (the
  push normally did that already), sets Delivery to *Merged*, and sets Version, Build and Version#. It never moves a ticket out of *Completed*:
  a ticket verified before the merge stays *Completed*;
- creates the Version ticket, or reuses a planned one, with a generated description, the last build and
  the tickets as sub-issues, and closes it;
- attaches the tickets with Delivery *Implemented* that no Version ticket has yet (section 5.2, item 6);
- raises an Alert if it detects a bypass or finds stale planned versions.

#### 5.2 What to check

1. **Pull `main`** and see that the heading was renamed to the version you expected.
2. **See that the Version ticket exists** and lists your tickets.
3. **See that your tickets show Delivery *Merged*** and the right Version.
4. **If an Alert was raised for your merge,** triage it. It is assigned to you (see the guide on working
   and committing, section 6).
5. **If the board was not updated,** the version is still finalized. The board step is skipped when the
   project token is missing or the hosting service reports an error. Re-run the finalize step, which is safe to
   repeat and skips what is already done, or correct the fields by hand.
6. **If you did work with no file change** (a setting, a secret, a check that was run), set its Delivery
   to *Implemented* and its Version to the version it belongs to. The next finalize attaches it to that
   version's ticket. To attach it at once, for example for a version that is already finalized, run the
   workflow by hand with the dry run off.

#### 5.3 What next

- If the tickets are not verified yet, verify them now. A human moves them from *Review* to *Completed*
  and closes them.
- Decide whether to continue the branch or retire it (see the guide on releases and hotfixes).

#### 5.4 Rules

- **Recommendation:** check the result after the merge, as above.
- **Rule:** a version number is never changed after it is finalized. If the bump was not what you
  intended, note it in a comment on the Version ticket and fix the ticket's Type. The next version
  proceeds normally.
- **Rule:** if you continue on the branch, sync `main` into it first, which brings in the automation's
  commit, and only then open a new `WIP-Version` heading.

**Why.**

- *Check the result* because the automation writes to several places, and a quick look finds a wrong
  version, a missing ticket or a failed board update while it is still fresh.
- *A finalized version number is never changed* because it is already in the history, in tags and in
  other people's work, and changing it would make the record untrustworthy.
- *Sync before a new heading* because the automation's commit renames the heading in the changelog. If you
  open a new heading before you have that commit, the two edits meet in the same file and can conflict.


---

### 6. If you need to bypass

#### 6.1 When it applies

You may merge despite a red check, or push straight to `main` without a pull request. Both are allowed, and
both are detected afterwards (see the guide on branching and merging, section 6.3):

- a direct push, with no pull request;
- a merge that is not identical to its branch's final state;
- a merge that differs from both of its parents;
- file changes with no changelog entries.

#### 6.2 What to do

1. **Do it deliberately,** and say why in the pull request, the commit message or a comment on the ticket.
2. **Expect the Alert.** It is assigned to you, and the automation also writes a placeholder entry in the
   changelog. Triage it promptly (see the guide on working and committing, section 6).
3. **Pull `main` right afterwards, then build and test it.** You skipped the sync that would have caught a
   mismatch, so this is the check you owe.
4. **Never hide it,** for example by editing history. The record is what makes the bypass recoverable.

#### 6.3 Rules

The rules about bypassing, including that a bypass is legitimate when there is a reason and that it is
never hidden, are in the guide on branching and merging, section 6.5. What this guide adds:

- **Recommendation:** after a bypass, build and test `main` at once.

**Why.** The system accepts that rules will sometimes be bypassed, and has a way to recover afterwards,
instead of a wall that gets forced through anyway (see the guide on branching and merging, section 6).
Building and testing `main` straight away is how you make up for the check you skipped.


---

### 7. The branch after the merge

After a merge the branch still exists, and what to do with it is the developer's choice.

| If… | Then |
|---|---|
| more work on the same feature is expected, a follow-up fix is likely, you are merging in stages, or a review failed and the ticket went back to *InProgress* | **Continue.** Sync `main` into the branch first, then open a new `WIP-Version` heading and carry on (see the guide on starting work, section 3.3). New work gets its own tickets. |
| the work is done and nothing more is expected | **Retire it,** tagging it first (see the guide on releases and hotfixes). |
| the work is set aside to resume later | **Suspend it** (see the guide on releases and hotfixes). |
| the work is being dropped | **Abandon it** (see the guide on releases and hotfixes). |

#### 7.1 Rules

- **Recommendation:** do not wait too long to retire a branch whose work is merged (how long is too long
  is in the guide on branching and merging, section 1.5).
- **Recommendation:** if you continue a branch, make that a deliberate choice, not a default.

**Why.** A branch left open and forgotten hides an unmade decision, and it falls behind `main`, which makes
its next merge harder. A deliberate "continue" keeps the history clean, because the new work starts from a
synced branch with its own heading.


---

### 8. Checklist

A one-page summary of the guide. It adds no new rules, and it can be copied into a pull request
description.

**Sync** (section 1)

- [ ] `main` is fetched, and if it has commits my branch lacks, it is merged into my branch (never
      rebased).
- [ ] Any conflict is resolved on the branch, logged under my ticket, with the details in a comment.
- [ ] I recompiled, and retested in proportion.
- [ ] If a push was rejected, I merged `origin/<branch>` and pushed again: no rebase, no force (section 1.4).

**Get ready** (section 2)

- [ ] Every item in the "before you open the pull request" checklist (section 2.1) is done.

**Open the pull request** (section 3)

- [ ] The title is the branch's functional purpose.
- [ ] The description is the open version's changelog entries pasted as they are, plus the tested build
      and the sync line.
- [ ] The pasted text has no *Closes*, *Fixes* or *Resolves* followed by a ticket number.

**Merge** (section 4)

- [ ] The advisory check is green, or I am bypassing deliberately and have said why.
- [ ] I merged with a merge commit, did not delete the branch, and did not close the tickets.

**After the merge** (sections 5 and 7)

- [ ] I pulled `main`: the heading is renamed to the expected version, the Version ticket lists my
      tickets, and they show Delivery *Merged* and the right Version.
- [ ] Any Alert raised for my merge is triaged.
- [ ] I decided whether to continue the branch (syncing `main` first, then a new `WIP-Version`) or retire
      it.

**In one line:** sync, get ready, open the pull request, merge, check.

---

## Guide 07: Issues and the Board in Practice

This guide covers the daily handling of tickets and the board: triaging new tickets, planning, reviewing
and verifying work, suspending and abandoning, handling Alerts, planning ahead with versions, and keeping
the board healthy. It is a procedure: each step says what to do and why. What the tickets and fields are
is defined in the guide on project structure, and what a developer does with a ticket while working is in
the guide on working and committing; this guide does not repeat them.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Roles, and responsible, not necessarily manual.** Developer, project owner and administrator are roles.
One person may hold several, and in a small team they often do. Where this guide names a role, it means
the person responsible; the step may be done by hand, by an assistant, or by a script or command that
person runs, and it is still that person's action.

---

### 1. Triage and planning

Anyone can create a ticket. Triage is what turns a new ticket into something the team can plan.

The steps:

1. **Check for a duplicate.** If there is one, link the two and abandon the new one with Resolution
   *Duplicate*.
2. **Check that it is complete:** a title, a Type, a description with enough detail, and a Size. If
   something is missing, comment, and set Waiting if the creator has to answer.
3. **Set the Priority.** It defaults to *Normal*, and the project owner can change it at any time.
4. **Decide where it goes.**
   - *ToDo*: accepted, not scheduled.
   - *OnDeck*: chosen to be worked on next.
   - *Abandoned*: not going ahead, with a Resolution (*Invalid*, *WontFix*, *Superseded* or *Obsolete*)
     and a comment saying why.
5. **Optionally set a target Version** if the ticket is aimed at a particular version.

#### 1.1 Rules

- **Rule:** triage is done by someone holding the project owner role.
- **Rule:** a ticket does not leave triage without a Type and a Size.
- **Rule:** abandoning a ticket needs a Resolution and a comment.
- **Recommendation:** triage new tickets regularly, so that none sits unlooked-at.

**Why.** Triage keeps the board honest. A ticket without a Type or a Size cannot be planned or numbered
correctly, and a dropped ticket with no reason invites someone to raise it again. Putting triage in one
role means someone is responsible for every new ticket being looked at, instead of everyone assuming
somebody else did.


---

### 2. Working the board

#### 2.1 What to look at, in order

1. **Alerts.** Open tickets of Type *Alert*. Each is *Critical* and is waiting for a person.
2. **Attention.** Tickets with an open flag: *AtRisk*, then *Caution*, then *Watch* (section 2.4).
3. **Waiting.** Tickets marked *Needs input*. Has the answer arrived? If so, clear it. If a ticket has waited
   a long time (the automation flags two weeks), ask again or decide without the answer.
4. **Review.** Tickets awaiting verification. Verify them (section 3).
5. **InProgress.** Yours should tell the truth. A ticket nobody has touched for about a month should be
   updated, suspended or abandoned.
6. **OnDeck.** What is next. Pick one.
7. **ToDo.** Anything new that has not been triaged goes through section 1.

Items 1 to 4 are the things that need a person, and one view, *Health* (section 2.2), lists them together.

#### 2.2 Saved views

The board has five saved views, in this order:

- **All:** every item on the board, test tickets and pull requests included, with all its fields and in
  ticket-number order, with no gap in the numbers, for finding anything and for audit.
- **Backlog:** a board of the tickets at *ToDo*, *OnDeck* and *Suspended*, the most urgent first.
- **Board:** the active work, with the columns *OnDeck*, *InProgress* and *Review* and a row for each Version,
  so you see what each version holds and where each ticket is.
- **Health:** everything that needs a person, or whose fields break a rule: tickets with an open Attention flag,
  tickets marked *Needs input*, tickets at *Review*, open Alerts, and the field-consistency checks of
  section 7.1 (for example *Completed* without Resolution *Done*, or a ticket whose issue is closed at any
  Progress but *Completed* or *Abandoned*). Start a work session here.
- **Versions:** the work tickets grouped by their Version ticket (the group reads "Version 0.7.0"), with Delivery,
  Build and Resolution, to see what each version holds and whether it shipped. Tickets only aimed at a version,
  which have no Version ticket yet, are in a group of their own, ordered by version.

Every view except All leaves out pull requests and test tickets by ending its filter with `is:issue AND -label:dummy`
(see *Ticket fields reference*; the automation puts each pull request on the board so that All has no gaps).
The views are defined in a file, `.github/views.json`, and created by a script, `views.py`, so every project
has the same ones. To change a view, change the file and run the script. Two settings of *All* are made by
hand when it is created, because the API cannot reach them: the sort *Created, ascending* and *Show hierarchy* off
(guide on the new-project bootstrap, section 6). Setting them up is part of
configuring the board, which is the administrator's job.

#### 2.3 Rules

- **Recommendation:** look at the board at the start of a work session, and take Alerts first.
- **Recommendation:** clear *Waiting* as soon as the answer arrives.
- **Recommendation:** keep *InProgress* honest. Update, suspend or abandon a ticket that has had no activity
  for about a month.

**Why.** The order puts the things that are waiting on a person ahead of the things that are merely
planned. An Alert is a warning that a rule was bypassed, and it loses value the longer it sits. A board
that shows false states makes the next person start from zero.

> **In GitHub.** The saved views are views of the project board. A filter can combine fields with `AND`, `OR`
> and parentheses, for example `status:Review OR (type:Alert AND is:open)`. A view's grouping, its board
> columns and rows, and its sorting can only be set when the view is created, and the API cannot sort a new
> view by Created, Updated or Closed, so the script creates a changed view again and then deletes the old
> one (GitHub never deletes the last view of a board).

#### 2.4 Attention flags

What the field is, and when the automation raises it, is in the guide on project structure (section 4.3).
This section is what to do with an open flag.

The steps:

1. **Read the comment** the automation left: why it raised the flag, and for new work, which build.
2. **Decide what is true.**
   - *New work on a finished ticket:* if the new work belongs to the ticket, reopen it (section 4.3). If
     it is a separate piece of work, leave the ticket as it is and create a ticket for the new work. If it
     was only an adjustment from syncing `main` after the ticket reached *Review*, confirm that and set *Fine*.
   - *A stale ticket:* update it, complete it if the work is in fact done and verified, suspend it, or
     abandon it.
   - *A long wait:* ask again, or decide without the answer, and clear Waiting.
   - *A broken field rule:* correct the field.
3. **Act,** and comment on what you decided.
4. **Close the flag.** Set *Fine* if nothing is wrong or you put it right. Set *Acknowledged* if
   something still has to be done and it is handled elsewhere, and say where in the comment: another
   ticket, or this ticket moved back to *ToDo*, *OnDeck*, *InProgress* or *Suspended*.

- **Rule:** whoever holds the ticket decides and closes the flag. For an unassigned ticket, someone
  holding the project owner role does.
- **Rule:** closing a flag comes with a comment, and an *Acknowledged* comment names where the work is
  handled.
- **Recommendation:** close the flag only after deciding. A flag closed without acting is not raised again
  for the same situation, so nothing will remind you.
- **Recommendation:** take the higher levels first, because *Caution* and *AtRisk* mean the board and
  the facts disagree.

**Why.** The automation cannot know what a person meant, so it points and a person decides. Setting
*Fine* or *Acknowledged* is the decision being recorded, and the comment says which and why, so the next
person does not have to ask.


---

### 3. Review and verification

The steps:

1. **Pick a ticket at *Review*.**
2. **Verify it.** Check the ticket's "done when" against the result. Verification can happen before the
   merge, on the build made on the branch (the most common case), or after it, on `main`; either is fine.
   Name the build you verified (the build, and the compile stamp where there is one). Check that the
   changelog entries match what was done, and, where test results were recorded, that they name the build.
3. **Decide the outcome.**
   - **It passes:** set Resolution to *Done* and Progress to *Completed* together, and close the issue.
     Add a comment saying what was verified and on which build.
   - **Its own work is wrong or incomplete:** send it back to *InProgress* with a comment saying what
     failed (see the guide on project structure, section 3.4). Its Delivery stays *Merged*, because the
     code is on `main`; it changes when new work is pushed.
   - **A separate problem, or one found after completion:** create a new *Bug* ticket that mentions the
     original as "introduced by #123".
   - **You cannot tell yet:** set Waiting, with a comment saying what is needed and from whom.

#### 3.1 Rules

- **Rule:** *Completed* is set only by a human who verified the result (see the guide on project
  structure, section 10).
- **Rule:** set Resolution *Done* together with *Completed*, and close the issue then.
- **Recommendation:** have someone other than the author verify, when that is possible. The author
  verifying their own work is acceptable.
- **Recommendation:** write a verification comment naming the build, at least when a real review took
  place. *Review* is sometimes a holding place for work already known to be done, and then a quick
  confirmation is enough.
- **Recommendation:** verify on a build you can name, before or after the merge, and say which build it
  was.

**Why.** Verification is the one step that only a person can take, so what it covered has to be clear from
the ticket afterwards, and a result with no build cannot be trusted later. A second pair of eyes catches
what the author has stopped seeing, which is why it is recommended even though it is not required.


---

### 4. Suspending, abandoning and reopening

#### 4.1 Suspend

Use it when the work will not be addressed soon but is expected back.

1. **Propose it,** with a comment saying why, what is left, and what would be needed to resume. The
   project owner decides.
2. **Set Progress to *Suspended*.** Resolution stays blank, and the issue stays open.
3. **If the ticket has a branch,** suspend the branch too (see the guide on releases and hotfixes,
   section 3).
4. **To resume,** set Progress back to *InProgress* (or *OnDeck*), and recover the branch if it was
   retired (see the guide on starting work, section 3.4).

#### 4.2 Abandon

Use it when the work is not going ahead.

1. **Propose it.** The project owner decides.
2. **Set Resolution** (*Duplicate*, *Invalid*, *WontFix*, *Superseded* or *Obsolete*) and a comment
   linking any related ticket.
3. **Set Progress to *Abandoned*** and close the issue. Clear Waiting.
4. **If the ticket has a branch,** abandon the branch too (see the guide on releases and hotfixes,
   section 3). The automation then sets the tickets' Delivery to *Dropped*.

#### 4.3 Reopen

A *Completed* or *Abandoned* ticket needs more work.

1. **Set Progress back** to *InProgress*, or to *ToDo* or *OnDeck* if it is not started.
2. **Clear Resolution,** and reopen the issue. The automation clears the End date at its next sweep. If
   the automation raised an Attention flag for the new work, set it to *Acknowledged* and say the ticket
   was reopened (section 2.4).
3. **Add a comment** saying why.

#### 4.4 Rules

- **Rule:** suspending needs a comment, and abandoning needs a Resolution and a comment.
- **Rule:** reopening clears Resolution, which you do, and the End date, which the automation does (see the
  guide on project structure, section 4.4).
- **Recommendation:** reopen a ticket only if its own scope is still unmet. For new work related to it,
  create a new ticket and link the two.

**Why.** A reason recorded when the work stops saves anyone from asking again later. Reopening keeps one
ticket as the record of one piece of work, and a new ticket keeps a finished one finished. The same
reasoning decides a failed review: send the ticket back if its own work is at fault, and create a new
ticket for something separate.


---

### 5. Alerts

What an Alert is, and how it is created, is in the guide on project structure (section 5.3). This section
covers who takes it and what to do with it.

#### 5.1 Who takes an Alert

- **A bypass, a merge that landed without changelog entries, or a changelog that could not be read:** the
  Alert is assigned to the person who pushed, who triages it.
- **Stale planned versions:** the Alert starts unassigned. Planned Version tickets belong to the project
  owner role (see the guide on project structure, section 10), so someone holding that role takes it.

#### 5.2 Triage

- **A bypass or a merge without entries:** the steps are in the guide on working and committing,
  section 6.2. Confirm that the result was built and tested, document what changed, comment, and move the
  Alert to *Review* for a human to complete.
- **A changelog that could not be read:** no version was finalized. Correct `CHANGELOG.md` by hand (one
  open `WIP-Version` heading, with at most one marker and no other text), run the finalize step again,
  comment on the Alert with what was wrong, and move it to *Review*.
- **Stale planned versions:** for each Version ticket the Alert lists, either set its Delivery to
  *Dropped* and close it with a comment saying what replaced it, or correct the number if it was a
  mistake. Then move the Alert to *Review*.
- **An Alert raised in error** (a false positive): abandon it with Resolution *Invalid* and a comment
  saying why.

#### 5.3 Moves

An Alert is *Critical* and starts at *ToDo*. Every move is manual: *InProgress* when someone starts,
*Review* when they believe it is handled, *Completed* with Resolution *Done* when a human has verified it.
Shipping a version never moves it. The person who takes it sets its Size and Risk when triaging.

*Done* means that something was done beyond analysing the Alert, for example documenting the change. An
Alert that analysis shows to be wrong is *Invalid*.

#### 5.4 Rules

- **Rule:** the person an Alert is assigned to triages it. An unassigned Alert is taken by someone holding
  the project owner role.
- **Rule:** an Alert raised in error is abandoned with Resolution *Invalid* and a comment.
- **Recommendation:** triage Alerts promptly, before other work.
- **Recommendation:** when an Alert was a false positive, raise a Bug ticket against the automation that
  raised it.

**Why.** An Alert is a record that a rule was bypassed or a number went stale, and its value falls the
longer it sits. Completing a false positive with *Done* would claim that a check was carried out when the
Alert was simply wrong, so it is *Invalid*. Raising a Bug for the false positive stops the same mistake
coming back.


---

### 6. Planning ahead with versions

#### 6.1 Target versions

- A ticket's Version field can aim it at a version (`V2.5.0`) before it ships. Someone holding the project
  owner role sets it.
- When the version ships, the automation overwrites the field with the version that really shipped. A
  ticket aimed at a later version that ships earlier corrects itself.
- A ticket with no target version is fine. It gets its version when it ships.
- A ticket with no file change has nothing for the automation to find in the changelog. When its work is in
  effect, the person sets its Delivery to *Implemented* and its Version to the version it belongs to. The
  automation attaches it to that version's ticket and does not change the field. Leave the Version blank until the
  version is finalized, unless the version already exists: a blank Version gets the version being finalized (or,
  at a scheduled run between two merges, the latest finalized version, which is the version the work was done
  under), and a number you only expect may never exist (the bump is decided at merge). Pure analysis counts
  as a change with no file: set *Implemented*, never leave the Delivery blank on a ticket you complete. If an *Implemented* ticket is
  aimed at a version that was passed (not finalized while a higher version is), the automation raises
  *Caution* on it: set its Version to the version it belongs to, or clear it.

#### 6.2 Planned Version tickets

- **Aim tickets with their Version field and nothing else.** The automation creates the Version ticket
  itself when the version is finalized, so the Version tickets exist in the order the versions shipped.
  Aimed tickets show on the *Board* view (a row for each Version), in the *Backlog*, and in the *Versions*
  view's group of tickets with no Version ticket yet, ordered by Version#.
- **Creating a Version ticket ahead of time is allowed but not recommended.** It would be titled exactly
  `Version 2.5.0`, with Type *Version*, Delivery blank and the issue open, as a place to record what you
  plan. But the *Versions* view orders its groups by the order the Version tickets were created in: a ticket
  made early for a later version (say `Version 2.0.0` while the project is at 1.30.0) would sort ahead of a
  version that ships first (1.31.0, created by the automation when it ships). A planned number is also a guess
  (the bump is decided at merge), so a planned ticket tends to go stale.
- Before the version is finalized a planned ticket is only a plan. Tickets are not attached to it as
  sub-issues ahead of time; the target Version field on each ticket says which version it is aimed at, and
  the automation attaches the tickets when it finalizes the version.
- When a version ships under that number, the automation reuses a planned ticket (it matches by the exact
  title). Otherwise it creates one.
- **If the planned version will not happen** under that number, mark it *Dropped*, close it, and comment
  what replaced it. Move its tickets' target Version to the new one.
- The automation's stale-versions Alert tells you when a planned number has been passed (section 5).

#### 6.3 Rules

- **Rule:** target versions and planned Version tickets are set by someone holding the project owner role.
- **Recommendation:** aim tickets with the Version field, and do not create Version tickets ahead of time
  (section 6.2).
- **Rule:** a planned Version ticket, if you create one, is titled exactly `Version X.Y.Z`, so that the
  automation can reuse it.
- **Rule:** tickets are not attached to a Version ticket as sub-issues before it is finalized.
- **Rule:** a planned version that will not happen is marked *Dropped* and closed with a comment saying
  what replaced it.
- **Recommendation:** plan ahead where you can. It is the ideal and not a requirement, so a ticket without a
  target version, or a version that was never planned, is normal.
- **Recommendation:** name a version number only when you are confident of it, and otherwise aim at "the
  next version".

**Why.** Planning ahead gives the team a shared picture of what is coming. But the number is a guess: the
bump is decided at merge from the tickets' Types and any marker, so a version planned as 2.5.0 may ship as
2.4.2 or 3.0.0, and every planned number is something to clean up if it turns out wrong. Keeping the
tickets unattached until finalize means a plan never has to be undone, and the Version field on each ticket
already carries the aim. The Version tickets are left to the automation, because the *Versions* view lists them
in creation order, which is then the order the versions shipped.


---

### 7. Housekeeping

#### 7.1 A regular board review

Go through these regularly. Each item has its own rule elsewhere, so this section is the list. The
automation's Attention flag already catches stale tickets, long waits and broken field rules (section
2.4). This review is for the rest, and for tickets whose flag was closed without a decision.

1. **Stale tickets:** no activity for about a month at *InProgress* or *OnDeck*, or a week at *Review*. Update,
   suspend or abandon them, or verify the ones at *Review* (sections 2 and 3).
2. **Long-suspended tickets:** resume them or abandon them (the automation flags six months).
3. **Tickets that have waited a long time** (the automation flags two weeks): ask again, or decide
   without the answer.
4. **Field consistency,** using the cross-field rules (see the guide on project structure, section 4.4). The
   *Health* view lists the tickets that break them:
   - *Completed* has Resolution *Done*, and *Abandoned* has a reason.
   - Open tickets have no Resolution and no End date.
   - Waiting is only on open tickets.
   - A backfilled ticket has its REF.
   - The issue is closed only at *Completed* or *Abandoned*.
   - A *Completed* work ticket has a Delivery, and a ticket with Delivery *Merged*, *Implemented* or *Released*
     has a Version.
5. **Labels:** the Area list and `dummy` are fixed. Remove strays and duplicates.
6. **Planned Version tickets:** closed if dropped, and none left behind for versions already passed.
7. **Branches:** merged branches not yet retired (a week or two up to about a month), and parked branches
   about a month old (suspend or abandon them).
8. **Placeholders:** search the changelog for `REF` entries that have not been backfilled, and backfill
   them.
9. **Board configuration:** the fields and their values match the standard.

#### 7.2 Rules

- **Rule:** someone holding the project owner role runs the board review, and someone holding the
  administrator role checks the board configuration.
- **Recommendation:** do the board review regularly.
- **Recommendation:** start the review in the *Health* view, which lists the consistency checks of item 4
  together with the tickets that need a person, so that the review is a quick look.

**Why.** Each rule is applied by a person at the moment they act, and nothing checks the whole board. The
review is where drift is caught: a ticket left in a state that stopped being true, a field that no longer
agrees with another, or a branch nobody decided about. A suspension that never ends is an unmade decision,
and so is a branch parked for months.

> **In GitHub.** The *Health* view is one filter that joins the checks with `OR`, for example
> `(status:Completed no:resolution) OR (is:open has:resolution)`.


---

### 8. Checklist

A one-page summary of the guide. It adds no new rules.

**Triage a new ticket** (section 1)

- [ ] I checked for a duplicate. If there was one, I linked it and abandoned the new ticket with
      Resolution *Duplicate*.
- [ ] It has a Type, a description with enough detail, and a Size, or I commented and set Waiting.
- [ ] Priority is set (it defaults to *Normal*).
- [ ] It is in the right place: *ToDo*, *OnDeck*, or *Abandoned* with a Resolution and a comment.
- [ ] A target Version is set if it is aimed at one.

**Each work session** (section 2)

- [ ] I looked at the Health view first, taking Alerts first, then Attention flags, Waiting and Review, and then
      InProgress, OnDeck and ToDo.
- [ ] Each open Attention flag on my tickets was decided and closed with *Fine* or *Acknowledged* and a
      comment, and not just dismissed.
- [ ] I cleared Waiting where the answer arrived.

**Verify a ticket** (section 3)

- [ ] I verified on a named build, before or after the merge.
- [ ] It passes: Resolution *Done* and Progress *Completed* set together, the issue closed, and a comment
      naming the build.
- [ ] Before I set *Completed*, the Delivery is set (*Merged* if files changed, *Implemented* if none did, even for
      pure analysis).
- [ ] It fails: back to *InProgress* with a comment, or a new *Bug* linked as "introduced by #123".

**Suspend, abandon or reopen** (section 4)

- [ ] Suspend: a comment, Progress *Suspended*, and the branch suspended too if there is one.
- [ ] Abandon: a Resolution and a comment, Progress *Abandoned*, the issue closed, Waiting cleared, and
      the branch abandoned too if there is one.
- [ ] Reopen: Progress set back, Resolution cleared, the issue reopened, and a comment.

**Alerts and planning** (sections 5 and 6)

- [ ] An Alert assigned to me is triaged before other work. A false positive is abandoned with *Invalid*.
- [ ] Tickets are aimed with their Version field. If I did create a planned Version ticket, it is titled
      exactly `Version X.Y.Z`, has no tickets attached before it is finalized, and is marked *Dropped* and
      closed if it will not happen.

**Housekeeping** (section 7)

- [ ] The regular board review is done.

**In one line:** triage, work the board, verify, close the loop, review.

---

## Guide 08: Releases, Hotfixes and Retiring Branches

This guide covers the steps that end or branch off the normal flow: declaring a version a release, fixing a
version that has already been released, and retiring a branch. It is a procedure: each step says what to do
and why, and the commands are in the "In GitHub" blocks. The rules and their reasons are in the guide on
branching and merging; the pieces it refers to (tickets, tags, the Version ticket) are defined in the guide
on project structure.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

### 1. Cut a release

A release is a version on `main` that is deliberately declared a release. Every merge makes a version, but
only some versions become releases.

The steps:

1. **Decide which version.** It must already be finalized on `main`.
2. **Verify it** (section 1.1).
3. **Run the release step** with that version. By default it is the latest on `main`.
4. **Check the result.** The tag `released/V<major>.<sub>.<mod>` exists on the commit where that version was
   finalized. The Version ticket shows Delivery *Released* and a comment with the date and the tag. Every
   ticket merged or implemented up to that version shows *Released*, unless newer work on it has been
   pushed since.
5. **Tell the project owner** that the release was made.

#### 1.1 Rules

- **Rule:** the developer decides which versions are releases, and tells the project owner. The remote
  automation carries it out.
- **Rule:** verify the version before releasing it: run the regression checks on it.
- **Strong recommendation:** record the results, naming the build (see the guide on working and
  committing, section 4). The regression checks are an ordinary Task: its result file is committed like
  any change and lands in a later version, and the result names the version and build that were tested.
- **Rule:** a release marks as *Released* only the tickets whose Delivery is *Merged* or *Implemented* and
  whose version is at or below the released one. A ticket with newer work pushed keeps *Pushed*.
- **Recommendation:** have the version's tickets completed before releasing it.
- **Rule:** the tag goes on the commit where the version was finalized, not simply on the current tip of
  `main`.
- **Rule:** only a finalized version can be released, and each version has at most one release tag.
- **A mistaken release tag may be deleted and redone.** A release tag is only an indicator that makes a
  version easy to find. Every change that lands on `main` produces its own version, so a version is the
  version whatever any tag says, and a tag on the wrong commit, or on a version that was not meant to be a
  release, harms nothing once it is removed. After deleting it, put the Version ticket and its tickets
  back to *Merged*.

**Why.** A release is a statement that a version is fit to be used, so it has to be verified, and the tag
has to point at exactly what was verified; tagging the tip would be wrong whenever `main` has moved on.
Because the version identifies a position in the history by itself, the tag can be corrected freely.

> **In GitHub.** The release step is a manually started run of the repository's workflow, given the
> version to release. The tag appears under the repository's tags, and a mistaken tag is removed with
> `git push origin --delete <tag-name>` and `git tag -d <tag-name>`; other clones drop it with
> `git fetch --prune --prune-tags`.


---

### 2. Hotfix

A hotfix fixes a version that has already been released, without carrying anything that has happened on
`main` since. The rules are in the guide on branching and merging (section 1.3); this section is the
procedure.

#### 2.1 Start

1. **Create a ticket for the fix.** Usually Type *Bug*, with a Priority of *Critical* or *Urgent*. Assign it
   to yourself and set it to *InProgress* (see the guide on starting work, section 2).
2. **Create the hotfix branch from the release tag,** not from `main` (for a further hotfix of the same
   release, from the previous hotfix's tag). Name it
   `hotfix-v<major>-<sub>-<mod>-<description>` (see the guide on starting work, section 3.2).
3. **Add the changelog heading:** a `## WIP-Version` at the top, with no marker, since markers are not
   allowed on a hotfix branch.
4. **Work as usual:** change, build, test, log, commit, push (see the guide on working and committing).
5. **Tell the project owner** that a hotfix has been started.

#### 2.2 Finish

6. **Verify the hotfix** the same way as any release (section 1.1).
7. **Run the hotfix-finalize step** with the explicit version, for example `V1.25.0-HF1`. It renames the
   heading to that version, tags `released/V1.25.0-HF1`, creates the Version ticket, and sets the tickets'
   Delivery straight to *Released*, because a hotfix is never merged and so skips *Merged*.
8. **Check the result:** the heading, the tag, the Version ticket and the tickets.
9. **Tell the project owner** that the hotfix has been released.

#### 2.3 Forward-port and retire

10. **Reintroduce the fix into `main`** as an ordinary branch and pull request, with its own ticket. The
    ticket's description says it is a forward-port of the hotfix ticket, so the link between them is kept in
    the tickets, not in the changelog. It gets whatever version `main` is at.
11. **Delete the hotfix branch.** Its release tag already keeps its history, so no retirement tag is
    added.

#### 2.4 Rules

The rules about what a hotfix is (it starts from a release tag and is never merged, its version lineage
and the single-digit limit on hotfix numbers, how the fix reaches `main`, and that a finished hotfix
branch is deleted without a retirement tag) are in the guide on branching and merging, sections 1.3
and 2.2. The rules for the procedure are these:

- **Rule:** the hotfix version is given explicitly when it is finished, because there is nothing to
  compute it from.
- **Rule:** verify the hotfix before finishing it, as for any release.
- **Rule:** the developer starts and finishes a hotfix, and tells the project owner when it is started and
  when it is released.
- **Recommendation:** keep a hotfix to the fix itself, and nothing else.

**Why.**

- *From the tag, never merged* because a hotfix patches exactly what was released, so it must start from
  exactly that and never carry unrelated work. Its own numbering lineage cannot collide with a version
  `main` has produced or will produce.
- *Developer-driven* because a critical problem in a released version is urgent, and waiting for approval
  would cost time the situation does not have. The project owner is told so that nothing happens without
  their knowledge.
- *A separate forward-port* because the fix still has to be part of `main`'s history, through the normal
  flow, with its own ticket, verification and version.


---

### 3. Retire a branch

Retiring means recording where a branch ended up with a tag and then deleting the branch. The rules are in
the guide on branching and merging (section 1.5); this section is the procedure.

The steps:

1. **Choose the outcome.**
   - **Archived:** the work is done and merged.
   - **Suspended:** the work is set aside and expected to return.
   - **Abandoned:** the work is discarded.
2. **Check the branch.**
   - For *archived*, confirm that all its commits are reachable from `main`. If they are not, it is not
     archived: suspend it or abandon it.
   - For *suspended* or *abandoned*, close any open pull request with a comment saying why.
3. **Update the tickets.**
   - *Archived:* nothing to change.
   - *Suspended:* move the tickets to *Suspended* with a comment. The developer proposes, and the project
     owner decides.
   - *Abandoned:* move the tickets to *Abandoned* with a Resolution and a comment. The automation also sets
     their Delivery to *Dropped*.
4. **Run the retire step** with the branch name and the outcome, and confirm by typing the branch name
   again. It tags the branch's last commit and then deletes the branch.
5. **Check the result.** The tag exists, the branch is gone, and the tickets show what you expect. Delete
   your local copy of the branch.

#### 3.1 Rules

- **Rule:** tag first, delete second. The one exception is a finished hotfix branch, whose release tag is
  already its record (section 2).
- **Rule:** the tag is named `<outcome>/<yyyy-mm-dd>_<branch>[_<comment>]`, using the UTC date of the
  branch's last commit.
- **Rule:** if a tag with that name already exists, add a short comment to make it unique. The retire step
  refuses a name that already exists.
- **Rule:** *archived* is only for a branch whose work is fully merged.
- **Recommendation:** for *suspended* and *abandoned*, add a short comment to the tag name saying why, in
  kebab-case. A longer note goes in an annotated tag.
- **To start again from a suspended or abandoned branch,** see the guide on starting work, section 3.4.

**Why.** A tag costs nothing and keeps the branch's history reachable. Three outcomes let a later reader
answer "was this merged", "can we pick it back up" and "did we decide to drop it". Typing the branch name
again before deleting guards against retiring the wrong branch.

> **In GitHub.** The retire step is a manually started run of the repository's workflow, given the
> branch, the outcome and the confirmation. By hand: `git tag <tag> origin/<branch>`,
> `git push origin <tag>`, `git push origin --delete <branch>`, then `git branch -d <branch>` for your
> local copy.


---

### 4. Checklist

A one-page summary of the guide. It adds no new rules.

**Cut a release** (section 1)

- [ ] The version is finalized on `main`.
- [ ] It is verified: the regression checks are run, and the results are recorded with the build (a
      strong recommendation).
- [ ] Its tickets are completed (a recommendation).
- [ ] The release step is run with that version, and the project owner is told.
- [ ] The tag is on the commit where the version was finalized, the Version ticket shows *Released* with
      its comment, and the tickets show *Released*.
- [ ] If the release was a mistake: the tag is deleted, and the Version ticket and its tickets are back to
      *Merged*.

**Hotfix** (section 2)

- [ ] A ticket exists for the fix (Type *Bug*, Priority *Critical* or *Urgent*), assigned to me and
      *InProgress*.
- [ ] The branch is created from the release tag and named `hotfix-v…`.
- [ ] The changelog has a `WIP-Version` heading with no marker.
- [ ] I worked as usual, and the project owner is told it started.
- [ ] The hotfix is verified, and the hotfix-finalize step was run with the explicit version (for example
      `V1.25.0-HF1`).
- [ ] I checked the heading, the tag, the Version ticket and the tickets, and the project owner is told it
      is released.
- [ ] The fix is forward-ported to `main` as its own ticket and pull request, linked to the hotfix ticket.
- [ ] The hotfix branch is deleted; its release tag keeps its history.

**Retire a branch** (section 3)

- [ ] The outcome is chosen: archived, suspended or abandoned.
- [ ] For *archived*, all commits are reachable from `main`. For *suspended* or *abandoned*, any open pull
      request is closed with a comment.
- [ ] The tickets are updated: *Suspended*, or *Abandoned* with a Resolution, and a comment.
- [ ] The retire step is run (tag first, then delete) and confirmed.
- [ ] The tag exists, the branch is gone, and my local copy is deleted.

**In one line:** release, hotfix, retire: verify, tag, check.

---

## Guide 09: Working with an AI Assistant

This guide covers how an AI assistant takes part in the process: what it may do on its own, what it must
ask first, how it handles tickets, the changelog, commits and documentation, and how a project instructs
it. It is written so that an assistant can follow it as instructions, and so that the person it works for
knows what to expect. The pieces it refers to (tickets, fields, the changelog) are defined in the guide on
project structure, and the steps it follows are in the other guides.

**How to read it.** Each topic states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Roles, and responsible, not necessarily manual.** Developer, project owner and administrator are roles.
One person may hold several. Anything a person is responsible for can be done by an assistant, by hand, or
by a script or command the person runs, and it is still that person's action.

---

### 1. What an assistant is in this process

An assistant is an AI that works for a person (a developer, the project owner or the administrator) and
does steps on their behalf. The person stays responsible for the result (see the guide on project
structure, section 10).

- **Rule:** the assistant follows the same rules as the person it acts for. Nothing in these guides is
  relaxed for an assistant.
- **Rule:** a few things are never the assistant's own decision. Verifying a ticket, which means setting
  *Completed* and *Done*, is the main one, because it means a person has looked.
- **Rule:** the assistant asks before any action that is hard to reverse or that leaves the project
  (section 3).
- **Rule:** the assistant works from these guides and their checklists. The checklist at the end of each
  guide is its step list.
- **Recommendation:** keep the project's instructions for assistants in a file in the repository that is
  shared by everyone, so that every developer's assistant gets the same rules (section 6). Personal
  preferences can stay in a personal file.

**Why.** An assistant is fast and literal, which is useful, and it makes the person's judgment more
important, not less. The guides are written to be followed step by step, so an assistant can follow them
exactly, and the limits are what keep that safe. A shared instructions file means the project does not
behave differently depending on whose assistant did the work.


---

### 2. What an assistant does without asking

#### 2.1 Routine work

- **Read-only operations of any kind,** including every read-only git operation (status, log, diff, show,
  blame, fetch, listing branches, viewing remotes) and browsing history, pull requests and tickets.
- **Writing and editing files inside the project.**
- **Running scripts, tests and builds inside the project.**
- **Following the procedures in these guides** for the person's task: creating a branch, writing
  changelog entries, staging, drafting a commit message, drafting a pull request description.
- **Syncing `main` into the person's own work branch,** as in the guide on syncing and merging (section
  1), and then recompiling. A sync changes only that branch, and nothing is shared until a push.
- **Writing or updating tests alongside new logic,** and running the existing tests before calling a
  change done.
- **Setting a ticket to *Review*** when its work is done (section 4).

How the project's own tools and services are run during development is part of the development process,
not of this one, and is not covered here.

- **Rule:** for routine work like this, the assistant acts and does not ask for confirmation.

**Why.** Asking about routine steps slows everything down, and people who are asked too often start
approving without reading, so the questions that matter get lost among the ones that do not.

#### 2.2 How it reports back

- **Recommendation:** be concise. Say what was done in a short summary, without narrating every step or
  recapping everything.
- **Rule:** report outcomes faithfully. If a test failed, say so, with the output. If a step was skipped,
  say that. When something is done and verified, say so plainly, without hedging.

**Why.** The person is responsible for the result, so they have to be able to rely on what the assistant
says it did.


---

### 3. What an assistant asks about first

#### 3.1 Ask first

- **Any git operation that records or shares work, or can lose it:** commit, push, merge, reset, a
  checkout that discards changes, branch or tag deletion, and force operations. A *merge* here means a
  merge into `main` or into any shared branch. For a commit, the assistant proposes the commit message and
  waits for explicit approval. Creating or switching a branch, fetching, and syncing `main` into the
  person's own work branch are routine and need no approval.
- **Risky or out-of-scope actions:** deleting files, changing anything outside the project, changing
  system or global settings, installing global packages, running commands that touch other projects, and
  anything destructive or hard to reverse.
- **Anything outward-facing:** sending content to an external service publishes it, and it may be cached
  or indexed even if it is deleted later.
- **A major version bump:** adding a `+V` marker.
- **Real decisions:** when there are several valid approaches, an ambiguous requirement or trade-offs, the
  assistant presents the options with a recommendation and asks which. It does not silently pick one, and
  it does not ask a plain yes or no in place of the choice.

#### 3.2 Rules

- **Rule:** the assistant commits, pushes and merges only with explicit approval.
- **Rule:** the assistant asks before risky, out-of-scope or outward-facing actions.
- **Rule:** an approval covers what was asked and no more, and it does not carry over to the next time.
  The exception is a kind of action the person has authorized durably.
- **Rule:** a durable authorization is recorded in the shared instructions file (section 6), for example
  "you may push my work branches", so that it is written down and can be withdrawn.
- **Rule:** a durable authorization may cover commits and pushes on the person's own work branches. It
  never covers anything on `main`, tags, releases, hotfix finalize,
  deleting or retiring branches, force pushes or skipping hooks: those are decided each time.
- **Rule:** for a real decision, the assistant presents the options, recommends one, and asks.
- **Rule:** the assistant never bypasses a rule on its own initiative: no skipping hooks, no force push,
  no direct push to `main`. A bypass is a deliberate decision of the person (see the guide on branching
  and merging, section 6).

**Why.** These are the actions that are hard to take back or visible to others, so they need a person's
go-ahead each time, and an approval for one thing is not an approval for the next. Writing a durable
authorization down means it is a decision someone made and can see, and not an assumption that grew. A
bypass is a decision the person has to own, because the Alert it creates is in their name.


---

### 4. Tickets and the board

#### 4.1 What an assistant may and may not set

| Field or action | The assistant |
|---|---|
| Progress up to *Review* | may set it, for the person it acts for. Sets *Review* when the work is done. |
| *Completed*, Resolution *Done*, closing a ticket | never. A person verifies (section 1). It may add a comment with its findings, when asked. |
| Delivery, Build, Version#, the dates | never by hand. The automation sets them. The one exception is Delivery *Implemented*, with the Version it belongs to, on a ticket with no file change: it may set that for the person it acts for, when the work is in effect. |
| Size on a ticket it creates | always sets one. |
| Size on someone else's ticket | says so if it looks wrong, and does not change it. |
| Priority | proposes it. The project owner role sets it. |
| Assignee | the person it acts for. |
| Attention | never raises a flag, and sets *Fine* or *Acknowledged* only when asked, because that records a decision. It may read the comment and propose what to do. |

#### 4.2 Writing to tickets and documents, and authorship

- **Rule:** an assistant writes to the tracker (tickets and comments) or to a shared document outside the
  files of the task only when the person has asked it to, with the design settled in chat first. Files in
  the repository are changed as part of the task the person gave (section 2). The one routine exception
  is setting a ticket to *Review* when its work is done.
- **Rule:** authorship belongs to the person the assistant acts for. The assistant never names itself, or
  the tool it runs on, in a ticket, a comment, a commit message, a code comment, a file, the changelog or
  any other project artifact, unless it has been told to.
- **Rule:** one ticket covers one thing. The assistant never bundles independent changes in one ticket.
- **Rule:** the assistant may set *Review* when work is done, and never *Completed*.
- **Rule:** the assistant creates a ticket with a Size and a clear description.
- **Recommendation:** a ticket body does not repeat what the platform already records, such as who created
  it and when.

**Why.**

- *Only when asked* because a ticket or document is shared: others read it, and a draft that was never
  agreed should not land there.
- *Authorship to the person* because the person is responsible for the work, and a project record that
  names its tools is noise to everyone who reads it later.
- *One ticket per thing* because a ticket that bundles independent things cannot be verified or numbered
  correctly.
- *Stopping short of *Completed** because verification is the one step that needs a person.


---

### 5. The changelog, commits and documentation

#### 5.1 The changelog

The assistant writes entries as it makes each change, following the guide on working and committing
(section 2): specific bullets, one block per ticket, and nothing but changes to files.

- **Rule:** the changelog contains real changes and critical notes only. No placeholders about status,
  such as "no changes yet" or "not committed", and no commentary about the process.
- **Rule:** the assistant opens the `WIP-Version` heading when work starts (see the guide on starting
  work, section 4). It adds a marker (`+V`, `+s` or `+m`) only when told to, and asks first for a major
  bump.

#### 5.2 Commits

- **Rule:** the assistant writes the commit message in the format of the guide on working and committing
  (section 5.2), derived from the entries it wrote, and proposes it. It commits only after explicit
  approval (section 3).
- **Rule:** the assistant builds locally and runs the existing tests before proposing a commit (see the
  guide on working and committing, section 4), and states plainly if anything failed.
- **Rule:** the assistant does not skip hooks, squash, rebase, or amend a pushed commit on its own
  initiative.

#### 5.3 Documentation

- **Rule:** the assistant updates what its change affects, using the checklist in the guide on working
  and committing (section 3), in the same change, and writes tests alongside new logic.
- **Recommendation:** list the documentation it updated as separate bullets in the changelog entry.

**Why.** An assistant that follows the same changelog and commit rules produces the same record a person
would, so the history reads as one. Asking for approval on the commit keeps the person in charge of what
enters the history. Keeping status commentary out of the changelog keeps it a record of changes, which is
what it is for. Using the same message format the hook would draft means the message is not written
twice.


---

### 6. Instructing an assistant

#### 6.1 Where the instructions live

- **Rule:** the project keeps one shared instructions file for assistants in the repository, named
  `AGENTS.md` and placed at the repository root. It is versioned and changed through the normal flow, like
  any other file. Everyone's assistant reads it.
- **Recommendation:** personal preferences stay in a personal file that is not committed.

#### 6.2 What goes in it

The file points to the guides and records only what is specific to the project. It does not repeat the
rules, because a copy can drift from the guide.

- where the process guides are published,
- how to build and test the project,
- which roles are held by whom,
- the durable authorizations, each with its date and who gave it (section 3),
- anything the assistant must not touch.

#### 6.3 A starter text

```
# Instructions for assistants

Follow the process guides: <where they are published>.
Work from the checklist at the end of each guide.

This project
- Build: <command>. Tests: <command>.
- Roles: <who holds developer, project owner and administrator>.
- Durable authorizations: <none, or a list: each with the date and who gave it>.
- Out of bounds: <anything the assistant must not touch>.
```

#### 6.4 Rules

- **Rule:** a durable authorization is written in the file with its date and who gave it, and is removed to
  withdraw it.
- **Recommendation:** keep the file short and pointing to the guides.

**Why.** One shared file means the project behaves the same whoever's assistant did the work. A short file
is one people actually keep up to date, and an authorization written down with a date and a name is a
decision that someone made and can see, and can take back.

#### 6.5 A starter text for personal preferences

Optional. A personal file holds how one person likes to work with an assistant, across projects. It is not
committed, and it never overrides the shared file or the rules in these guides; where they differ, the
shared file and the guides win.

```
# Preferences (personal)

Communication
- <how short or detailed the replies should be; whether to summarise at the end>

Autonomy
- <what to do without asking; what to always ask about first>

Tools and environment
- <how the local environment is set up, and what must never be started, stopped or installed by the assistant>

Style
- <rules about wording in code comments, messages and documents>
```

> **In GitHub.** The file is `AGENTS.md` at the repository root, which many assistant tools look for on
> their own. Personal preferences go in a separate file that is listed in the ignore file.


---

### 7. Checklist

A one-page summary of the guide. It adds no new rules.

**Setup** (section 6)

- [ ] The repository has a shared `AGENTS.md` pointing to the guides, with the build and test commands, the
      roles, any durable authorizations and what is out of bounds.
- [ ] Personal preferences are in a separate uncommitted file.

**Without asking** (section 2)

- [ ] Routine work was done without asking: read-only operations, edits inside the project, scripts,
      tests and builds, the guides' procedures (including syncing `main` into the person's own work
      branch), tests with new logic, and *Review* when work is done.
- [ ] The report is concise and faithful: test failures are stated with their output, and skipped steps
      are named.

**Asked first** (section 3)

- [ ] Commit, push, merge and other state-changing git operations only with explicit approval, and the
      commit message proposed first. Syncing `main` into the person's own work branch is routine.
- [ ] Risky, out-of-scope and outward-facing actions were asked about. An approval covered only what was
      asked, and any durable authorization is written in `AGENTS.md`.
- [ ] A real decision was put as options with a recommendation, and asked.
- [ ] No rule was bypassed on the assistant's own initiative (no skipped hooks, no force push, no direct
      push to `main`), and a major bump was asked about.

**Tickets and the board** (section 4)

- [ ] *Review* was set when the work was done. *Completed*, *Done* and closing were left to a person, and
      Delivery (apart from *Implemented* on a ticket with no file change), Build, Version# and the dates
      were left to the automation.
- [ ] Tickets and documents were written to only when asked. A ticket the assistant created has a Size,
      the Priority is proposed, and the assignee is the person it acts for. A Size that looks wrong on
      someone else's ticket was reported, not changed.
- [ ] One ticket covers one thing, authorship is the person's, and the assistant did not name itself
      anywhere.

**Changelog, commits and documentation** (section 5)

- [ ] Changelog entries are real changes only. The `WIP-Version` heading was opened at the start, and a
      marker only when told.
- [ ] The build was run and the tests run before a commit was proposed, and the message is in the standard
      format, built from the entries.
- [ ] The documentation was updated by the checklist, with tests alongside new logic.

**In one line:** act on routine work, ask about the rest, leave verification to a person, never name
itself.

---

## Guide 10: New-Project Bootstrap

This guide is the checklist for applying the standard to a new repository: the files and folders, the
automation, the repository and board settings, the issue types and labels, the first version, and a trial
run that proves the setup works. Most of it is work for the administrator role. The pieces it refers to
(the structure, tickets, fields, the changelog) are defined in the guide on project structure, and the
rules about versions and branches are in the guide on branching and merging.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Roles, and responsible, not necessarily manual.** Developer, project owner and administrator are roles.
One person may hold several, and in a small team they often do. Where this guide names a role, it means
the person responsible; the step may be done by hand, by an assistant, or by a script or command that
person runs, and it is still that person's action.

---

### 1. Create the repository and its structure

- **Rule:** a new project has the locations of the guide on project structure (section 2.1), under those
  names: the readme, `CHANGELOG.md`, `doc/` with `doc/wiki/`, `tests/` if it has code or scripts,
  `.githooks/`, `.github/`, the ignore file, `.gitattributes` and `AGENTS.md`.
- **Rule:** `.gitattributes` contains the line `* text=auto eol=lf`, so the changelog, the hooks and the
  scripts keep Unix line endings on every platform (see project structure, section 2.2).
- **Rule:** the changelog starts with a title line and no version heading. The first merge to `main`
  produces version `V0.1.0`: it is not a small change, and it is not a release (section 7).
- **Rule:** the readme says what the project is and how to set it up, including the one command that
  activates the hooks.
- **Recommendation:** copy the structure from an existing project that already follows the standard, or
  from a template repository, instead of creating it by hand.

**Why.** Fixed names mean a new project starts looking like every other one, and anyone can open it and
know where to look. Starting the changelog with no version gives the first merge a clean `V0.1.0`, which
is the honest description of a project's first version: something exists, and nothing has been released.

> **In GitHub.** Create the repository, then add the files and folders listed above. A template
> repository that already has them, and the automation and settings, is the natural way to start a
> project this way.


---

### 2. Install the automation

#### 2.1 What it is made of

- **The local hooks,** in `.githooks/`: three small entry scripts and one shared script that stamps the
  build, drafts the commit message and warns. They need a runtime (here Python 3).
- **The remote workflow,** `.github/workflows/versioning.yml`, and its logic in `.github/scripts/`, with
  unit tests under `tests/`. It includes the scheduled run, three times a day (see project structure,
  section 2.3).
- **The schedule re-enabler,** `.github/workflows/reenable-schedule.yml` and its script: GitHub switches a
  scheduled workflow off after 60 days without activity in the repository, and this one, which has no
  schedule of its own, switches it back on at the next push or on request.
- **The saved views,** `.github/views.json` and the script `.github/scripts/views.py` that creates them
  (section 6).
- **The pull request template,** in `.github/`.
- **Optionally,** a workflow that copies the wiki pages to the hosting wiki.

#### 2.2 The steps

1. **Copy the automation files** from the standard, unchanged.
2. **Keep the hook scripts executable** (on Linux the executable bit has to be committed, or git ignores
   them).
3. **Activate the hooks** with the one command in the readme.
4. **Run the automation's tests** locally.
5. **Confirm the workflow is enabled,** with its schedule, and declares the permissions it needs in its
   own file: write access to contents, issues and pull requests. The re-enabler declares its own, narrower
   permission (write access to actions).
6. **Run the preflight** (section 2.3) once the project token (section 4) and the board (section 6) exist.

#### 2.3 The preflight

The preflight is the first thing the automation does, on every run and on request. It checks, before
anything else:

1. that it can **reach the repository** and has the permissions it needs;
2. that the **project token** exists and works;
3. which **board belongs to the repository**: it identifies the board from the repository and stores its
   number in a repository variable, so that nothing needs the number typed in;
4. that the board has **the fields and values** the automation needs.

When a check fails, the automation says exactly which one and why, and skips the steps that depend on it.
The version is still finalized, and the board can be corrected afterwards. If the repository has no board,
or more than one, it stops at step 3 and asks the administrator to say which.

#### 2.4 Keeping in step with the standard

- A **manifest file** in the project names the version of the standard it follows, and lists a hash (a
  fingerprint) of each automation file as it is in that version.
- A **check script** compares the project's files with the manifest and reports each as unchanged, edited
  locally, or from an older version.
- To update a project, copy the new files from the standard, replace the manifest, and run the check.

#### 2.5 Rules

- **Rule:** the automation is copied unchanged from the standard. The project's own values are never
  written into its files: the board is identified by the preflight and stored in a repository variable.
- **Rule:** the automation's tests are part of the repository and are run before any change to it (see the
  guide on working and committing, section 3).
- **Rule:** the preflight runs first, before any other step of the automation.
- **Recommendation:** when the standard's automation changes, copy the new version into the project and run
  the check script, and run the check when unsure whether the files still match.
- **Recommendation:** keep the actions the workflows use (`actions/checkout`) on a release built for the
  runtime the hosting service currently supports. A run that warns that an action targets a deprecated
  runtime is the sign to move: change the version in every workflow file in one ticket, and prove the steps
  that push to git (they rely on the credentials that checkout leaves in the clone).

**Why.** If every project edits its own copy, the copies drift apart and none of them matches the guides.
Keeping project values out of the files, and checking the files against a manifest, makes drift visible.
The preflight turns a vague failure later ("the board did not update") into a clear one at the start.

> **In GitHub.** The board is a GitHub Project, linked to the repository. Its number is stored in a
> repository variable. The manifest is a file in `.github/`, and the check script sits beside the
> automation's scripts.


---

### 3. Repository settings

#### 3.1 The settings

- **Merge methods:** only *merge commit* is allowed. Squash merging and rebase merging are disabled.
- **Automatically delete head branches:** off.
- **Default branch:** `main`.
- **Branch protection on `main`,** where the plan offers it: require a pull request before merging, and
  require the branch to be up to date. Leave the administrator bypass open (do not tick "do not allow
  bypassing the above settings").
- **Actions:** enabled. The workflow declares the permissions it needs (write access to contents, issues and
  pull requests) in its own file, so the repository's default token permission may stay read-only, and an
  organization may require it to be.
- **Issues and projects:** enabled, and the board is linked to the repository.
- **Wiki:** enabled and initialized (by creating a first page) if the wiki sync is used. It may not be
  offered for private repositories on every plan.
- **Collaborators and roles:** the administrator role has admin access, and developers have write access.

#### 3.2 Rules

- **Rule:** only merge commits are allowed, and head branches are not deleted automatically.
- **Rule:** the default branch is `main`, Actions is enabled, and the workflow declares the permissions it
  needs.
- **Rule:** the board is linked to the repository, so that the preflight can identify it.
- **Rule:** the preflight also reads these settings and reports any that do not match.
- **Recommendation:** use branch protection where it is available, with the administrator bypass left open.

**Why.**

- *Merge commits only* keeps every tested commit as it was.
- *No automatic branch deletion* keeps the rule that a branch is tagged first and deleted second.
- *The administrator bypass stays open* because a bypass is allowed, with an Alert as its record (see the
  guide on branching and merging, section 6).
- *The board linked to the repository* is how the automation finds it.
- *The preflight checks the settings* so that this part of the bootstrap is verified and not just trusted,
  and so that a setting changed later is noticed.

> **In GitHub.** The merge methods and the head-branch setting are under the repository's general
> settings, in the pull request section. Branch protection is under branches or rules. The default
> token permission is under Actions, in general settings, and an organization policy may fix it to read-only. The board is linked from the project's settings or
> from the repository's projects tab.


---

### 4. The project token

#### 4.1 What it is and why it is needed

The automation writes to the board: it sets Delivery, Version, Build, the dates and the Attention flags,
advances a ticket from *ToDo* or *OnDeck* to *InProgress*, and it creates and closes Version tickets. The credential a workflow gets by default cannot write to an organization's board,
so the project keeps its own token, stored as a secret. The same token lets the preflight store the board's
number in a repository variable. Without it the automation still versions, and only the board steps are
skipped, with a clear message.

#### 4.2 The steps

1. **Create the token** under an account that has access to the board and administrator access to the
   repository. At present that is a classic personal access token with the `project` and `repo` scopes. A
   fine-grained token can replace it once it covers the same needs.
2. **Store it as a repository secret** named `PROJECT_TOKEN`.
3. **Note when it expires** and renew it before then.
4. **Run the preflight** to check that it works.

#### 4.3 Rules

- **Rule:** the token is stored only as a secret. It never goes in a file, a ticket, a comment, a commit or
  a chat, and an assistant never reads or prints it.
- **Rule:** the token belongs to an account holding the administrator role.
- **Rule:** a lost or exposed token is revoked and replaced at once.
- **Rule:** the preflight reads the token's expiry date and warns when it is close to expiring.
- **Recommendation:** give the token an expiry, and record when it expires so it is renewed in time.
- **Recommendation:** give it only the access the automation needs.

**Why.** A token that can write to the repository and the board is a powerful credential, so where it is
kept and who owns it matter more than how convenient it is. An expiry limits the damage if it leaks, and
the preflight's warning means the board does not stop updating without notice.

> **In GitHub.** The token is created under the account's developer settings. The secret is added under the
> repository's settings, in the secrets section for Actions, with the name `PROJECT_TOKEN`.


---

### 5. Issue types and labels

#### 5.1 Issue types

- **Rule:** the eight issue types exist, with these names: *Feature*, *Enhancement*, *Change*, *Bug*,
  *Refactor*, *Task*, *Version* and *Alert*. Each carries its short definition from the *Ticket fields
  reference* as its description.
- **Prerequisite:** the repository belongs to an organization, because issue types are an organization
  feature.

They are set up once, by the administrator, for the organization.

#### 5.2 Labels

- **Rule:** the labels are exactly the 14 Area labels: `requirements`, `research`, `design`,
  `implementation`, `assembly`, `testing`, `analysis`, `debugging`, `documentation`, `tool`, `process`,
  `config`, `content` and `build`, plus the marker label `dummy` for throwaway tickets made to test the
  automation (see the *Ticket fields reference*). There are no other labels.
- **Rule:** each label carries its meaning from the *Ticket fields reference* as its description, so the
  meaning shows wherever the label is used.
- **Rule:** the labels a new repository starts with that are not on this list (for example `bug`,
  `enhancement`, `duplicate`, `invalid`, `question`, `wontfix`, `good first issue`, `help wanted` and
  `accessibility`; the set changes over time) are deleted. `documentation` stays, because it is on the list.
  After deleting, check that exactly the 14 Area labels and `dummy` remain.
- **Recommendation:** create the labels with a script, so that every project gets the same list.

**Why.**

- The Type, Resolution, Waiting and Origin fields replace what those default labels were used for, so
  keeping them would record the same fact twice.
- A fixed list is the same in every project, so filtering and reporting by Area works across all of them.
- Allowing only the Area labels, and `dummy` as the one marker, keeps the list from growing into a second,
  unmanaged classification.

> **In GitHub.** Issue types are under the organization's settings, in the planning section. Labels are
> under the repository's issues, in the labels page, and can be created in bulk with the command line.


---

### 6. The board

#### 6.1 What to create

A project board linked to the repository, with these fields. The meaning of each value is in the *Ticket
fields reference*.

| Field | Kind | Values |
|---|---|---|
| Status | single select | ToDo, OnDeck, InProgress, Review, Completed, Suspended, Abandoned |
| Origin | single select | Backfilled, Backdated |
| REF | text | |
| Waiting | single select | Needs input |
| Attention | single select | Fine (green), Acknowledged (purple), Watch (yellow), Caution (orange), AtRisk (red) |
| Resolution | single select | Done, Duplicate, Invalid, WontFix, Superseded, Obsolete |
| Delivery | single select | Committed, Pushed, Merged, Implemented, Released, Dropped |
| Priority | single select | Critical, Urgent, High, Normal, Low, Wishlist |
| Size | single select | XS, S, M, L, XL |
| Risk | single select | 1 Very low, 2 Low, 3 Medium, 4 High, 5 Very high |
| Version | text | |
| Build | text | |
| Version# | number | |
| Start date, End date | date | |

Type is the issue type and Area is labels, so neither is a board field. Every field above is a kind that a
script can create.

**Saved views:** All, Backlog, Board, Health and Versions (see the guide on issues and the board in practice,
section 2). They are defined in `.github/views.json` and created with `.github/scripts/views.py`, which is a dry
run until it is given `--apply` and needs the project token; run it once the fields exist.

**Two settings of the *All* view are made by hand, once, when the views are created,** because the API cannot
reach them: sort it by *Created, ascending* (ticket-number order), and turn off *Show hierarchy*, so that tickets
are not listed inside their Version ticket and the list is flat. The script prints a reminder of them at the end of
every run, and a view that is created again loses them, so make them again.

#### 6.2 Rules

- **Rule:** the board has exactly these fields with these values. The built-in Status values of a new
  board are replaced with the ones above.
- **Rule:** Build is a text field, not a number, because a build stamp is too large for a number
  field.
- **Rule:** the board is linked to the repository, and the preflight checks the fields and their values.
- **Rule:** the saved views are the ones in `.github/views.json`, created by `views.py`, and a view is changed
  by changing the file and running the script again.
- **Recommendation:** create the fields with a script, or start from a template board that already has
  them, so that every project gets the same board.

**Why.** The automation reads and writes these fields by name, so a board that differs breaks it, and a
build stamp stored in a number field is rejected by the hosting service.

> **In GitHub.** The board is a GitHub Project owned by the organization and linked to the repository. The
> fields are added in the project's settings, and the saved views are views of the project. A new board has
> one default view, and GitHub never deletes a board's last view, so the script creates the new views first and
> then deletes the default one (`--delete-unlisted`).


---

### 7. The first version and the roles

#### 7.1 The first version

- The changelog starts with a title line and no version heading (section 1).
- The first change to `main` goes through the normal flow: a branch with a `WIP-Version` heading and its
  entries, and a pull request. Its merge produces version `V0.1.0`. It is not a small change and it is not
  a release, so there is no `released/` tag.
- Versions below 1.0.0 are the project's early life. Moving to `V1.0.0` is a deliberate decision, made with
  the `+V` marker on a later version.

#### 7.2 The roles

- **Rule:** the project records who holds each role (developer, project owner and administrator) in
  `AGENTS.md`, so that assistants and people alike know.
- **Rule:** the administrator role has administrator access to the repository and holds the project token.
  Developers have write access. The project owner role triages the board.
- One person may hold several roles, and in a small team usually does.

#### 7.3 Rules

- **Rule:** the first merge is a real change, logged and merged by pull request like any other, so that
  the first version comes from the normal flow.
- **Recommendation:** make that first change the initial structure of the project.

**Why.** A first version that comes from the normal flow proves the flow works, and it avoids a bypass
Alert on the very first push. An empty repository starts with a single commit made by the hosting service,
and everything after it follows the process. Recording the roles at the start avoids anyone guessing later
who decides what.


---

### 8. Prove the setup

A full trial through the real repository would use up the first version: the first merge produces
`V0.1.0`, so a trial would become the project's first version, and it would leave test tickets and tags to
clean up. So the setup is proved in two levels, neither of which leaves anything behind.

#### 8.1 Level 1: without side effects

1. **Run the preflight.** It confirms the repository, the project token, the board and its fields, and the
   repository settings.
2. **Run the automation's tests.**
3. **Run the finalize step in dry-run mode.** It prints every write it would make, such as the heading
   rename, the ticket updates and the Version ticket, without making any.
4. **Test the hooks with a throwaway commit** on a local branch that is never pushed. Check that the build
   is stamped, that the message is drafted, and that the warnings appear. Then delete the branch.

#### 8.2 Level 2: the first real merge

The first real change (the initial structure, by pull request) is the live proof. After it merges, check it
as in the guide on syncing and merging (section 5.2): the heading is renamed to `V0.1.0`, the Version ticket
exists and lists the tickets, and the tickets show Delivery *Merged*.

#### 8.3 Rules

- **Recommendation:** later changes to the automation are tried the same way, with throwaway tickets and
  branches (see the guide on working and committing, section 4.4), never with real tickets.
- **Rule:** run level 1 before the first real change, and fix every failure it reports.
- **Rule:** check the result of the first merge, as in the guide on syncing and merging (section 5.2).
- **Recommendation:** if something fails on the first real merge, correct the board by hand and fix the
  cause. The version number stays as it is.

**Why.** Level 1 finds nearly every setup mistake with nothing to clean up, and the first merge shows what
only a live run can: whether the automation really writes to the board. Keeping the trial out of the real
repository means the first version is a real one.

> **In GitHub.** The finalize step has a dry-run mode that prints every write instead of making it. The
> preflight is the automation's own first step and can also be started on request from the repository's
> Actions page.


---

### 9. Checklist

A one-page summary of the guide. It adds no new rules.

**Structure** (section 1)

- [ ] The locations exist under the standard names, including `.gitattributes` with
      `* text=auto eol=lf`. The changelog has a title and no version, and the readme explains the setup and
      the command that activates the hooks.

**Automation** (section 2)

- [ ] The files are copied unchanged, the hook scripts are executable and activated, the tests pass, the
      workflow is enabled with its schedule and its permissions, the schedule re-enabler is in place, and
      the manifest is in place and the check passes.

**Repository settings** (section 3)

- [ ] Only merge commits are allowed, and head branches are not deleted automatically.
- [ ] The default branch is `main`, Actions is enabled with the workflow declaring its permissions, and
      issues and projects are enabled with the board linked.
- [ ] The wiki is initialized if it is used. Branch protection is on if the plan offers it, with the
      administrator bypass left open. Access matches the roles.

**The project token** (section 4)

- [ ] It is created under an administrator account with the `project` and `repo` scopes, and stored as
      `PROJECT_TOKEN`. Its expiry is recorded, and it is nowhere else.

**Issue types and labels** (section 5)

- [ ] The eight issue types exist with their descriptions.
- [ ] The 14 Area labels and `dummy` exist with their descriptions, and the default labels not on the list
      are deleted.

**The board** (section 6)

- [ ] The fields and values are exactly the standard's, Build is text, and the built-in Status values are
      replaced.
- [ ] The saved views of `.github/views.json` exist (All, Backlog, Board, Health, Versions) and `views.py`
      reports them up to date.
- [ ] On the All view, the sort is *Created, ascending* and *Show hierarchy* is off (both by hand).

**The first version and the roles** (section 7)

- [ ] The first change goes by pull request (the initial structure).
- [ ] The roles are recorded in `AGENTS.md`.

**Proof** (section 8)

- [ ] The preflight reports no problems, the tests pass, the dry-run finalize looks right, and a throwaway
      commit shows the hooks working.
- [ ] After the first merge: the heading is `V0.1.0`, the Version ticket lists the tickets, and the tickets
      show Delivery *Merged*.

**In one line:** structure, automation, settings, token, labels, board, roles, proof.

---

## Appendix A: Cheat sheet, the daily flow

The whole flow on one page, from starting work to a verified result. Each step names the guide section that
explains it. It adds no new rules.

### Once per clone

- [ ] Clone the repository, follow the readme's setup, and activate the hooks (*Starting work*, section 1).

### Start

1. **Find or create the ticket.** Search first. A new ticket needs a Title, Type, Description and Size, or
   start with a `REF` (*Starting work*, section 2).
2. **Assign it to yourself and set it to *InProgress*.**
3. **Update `main` and create the branch** from it: kebab-case, no `/`. A hotfix starts from the release tag
   (*Starting work*, section 3).
4. **Open the changelog entry:** a `## WIP-Version` heading, a `### WIP-Build` placeholder, and the ticket
   block with the ticket's exact title (*Starting work*, section 4).

### Work

5. **Change, build, test, log, commit.** Build locally before every commit, add a fresh `### WIP-Build`
   under the open version for each commit, log each change as a specific bullet, and commit through the editor so the message is drafted from the changelog (*Working and
   committing*, sections 1, 2, 4 and 5).
6. **Update what the change affects:** find the row for each change in the checklist (*Working and
   committing*, section 3).
7. **Keep the ticket current:** Progress, Waiting, comments, Size and Risk (*Working and committing*,
   section 7).
8. **Push.** Delivery becomes *Pushed* (*Starting work*, section 5).

### Land

9. **Sync `main` into the branch** by merging, never by rebasing. Recompile, and retest in proportion
   (*Syncing and merging*, section 1).
10. **Get ready:** tickets at *Review* with Risk revised, every `REF` backfilled (strongly recommended), test results worth keeping recorded
    (strongly recommended), documentation updated (*Syncing and merging*, section 2).
11. **Open the pull request:** a title that states the purpose, and a description that pastes the open
    version's changelog entries plus the tested build and the sync line (*Syncing and merging*, section 3).
12. **Merge with a merge commit.** Do not delete the branch and do not close the tickets (*Syncing and
    merging*, section 4).

### After

13. **Pull `main` and check:** the heading is renamed to the expected version, the Version ticket lists your
    tickets, and they show Delivery *Merged* (*Syncing and merging*, section 5).
14. **Triage any Alert** assigned to you (*Issues and the board in practice*, section 5), and decide any
    Attention flag on your tickets (*Issues and the board in practice*, section 2.4).
15. **Verify** (a person), before or after the merge: set Resolution *Done* and Progress *Completed*
    together, and close the issue
    (*Issues and the board in practice*, section 3).
16. **Continue the branch or retire it** (*Syncing and merging*, section 7; *Releases, hotfixes and retiring
    branches*, section 3).

### Never

- Never rebase, squash, or amend a commit that others have built on.
- Never use a closing keyword (*Closes*, *Fixes*, *Resolves*) in a pull request.
- Never edit an earlier changelog entry, except to replace a placeholder or to correct a critical mistake.
- Never commit without building.
- Never bypass a rule silently: say why, and expect the Alert.

**In one line:** ticket, branch, entry, build, commit, push, sync, pull request, merge, check, verify.

---

## Appendix B: Cheat sheet, if this then that

Situations, what to do, and where to read more. It adds no new rules. "Branching" means the guide on
branching and merging.

### While working

| If… | Then… | See |
|---|---|---|
| I changed something and have no ticket | Start a `REF` block with a UTC token, and backfill it before the pull request. | Starting work, section 4; Working and committing, section 6 |
| a change serves several tickets | Describe it in full under one, mention the others, and give each of the others a block that points to it. | Working and committing, section 2.4 |
| the hook did not stamp my commit, or I skipped the hooks | The automation fills in the build heading with the commit's hash and adds a note. Skipping is allowed but not hidden. | Starting work, section 5.1 |
| an existing test fails and it is not my change | Raise a Bug ticket, mention it in my ticket, and do not hide or delete the test. | Working and committing, section 4 |
| an earlier changelog entry is critically wrong | Create a correction ticket, log it in the current version, comment on the original ticket, and correct the old entry with a note. | Working and committing, section 2.5 |
| I need an answer before I can go on | Set Waiting with a comment saying what is needed and from whom. | Working and committing, section 7 |
| the work is bigger or smaller than its Size | Correct the Size and say why in a comment. | Working and committing, section 7 |

### Landing

| If… | Then… | See |
|---|---|---|
| my branch is behind `main` | Merge `main` into it, recompile, and retest in proportion. | Syncing and merging, section 1 |
| `main` has nothing my branch lacks | No sync is needed. | Syncing and merging, section 1.1 |
| I got a conflict while syncing | Resolve it on the branch, log it under my ticket, put the details in a comment, and rebuild and retest. | Syncing and merging, section 1.2 |
| `main` moved after my sync | Sync again. | Syncing and merging, section 1.2 |
| my push was rejected because someone else pushed to the branch | Fetch and merge `origin/<branch>`, resolve any conflict on the branch, rebuild, push. Never rebase or force. | Syncing and merging, section 1.4 |
| I want to force a different version bump | Add `+V`, `+s` or `+m` after `WIP-Version` (never on a hotfix). | Branching, section 3.3 |
| the advisory check is red | Sync again before merging. | Syncing and merging, section 4 |
| I need to bypass a rule | Do it deliberately, say why, expect the Alert, then pull `main` and build and test it. | Syncing and merging, section 6 |
| the version came out wrong | Note it on the Version ticket and fix the ticket's Type. The number is never changed. | Syncing and merging, section 5.4 |
| the board was not updated after the merge | Re-run the finalize step or correct the fields by hand. | Syncing and merging, section 5.2 |

### Tickets

| If… | Then… | See |
|---|---|---|
| a review fails and the ticket's own work is wrong | Send it back to *InProgress* with a comment. | Project structure, section 3.4 |
| a review finds a separate problem | Create a new Bug that mentions the original as "introduced by #123". | Project structure, section 3.4 |
| a ticket needs more work after it is *Completed* | Reopen it only if its own scope is unmet. Otherwise create a new ticket and link the two. | Issues and the board in practice, section 4.3 |
| work is set aside to resume later | Suspend the ticket, with a comment, and the branch too. | Issues and the board in practice, section 4.1 |
| work is being dropped | Abandon it with a Resolution and a comment, and the branch too. | Issues and the board in practice, section 4.2 |
| an Alert is assigned to me | Triage it before other work. | Issues and the board in practice, section 5 |
| the automation flagged my ticket (*Watch*, *Caution* or *AtRisk*) | Read its comment, decide, act, and set *Fine*, or *Acknowledged* if it is handled elsewhere. | Issues and the board in practice, section 2.4 |
| an Alert was raised in error | Abandon it with Resolution *Invalid* and a comment, and raise a Bug against the automation. | Issues and the board in practice, section 5 |
| a planned version will not happen | Mark it *Dropped*, close it, and comment what replaced it. | Issues and the board in practice, section 6 |

### Branches and releases

| If… | Then… | See |
|---|---|---|
| my branch is merged and the work is done | Retire it, tagging it first (archived). | Releases, hotfixes and retiring branches, section 3 |
| a hotfix is finished and released | Delete the hotfix branch: its release tag keeps its history. | Releases, hotfixes and retiring branches, section 2 |
| I want to keep working on a merged branch | Sync `main` into it first, then open a new `WIP-Version` heading. | Starting work, section 3.3 |
| I want to restart a suspended or abandoned branch | Recreate it from its tag, and sync `main` first. | Starting work, section 3.4 |
| a critical problem is found in a released version | Start a hotfix from the release tag. | Releases, hotfixes and retiring branches, section 2 |
| I want to declare a version a release | Verify it, run the release step, and tell the project owner. | Releases, hotfixes and retiring branches, section 1 |
| a release was declared by mistake | Delete the tag and put the Version ticket and its tickets back to *Merged*. | Releases, hotfixes and retiring branches, section 1.1 |

### Assistants and new projects

| If… | Then… | See |
|---|---|---|
| I am an assistant and the action is risky, outward-facing, or a commit, push or merge into `main` or a shared branch | Ask first, and propose the commit message. Syncing `main` into the person's own branch is routine. | Working with an assistant, section 3 |
| I am an assistant and there is a real choice to make | Present the options with a recommendation and ask. | Working with an assistant, section 3 |
| I am starting a new project | Follow the bootstrap checklist. | New-project bootstrap, section 9 |

---

## Appendix C: Ticket fields reference

Every ticket field with its values, what they mean, who sets them and when. The idea behind each field,
and the rules that tie the fields together, are in section 4 of *Project structure*. How the fields work
together over a ticket's life is in *Appendix E: Ticket model*.

**Where each field lives (GitHub).** Type is the native issue type, Area is a set of labels, and every
other field is a board field.

---

### Type

One value per ticket. Says what sort of ticket it is and why the change is made.

| Value | Meaning | Version bump |
|---|---|---|
| **Feature** | New capability that did not exist before. | sub |
| **Enhancement** | An improvement to something that already works: better performance, smarter behavior, easier use. | sub |
| **Change** | A change to existing behavior that is neither an improvement nor a fix: a new default, a different threshold, an adjustment someone asked for. | mod |
| **Bug** | Something that behaves differently from what was intended, and the fix for it. | mod |
| **Refactor** | Internal restructuring with no change in what the product does. | mod |
| **Task** | Work that does not change the product's behavior: testing, analyzing, building, releasing, writing documentation, and creating a new tool. | mod |
| **Version** | Bookkeeping ticket for one version. It does no work and never counts toward a bump. | none |
| **Alert** | An automatic check that needs a person to review something, such as a detected bypass or a stale planned version. It never counts toward a bump. | none |

Set by a person when the ticket is created; the automation sets it on Version and Alert tickets.

### Area

Several values per ticket. Says what kind of work the ticket involves. Descriptive only: it never affects
version numbers or any automation. At least one is suggested on a work ticket; none is allowed.

| Value | Meaning |
|---|---|
| `requirements` | Working out what is needed, with the people who need it. |
| `research` | Investigating options or unknowns: technologies, parts, approaches. |
| `design` | Deciding how it will be built, before building it (software, hardware, mechanical). |
| `implementation` | Producing the thing itself: code, circuit, enclosure, configuration of the product. |
| `assembly` | Putting physical parts together: electronics, mechanical parts, enclosures. |
| `testing` | Unit, functional and acceptance or QA testing. |
| `analysis` | Examining existing behaviour or data to understand it, without necessarily fixing it. |
| `debugging` | Finding and fixing the cause of a fault. |
| `documentation` | Wiki, readme, guides, comments and other written documentation. |
| `tool` | Developer tooling and scripts that support the work. |
| `process` | How the team works: git, changelog, versioning, hooks, the board, repository settings. |
| `config` | Settings that tune how the product behaves: feature flags, pin assignments, intervals. |
| `content` | Data the product or its tests use: test fixtures, sample data, lookup tables, a database seed. |
| `build` | Build system, toolchain, compiling and releasing. |

The list is the same for every project. Adding a value is a change to the standard, not something a
project does on its own. Set by a person.

### The `dummy` label

Not an Area. A marker for a throwaway ticket or Version ticket made to test the automation (a trial of a
new step, a test of a rule). It is the only label besides the 14 Area labels.

| Label | Meaning |
|---|---|
| `dummy` | A throwaway ticket or version made to test the automation; left out of the board's working views. |

Set by a person when the test ticket is created. A test ticket is titled `DUMMY ...` and is closed as
*Abandoned*, with Resolution *Invalid*, when the test is over. Every saved view of the board except All excludes the
label (`-label:dummy`), so test tickets never appear among real work. It never affects version numbers or
any automation, and it is not part of Area.

### Origin and REF

**Origin** is blank for a ticket created in the normal flow.

| Value | Meaning | Example |
|---|---|---|
| *(blank)* | Created before or while the work was done. | Most tickets. |
| **Backfilled** | Created after the work was done, to replace a ticket-less placeholder in the changelog. | A quick fix logged as a placeholder and ticketed afterwards. |
| **Backdated** | Created to document history from before the process existed. | Tickets written when a project adopted the ticket system, covering earlier development. |

**REF** is a text field. For a Backfilled ticket it holds the placeholder token or tokens (separated by
commas, if one ticket replaces several entries) from the changelog. Blank otherwise. Both are set by a
person.

### Progress (Status)

Where the work is.

| Value | Meaning | Who sets it |
|---|---|---|
| **ToDo** | Accepted, not scheduled. | the person creating the ticket |
| **OnDeck** | Chosen to be worked on next. | a person |
| **InProgress** | Work has started. | a person; the automation also moves a ticket here when code for it is pushed (or merged) and it was still *ToDo* or *OnDeck* |
| **Review** | The developer (or an assistant) believes the work is done and wants it checked. May be a real review or a formality. | a person, never the automation |
| **Completed** | A human has verified the result. | a human only |
| **Suspended** | Set aside, expected to resume. | a person |
| **Abandoned** | Dropped, not expected to return. | a person |

The path is *ToDo, OnDeck, InProgress, Review, Completed*. *Suspended* and *Abandoned* are exits from any
open state. What the automation may and may not do to Progress, and when the issue is closed, is set out in
*Project structure*, section 4.3; what an assistant may set is in *Working with an AI assistant*,
section 4.1.

### Waiting

Blank by default.

| Value | Meaning |
|---|---|
| **Needs input** | The ticket is waiting for someone's feedback, an answer to a question, or a verification. |

Set by a person together with a comment that says what is needed and from whom. When it is cleared is in
*Project structure*, section 4.3.

### Attention

Whether a work ticket's state has been looked at and is sound. Blank by default: nothing has affected it.
Version and Alert tickets have no Attention.

| Value | Colour | Meaning | Set by |
|---|---|---|---|
| *(blank)* | none | Nothing has affected it. | n/a |
| **Fine** | green | Looked at: nothing is wrong, or it was put right. | a person |
| **Acknowledged** | purple | Looked at: something has to be done, and it is handled elsewhere (another ticket, or this ticket moved back to *ToDo*, *OnDeck*, *InProgress* or *Suspended*). The comment says where. | a person |
| **Watch** | yellow | An open flag, the lowest level. | the automation |
| **Caution** | orange | An open flag, the middle level. | the automation |
| **AtRisk** | red | An open flag, the highest level. Reserved: no rule uses it yet. | the automation |

A level says how serious something looks, not what it is. The comment the automation adds says why.
Setting the field changes nothing else on the ticket. The causes the automation uses, the idle times and
waits, and when a flag is raised again are set out once, in *Project structure*, section 4.3.

### Resolution

How a ticket ended. Blank while the ticket is open.

| Value | Meaning | Used with |
|---|---|---|
| **Done** | The work was done and verified. | *Completed* |
| **Duplicate** | The same as another ticket, which the comment links. | *Abandoned* |
| **Invalid** | Not a real problem, or based on a misunderstanding; includes a fault that cannot be reproduced. | *Abandoned* |
| **WontFix** | A valid request or fault that was decided not to act on. | *Abandoned* |
| **Superseded** | Replaced by a different approach or ticket: the work was real, but something else took its place. | *Abandoned* |
| **Obsolete** | No longer relevant because the thing it was about changed or was removed. | *Abandoned* |

Set by the person making the move to *Completed* or *Abandoned*. When it is set and cleared is in *Project
structure*, section 4.3.

### Delivery

Where the ticket's delivered work is: a fact about the work, independent of Progress and Resolution.

| Value | Meaning | Set by |
|---|---|---|
| *(blank)* | No code for this ticket exists on the hosting service, and its work is not yet in effect. | n/a |
| **Committed** | Optional personal marker: the work is committed locally and not yet pushed. | the developer, by hand only |
| **Pushed** | Code for the ticket is on a branch on the hosting service, not yet merged. | the automation, when a push contains a changelog entry for the ticket |
| **Merged** | The work is on `main`, in a finalized version. | the automation, at finalize |
| **Implemented** | The work is in effect and involved no file change (a setting, a secret, a check that was run). | a person, with the Version it belongs to; the automation then attaches the ticket to that version's ticket |
| **Released** | The version containing it has been declared a release. | the automation, when a release is cut |
| **Dropped** | The code or version was planned or pushed but will never be delivered. | the automation when a branch is abandoned; a person for a planned version |

The rules for Delivery (when it moves back, what *Committed* and *Implemented* are for, and the two
Delivery and Version rules a *Completed* ticket must meet) are in *Project structure*, sections 4.3 and 4.4.
How *Implemented* tickets are attached to their Version tickets is in section 5.2 of the same guide, and
what a release does to Delivery is in *Releases, hotfixes and retiring branches*, section 1.1.

### Priority

How urgent, by consequence rather than by deadline. A ticket with no priority is treated as *Normal*. The
creator proposes it and the owner can change it at any time; *Critical* needs a comment saying why (the
Alerts the automation creates are *Critical* without one).

| Value | Meaning |
|---|---|
| **Critical** | Act now: a fault in released software, or an unverified bypass. Every Alert ticket is Critical. |
| **Urgent** | Must be in the current or next version; it blocks other work or a release. |
| **High** | Important; planned for the next few versions. |
| **Normal** | The default for ordinary work. |
| **Low** | Nice to have; do it when convenient. |
| **Wishlist** | An idea or backlog item with no commitment to do it. |

### Size

Estimated developer effort, from starting the work to moving it to *Review*, including testing and
documentation. It is effort, not calendar time, and it is not risk. A day means eight hours of effort.
Every work ticket gets a Size when it is created, and a Size can be corrected as understanding improves.

| Value | Estimated effort |
|---|---|
| **XS** | up to 1 hour |
| **S** | up to 4 hours |
| **M** | up to 2 days |
| **L** | up to 2 weeks |
| **XL** | more than 2 weeks |

### Risk

How likely the work is to go wrong. Size assumes the work succeeds; Risk says how likely that estimate is to
be badly wrong. Proposed by the creator and revised by the developer before the ticket moves to *Review*.
Informational only: it drives no rule or automation.

| Value | Meaning |
|---|---|
| **1 Very low** | Nothing depends on it. |
| **2 Low** | Isolated and easy to undo. |
| **3 Medium** | Some uncertainty. |
| **4 High** | Likely to go wrong: critical failure or major delay. |
| **5 Very high** | May not be feasible. |

### Version, Build and Version#

| Field | Holds | Set by |
|---|---|---|
| **Version** (text) | The version a ticket is aimed at and, once it ships, the version it really shipped in (`V2.1.0`, or `V2.1.0-HF1` for a hotfix). | a person may set it ahead of time; the automation overwrites it with the real version (for a backfilled ticket, the version where its placeholder appears). On an *Implemented* ticket the person's value stays |
| **Build** (text) | The latest build of the ticket: the most recent build stamp among the build blocks that mention it. | the automation |
| **Version#** (number) | A number derived from Version, used only to sort versions. It keeps a digit for the hotfix number. | the automation: at finalize, and on every scheduled run for any ticket that has a Version (also one that is only aimed at a version) and a blank or different Version# |

### Start date and End date

Dates the automation noticed, never planned ones. Set by the automation; a person may correct one by hand.

| Field | Set when | Rules |
|---|---|---|
| **Start date** | The automation first sees the ticket at *InProgress* or beyond. | Set only if blank: never overwritten, whether set earlier or by a person. |
| **End date** | The automation first sees the ticket *Completed* or *Abandoned*. | Set only if blank. Cleared by the automation when it sees the ticket open again, and set again the next time it ends. |

The automation cannot be told when a person changes Progress, so the dates are found by a sweep on every
run and a scheduled run; a date is accurate to the day it was noticed, in UTC. Version and Alert
tickets have no dates.

---

### Which fields apply to which tickets

| Field | Work ticket | Version ticket | Alert ticket |
|---|---|---|---|
| Type | the work Type | Version | Alert |
| Area | suggested | none | `process` |
| Origin, REF | as needed | none (Origin may stay Backdated on old ones) | blank |
| Progress | yes | none | yes, all moves manual |
| Waiting | yes | none | as for any ticket |
| Attention | yes | none | none |
| Resolution | yes | none | as for any ticket |
| Delivery | yes | *Merged*, *Released* or *Dropped* | none |
| Priority | Normal by default | none | Critical, always |
| Size | required at creation | none | set by the person who takes it |
| Risk | proposed by the creator | none | set by the person who takes it |
| Version, Build, Version# | yes | its own version; its last build | the version in which it was raised |
| Start date, End date | yes | none | none |
| Assignee | assigned to the person who starts the work | none | the person who pushed, for a bypass, a merge without changelog entries or an unreadable changelog; none for stale planned versions |

---

## Appendix D: Ticket examples

Example tickets for each Type, shown as full forms with their critical fields, to show how much detail
a ticket should carry. The examples are generic, not taken from any one product. Two of them are shown
in section 3.5 of *Project structure*; the rest are here.

The descriptions state the problem or the need in detail. The solution is worked out in the comments,
except where a description labels a suggestion as a proposed implementation.

All names, numbers, versions and builds are invented for illustration.

| Type | Example title | Priority | Size | Shown |
|---|---|---|---|---|
| **Feature** | Add CSV export to the reports page | Normal | M | section 3.5 |
| **Feature** | Support a second language in the interface | Normal | L | here |
| **Enhancement** | Speed up report generation for large data sets | High | M | here |
| **Enhancement** | Make error messages say what to do next | Normal | S | here |
| **Change** | Raise the default timeout from 10 to 30 seconds | Normal | XS | here |
| **Change** | Change the login lockout from 3 to 5 attempts | Low | XS | here |
| **Bug** | Report totals ignore the last day of the month | High | S | section 3.5 |
| **Bug** | Upload fails silently when the file name has an accent | Urgent | S | here |
| **Refactor** | Split the settings module into smaller parts | Low | L | here |
| **Refactor** | Replace the duplicated date parsing with one function | Normal | S | here |
| **Task** | Run the full regression test on the release candidate | Urgent | M | here |
| **Task** | Write the user guide for the export feature | Normal | S | here |
| **Task** | Measure current draw in sleep mode | Normal | S | here |
| **Version, Alert** | Generated by the automation (see *Project structure*, special tickets) | | | |

---

##### Feature: "Support a second language in the interface"

| Field | Value |
|---|---|
| **Title** | Support a second language in the interface |
| **Type** | Feature |
| **Area** | requirements, research, design, implementation, config, testing, documentation |
| **Priority** | Normal |
| **Size** | L |
| **Risk** | 3 (Medium) |
| **Assignee** | Alex |

> **Purpose.** A customer group in a new market needs the product in their language, and the current
> interface is English only. Without it the product cannot be offered there.
>
> **What is wanted.** Every user-facing text on the main screens (sign-in, home, reports, settings) can
> be shown in a second language chosen by the user. The choice is remembered between sessions and can be
> changed at any time without signing out. Text without a translation falls back to English rather than
> showing blank space or a placeholder key.
>
> **Details that matter.** Dates, numbers and decimal separators follow the chosen language. Layouts
> must still fit when the translated text is up to 40% longer. The language of exported files is not
> affected.
>
> **Out of scope.** Right-to-left languages, translating the documentation, and a third language (but
> the work must not make a third language hard to add).
>
> **Open questions.** Who provides and checks the translations, and how new text is flagged as needing
> translation. These should be settled in the comments before work starts.
>
> **Done when.** All strings on the main screens are translated and reviewed by a native speaker, the
> fallback works, nothing is cut off at the longest translations, and adding a language is described in
> the developer documentation.

##### Enhancement: "Speed up report generation for large data sets"

| Field | Value |
|---|---|
| **Title** | Speed up report generation for large data sets |
| **Type** | Enhancement |
| **Area** | analysis, implementation, testing |
| **Priority** | High |
| **Size** | M |
| **Risk** | 3 (Medium) |
| **Assignee** | Sam |

> **Problem.** A monthly report over about 50,000 entries takes around 40 seconds to appear. Users
> reload the page or leave, and support has had two complaints. Reports of a few hundred entries are fast
> and are not the concern.
>
> **Measured.** 38 to 42 seconds on version 2.3.1, build 20260301120000, on the standard test data set
> (50,000 entries), repeated five times. The time is spent before the first row is shown, not in drawing
> the page.
>
> **Target.** 10 seconds or less for the same data set on the same machine, without changing the numbers
> in the report: the new output must be identical to the current output for every report in the
> regression set.
>
> **Constraints.** No change to the report layout. No new external dependency.
>
> **Done when.** The target is met on the standard data set, the output matches the current output on
> the regression set, and the before and after timings are recorded in a comment with the build used.

##### Enhancement: "Make error messages say what to do next"

| Field | Value |
|---|---|
| **Title** | Make error messages say what to do next |
| **Type** | Enhancement |
| **Area** | design, implementation, documentation |
| **Priority** | Normal |
| **Size** | S |
| **Risk** | 1 (Very low) |
| **Assignee** | Alex |

> **Problem.** Many error messages only say that something failed ("Error 4021", "Operation not
> allowed"). Users contact support to ask what to do, and support gives the same answers each time.
>
> **What is wanted.** The ten messages support is asked about most (list attached in the first comment)
> each say what happened in plain words and what the user can do next. Wording is consistent: same tone,
> no internal codes in the visible text, the code kept only in the details section for support.
>
> **Out of scope.** Changing when errors occur, and the less frequent messages (a follow-up ticket can
> cover them if this works).
>
> **Done when.** The ten messages are rewritten, reviewed by someone from support, and the error
> reference in the user guide matches the new wording.

##### Change: "Raise the default timeout from 10 to 30 seconds"

| Field | Value |
|---|---|
| **Title** | Raise the default timeout from 10 to 30 seconds |
| **Type** | Change |
| **Area** | config, testing, documentation |
| **Priority** | Normal |
| **Size** | XS |
| **Risk** | 2 (Low) |
| **Assignee** | Sam |

> **Why.** On slow connections about 12% of requests time out at 10 seconds and then succeed when
> retried. A longer default removes most of those failures. This is a deliberate change to a value that
> was working as designed, not a bug.
>
> **What changes.** The default request timeout becomes 30 seconds. Values that a user or administrator
> has set themselves are not touched. Nothing else about retries changes.
>
> **Impact to check.** A request that really is stuck now takes up to 30 seconds to be reported as
> failed; confirm the interface still shows progress during that time.
>
> **Done when.** The default is 30 seconds on a fresh install and unchanged on an upgraded install with
> a custom value, and the settings documentation shows the new default.

##### Change: "Change the login lockout from 3 to 5 attempts"

| Field | Value |
|---|---|
| **Title** | Change the login lockout from 3 to 5 attempts |
| **Type** | Change |
| **Area** | config, documentation |
| **Priority** | Low |
| **Size** | XS |
| **Risk** | 2 (Low) |
| **Assignee** | Alex |

> **Why.** After a review of support requests, three failed attempts locks out too many legitimate users
> who mistype a password, while five attempts is still within the agreed security policy.
>
> **What changes.** The number of failed sign-in attempts that trigger the lockout goes from 3 to 5. The lockout
> duration and the counter reset rules stay as they are. The message shown at lockout is unchanged.
>
> **Done when.** The fifth consecutive failure (not the third) triggers the lockout in a test, an
> upgraded install behaves the same as a fresh one, and the security section of the documentation states
> the new number.

##### Bug: "Upload fails silently when the file name has an accent"

| Field | Value |
|---|---|
| **Title** | Upload fails silently when the file name has an accent |
| **Type** | Bug |
| **Area** | debugging, testing |
| **Priority** | Urgent |
| **Size** | S |
| **Risk** | 2 (Low) |
| **Assignee** | Alex |

> **Problem.** Uploading a file whose name contains an accented character (for example `résumé.pdf`)
> appears to work: the progress bar completes and no error is shown. The file never appears in the list.
>
> **How to reproduce.**
> 1. Rename any file to `résumé.pdf`.
> 2. Upload it from the files page.
> 3. Refresh the list.
>
> **Expected.** The file appears in the list, or a clear error explains why it was refused.
>
> **Actual.** Nothing appears and nothing is reported. The server log contains one line,
> `invalid name encoding`, for each attempt.
>
> **Found on.** Version 2.3.1, build 20260301120000, reported by two users on different systems. File
> names with only plain letters and digits upload correctly.
>
> **Impact.** Users believe the upload succeeded and lose the file without knowing. This is why the
> priority is higher than the size of the problem suggests.
>
> **Open question.** Which characters are affected? Accents are confirmed; other non-ASCII characters
> have not been tried. Record what is found in the comments.
>
> **Done when.** Files with accented and other non-ASCII names upload and appear in the list, any name
> that still cannot be accepted produces a visible error, and tests cover both cases.

##### Refactor: "Split the settings module into smaller parts"

| Field | Value |
|---|---|
| **Title** | Split the settings module into smaller parts |
| **Type** | Refactor |
| **Area** | design, implementation, testing |
| **Priority** | Low |
| **Size** | L |
| **Risk** | 3 (Medium) |
| **Assignee** | Sam |

> **Why.** The settings module has grown to about 2,400 lines and mixes five unrelated concerns
> (storage, validation, defaults, migration of old settings, and the screens that edit them). Changes to
> one concern keep breaking another, and new people cannot tell where to add things.
>
> **What must not change.** Behaviour. Every setting must be stored, validated, defaulted and migrated
> exactly as before, and the public interface other modules use must stay the same, so nothing outside
> the module has to change.
>
> **How it will be verified.** The existing tests pass unchanged. Before starting, export the complete
> settings output for the standard test configurations; after the split, the output must be identical.
>
> **Out of scope.** Changing any setting's meaning, adding settings, or renaming things for style.
>
> **Done when.** The module is split along the five concerns, each part has a short comment on its
> purpose, the exported output is byte-for-byte identical, and the developer documentation describes the
> new layout.

##### Refactor: "Replace the duplicated date parsing with one function"

| Field | Value |
|---|---|
| **Title** | Replace the duplicated date parsing with one function |
| **Type** | Refactor |
| **Area** | implementation, testing |
| **Priority** | Normal |
| **Size** | S |
| **Risk** | 2 (Low) |
| **Assignee** | Alex |

> **Why.** Dates typed or imported by users are parsed in four different places, each with slightly
> different rules (two accept `dd/mm/yyyy`, one also accepts `yyyy.mm.dd`, one ignores surrounding
> spaces). A fix made in one place has been missed in the others twice.
>
> **What is wanted.** One parsing function used by all four places, accepting exactly the formats that
> are accepted today (the union of the four), with the same results for every input that works now.
>
> **What must not change.** Which inputs are accepted or rejected, and the dates they produce. Where the
> four places disagree today, list the differences in a comment first and decide which behaviour wins
> before changing anything.
>
> **Done when.** The four places call the one function, a test table of accepted and rejected inputs
> passes in all four, and the differences found are recorded in the ticket.

##### Task: "Run the full regression test on the release candidate"

| Field | Value |
|---|---|
| **Title** | Run the full regression test on the release candidate |
| **Type** | Task |
| **Area** | testing |
| **Priority** | Urgent |
| **Size** | M |
| **Risk** | 1 (Very low) |
| **Assignee** | Sam |

> **What is needed.** Run the complete regression checklist (version 12 of the checklist document) on
> the release candidate build and record the result of every item.
>
> **Scope.** All 86 items, on the build named in the first comment, on one clean installation. Items that
> need special equipment are listed at the top of the checklist.
>
> **Reporting.** Add one comment with the build used, the date, and pass or fail for each item. Every
> failure becomes its own Bug ticket linked from this one.
>
> **Done when.** All items have a recorded result, every failure has a Bug ticket, and the comment states
> whether the build is fit for release.

##### Task: "Write the user guide for the export feature"

| Field | Value |
|---|---|
| **Title** | Write the user guide for the export feature |
| **Type** | Task |
| **Area** | documentation |
| **Priority** | Normal |
| **Size** | S |
| **Risk** | 1 (Very low) |
| **Assignee** | Alex |

> **What is needed.** A short section in the user guide explaining how to export a report to CSV.
>
> **Audience.** A user who has never exported data. Assume they can find the reports page and nothing
> more.
>
> **Contents.** Where the button is, what the file contains (columns, date and number format, encoding),
> how to open it in a spreadsheet so accented characters display correctly, and what happens with an
> empty report. Two screenshots.
>
> **Dependencies.** The export feature must be merged first, so the screenshots and wording match the
> real behaviour.
>
> **Done when.** The section is added to the guide, a colleague who has not seen the feature follows it
> successfully, and the guide's contents list is updated.

##### Task: "Measure current draw in sleep mode"

| Field | Value |
|---|---|
| **Title** | Measure current draw in sleep mode |
| **Type** | Task |
| **Area** | testing, analysis |
| **Priority** | Normal |
| **Size** | S |
| **Risk** | 1 (Very low) |
| **Assignee** | Sam |

> **Why.** The battery life estimate assumes 20 microamps in sleep mode, but the figure has never been
> measured on the current board. The estimate drives the stated battery life of 12 months.
>
> **Setup.** Board revision C, the firmware build named in the first comment, powered through the
> current meter at the nominal battery voltage. Radio off, sensors off, no debug connection attached, at
> room temperature.
>
> **What to record.** The average current after it has settled (at least one minute), the lowest and
> highest values seen, and the exact meter and range used.
>
> **Done when.** The measurements are posted in a comment with the build and setup used, compared with
> the 20 microamp assumption, and the battery life estimate in the documentation is updated if the
> measured value differs.

---

## Appendix E: Ticket model

The design of a ticket as a whole: the questions a ticket answers, why each has its own field, how the
fields work together, and the life of a ticket from creation to release. The values of every field are in
*Appendix C: Ticket fields reference*, and the rules and their reasons are in section 4 of *Project
structure*. This appendix is the picture that ties them together.

---

### 1. The idea

A ticket is a record of one thing to be done. Everything worth knowing about it falls into a small number of
separate questions, and each question gets its own field. Keeping them apart is deliberate: a field that
answers two questions ends up meaning two things (for example, "in progress" cannot also say whether the
code has shipped).

| Space | Question | Where it lives (GitHub) | Set by |
|---|---|---|---|
| **Type** | What sort of ticket is this, and why is the change being made? | the issue type | a person (the automation for Version and Alert tickets) |
| **Area** | What kind of work does it involve? | labels, several per ticket | a person |
| **Origin**, **REF** | Was the ticket created after the work, and which placeholder did it replace? | board fields | a person |
| **Progress** | Where is the work? | the board's Status field | a person (the automation only advances *ToDo* and *OnDeck* to *InProgress*) |
| **Waiting** | Is it waiting for someone's input? | board field | a person |
| **Attention** | Has the ticket's state been looked at, and is it sound? | board field | the automation raises flags; a person closes them |
| **Resolution** | How did it end? | board field | a person |
| **Delivery** | Where is the delivered work? | board field | the automation (apart from *Committed*, *Implemented* and *Dropped* on a planned Version ticket) |
| **Planning** | How urgent, how big, how risky, which version and build, when? | Priority, Size, Risk, Version, Build, Version#, Start date, End date | a person, except Build, Version#, the real Version and the dates |

Two principles decide who sets a field. **Judgment belongs to people, facts belong to the automation**:
whether the work is done, verified or urgent is a person's call, while where the code is, which build it is
in and when it was noticed are facts the automation records.

### 2. Why each space is separate

- **Type and Area.** Type is the main reason for the change and is one value, because the version number is
  computed from it. Area says what work the ticket takes and is several values, because one ticket often
  involves design, implementation and documentation together. Area never affects any rule.
- **Origin and REF.** A ticket made late has less to say about how the work was planned, and a reader of the
  history should be able to tell. Origin records that; REF links a backfilled ticket to the changelog
  placeholder it replaced.
- **Progress, Waiting and Attention.** A ticket can wait, or look stale, in any open state. If either were a
  Progress value, it would replace the real state and lose where the ticket was. So Progress stays a clean
  path, Waiting says someone is owed an answer, and Attention says that the automation saw something that
  does not add up and a person should look.
- **Resolution.** "How did it end" is a different question from "where is it". The reasons for dropping work
  are worth keeping: they answer a later "did we already decide not to do this".
- **Delivery.** Where the code is, is a fact the automation can see. It is independent of Progress and
  Resolution: a ticket whose code shipped but is not yet verified is *Released* and *Review* at once, and
  both are true.
- **Planning.** Urgency, effort and risk are separate so they can disagree: a small change can be risky and
  a large one can wait. One Version field, corrected by the automation, means a ticket aimed at a later
  version that ships earlier fixes itself.

### 3. The life of a work ticket

The path of an ordinary ticket, with what changes at each step and who changes it.

| Step | Progress | Delivery | Other fields | Who |
|---|---|---|---|---|
| **Created** | *ToDo* | blank | Type, Size, Priority (default *Normal*), Risk proposed, Area suggested; Version may be set to aim it | the creator |
| **Chosen next** | *OnDeck* | blank | | a person |
| **Started** | *InProgress* | blank | Assignee; Start date appears at the automation's next sweep | a person |
| **First push** | *InProgress* (advanced by the automation if still *ToDo* or *OnDeck*) | *Pushed* | Build | the automation |
| **Work done** | *Review* | *Pushed* | Risk revised by the developer | a person, never the automation |
| **Merged** | unchanged | *Merged* | Version and Build set to the real values | the automation, at finalize |
| **Verified** | *Completed* | *Merged* | Resolution *Done*, Waiting cleared, End date at the next sweep, issue closed | a human only |
| **Released** | unchanged | *Released* | | the automation, when a release is cut |

Side paths:

- **Waiting.** At any open step a person sets Waiting to *Needs input* with a comment saying what is needed
  and from whom, and clears it when the answer arrives.
- **Sent back.** A reviewer may move a ticket from *Review* to *InProgress*.
- **Suspended.** Set aside and expected to return; the issue stays open, and a suspended branch keeps its
  *Pushed* code.
- **Abandoned.** Dropped. Resolution is one of *Duplicate*, *Invalid*, *WontFix*, *Superseded* or *Obsolete*,
  with a comment linking any related ticket; Waiting is cleared and the issue is closed. If the branch is
  retired as abandoned, the automation sets Delivery to *Dropped*.
- **New work after the fact.** Pushing again on a ticket that is *Merged*, *Implemented*, *Released* or
  *Dropped* returns Delivery to *Pushed*. If the ticket looked finished (*Completed*, *Abandoned*, *Review* or
  *Suspended*), the automation raises Attention rather than changing Progress, and a person decides (the
  conditions are in *Project structure*, section 4.3).
- **No file change.** A ticket whose work is a setting, a secret or a check that was run has no changelog
  entries. When its work is in effect a person sets Delivery *Implemented* and its Version, and the
  automation attaches it to that version's Version ticket.
- **Late tickets.** A ticket created after the work has Origin *Backfilled* (with REF) or, for history from
  before the process, *Backdated*.

#### Attention

Attention is a separate, parallel track on a work ticket. It starts blank. The automation raises *Watch* or
*Caution* with a comment saying why; a person looks and sets *Fine* (nothing wrong, or put right) or
*Acknowledged* (something has to be done, and it is handled elsewhere). Setting it changes nothing else.
What raises each level is in *Project structure*, section 4.3.

### 4. How the fields hold together

The fields are kept consistent by rules that span them: a *Completed* ticket has Resolution *Done* and a
closed issue, an open ticket has no Resolution or End date, shipped work has a Version, and so on. The
full table is in *Project structure*, section 4.4, and the automation flags a ticket that breaks one.

### 5. Special tickets

Version and Alert tickets are created by the automation. They are exempt from the rule that every ticket
gets a Size, and only some fields apply to them (the table is at the end of Appendix C).

- **A Version ticket** is the bookkeeping record of one version, titled `Version X.Y.Z`. It has no Progress:
  its Delivery describes its life (planned, *Merged*, *Released* or *Dropped*), and the version's tickets
  are its sub-issues. Aiming a ticket at a future version needs no planned Version ticket, only the
  Version field.
- **An Alert ticket** is a real check that a person must do. It is created *Critical*, in *ToDo*, with the
  Area `process`, and every later move is manual.

The stages, the rules and the causes of each are in *Project structure*, sections 5.2 and 5.3.

### 6. How the model drives the automation

- **Version numbers.** The Type of each ticket in a version decides the bump, and a marker can override it
  (the rules are in *Branching and merging strategy*, section 3.3).
- **Delivery, Version, Build and dates** are written by the automation from pushes, merges, releases and a
  sweep that runs after each finalize and on every scheduled run. The scheduled run also sets Version# on any ticket that has a
  Version, so a ticket only aimed at a version sorts with the others.
- **Attention** is raised from the same sweep and from pushes.
- **Nothing in Area, Risk, Priority or Size** drives any rule.

### 7. Where each part is defined

| To see | Read |
|---|---|
| Every value and who sets it | *Appendix C: Ticket fields reference* |
| The idea and rules of each field | *Project structure*, section 4 |
| Version and Alert tickets in full, with examples | *Project structure*, section 5 |
| How version numbers follow the Types | *Branching and merging strategy* |
| Creating a ticket and keeping it current | *Starting work* and *Working and committing* |
| Review, verification and the daily board | *Issues and the board in practice* |
| Example tickets | *Appendix D: Ticket examples* |
