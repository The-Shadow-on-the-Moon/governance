# Concepts and Vocabulary

This guide defines the words the other guides use, and the git and GitHub names they rely on. Read it first,
or come back to it when a word is unclear. The rules that use these words are in the other guides.

**How to read it.** Each topic states what something is. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

---

## 1. Version, build, compile stamp and release

Four words that are easy to confuse. Each answers a different question.

| | What it is | Assigned | Lives in | Identifies |
|---|---|---|---|---|
| **Version** | `V<major>.<sub>.<mod>`, with `-HF<n>` added for a hotfix | when a branch merges into `main` | the topmost finalized heading of the changelog | a position in the history |
| **Build** | a UTC timestamp, `yyyymmddhhmmss` | when a commit is made, by the local hook | a build heading in the changelog | one commit's worth of changes |
| **Compile stamp** | a UTC timestamp, `yyyymmddhhmmss` | every time the product is compiled | inside the compiled product | exactly what was compiled |
| **Release** | a version declared a release | deliberately, after verifying it | a tag `released/V…` | a version that is fit to be used |

- A version cannot be known while a branch is being written, because it depends on what else has landed on
  `main`. A build can, because it is stamped at the commit. A release is a decision, and many versions are
  never one.
- **Rule:** a product that is compiled carries a compile stamp, generated afresh on every compile and
  embedded in the product itself. It is a UTC timestamp and needs no lookup and no git command. It is
  unique in practice, even for repeated compiles of the same commit, though its resolution is one second.
- **Rule:** a recorded test result names the build it applies to and, where the product has one, the
  compile stamp of what was tested (see the guide on working and committing, section 4).
- **Rule:** the `V` is part of a version wherever it is written as a version: the changelog heading, the
  Version field and the release tag (`V2.4.1`, `released/V2.4.1`). A Version ticket's title is the one
  exception and has no `V` (`Version 2.4.1`).
- The word *release* is used only for the tag. A stamp embedded at compile time is a *compile stamp*.

**Why.** The version says where in the history something is, the build says which commit, and the compile
stamp says which binary. Only the last one can tell you, when a device or a deployed copy misbehaves, exactly
what is running on it. A timestamp is practically unique without any state to check, and always UTC so that stamps from
different machines and places order correctly.

This section does not apply to a product that is never compiled.


---

## 2. Timestamps and the UTC rule

### 2.1 The formats

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

### 2.2 The rules

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

## 3. The changelog's words

The terms below are in the order they appear in the file, from the top of the structure down. Each ends
with where it is explained. Nothing here is new: it collects what the other guides define.

| Term | What it means | See |
|---|---|---|
| **Changelog** | The file in the repository that records every change to files, grouped by version, then build, then ticket. | project structure, section 7 |
| **Open version** | The `## WIP-Version` heading on a branch: the version being worked on. It has no number until the branch merges. | starting work, section 4 |
| **Marker** | `+V`, `+s` or `+m` written after `WIP-Version`, to force a major, sub or mod bump for that one release. | branching and merging, section 3.3 |
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

## 4. Tickets and the board's words

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

## 5. Branches and tags' words

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

## 6. Roles and automation's words

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

## 7. Git: names and concepts used

### 7.1 Concepts

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

### 7.2 Commands and flags the guides use

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

## 8. GitHub: names used

These are the names the guides use for GitHub's own features. Nothing here is new: it collects what the
other guides define.

| Term | What it means | See |
|---|---|---|
| **Organization** | The account that owns the repository and the board. The standard needs one, because issue types are an organization feature. | new-project bootstrap, section 5 |
| **Issue** | A ticket. | project structure, section 3 |
| **Issue type** | The native single value on an issue that says what sort of ticket it is. It carries the Type. | fields reference |
| **Label** | A tag on an issue. The only labels are the 14 Area labels. | fields reference |
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
