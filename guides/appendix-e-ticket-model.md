# Appendix E: Ticket model

The design of a ticket as a whole: the questions a ticket answers, why each has its own field, how the
fields work together, and the life of a ticket from creation to release. The values of every field are in
*Appendix C: Ticket fields reference*, and the rules and their reasons are in section 4 of *Project
structure*. This appendix is the picture that ties them together.

---

## 1. The idea

A ticket is a record of one thing to be done. Everything worth knowing about it falls into a small number of
separate questions, and each question gets its own field. Keeping them apart is deliberate: a field that
answers two questions ends up meaning two things (for example, "in progress" cannot also say whether the
code has shipped).

| Space | Question | Where it lives (GitHub) | Set by |
|---|---|---|---|
| **Type** | What sort of ticket is this, and why is the change being made? | the issue type | a person (the automation for Version and Alert tickets) |
| **Area** | What kind of work does it involve? | labels, several per ticket | a person |
| **Origin**, **REF** | Was it created after the work, and which placeholder did it replace? | board fields | a person |
| **Progress** | Where is the work? | the board's Status field | a person (the automation only advances *ToDo* and *OnDeck* to *InProgress*) |
| **Waiting** | Is it waiting for someone's input? | board field | a person |
| **Attention** | Has its state been looked at, and is it sound? | board field | the automation raises flags; a person closes them |
| **Resolution** | How did it end? | board field | a person |
| **Delivery** | Where is the delivered work? | board field | the automation (apart from *Committed* and *Implemented*) |
| **Planning** | How urgent, how big, how risky, which version and build, when? | Priority, Size, Risk, Version, Build, Version#, Start date, End date | a person, except Build, Version#, the real Version and the dates |

Two principles decide who sets a field. **Judgment belongs to people, facts belong to the automation**:
whether the work is done, verified or urgent is a person's call, while where the code is, which build it is
in and when it was noticed are facts the automation records.

## 2. Why each space is separate

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

## 3. The life of a work ticket

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
  *Dropped* returns Delivery to *Pushed*. If the ticket is *Completed*, *Abandoned*, *Review* or *Suspended*
  and its earlier work was already pushed or delivered (recognised by a recorded Build older than the one
  being pushed, or by Delivery *Implemented*), the automation raises Attention *Caution* rather than
  changing Progress, and a person decides.
- **No file change.** A ticket whose work is a setting, a secret or a check that was run has no changelog
  entries. When its work is in effect a person sets Delivery *Implemented* and its Version, and the
  automation attaches it to that version's Version ticket.
- **Late tickets.** A ticket created after the work has Origin *Backfilled* (with REF) or, for history from
  before the process, *Backdated*.

### Attention

Attention is a separate, parallel track on a work ticket. It starts blank. The automation raises *Watch*
(no activity for too long, or waiting for input for two weeks) or *Caution* (new work on a ticket that looked
finished, or a broken field rule), with a comment saying why. A person looks and sets *Fine* (nothing wrong,
or put right) or *Acknowledged* (something has to be done, and it is handled elsewhere). Setting it changes
nothing else.

## 4. How the fields hold together

These are the rules that span fields (the full table is in *Project structure*, section 4.4).

| When | Then |
|---|---|
| Progress is *Completed* | Resolution is *Done*, the issue is closed. |
| Progress is *Abandoned* | Resolution is one of the reasons, the issue is closed. |
| Progress is open (*ToDo*, *OnDeck*, *InProgress*, *Review*, *Suspended*) | Resolution and End date are blank, the issue is open. |
| A ticket is *Completed* or *Abandoned* | Waiting is cleared. |
| Origin is *Backfilled* | REF names the placeholder it replaced. |
| Code is merged or released | Delivery says so, whatever Progress and Resolution are. |
| A ticket has no file change and its work is in effect | Delivery is *Implemented* and Version names its version. |

## 5. Special tickets

Version and Alert tickets are created by the automation. They are exempt from the rule that every ticket
gets a Size, and only some fields apply to them (the table is at the end of Appendix C).

### Version tickets

A bookkeeping record for one version, titled `Version X.Y.Z`, or `Version X.Y.Z-HFn` for a hotfix. It has no
Progress: its Delivery describes its life.

| Stage | Delivery | Issue |
|---|---|---|
| **Planned** (optional, not recommended; created by a person) | blank | open |
| **Finalized** (created or reused by the automation at finalize) | *Merged* | closed by the automation |
| **Released** | *Released* | stays closed |
| **Planned, then dropped** (marked by a person) | *Dropped* | closed, with a comment saying what replaced it |

A hotfix version goes straight to *Released*, because a hotfix is never merged into `main`. At finalize the
automation writes the description (date, bump and why, pull request, tickets with their Type) and attaches
the version's tickets, and any *Implemented* ones, as sub-issues, so the board shows how many are complete.
A planned Version ticket whose number is lower than the one just finalized can no longer happen, and the
automation raises one Alert listing them. Aiming a ticket at a future version needs no planned Version ticket (its
Version field is enough), and leaving the Version tickets to the automation keeps them in the order the versions
shipped, which the Versions view relies on.

### Alert tickets

A real check that a person must do, raised for a detected bypass, a merge without changelog entries, or
stale planned versions. It has Priority *Critical*, Area `process` and Progress *ToDo* at creation. Every
later move (*InProgress*, *Review*, *Completed*) is manual, and shipping a version never moves it. A bypass
or a merge without entries is assigned to the person who pushed; an Alert for stale versions is unassigned
until someone takes it. Size and Risk are set by whoever triages it. Alerts have no Attention.

## 6. How the model drives the automation

- **Version numbers.** The Type of each ticket in a version decides the bump: any *Feature* or
  *Enhancement* gives a sub-version, otherwise a mod; *Version* and *Alert* are ignored; markers `+V`, `+s`
  and `+m` override it.
- **Delivery, Version, Build and dates** are written by the automation from pushes, merges, releases and a
  sweep that runs after each finalize and once a day. The daily run also sets Version# on any ticket that has a
  Version, so a ticket only aimed at a version sorts with the others.
- **Attention** is raised from the same sweep and from pushes.
- **Nothing in Area, Risk, Priority or Size** drives any rule.

## 7. Where each part is defined

| To see | Read |
|---|---|
| Every value and who sets it | *Appendix C: Ticket fields reference* |
| The idea and rules of each field | *Project structure*, section 4 |
| Version and Alert tickets in full, with examples | *Project structure*, section 5 |
| How version numbers follow the Types | *Branching and merging strategy* |
| Creating a ticket and keeping it current | *Starting work* and *Working and committing* |
| Review, verification and the daily board | *Issues and the board in practice* |
| Example tickets | *Appendix D: Ticket examples* |
