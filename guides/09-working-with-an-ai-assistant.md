# Working with an AI Assistant

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

## 1. What an assistant is in this process

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

## 2. What an assistant does without asking

### 2.1 Routine work

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

### 2.2 How it reports back

- **Recommendation:** be concise. Say what was done in a short summary, without narrating every step or
  recapping everything.
- **Rule:** report outcomes faithfully. If a test failed, say so, with the output. If a step was skipped,
  say that. When something is done and verified, say so plainly, without hedging.

**Why.** The person is responsible for the result, so they have to be able to rely on what the assistant
says it did.


---

## 3. What an assistant asks about first

### 3.1 Ask first

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

### 3.2 Rules

- **Rule:** the assistant commits, pushes and merges (into `main` or a shared branch) only with explicit
  approval.
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

## 4. Tickets and the board

### 4.1 What an assistant may and may not set

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

### 4.2 Writing to tickets and documents, and authorship

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

## 5. The changelog, commits and documentation

### 5.1 The changelog

The assistant writes entries as it makes each change, following the guide on working and committing
(section 2): specific bullets, one block per ticket, and nothing but changes to files.

- **Rule:** the changelog contains real changes and critical notes only. No placeholders about status,
  such as "no changes yet" or "not committed", and no commentary about the process.
- **Rule:** the assistant opens the `WIP-Version` heading when work starts (see the guide on starting
  work, section 4). It adds a marker (`+V`, `+s` or `+m`) only when told to, and asks first for a major
  bump.

### 5.2 Commits

- **Rule:** the assistant writes the commit message in the format of the guide on working and committing
  (section 5.2), derived from the entries it wrote, and proposes it. It commits only after explicit
  approval (section 3).
- **Rule:** the assistant builds locally and runs the existing tests before proposing a commit (see the
  guide on working and committing, section 4), and states plainly if anything failed.
- **Rule:** the assistant does not skip hooks, squash, rebase, or amend a pushed commit on its own
  initiative.

### 5.3 Documentation

- **Rule:** the assistant updates what its change affects, using the checklist in the guide on working
  and committing (section 3), in the same change, and writes tests alongside new logic.
- **Recommendation:** list the documentation it updated as separate bullets in the changelog entry.

**Why.** An assistant that follows the same changelog and commit rules produces the same record a person
would, so the history reads as one. Asking for approval on the commit keeps the person in charge of what
enters the history. Keeping status commentary out of the changelog keeps it a record of changes, which is
what it is for. Using the same message format the hook would draft means the message is not written
twice.


---

## 6. Instructing an assistant

### 6.1 Where the instructions live

- **Rule:** the project keeps one shared instructions file for assistants in the repository, named
  `AGENTS.md` and placed at the repository root. It is versioned and changed through the normal flow, like
  any other file. Everyone's assistant reads it.
- **Recommendation:** personal preferences stay in a personal file that is not committed.

### 6.2 What goes in it

The file points to the guides and records only what is specific to the project. It does not repeat the
rules, because a copy can drift from the guide.

- where the process guides are published,
- how to build and test the project,
- which roles are held by whom,
- the durable authorizations, each with its date and who gave it (section 3),
- anything the assistant must not touch.

### 6.3 A starter text

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

### 6.4 Rules

- **Rule:** a durable authorization is written in the file with its date and who gave it, and is removed to
  withdraw it.
- **Recommendation:** keep the file short and pointing to the guides.

**Why.** One shared file means the project behaves the same whoever's assistant did the work. A short file
is one people actually keep up to date, and an authorization written down with a date and a name is a
decision that someone made and can see, and can take back.

### 6.5 A starter text for personal preferences

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

## 7. Checklist

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
