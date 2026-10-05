# Branching and Merging Strategy

This guide explains how branches are used, named and retired, and why. It is the reference the
procedural guides (starting work, syncing, merging, releases) point back to.

**How to read it.** Each topic states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides. Departing from it is
  legitimate when there is a reason.
- **In GitHub**: how the topic looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

---

## 1. Branch types

### 1.1 `main`

- **Rule:** `main` is the single integration line. There is no long-lived `develop` or staging
  branch.
- **Rule:** every merge into `main` produces a new version. When a merge lands without changelog
  entries, the automation records that itself and still assigns a version (see section 6).
- **Rule:** a release is a tag placed on `main`, never a branch.

**Why.** One line of history keeps the order of changes unambiguous. Because versions are assigned at
merge time (see *Concepts*), that order is also the order of the versions. Keeping releases as tags
means a release can be chosen after the fact from versions that already exist, without a second
long-lived line to keep in step.

### 1.2 Work branch

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

### 1.3 Hotfix branch

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

### 1.4 Parked branch

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

### 1.5 Retiring a branch: archived, suspended, abandoned

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

## 2. Naming

### 2.1 Branch names

- **Rule:** a branch is named `main` or uses `kebab-case`: lowercase words separated by hyphens.
- **Rule:** a branch name never contains `/`.
- **Rule:** a hotfix branch is named `hotfix-v<major>-<sub>-<mod>-<description>`, with the version's
  dots written as hyphens (for example `hotfix-v1-25-0-fix-sensor-timeout`).

**Why.** Branch names are embedded in tag names (section 2.2), where `/` already separates the
namespace from the rest. A `/` in a branch name would make the tag ambiguous and nest tag paths
unpredictably. One style also makes names predictable, searchable and easy to type, and the dots in a
version would break pure kebab-case, hence the hyphens.

### 2.2 Tag names

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

## 3. Where versions come from

### 3.1 When a version is assigned

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

### 3.2 What each part means

| Part | Meaning |
|---|---|
| **major** | A large redesign or a major new capability. |
| **sub** | A new feature, smaller than a major. |
| **mod** | A bug fix or a small change. |

### 3.3 How the bump is decided

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
- **Rule:** a marker applies to that one release only. The next `WIP-Version` heading is plain
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

- *Tickets, not the merge request,* carry the bump because the tickets are where the nature of each
  change is already recorded, as a Type. A branch may hold a feature and a fix together (see
  section 1.2), which a single label on the merge request cannot express.
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

## 4. Keeping `main` clean

### 4.1 The principle

A merge into `main` should look exactly like the branch, plus the version bookkeeping on top. The
result of the merge is identical to the branch's final state.

**Why.** If `main` has moved while a branch was away, merging the branch back becomes a real
three-way merge. Any conflict is then resolved for the first time on the shared line, at the moment
of landing, and untested. Everything below exists to move that work onto the branch, where it can be
done deliberately and checked before it reaches `main`.

### 4.2 Sync before merging

- **Rule:** a branch is brought up to date with `main` before it is merged, whether or not git
  reports a conflict.

**Why.** A conflict-free merge is only a textual statement. It says nothing about whether the
combined code behaves correctly. Changes that look unrelated can still interact through shared
resources: memory, peripherals, timing, voltage levels on a line, power draw, and similar. Nothing in
the text of the changes will show that. This matters more for software that runs unattended, as
firmware does: nobody is there to notice a fault or restart the device, so it has to work correctly
the first time, and anything that removes risk before a change lands on `main` is worth its cost.

### 4.3 Sync by merging, never by rebasing

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

### 4.4 Resolve conflicts on the branch

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

### 4.5 After a sync: recompile, and retest in proportion

- **Rule:** after a sync that brought changes in from `main`, recompile before going further.
- **Strong recommendation:** retest in proportion to what came in. The developer judges how
  different the incoming changes are from what the branch started with: a changed log message is not
  a change to a module the branch also touches. When in doubt, even a small doubt, retest.

**Why.** A clean merge is not proof that the code still builds, and the sync is what creates the
combined code: only building and running it on the branch verifies what will land on `main`.
Compilation is done locally by the developer and nothing else compiles the code, so skipping it
leaves no other check.

### 4.6 Enforcement

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

## 5. How a branch lands

### 5.1 Through a pull request

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

### 5.2 Merge commits only

- **Rule:** a branch is merged with a merge commit. Squash merging and rebase merging are not used.

**Why.** This is the same reasoning as for never rebasing (section 4.3). Every commit on the branch
carries its build stamp and the tests that were run against it. A squash replaces all of them with one
new commit that was never built or tested as such. A rebase merge rewrites them with new identities.
A merge commit keeps every tested commit exactly as it was, so what reached `main` is what was tested.

### 5.3 What the merge looks like

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

## 6. Enforcement

### 6.1 The principle

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

### 6.2 Three layers

1. **Warn.** Checks and local reminders say when a rule is about to be broken. They never block, and a
   missing tool or an error in a check lets the work continue.
2. **Bypass.** The developer may go around a warning on purpose: merge anyway, push straight to `main`,
   or skip the local checks.
3. **Record.** The more serious bypasses are detected automatically afterwards and logged, so that a
   person reviews them.

### 6.3 What is detected and recorded

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

### 6.4 What cannot be checked

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

### 6.5 When you need to bypass

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
