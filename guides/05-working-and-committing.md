# Working and Committing

This guide covers the work itself, once a branch exists: the rhythm of working, how to write the changelog,
which documentation to update as you go, how to build and test, how to commit, how to turn a placeholder
into a real ticket, and how to keep the ticket current. The pieces it refers to (tickets, fields, the
changelog) are defined in the guide on project structure, and the steps for starting a branch are in the
guide on starting work.

**How to read it.** Each topic states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

## 1. The rhythm of work

Work goes in small logical steps. Each step has the same shape: change, build, test in proportion, log the
change in the changelog, commit.

- **Rule:** every commit builds. Compiling is done locally by the developer, and nothing else compiles
  the code.
- **Rule:** every commit that changes files adds a build block to the changelog, with at least one ticket
  block or `REF` block.
- **Recommendation:** commit when a logical step is complete and verified, not only at the end of the day.
- **Recommendation:** do not mix unrelated changes in one commit.

**Why.** Each commit is a point you can return to, and its build stamp is the evidence of what was tested.
Small commits make a failure traceable to the step that caused it. A commit that mixes unrelated changes
is hard to trace and hard to undo.


---

## 2. Writing changelog entries

### 2.1 What an entry is

An entry describes the changes to files made in this commit, one block per ticket. The ticket says *why*
the work exists, and the entry says *what changed in the files*.

### 2.2 How to word a bullet

- Each bullet is one concrete change. It starts with the file or component, then says what changed.
- Add what it was before when that clarifies ("Previously …"), and the reason when it is not obvious from
  the ticket.
- Code, tests and documentation get their own bullets, so a reader can see that all three were handled.

### 2.3 Rules

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

### 2.4 A change that serves several tickets

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

### 2.5 Correcting an earlier entry

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

## 3. What to update as you go

### 3.1 The principle

- **Rule:** the documentation a change affects is updated in the same change, and merged in the same pull
  request.
- **Rule:** new logic comes with tests, written alongside it and not afterwards.
- **Recommendation:** update documentation as you make the change, not at the end.

**Why.** A wiki or readme that is changed together with the code cannot quietly go stale, and tests
written with the logic describe what it was meant to do.

### 3.2 The checklist

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

## 4. Building and testing

### 4.1 Before a commit

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

### 4.2 Testing

Testing helps, and the higher the risk of a change, the more it helps. How much to test is the
developer's judgment, and recording results is a strong recommendation (section 4.3). After a sync that
brought in changes, recompiling is a rule and retesting is a strong recommendation (see the guide on
branching and merging, section 4.5).

### 4.3 Recording results

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

### 4.4 Trying an automation change

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

## 5. The commit

### 5.1 Staging and the hooks

Stage by logical change, with each change's changelog entry in the same commit. When you commit, two
hooks run: one stamps the build in the staged changelog, and one drafts the commit message from the
entries you wrote.

The hook stamps a `### WIP-Build` placeholder that is already there; it does not add one. So before each
commit that logs a change, put a fresh `### WIP-Build` heading directly under the open `## WIP-Version`
heading, above the builds already stamped, and write that commit's ticket blocks under it. The first
commit of a branch uses the placeholder opened in the guide on starting work; every later commit needs its
own.

```
## WIP-Version
### WIP-Build                              the new commit's entries go here
#### #201 — Add CSV export to the reports page
- reports page: the Export button now keeps the report's column order.
### Build 20261006091200 (branch csv-export)   the earlier commit, already stamped
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
```

### 5.2 The message

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

### 5.3 What not to rewrite

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

## 6. Placeholders and backfill

A placeholder entry (`REF`, or `AUTO-REF` written by the automation) records that a change happened before
its ticket or description existed. It is a loan, and this section is how it is repaid.

### 6.1 Backfilling a REF

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

### 6.2 Triaging an Alert and its AUTO-REF

1. Confirm that the merged result was built and tested.
2. Document what changed, in place or in a new block under the Alert's ticket, as above.
3. Comment on the Alert with what you found.
4. Move it to *Review*; a human completes it.

### 6.3 Rules

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

## 7. Keeping the ticket current

### 7.1 What to keep current

| Item | What to do |
|---|---|
| **Progress** | *InProgress* while you work. *Review* when the work is done and ready to merge. Back to *InProgress* if a review fails. You propose *Suspended* or *Abandoned*, and the project owner decides. A human who verified the result sets *Completed*. |
| **Waiting** | Set it when you need someone's input, with a comment saying what is needed and from whom. Clear it when the answer arrives. |
| **Attention** | If the automation raised it on your ticket, read its comment, decide what is true (reopen, leave as it is, correct a field, or abandon), act, and then set *Fine*, or *Acknowledged* if it is handled elsewhere. |
| **Comments** | Record decisions, findings and changes of scope as they happen. The solution and its discussion belong here. |
| **Size** | Correct it when you learn the work is bigger or smaller, and say why in a comment. |
| **Risk** | Revise it before moving the ticket to *Review*. |
| **Work that splits** | If it turns out to be several independent changes, split them into separate tickets. |

### 7.2 Rules and recommendations

- **Rule:** set Waiting together with a comment, and clear it when answered.
- **Rule:** revise Risk before moving to *Review*.
- **Rule:** *Completed* is set only by a human who verified the result.
- **Recommendation:** update the ticket whenever its state changes, so it tells the truth when you stop
  for the day.
- **Recommendation:** move a ticket to *Review* before the merge, once the work is done and ready to merge.
  The automation then has nothing to change when the version is finalized.
- **Recommendation:** deal with an Attention flag on your ticket when you see it, and close it only after
  deciding. A flag closed without acting is not raised again for the same situation, so nothing will remind you.
- **Recommendation:** comment on decisions and scope changes as they happen, not afterwards.
- **Recommendation:** when you correct a Size, say why.

**Why.** The board and the tickets are how the team sees the project. A ticket that says "in progress"
when the work is finished, or that hides a decision made in a conversation, makes the next person start
from zero. Moving to *Review* before the merge keeps the order of events simple: the ticket says the work
is done, the pull request lands it, and the version records it.

### 7.3 Before moving a ticket to Review

- ☐ The changelog entries are complete.
- ☐ The tests that matter and their results are recorded, naming the build (section 4; a strong
  recommendation).
- ☐ The documentation the change affects is updated (section 3).
- ☐ Risk is revised.


---

## 8. Checklist

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
