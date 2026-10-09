# Issues and the Board in Practice

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

## 1. Triage and planning

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

### 1.1 Rules

- **Rule:** triage is done by someone holding the project owner role.
- **Rule:** a ticket does not leave triage without a Type and a Size.
- **Rule:** abandoning a ticket needs a Resolution and a comment.
- **Recommendation:** triage new tickets regularly, so that none sits unlooked-at.

**Why.** Triage keeps the board honest. A ticket without a Type or a Size cannot be planned or numbered
correctly, and a dropped ticket with no reason invites someone to raise it again. Putting triage in one
role means someone is responsible for every new ticket being looked at, instead of everyone assuming
somebody else did.


---

## 2. Working the board

### 2.1 What to look at, in order

1. **Alerts.** Open tickets of Type *Alert*. Each is *Critical* and is waiting for a person.
2. **Attention.** Tickets with an open flag: *AtRisk*, then *Caution*, then *Watch* (section 2.4).
3. **Waiting.** Tickets marked *Needs input*. Has the answer arrived? If so, clear it. If a ticket has waited
   a long time (the automation flags two weeks), ask again or decide without the answer.
4. **Review.** Tickets awaiting verification. Verify them (section 3).
5. **Fix.** Tickets whose fields contradict each other (section 2.5). Correct the field; the ticket drops out
   by itself.
6. **InProgress.** Yours should tell the truth. A ticket nobody has touched for about a month should be
   updated, suspended or abandoned.
7. **OnDeck.** What is next. Pick one.
8. **ToDo.** Anything new that has not been triaged goes through section 1.

Items 1 to 5 are the things that need a person, and three views list them (section 2.2): *Decide* (items 1
and 2), *Follow up* (items 3 and 4) and *Fix* (item 5).

### 2.2 Saved views

The board has seven saved views, in this order:

- **All:** every item on the board, test tickets and pull requests included, with all its fields and in
  ticket-number order, with no gap in the numbers, for finding anything and for audit.
- **Backlog:** a board of the tickets at *ToDo*, *OnDeck* and *Suspended*, the most urgent first.
- **Board:** the active work, with the columns *OnDeck*, *InProgress* and *Review* and a row for each Version,
  so you see what each version holds and where each ticket is.
- **Decide:** what the automation noticed and a person must judge: tickets with an open Attention flag
  (*Watch*, *Caution* or *AtRisk*) and open Alerts. Start a work session here.
- **Follow up:** the ordinary queues: tickets marked *Needs input*, and tickets at *Review* awaiting
  verification.
- **Fix:** tickets whose fields contradict each other. The refresh lists the broken rules in each ticket's
  Fix field and this view shows every ticket that has any (section 2.5).
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

### 2.3 Rules

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

### 2.4 Attention flags

What the field is, and when the automation raises it, is in the guide on project structure (section 4.3).
This section is what to do with an open flag. A broken field rule is not a flag: it shows in *Fix* and needs
nothing but the correction (section 2.5).

The steps:

1. **Read the comment** the automation left: why it raised the flag, and for new work, which build.
2. **Decide what is true.**
   - *New work on a finished ticket:* if the new work belongs to the ticket, reopen it (section 4.3). If
     it is a separate piece of work, leave the ticket as it is and create a ticket for the new work. If it
     was only an adjustment from syncing `main` after the ticket reached *Review*, confirm that and set *Fine*.
   - *A stale ticket:* update it, complete it if the work is in fact done and verified, suspend it, or
     abandon it.
   - *A long wait:* ask again, or decide without the answer, and clear Waiting.
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

### 2.5 The conditions the board shows

Everything the board draws attention to is a *condition*, and each has one of three natures, which is also
the view it shows in. The list below is the registry in `conditions.py`; a new condition is one new entry
there.

| Id | Name | View | Cleared by |
|---|---|---|---|
| `stale` | Stale | Decide | a person decides (Fine or Acknowledged) |
| `waited-too-long` | Waited too long | Decide | a person decides (Fine or Acknowledged) |
| `new-work-on-finished-ticket` | New work on a finished ticket | Decide | a person decides (Fine or Acknowledged) |
| `passed-version` | Aimed at a passed version | Decide | a person decides (Fine or Acknowledged) |
| `open-alert` | Open Alert | Decide | a person, through InProgress, Review and Completed |
| `waiting` | Waiting | Follow up | a person, when it is answered; always at Completed or Abandoned |
| `review` | Review | Follow up | a person: Completed with Done, or back to InProgress |
| `completed-without-done` | Completed without Done | Fix | nobody: it goes when the fields agree again |
| `abandoned-without-reason` | Abandoned without a reason | Fix | nobody: it goes when the fields agree again |
| `open-with-resolution` | Open with a Resolution | Fix | nobody: it goes when the fields agree again |
| `open-with-end-date` | Open with an End date | Fix | nobody: it goes when the fields agree again |
| `waiting-on-closed` | Waiting on a closed ticket | Fix | nobody: it goes when the fields agree again |
| `backfilled-without-ref` | Backfilled without a REF | Fix | nobody: it goes when the fields agree again |
| `completed-without-delivery` | Completed without a Delivery | Fix | nobody: it goes when the fields agree again |
| `shipped-without-version` | Shipped without a Version | Fix | nobody: it goes when the fields agree again |
| `issue-open` | Issue still open | Fix | nobody: it goes when the fields agree again |
| `issue-closed` | Issue closed too soon | Fix | nobody: it goes when the fields agree again |

- **Decide** conditions are judgments: a person looks, acts and closes the flag (section 2.4).
- **Follow up** conditions are queues that people set and clear in the course of the work.
- **Fix** conditions are not judgments. A rule that spans fields (guide on project structure, section 4.4) is
  true or false from the ticket's other fields, so the refresh lists the broken ones in the ticket's Fix
  field and removes each when it stops being true. Nobody closes it: correct the field. A ticket with two
  broken rules keeps both ids until both are put right.
- The refresh runs after a merge to `main`, on every scheduled run and on request, and an *Implemented*
  ticket waiting for its Version is attached just before it, so it is not shown as broken. A change to a
  board field alone starts no run: if Fix still shows a ticket you have just corrected, it goes at the next
  refresh, or ask for one (the workflow mode `conditions`).


---

## 3. Review and verification

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

### 3.1 Rules

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

## 4. Suspending, abandoning and reopening

### 4.1 Suspend

Use it when the work will not be addressed soon but is expected back.

1. **Propose it,** with a comment saying why, what is left, and what would be needed to resume. The
   project owner decides.
2. **Set Progress to *Suspended*.** Resolution stays blank, and the issue stays open.
3. **If the ticket has a branch,** suspend the branch too (see the guide on releases and hotfixes,
   section 3).
4. **To resume,** set Progress back to *InProgress* (or *OnDeck*), and recover the branch if it was
   retired (see the guide on starting work, section 3.4).

### 4.2 Abandon

Use it when the work is not going ahead.

1. **Propose it.** The project owner decides.
2. **Set Resolution** (*Duplicate*, *Invalid*, *WontFix*, *Superseded* or *Obsolete*) and a comment
   linking any related ticket.
3. **Set Progress to *Abandoned*** and close the issue. Clear Waiting.
4. **If the ticket has a branch,** abandon the branch too (see the guide on releases and hotfixes,
   section 3). The automation then sets the tickets' Delivery to *Dropped*.

### 4.3 Reopen

A *Completed* or *Abandoned* ticket needs more work.

1. **Set Progress back** to *InProgress*, or to *ToDo* or *OnDeck* if it is not started.
2. **Clear Resolution,** and reopen the issue. The automation clears the End date at its next sweep. If
   the automation raised an Attention flag for the new work, set it to *Acknowledged* and say the ticket
   was reopened (section 2.4).
3. **Add a comment** saying why.

### 4.4 Rules

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

## 5. Alerts

What an Alert is, and how it is created, is in the guide on project structure (section 5.3). This section
covers who takes it and what to do with it.

### 5.1 Who takes an Alert

- **A bypass, a merge that landed without changelog entries, or a changelog that could not be read:** the
  Alert is assigned to the person who pushed, who triages it.
- **Stale planned versions:** the Alert starts unassigned. Planned Version tickets belong to the project
  owner role (see the guide on project structure, section 10), so someone holding that role takes it.

### 5.2 Triage

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

### 5.3 Moves

An Alert is *Critical* and starts at *ToDo*. Every move is manual: *InProgress* when someone starts,
*Review* when they believe it is handled, *Completed* with Resolution *Done* when a human has verified it.
Shipping a version never moves it. The person who takes it sets its Size and Risk when triaging.

*Done* means that something was done beyond analysing the Alert, for example documenting the change. An
Alert that analysis shows to be wrong is *Invalid*.

### 5.4 Rules

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

## 6. Planning ahead with versions

### 6.1 Target versions

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

### 6.2 Planned Version tickets

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

### 6.3 Rules

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

## 7. Housekeeping

### 7.1 A regular board review

Go through these regularly. Each item has its own rule elsewhere, so this section is the list. The
automation's Attention flag already catches stale tickets and long waits (section 2.4), and the *Fix* view
lists broken field rules at any time (section 2.5). This review is for the rest, and for tickets whose flag
was closed without a decision.

1. **Stale tickets:** no activity for about a month at *InProgress* or *OnDeck*, or a week at *Review*. Update,
   suspend or abandon them, or verify the ones at *Review* (sections 2 and 3).
2. **Long-suspended tickets:** resume them or abandon them (the automation flags six months).
3. **Tickets that have waited a long time** (the automation flags two weeks): ask again, or decide
   without the answer.
4. **Field consistency,** using the cross-field rules (see the guide on project structure, section 4.4). The
   *Fix* view lists the tickets that break them, and each ticket's Fix field names the rules (section 2.5).
   There should be none: correct each.
5. **Labels:** the Area list and `dummy` are fixed. Remove strays and duplicates.
6. **Planned Version tickets:** closed if dropped, and none left behind for versions already passed.
7. **Branches:** merged branches not yet retired (a week or two up to about a month), and parked branches
   about a month old (suspend or abandon them).
8. **Placeholders:** search the changelog for `REF` entries that have not been backfilled, and backfill
   them.
9. **Board configuration:** the fields and their values match the standard.

### 7.2 Rules

- **Rule:** someone holding the project owner role runs the board review, and someone holding the
  administrator role checks the board configuration.
- **Recommendation:** do the board review regularly.
- **Recommendation:** start the review in the *Fix* view, which lists every ticket that breaks a rule, and
  then look at *Decide*, so that the review is a quick look.

**Why.** Each rule is applied by a person at the moment they act, and nothing checks the whole board. The
review is where drift is caught: a ticket left in a state that stopped being true, a field that no longer
agrees with another, or a branch nobody decided about. A suspension that never ends is an unmade decision,
and so is a branch parked for months.

> **In GitHub.** Each condition view is one short filter: *Fix* is `has:fix`, because the refresh writes the
> broken rules into a field and no filter has to repeat them. A view filter may be at most 512 characters,
> and a filter that repeated every rule had reached that limit.


---

## 8. Checklist

A one-page summary of the guide. It adds no new rules.

**Triage a new ticket** (section 1)

- [ ] I checked for a duplicate. If there was one, I linked it and abandoned the new ticket with
      Resolution *Duplicate*.
- [ ] It has a Type, a description with enough detail, and a Size, or I commented and set Waiting.
- [ ] Priority is set (it defaults to *Normal*).
- [ ] It is in the right place: *ToDo*, *OnDeck*, or *Abandoned* with a Resolution and a comment.
- [ ] A target Version is set if it is aimed at one.

**Each work session** (section 2)

- [ ] I looked at *Decide* first (Alerts, then Attention flags), then *Follow up* (Waiting and Review) and *Fix*,
      and then InProgress, OnDeck and ToDo.
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
