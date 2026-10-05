# Project Structure

This guide explains the pieces a project is made of, what each one means, how they connect and how they
are created. It is the reference the procedural guides (starting work, committing, merging, issues and
the board) point back to. The values of every ticket field are in the *Ticket fields reference*
appendix.

**How to read it.** Each topic states what something is and why it exists. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Vocabulary.** This guide says *ticket* for a unit of tracked work. GitHub calls it an *issue*; the
two words mean the same thing here.

---

## 1. The map

### 1.1 The pieces

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

### 1.2 How they connect

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

## 2. The repository

### 2.1 What lives where

| Location | Holds |
|---|---|
| **readme** (root) | What the project is, how to build and use it. |
| **`CHANGELOG.md`** (root) | The changelog (structure in section 7). |
| **Source folders** | The project's own code. Project-specific, so this guide says nothing about them. |
| **`tests/`** | Automated tests, for the product and for the automation scripts, and the recorded test results in `tests/results/`. Present when the project has code or scripts of its own. |
| **`doc/`** | Project documentation other than the readme and the changelog. |
| **`doc/wiki/`** | The wiki pages, one markdown file per page. |
| **`.githooks/`** | The local git hooks. |
| **`.github/`** | Server-side workflows and their scripts, and the pull request template. |
| **`AGENTS.md`** (root) | The shared instructions for AI assistants (see the guide on working with an assistant). |
| **Ignore file** (`.gitignore`) | What stays out of the repository. |

### 2.2 Rules

- **Rule:** these locations exist in every project, under these names, and hold only what the table
  lists. The exception is `tests/`, which is needed only when the project has code or scripts of its
  own.
- **Rule:** the hooks and the automation are part of the repository. They are versioned and changed
  through the same flow as code, and their logic has tests.
- **Rule:** the hooks are activated once per clone, with one command. A fresh clone has no hooks until
  that step is done. (The procedure is in the guide on starting work; this guide only states that the
  step exists.)
- **Recommendation:** keep personal and generated files out of the repository through the ignore file,
  so nobody commits the state of their own machine.

**Why.**

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

---

## 3. Tickets

### 3.1 What each part of a ticket means

| Part | Meaning |
|---|---|
| **Number** | A permanent, unique identifier given automatically at creation and never reused. Everything refers to the ticket by it: changelog entries, pull requests, commits. |
| **Title** | One line saying what the ticket is about. It appears in the changelog heading and becomes the summary line of the drafted commit message. |
| **Description** | What and why: the problem or purpose, the expected result, and how to tell it is done. |
| **Comments** | The running record: decisions, findings, questions, and verification results. |
| **Assignee** | Who owns the ticket. |
| **Links** | The pull requests that carry its work, the Version ticket that groups it, and related tickets, mostly through plain `#123` mentions. |
| **Fields** | The board fields (section 4). |

### 3.2 Creating a ticket

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

### 3.3 Titles, descriptions and comments

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

### 3.4 When a review fails

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

### 3.5 Examples

Two typical tickets, shown as full forms with their critical fields, to show how much detail a ticket
should carry. The examples are generic, not taken from any one product. The descriptions state the
problem or the need in detail; the solution is worked out in the comments, except where a description
labels a suggestion as a proposed implementation.

More examples, covering every Type, are in appendix D (*Ticket examples*).

#### Feature: "Add CSV export to the reports page"

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

#### Bug: "Report totals ignore the last day of the month"

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

## 4. Ticket fields

A ticket's details are held in fields. This section explains the idea behind each one and the rules that
tie them together. The values of every field, with their meanings, are in the *Ticket fields reference*
appendix.

### 4.1 One question per field

Each field answers one question about a ticket, and the fields are kept separate on purpose. Mixing two
questions in one field is how a single value ends up meaning two things: "in progress" cannot also say
whether the code has shipped, and "closed" cannot also say whether the work was done or dropped.

### 4.2 The fields at a glance

| Field | Question it answers | Values | Set by |
|---|---|---|---|
| **Type** | What sort of ticket is this, and why is the change being made? | one | a person (the automation for Version and Alert tickets) |
| **Area** | What kind of work does it involve? | several | a person |
| **Origin**, **REF** | Was the ticket created after the work, and which placeholder did it replace? | one; text | a person |
| **Progress** | Where is the work? | one | a person; the automation only advances *ToDo* and *OnDeck* to *InProgress* |
| **Waiting** | Is it waiting for someone's input? | one | a person |
| **Attention** | Has the ticket's state been looked at, and is it sound? | one | the automation raises *Watch*, *Caution* and *AtRisk*; a person sets *Fine* or *Acknowledged* |
| **Resolution** | How did it end? | one | a person |
| **Delivery** | Where is the code? | one | the automation (apart from an optional personal marker) |
| **Priority**, **Size**, **Risk** | How urgent, how big, how risky? | one each | a person |
| **Version**, **Build**, **Version#** | Which version and build? | text, text, number | a person may aim it; the automation sets the real values |
| **Start date**, **End date** | When did the work actually start and end? | dates | the automation |

### 4.3 The idea of each field

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
  - *Caution:* new work arrives on a ticket that is *Completed*, *Abandoned*, *Review* or *Suspended*, or
    a rule in section 4.4 is broken (for example *Completed* without Resolution *Done*).
  - *Watch:* a ticket looks out of date: no activity at *Review* for a week, at *OnDeck* or
    *InProgress* for a month, or at *Suspended* for six months, or a ticket that has been waiting for
    input for two weeks. Activity means a comment, a change to a field, or a new build that mentions the
    ticket; the automation's own flag comments do not count.
- **Rule:** a broken rule is raised only if the ticket, meaning its issue or its board fields, has not
  changed for five minutes. Fixing a ticket takes several edits (for example *Completed*, *Done* and
  closing the issue), and a ticket in the middle of them is not yet wrong.
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

- **Rule:** Delivery says where a ticket's code is: *Committed* (an optional personal marker, set by hand),
  *Pushed*, *Merged*, *Released*, or *Dropped*. Apart from *Committed* it is set by the automation, and
  people only correct a mistake.
- **Rule:** Delivery depends only on the code, never on Progress or Resolution. It can move back: new
  work pushed on a ticket that is already *Merged*, *Released* or *Dropped* returns it to *Pushed*.

*Why.* Where the code is, is a fact the automation can see, and mixing it with anyone's judgment would
make it unreliable. A ticket whose code has shipped but is not yet verified is *Merged* or *Released* and
*Review* at the same time, and both are true.

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
  mention it), and Version# is derived from Version only to sort versions.
- **Rule:** Start date and End date are the dates the automation noticed the ticket start and end. A
  person may correct one by hand. The automation clears the End date when it sees the ticket open again.

*Why.* Keeping urgency, effort and risk in separate fields lets them disagree, which they do: a small
change can be risky, and a large one can wait. One Version field that the automation corrects means a
ticket planned for a later version that ships earlier fixes itself.

### 4.4 Rules that span fields

| When | Then |
|---|---|
| Progress is *Completed* | Resolution is *Done*; both are set together by the person. |
| Progress is *Abandoned* | Resolution is one of the reasons; both are set together by the person. |
| Progress is *ToDo*, *OnDeck*, *InProgress*, *Review* or *Suspended* | Resolution and End date are blank. |
| A ticket becomes *Completed* or *Abandoned* | Waiting is cleared. |
| A ticket leaves *Completed* or *Abandoned* | The person clears Resolution; the automation clears the End date. |
| Origin is *Backfilled* | REF names the placeholder it replaced. |
| Code is merged or released | Delivery says so, whatever Progress and Resolution are. |
| A ticket is *Completed* or *Abandoned* | The GitHub issue is closed, by a person. |
| A ticket is a Version ticket | Only the version and Delivery fields apply (see the special tickets section). |
| A work ticket breaks one of these rules | The automation raises *Caution* in Attention, with a comment. |

> **In GitHub.** Type is the native issue type. Area is a set of labels. The other fields are board
> fields: Progress is the board's *Status* field, Delivery is a single-select field, and Start
> date and End date are date fields. The automation reads Type from the issue and writes the other fields
> to the board.


---

## 5. Special tickets

### 5.1 What makes them special

Version and Alert tickets are created by the automation, not planned by people. They do not follow the
work-ticket rules: they are exempt from the rule that every ticket gets a Size at creation, and only
some fields apply to them (the *Ticket fields reference* appendix has the table).

### 5.2 Version tickets

A Version ticket is a bookkeeping record for one version, titled `Version X.Y.Z` (without the `V`), or
`Version X.Y.Z-HFn` for a hotfix. The work tickets of the version point to it through their Version
field, and the automation attaches them as sub-issues of the Version ticket, so the board shows how many
of them are complete. A Version ticket does no work and is never verified.

| Stage | What happens | Delivery | Issue |
|---|---|---|---|
| **Planned** (optional) | A person creates it ahead of time for a future version. | blank | open |
| **Finalized** | The automation creates it, or reuses the planned one with the same title, when the version is finalized. | Merged | closed by the automation |
| **Released** | A release is cut on that version. The automation posts a comment with the date and the tag name. | Released | stays closed |
| **Planned, then dropped** | The version never happened under that number. A person marks it. | Dropped | closed, with a comment saying what replaced it |

- **Rule:** the automation writes the description at finalize: the date (UTC), the bump and why (which
  ticket gave it, or the marker that forced it), the pull request, and the tickets with their Type.
  Build holds the last build of the version.
- **Rule:** a hotfix version goes straight from planned or created to *Released* when the hotfix is
  finished, because a hotfix is never merged into `main`.
- **Rule:** when a version is finalized, any planned Version ticket with a lower number can no longer
  happen under that number. The automation raises one Alert listing them (section 5.3). Hotfix versions
  do not run this check.
- **Recommendation:** planning ahead by creating a Version ticket is optional. When a planned number turns
  out wrong, the alert above is how the mismatch is cleaned up.

*Why.* Delivery already describes a version's life (planned, merged, released, dropped), so a Version
ticket needs no Progress. One ticket per version gives a single place to see what shipped in it and how
much of it has been verified. Closing it at finalize keeps bookkeeping records from crowding the open
tickets that need attention.

### 5.3 Alert tickets

An Alert is a real check that a person must do. The automation raises one when something needs a person
to review it: a detected bypass, a merge that landed without changelog entries, or planned versions that
can no longer happen. It is not the same as the Attention flag: an Alert is about a rule that was bypassed
and is a ticket of its own, while Attention is a flag on a work ticket whose own state needs a look.

- **Rule:** an Alert has Priority *Critical*, Area `process` and Progress *ToDo* when it is created. Size
  and Risk are blank until the person who takes it triages it.
- **Rule:** every move of an Alert after creation is manual: *InProgress* when someone starts, *Review*
  when they believe it is handled, *Completed* when a human verifies it. Shipping a version never moves
  it. A person closes it.
- **Rule:** an Alert for a bypass or for a merge without changelog entries is assigned to the person who
  pushed, because they know the context. An Alert for stale planned versions is unassigned until someone
  takes it.
- For a bypass, the changelog also gets an entry that points at the Alert. What the person does with it
  is described in the guide on branching and merging, in the section on enforcement.

*Why.* A bypass is a decision that needs follow-up, and the follow-up must exist even when the person who
bypassed is too busy to remember it. An Alert makes the follow-up a ticket at the top of the queue,
instead of a note someone has to remember.

### 5.4 Examples

The automation generates these texts. The names, numbers and dates are invented for illustration.

#### Version ticket: "Version 2.4.1"

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

#### Alert ticket for a bypass: "Merge to main not identical to its branch (V2.4.1)"

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

#### Alert ticket for stale planned versions: "Stale planned Version tickets after V2.4.1"

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


---

## 6. Pull requests

### 6.1 What a pull request is

A pull request is the proposal to merge a branch into `main`. It is the place where the branch's checks
run, where discussion about the change happens, and where the lasting record of what landed stays. The
rules for using one (it is required, how it is titled, how tickets are referenced, how it is merged) are
in the guide on branching and merging; this section only defines it and says what it carries.

### 6.2 What it carries

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

### 6.3 Creating and ending one

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

### 6.4 Example

#### Pull request: "Add CSV export to the reports page"

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

## 7. The changelog

### 7.1 What it is

The changelog is a running record of every change to files, grouped by version, then by build (one per
commit), then by ticket. It is also the source the automation reads to number versions, to draft commit
messages and to update the board. How to write entries is in the guide on working and committing; this
section describes what the file contains and how it is structured.

### 7.2 The structure

```
## WIP-Version                         the open version, on a branch (a marker may follow: +V, +s, +m)
### WIP-Build                          placeholder for the commit being made
### Build 20261005143045 (branch <name>)  stamped at commit time, one per commit that logs a change
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
| `#### #123 — title` | The changes belonging to one ticket. |
| `#### REF <token> — reason` | Changes made without a ticket yet: a placeholder to be backfilled. |
| `#### AUTO-REF … (tracked as #N)` | An entry the automation wrote, pointing at an Alert. |
| `## V2.4.1 — date time UTC` | A finalized version. Newest first. |

### 7.3 Rules

- **Rule:** the changelog records changes to files and nothing else. Repository settings, tags, branches,
  secrets and git configuration are tracked in tickets, and so are known bugs and planned work. There
  are no "Known bugs" or "Planned" sections.
- **Rule:** every commit that changes files adds a build block with at least one ticket block or `REF`
  block.
- **Rule:** the newest version comes first. Stamps and everything the automation writes are UTC (see the
  guide on concepts, section 2).
- **Rule:** the topmost finalized version heading is the single source of truth for the version (see the
  guide on branching and merging).
- **Rule:** entries of commits already made are not edited, except to replace a placeholder (section
  7.4) or to make a critical correction (see the guide on working and committing).
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

### 7.4 Placeholder entries: REF and AUTO-REF

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

The procedure for backfilling a `REF` is in the guide on working and committing, and the procedure for
triaging an Alert, including its `AUTO-REF`, is in the guide on issues and the board.

### 7.5 Example

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

## 8. Branches and tags

A short recap, with no new rules. The full rules and their reasons are in the guide on branching and
merging; if the two ever differ, that guide is the reference.

### 8.1 Branches

- `main` is the one integration line. Every other branch is named in kebab-case, with no `/`.
- A branch is a **work branch** (starts from `main` and merges back), a **hotfix branch** (starts from a
  release tag and never merges), or a **parked branch** (finished work deliberately kept off `main`).
- A hotfix branch is named `hotfix-v<major>-<sub>-<mod>-<description>`, with the version's dots written
  as hyphens.

### 8.2 Tags

| Namespace | Format | Applied when |
|---|---|---|
| `archived/` | `archived/<yyyy-mm-dd>_<branch>[_<comment>]` | a merged branch is retired |
| `suspended/` | `suspended/<yyyy-mm-dd>_<branch>[_<comment>]` | a branch is set aside to resume later |
| `abandoned/` | `abandoned/<yyyy-mm-dd>_<branch>[_<comment>]` | a branch is discarded |
| `released/` | `released/V<major>.<sub>.<mod>` or `released/V<major>.<sub>.<mod>-HF<n>` | a version, or a finished hotfix, is declared a release |

The date is the UTC date of the branch's last commit when it is tagged. The optional comment is short and
in kebab-case.

### 8.3 How they fit in the map

- A branch's name appears in the changelog's build headings and in the pull request description. A tag
  records where a retired branch ended up, or which version was released.
- To find things, list a namespace: everything suspended, everything released, everything abandoned.

> **In GitHub.** Branches and tags are git branches and tags, and the tags show under the repository's
> tags and releases. `git tag -l 'suspended/*'` lists a namespace.


---

## 9. Documentation

### 9.1 The three places

Documentation lives in three places, and each answers a different question.

| Place | Holds | Kept up to date? |
|---|---|---|
| **Readme** (root) | What the project is, its requirements, and how to build and use it. The entry point: kept short, and linking to the wiki for detail. | Yes |
| **Wiki** (`doc/wiki/`) | Current-state reference pages: how the project works now. One topic per page, with a `Home` page as the index. | Yes, whenever what a page describes changes |
| **Records** (`doc/`, outside the wiki) | Point-in-time documents: design records (why something was decided), analyses and investigations, measurements. | No: dated, and not rewritten afterwards |

### 9.2 Rules

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

## 10. Who sets what

A lookup table of who is responsible for each thing. It adds no new rules.

### 10.1 The actors

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

### 10.2 Ticket fields

| Field | Developer | Project owner | Local automation | Remote automation |
|---|---|---|---|---|
| Type, Area, Origin, REF, Waiting, Size, Risk | sets | may change | | sets Type on Version and Alert tickets |
| Attention | sets *Fine* or *Acknowledged*, after deciding | sets *Fine* or *Acknowledged*, after deciding | | raises *Watch*, *Caution* and *AtRisk*, with a comment |
| Priority | proposes | sets | | |
| Progress up to *Review* | sets | may change | | advances *ToDo* and *OnDeck* to *InProgress* when code for the ticket is pushed |
| *Completed* and *Done* | sets, after verifying | sets, after verifying | | |
| *Abandoned*, *Suspended* and the abandon reasons | proposes | decides | | |
| Version (the target) | | sets | | overwrites it with the real version |
| Delivery, Build, Version#, Start and End dates | | | | sets |

*Completed* and *Done* may be set by the developer or the project owner, whoever verified the result. The
developer may also set the optional *Committed* marker in Delivery.

### 10.3 Everything else

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

### 10.4 Administration

| Item | Who does it |
|---|---|
| Repository settings, branch protection and its bypass | the administrator |
| Issue types, labels, and the board's fields and views | the administrator |
| The project token and other secrets | the administrator holds and renews them |
| Installing and updating the automation | the administrator |

The settings are listed in the new-project bootstrap guide. One person may be administrator and developer
at once.

### 10.5 Where the steps are

This guide says who is responsible. The steps, commands and scripts for doing each thing are in the
procedural guides: starting work, working and committing, syncing and merging, issues and the board, and
releases and hotfixes.

> **In GitHub.** The local automation is the git hooks kept in the repository and any scripts run on a
> developer's machine. The remote automation is the repository's workflow, which runs on pushes, on pull
> requests and on request.


### 10.6 A small team

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
