# Adopting the Standard in an Existing Project

This guide is the procedure for bringing a project that already exists, with its history, branches, tags,
issues and habits, into line with the standard. It does not repeat how each piece is set up: the guide on
new-project bootstrap holds the settings, the automation, the labels and the board, and the other guides hold
the rules. This one says what is different when the project is not empty: what to measure, what can be changed,
what can only be accepted, and in what order to do it. The measure is the audit tools (see the wiki page on
them), and appendix G says what to do about each finding.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Roles, and responsible, not necessarily manual.** Most steps that change repository, organization or board
settings belong to the administrator role; the rest belong to the developer. One person may hold several
roles. Where this guide names a role it means the person responsible; the step may be done by hand, by an
assistant, or by a script or command that person runs, and it is still that person's action.

---

## 1. The principles

An existing project cannot be made to look as if it had followed the standard from its first commit, and it
should not try. These rules say how adoption stays honest.

- **Rule:** history is never rewritten to make a rule pass. No rebase, squash, filter or force-push of
  `main` or of any published branch, and no tag moved. The past stays as it was, and what differs is
  recorded.
- **Rule:** the standard applies from a **cut-over**: the commit at which the adoption lands on `main`.
  Before it, deviations are history. After it, a deviation is a failure like any other.
- **Rule:** the adoption goes through the normal flow it introduces: a ticket per piece of work, an adoption
  branch, a changelog entry, a pull request and a merge commit. It is not done by pushing to `main`.
- **Rule:** the audit is the measure. The project is adopted when a re-audit reports no failed rule after the
  cut-over, and every other deviation is recorded with a reason (section 3).
- **Rule:** changes to repository, organization and board settings are made only by the administrator, or by
  an assistant the administrator told to (guide on working with an AI assistant). The audit tools only read.
- **Recommendation:** work in the order of section 4. Each stage depends on the ones before it, and the cheap,
  reversible ones come first.
- **Recommendation:** keep the project working. Work in progress continues; the adoption is planned around it
  (section 2), not the other way round.

**Why.** A standard that asked projects to falsify their past would be abandoned, and one that ignored the
past would never let a project reach a clean report. Separating "what the project did" from "what the project
does from now on" keeps both true. Using the normal flow for the adoption proves, with the first real merge,
that the project now works the way the standard says.

---

## 2. Before you start (stage 0)

Decide these and write them in the adoption ticket (a ticket of its own, with a sub-ticket per stage if the
project owner wants the stages tracked separately).

1. **Run the audit first and keep it.** Run the audit tools against the project and keep the report as the
   starting point (`audit.py <project> --md before.md --json before.json`). It shows how far the project is,
   and it is what the final report is compared with.
2. **Choose the cut-over.** It is the merge of the adoption pull request. Nothing needs to be dated in
   advance, but the team must know that from that merge the rules apply.
3. **Decide how the version continues.** The topmost finalized version heading of the changelog is the
   single source of truth (guide on branching and merging, section 3.1). Take the project's current version,
   write it in the form `V<major>.<sub>.<mod>` without padding, and the next merge continues from it. A
   project with no version of its own starts at `V0.1.0` as a new project does (guide on new-project
   bootstrap, section 7.1).
4. **Take a backup.** A mirror clone of the repository (`git clone --mirror`), kept outside the project, so
   nothing done in the next stages can lose anything.
5. **Settle the open work.** List the open branches and pull requests. Branches that will keep going are
   brought up to date with `main` after the adoption lands (guide on syncing and merging, section 1). Branches
   nobody will resume are retired in stage 4. Changes that rewrite every file (line endings, stage 2) wait
   until no branch is mid-conflict.
6. **Record the roles.** Who holds the administrator, project owner and developer roles (guide on new-project
   bootstrap, section 7.2).

- **Rule:** the audit report, the cut-over, the version the project continues from and the backup exist
  before any stage starts.
- **Rule:** a project with more than one deployment line, such as a `develop` or `staging` branch, decides
  here which commit becomes `main` (section 5.1).
- **Recommendation:** announce the cut-over to everyone who pushes to the repository, with the date and what
  changes for them (merge commits only, hooks, tickets, branch names).

**Why.** Every later decision depends on these. The backup removes the fear that makes people skip a step, and
the first audit is the only way to show progress later.

> **In GitHub.** `git clone --mirror <url> backup.git` makes the backup. `python tools/audit.py <project>
> --md before.md --json before.json` makes the first report (add `--offline` if `gh` is not available yet).
> After the cut-over, `--since <cut-over commit>` judges the history from there.

---

## 3. Triage the report

Every finding of the audit falls into one of four classes. The class decides what is done with it.

| Class | Meaning | What is done | Example |
|---|---|---|---|
| **Fix now** | A missing or wrong thing that can be put right cheaply and without harm. | Do it in its stage. | No `.githooks/` folder. |
| **Convert** | Existing material in the wrong form, changed once. | Do it in its stage, with care for what points at it. | Tags named `v1.2`; labels not on the list; a changelog in another format. |
| **Accept as history** | The past, which cannot change without rewriting history. | Record it with a reason; do not touch it. | Commits on `main` that are not merges; `fix:` subjects. |
| **Not applicable** | A rule the project has a real reason not to follow. | Record it with the reason, and have the project owner agree. | No GitHub wiki, because the plan does not offer one. |

- **Rule:** an accepted or not-applicable deviation is recorded in the project, in the file
  `.github/audit-baseline.json`, with the check it belongs to, the reason, the date and who agreed. A
  deviation nobody recorded is a failure.
- **Rule:** only a deviation in the past, or one the project owner agrees is not applicable, may be accepted.
  A deviation that is still being made (a direct commit after the cut-over) is a failure to fix, never to
  accept.
- **Recommendation:** accept the smallest set. A deviation that can be fixed without rewriting history is
  fixed.
- **Recommendation:** run the audit with `--since` (the cut-over, as a date or a commit) to judge the history
  only from there, and keep the baseline file for what is left. The audit shows the recorded deviations as
  accepted, and reports an entry that accepts nothing any more. Both are described in the wiki page on the
  audit tools.
- **Recommendation:** read the adoption plan at the end of the audit report: it groups the open findings by
  stage, with their class and role, in the order of this guide.

Appendix G lists every finding the audit can report, with the class it usually has, the stage that deals
with it, what to do, who does it and whether it can be undone. Use it as the work list: go through the report
finding by finding.

**Why.** Four classes keep the work small and the record honest. Most findings fall in the first two and are a
matter of doing the stages; the third is the one that would otherwise make adoption look impossible, and
writing it down turns an unfixable failure into a known fact.

---

## 4. The stages

Do the stages in order. Each ends with a re-run of the audit for the area it covers, and a check that the
project still works (the build, the tests, a push).

### 4.1 Stage 1: GitHub settings

Administrator. These settings do not change the code, and most can be undone, so they come first.

1. **Ownership.** Issue types exist only in an organization. If the repository belongs to a person, either
   transfer it to an organization (the administrator decides who owns it; links to the old address are
   redirected by the host, but clones should update their remote), or keep it and let the Type live in the
   board field Kind (guide on new-project bootstrap, section 5.1); the audit then judges the field and not the
   issue types.
2. **Issue types and labels.** Create the eight issue types (not for a project that keeps the Type in the
   field Kind) and the 14 Area labels and `dummy`
   (guide on new-project bootstrap, section 5). Before deleting a label that is not on the list, move its
   issues to the Area label that replaces it, because deleting a label removes it from every issue that has
   it.
3. **Merge methods and branches.** Allow only merge commits, turn off automatic deletion of head branches, and
   make `main` the default branch (guide on new-project bootstrap, section 3). Protection of `main` comes after
   the first compliant merge (stage 6), so the adoption itself can land.

- **Rule:** settings that change how the team works (merge methods, protection) are announced before they are
  changed.
- **Rule:** map every old label to an Area label (or to none) before deleting any, and write the mapping in
  the adoption ticket.
- **Recommendation:** leave the protection of `main` and the administrator bypass for stage 6.

**Why.** These are the cheapest changes, and the later stages depend on them: the board needs the types and
the labels, and the automation needs `main` and merge commits.

### 4.2 Stage 2: the adoption branch, files and automation

Developer, with the administrator for the workflow. Create one branch for the adoption (for example
`adopt-the-standard`) from an up-to-date `main` (guide on starting work, section 3). Everything in this stage
is committed on it.

1. **Line endings first, on their own.** Add `.gitattributes` with `* text=auto eol=lf` and renormalize the
   files in a commit of its own, so the change is one reviewable step. List that commit in
   `.git-blame-ignore-revs` so the history of each line stays readable.
2. **Structure.** Add what is missing of the locations in the guide on project structure (section 2.1): the
   readme, `doc/` with `doc/wiki/`, `.githooks/`, `.github/`, `tests/` where there is code, the ignore file
   and `AGENTS.md`, with the roles and the pointer to the guides.
3. **Automation.** Copy the automation files from the standard unchanged, keep the hook scripts executable,
   activate the hooks and run the tests (guide on new-project bootstrap, section 2).
4. **The changelog.** Keep the old changelog as the record of the earlier history, in `doc/` under a name
   that says so (for example `doc/changelog-before-the-standard.md`). Start the new `CHANGELOG.md` with a
   title and **one** finalized heading for the version the project continues from, with a single build and a
   `REF` block that says the earlier history is in that file. This is the only finalized heading written by
   hand. The adoption itself is logged above it in a `WIP-Version` heading, with the ticket of the adoption.
5. **Tests.** Where the automation has its own scripts, the tests come with them.

- **Rule:** the line-endings change is a commit of its own, made when no other branch is waiting to merge.
- **Rule:** the old changelog is kept, not deleted and not edited.
- **Rule:** the baseline heading is the only finalized version written by hand, and it states the version the
  project had at the cut-over.
- **Rule:** the adoption commits go through the hooks like any other (guide on starting work, section 5): the
  hooks are in place before the second commit.
- **Recommendation:** announce to other developers that they need `git config core.hooksPath .githooks` after
  the merge.

**Why.** Renormalizing mixes with nothing else, so it can be reviewed and ignored by blame. The old changelog
cannot be converted entry by entry without inventing builds and tickets it never had, so it stays as it is, and
the new one starts with a baseline.

### 4.3 Stage 3: token, board and preflight

Administrator (guide on new-project bootstrap, sections 4 and 6).

1. **The project token** is created and stored as `PROJECT_TOKEN`.
2. **The board** is created and linked to the repository, with the fields, values and views of the standard
   (`fields.py` and `views.py` create them).
3. **Run the preflight** and fix what it reports before going on.

- **Rule:** the preflight reports no problem before the adoption branch is merged.

**Why.** The first merge needs the token and the board, or the automation can finalize the version but cannot
write the tickets.

### 4.4 Stage 4: git names, branches and tags

Developer, with the project owner agreeing what is retired. These changes act on shared git state, so each is
announced.

1. **Branches.** For each branch that is not `main`:
   - one that is merged: retire it as *archived*;
   - one nobody will resume: retire it as *abandoned*;
   - one that is set aside: retire it as *suspended*;
   - one that is still active: rename it to kebab-case (create the new name, push it, move any pull request,
     then retire the old name).

   Retiring means tag first and delete second (guide on releases, hotfixes and retiring branches, section 3).
2. **Tags.** Give each existing tag a name in the standard form. A tag that marks a real release becomes
   `released/V<major>.<sub>.<mod>`. A tag with no use is left alone and recorded as history, or removed by the
   administrator when the team agrees. Put the new tag on the same commit as the old one, push it, and keep
   the old tag until everybody has moved. Then the administrator deletes the old tag (the commit stays
   reachable under the new one), or, when something outside the team depends on the name, records it as an
   accepted deviation, so the audit stops reporting it.
3. **The integration line.** A project whose real line is not `main` follows section 5.1.

- **Rule:** no tag is moved to another commit, and no branch is deleted before its tag exists.
- **Rule:** after the cut-over, every branch and tag is created in the standard form.
- **Recommendation:** do not rename tags other people or other systems depend on without telling them; record
  such a tag as accepted instead.

**Why.** Branches and tags are cheap to add and the retire procedure is already the standard's. Moving a tag
would change what a version means, so a rename is always an addition.

### 4.5 Stage 5: the tickets

Project owner, with the developers. The board lists the project's work, and it checks itself against the open
and closed state of the issues.

1. **Bring the issues onto the board.** Add every open issue, and the closed issues the team still needs (for
   example those the old changelog cites). Older closed issues may stay off the board.
2. **Give each one its fields.** The Type (the issue type, or the field Kind), the Area label, the Size and, for a closed issue, the Status
   *Completed* or *Abandoned* and a Resolution. An open issue is not *Completed* or *Abandoned*.
3. **Mark late tickets.** A ticket written now to document work that happened before the process is given the
   Origin *Backdated*; one written after the work to replace a `REF` is *Backfilled* and keeps the `REF` token
   (guide on project structure, section 4.3).
4. **Open work.** Open issues continue as they were, on the board, from their Status.

- **Rule:** every ticket on the board has a Type (an issue type, or Kind), and every work ticket has a Size (guide on project
  structure, section 3).
- **Rule:** a closed work ticket is *Completed* or *Abandoned*, and Resolution is set exactly when it is.
- **Rule:** a ticket written after the work is not given dates or builds it never had.
- **Recommendation:** triage the open backlog once, with the project owner (guide on issues and the board in
  practice, section 1), instead of editing the issues one by one.

**Why.** A board that mixes finished and unfinished work, or leaves types and sizes empty, cannot be trusted,
and the automation relies on these fields. Marking late tickets keeps the difference between tracked work and
documented work visible.

### 4.6 Stage 6: land and prove

Developer and administrator.

1. **Run level 1 of the proof** (guide on new-project bootstrap, section 8.1): the preflight, the tests, the
   finalize step in dry-run mode, and a throwaway commit to see the hooks.
2. **Open the pull request** for the adoption branch and land it as any pull request is landed (guide on
   syncing and merging, sections 2 to 5). Its merge is the **cut-over**, and the version it produces continues
   from the baseline of stage 2.
3. **Check the result** as for a first merge (guide on syncing and merging, section 5.2): the heading is
   renamed, the Version ticket lists the tickets, and the tickets show Delivery *Merged*.
4. **Turn on protection** of `main` where the plan offers it, with the administrator bypass left open.
5. **Re-audit.** Run the audit tools again. Every failed rule is fixed, or recorded as accepted or not
   applicable, and nothing the project still does wrong is among them.

- **Rule:** the adoption lands by pull request and a merge commit, and nothing is pushed to `main` for it.
- **Rule:** the project is adopted when the re-audit shows no failed rule that is not recorded under section
  3.
- **Recommendation:** keep the first and the final report in the adoption ticket, as the record of the
  work.

**Why.** The first merge is the proof that the setup does what it should, and the second audit is the proof
that the project does.

### 4.7 Stage 7: keep it

Everyone.

- **Rule:** the accepted deviations are reviewed at each release: a deviation that can now be fixed is fixed.
- **Recommendation:** re-run the audit before each release and after any change to the repository settings or
  the board.
- **Recommendation:** when the standard changes, update the automation (guide on new-project bootstrap,
  section 2.4) and re-run the audit.

**Why.** A project drifts. The audit is cheap enough to run whenever something changes.

---

## 5. Special cases

### 5.1 A line other than `main`

A project whose work is integrated in `develop`, `staging` or a release branch changes its integration line to
`main`. This is the largest change of the adoption, so it is planned on its own.

1. Agree which branch holds the current state of the project. Nothing is lost: its commits stay reachable.
2. Make `main` that state by merging the line into `main` with a merge commit, not by moving `main`.
3. Move the open pull requests to `main`, and tell everyone the old line is closed.
4. Retire the old line as *archived* once its last commit is reachable from `main`.

- **Rule:** `main` is brought up to the state of the real line by a merge, and no branch is force-pushed.
- **Rule:** the old line is retired with its tag, never just deleted.

### 5.2 Existing versions and releases

The version the project continues from is written in the baseline heading (stage 2). Releases that really
happened are tagged `released/V<major>.<sub>.<mod>` on the commits that were released, when those commits are
known (stage 4). A release whose commit is not known is not tagged: a wrong tag is worse than a missing one.

A release made before the adoption can still be fixed by a hotfix: the hotfix branch starts from its tag and
its first commit is the overlay that brings the automation and a baseline changelog (guide on releases,
hotfixes and retiring branches, section 2.1). A release without a tag cannot be fixed this way, because there
is nothing to start from.

### 5.3 Clones of the team

After the cut-over every developer updates their clone: fetch, switch to `main`, activate the hooks, delete the
local copies of the retired branches. A clone that skips the hooks is warned by the remote automation on its
next push.

### 5.4 When the plan lacks a feature

If the hosting plan does not offer branch protection or a wiki for a private repository, the matching
findings are *not applicable* and are recorded as such. A plan without issue types (a personal account) keeps
the Type in the field Kind instead (stage 1), and its findings are judged for the field. The finding stays in the report as a reminder
and is revisited when the plan changes.

---

## 6. Checklist

A one-page summary of the guide. It adds no new rules.

**Before** (section 2)

- [ ] The audit report is saved; the cut-over, the continuing version, the backup and the roles are decided;
      open branches and pull requests are settled.

**Triage** (section 3)

- [ ] Every finding has a class, and accepted or not-applicable ones are recorded with a reason, a date and who
      agreed.

**Stages** (section 4)

- [ ] 1: the repository belongs to an organization (or keeps the Type in the field Kind), the types and labels
      exist (old labels mapped first), only merge commits are allowed, `main` is the default.
- [ ] 2: line endings renormalized in a commit of its own; structure and automation in place; hooks active;
      the old changelog kept and a baseline heading written.
- [ ] 3: the token, the board and the preflight are in order.
- [ ] 4: branches retired or renamed; tags given standard names by addition; the integration line is `main`.
- [ ] 5: issues are on the board with type, label, Size, Status and Resolution; late tickets marked.
- [ ] 6: level 1 of the proof passed; the adoption landed by pull request; the first merge checked; protection
      on; the audit shows no unrecorded failure.
- [ ] 7: deviations reviewed at each release; the audit re-run when something changes.

**In one line:** audit, decide, settings, branch, board, names, tickets, land, re-audit.
