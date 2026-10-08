# Syncing and Merging

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

## 1. Sync `main` into your branch

The steps:

1. **Fetch** and look at what came in from `main`.
2. **Merge `main` into your branch.** Never rebase.
3. **If there are conflicts,** resolve them as an ordinary commit on the branch.
4. **Recompile.** Retest in proportion.
5. **Push.**

### 1.1 When to sync

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

### 1.2 Conflicts and adjustments

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

### 1.3 After syncing

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

### 1.4 When a push is rejected

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

## 2. Get ready to land

### 2.1 Before you open the pull request

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

### 2.2 Rules

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

## 3. Open the pull request

The steps:

1. **Open the pull request** from your branch into `main`.
2. **Write the title:** the branch's functional purpose, the way a version heading would read.
3. **Write the description:** paste the changelog entries of the open version, as they are, and add the
   tested build and the sync status.
4. **Check the pasted text** for closing keywords.
5. **Look at the checks.** The advisory check says whether the branch is behind `main`. If it is, go back
   to section 1.

### 3.1 The description

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

## 4. Merge

The steps:

1. **Read the checks.** The advisory check is green when the branch is up to date with `main`. If it is
   red, `main` has moved: go back to section 1 and sync again. If its comment lists a merge in your branch
   with a manual conflict resolution, confirm that the result was built and tested.
2. **Merge with a merge commit.** It is the only method available.
3. **Do not delete the branch from the merge screen.** Retire it later, tagging it first (see the guide on
   releases and hotfixes).
4. **Do not close the tickets.** Closing is a person's step after verification.

### 4.1 Rules

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

## 5. After the merge

### 5.1 What the automation does

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

### 5.2 What to check

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

### 5.3 What next

- If the tickets are not verified yet, verify them now. A human moves them from *Review* to *Completed*
  and closes them.
- Decide whether to continue the branch or retire it (see the guide on releases and hotfixes).

### 5.4 Rules

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

## 6. If you need to bypass

### 6.1 When it applies

You may merge despite a red check, or push straight to `main` without a pull request. Both are allowed, and
both are detected afterwards (see the guide on branching and merging, section 6.3):

- a direct push, with no pull request;
- a merge that is not identical to its branch's final state;
- a merge that differs from both of its parents;
- file changes with no changelog entries.

### 6.2 What to do

1. **Do it deliberately,** and say why in the pull request, the commit message or a comment on the ticket.
2. **Expect the Alert.** It is assigned to you, and the automation also writes a placeholder entry in the
   changelog. Triage it promptly (see the guide on working and committing, section 6).
3. **Pull `main` right afterwards, then build and test it.** You skipped the sync that would have caught a
   mismatch, so this is the check you owe.
4. **Never hide it,** for example by editing history. The record is what makes the bypass recoverable.

### 6.3 Rules

The rules about bypassing, including that a bypass is legitimate when there is a reason and that it is
never hidden, are in the guide on branching and merging, section 6.5. What this guide adds:

- **Recommendation:** after a bypass, build and test `main` at once.

**Why.** The system accepts that rules will sometimes be bypassed, and has a way to recover afterwards,
instead of a wall that gets forced through anyway (see the guide on branching and merging, section 6).
Building and testing `main` straight away is how you make up for the check you skipped.


---

## 7. The branch after the merge

After a merge the branch still exists, and what to do with it is the developer's choice.

| If… | Then |
|---|---|
| more work on the same feature is expected, a follow-up fix is likely, you are merging in stages, or a review failed and the ticket went back to *InProgress* | **Continue.** Sync `main` into the branch first, then open a new `WIP-Version` heading and carry on (see the guide on starting work, section 3.3). New work gets its own tickets. |
| the work is done and nothing more is expected | **Retire it,** tagging it first (see the guide on releases and hotfixes). |
| the work is set aside to resume later | **Suspend it** (see the guide on releases and hotfixes). |
| the work is being dropped | **Abandon it** (see the guide on releases and hotfixes). |

### 7.1 Rules

- **Recommendation:** do not wait too long to retire a branch whose work is merged (how long is too long
  is in the guide on branching and merging, section 1.5).
- **Recommendation:** if you continue a branch, make that a deliberate choice, not a default.

**Why.** A branch left open and forgotten hides an unmade decision, and it falls behind `main`, which makes
its next merge harder. A deliberate "continue" keeps the history clean, because the new work starts from a
synced branch with its own heading.


---

## 8. Checklist

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
