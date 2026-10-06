# Starting Work

This guide covers the steps from "I am going to work on something" to the first push: getting a ticket,
creating the branch, opening the changelog entry, and making the first commit. It is a procedure: each
step says what to do and why, and the commands are in the "In GitHub" blocks. The pieces it refers to
(tickets, fields, the changelog, branches and tags) are defined in the guide on project structure, and the
rules about branches in the guide on branching and merging.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

## 1. Before you start

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

## 2. Get a ticket, or a REF

The steps:

1. **Check for an existing ticket.** Search the open and closed tickets for the same thing before
   creating one.
2. **If there is none, create it.** Fill in what the guide on project structure says a ticket needs, and
   assign it to yourself.
3. **Or start with a `REF`.** For a small or urgent change, or exploratory work, you may start without a
   ticket. Every `REF` is backfilled later (see the guide on working and committing).
4. **Mark it started.** Set Progress to *InProgress*. The Start date is filled in by the automation.
5. **If you need input before starting,** set Waiting, with a comment saying what is needed and from whom.

### 2.1 Rules

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

## 3. Create the branch

### 3.1 A new work branch

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

### 3.2 A hotfix branch

- **Rule:** a hotfix branch starts from the release tag being patched, not from `main`. A further
  hotfix for the same release starts from the tag of the latest hotfix, so that it includes the earlier
  fixes.
- **Rule:** it is named `hotfix-v<major>-<sub>-<mod>-<description>`, with the version's dots written as
  hyphens (for example `hotfix-v1-25-0-fix-sensor-timeout`).

The details of finishing a hotfix are in the guide on releases and hotfixes.

**Why.** A hotfix patches exactly what was released, so it must start from exactly that, and not from a
`main` that has moved on.

> **In GitHub.** `git switch -c hotfix-v1-25-0-fix-sensor-timeout released/V1.25.0`.

### 3.3 Continue on an existing branch

When the branch still exists and the new work belongs with it (a follow-up, the next stage of the same
feature, or a fix to what it delivered):

- **Rule:** bring `main` into the branch first (see the guide on branching and merging, section 4). If
  the branch was merged before, this brings in the automation's commit that renamed the version
  heading.
- **Rule:** if the branch was merged before, add a new `WIP-Version` heading before the next logged change
  (section 4 of this guide), after that sync, because finalizing a version leaves no empty heading
  behind.

### 3.4 Recover a suspended or abandoned branch

- **Rule:** recreate the branch from its tag. The tag stays as history.
- **Recommendation:** bring `main` into it before doing anything else, since it stood still while `main`
  moved.
- **Rule:** the ticket goes from *Suspended* or *Abandoned* back to *InProgress*, and its Resolution is
  cleared.
- If the branch's changelog already has an open `WIP-Version`, continue it. Do not open a second heading.

> **In GitHub.** `git switch -c <branch-name> suspended/<date>_<branch-name>`, or use the `abandoned/`
> tag for an abandoned branch.


---

## 4. Open the changelog entry

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

### 4.1 Rules

- **Rule:** a branch has at most one open `WIP-Version` heading, at the top of the changelog.
- **Rule:** a marker is only for forcing the version bump. It applies to that one release, and it is not
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

### 4.2 Example

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

## 5. First commit and push

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
   entries, and moves a ticket still at *ToDo* or *OnDeck* to *InProgress*. If one of them is *Completed*, *Abandoned*, *Review* or *Suspended* and earlier work on it was
   already pushed or delivered, it also raises *Caution* in Attention, with a comment, because new work has
   arrived on it. The first push of a ticket raises nothing, even if the ticket is already at *Review* (see
   the guide on project structure, section 4.3).
5. **Check the ticket.** Delivery shows *Pushed*. The Start date appears after the automation's next
   sweep.

### 5.1 Rules

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

## 6. Checklist

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
