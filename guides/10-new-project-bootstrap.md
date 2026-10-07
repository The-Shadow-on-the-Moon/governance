# New-Project Bootstrap

This guide is the checklist for applying the standard to a new repository: the files and folders, the
automation, the repository and board settings, the issue types and labels, the first version, and a trial
run that proves the setup works. Most of it is work for the administrator role. The pieces it refers to
(the structure, tickets, fields, the changelog) are defined in the guide on project structure, and the
rules about versions and branches are in the guide on branching and merging.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the person decides.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Roles, and responsible, not necessarily manual.** Developer, project owner and administrator are roles.
One person may hold several, and in a small team they often do. Where this guide names a role, it means
the person responsible; the step may be done by hand, by an assistant, or by a script or command that
person runs, and it is still that person's action.

---

## 1. Create the repository and its structure

- **Rule:** a new project has the locations of the guide on project structure (section 2.1), under those
  names: the readme, `CHANGELOG.md`, `doc/` with `doc/wiki/`, `tests/` if it has code or scripts,
  `.githooks/`, `.github/`, the ignore file, and `AGENTS.md`.
- **Rule:** the changelog starts with a title line and no version heading. The first merge to `main`
  produces version `V0.1.0`: it is not a small change, and it is not a release (section 7).
- **Rule:** the readme says what the project is and how to set it up, including the one command that
  activates the hooks.
- **Recommendation:** copy the structure from an existing project that already follows the standard, or
  from a template repository, instead of creating it by hand.

**Why.** Fixed names mean a new project starts looking like every other one, and anyone can open it and
know where to look. Starting the changelog with no version gives the first merge a clean `V0.1.0`, which
is the honest description of a project's first version: something exists, and nothing has been released.

> **In GitHub.** Create the repository, then add the files and folders listed above. A template
> repository that already has them, and the automation and settings, is the natural way to start a
> project this way.


---

## 2. Install the automation

### 2.1 What it is made of

- **The local hooks,** in `.githooks/`: three small entry scripts and one shared script that stamps the
  build, drafts the commit message and warns. They need a runtime (here Python 3).
- **The remote workflow,** `.github/workflows/versioning.yml`, and its logic in `.github/scripts/`, with
  unit tests under `tests/`.
- **The saved views,** `.github/views.json` and the script `.github/scripts/views.py` that creates them
  (section 6).
- **The pull request template,** in `.github/`.
- **Optionally,** a workflow that copies the wiki pages to the hosting wiki.

### 2.2 The steps

1. **Copy the automation files** from the standard, unchanged.
2. **Keep the hook scripts executable** (on Linux the executable bit has to be committed, or git ignores
   them).
3. **Activate the hooks** with the one command in the readme.
4. **Run the automation's tests** locally.
5. **Confirm the workflow is enabled** and declares the permissions it needs in its own file: write access
   to contents, issues and pull requests.
6. **Run the preflight** (section 2.3) once the project token (section 4) and the board (section 6) exist.

### 2.3 The preflight

The preflight is the first thing the automation does, on every run and on request. It checks, before
anything else:

1. that it can **reach the repository** and has the permissions it needs;
2. that the **project token** exists and works;
3. which **board belongs to the repository**: it identifies the board from the repository and stores its
   number in a repository variable, so that nothing needs the number typed in;
4. that the board has **the fields and values** the automation needs.

When a check fails, the automation says exactly which one and why, and skips the steps that depend on it.
The version is still finalized, and the board can be corrected afterwards. If the repository has no board,
or more than one, it stops at step 3 and asks the administrator to say which.

### 2.4 Keeping in step with the standard

- A **manifest file** in the project names the version of the standard it follows, and lists a hash (a
  fingerprint) of each automation file as it is in that version.
- A **check script** compares the project's files with the manifest and reports each as unchanged, edited
  locally, or from an older version.
- To update a project, copy the new files from the standard, replace the manifest, and run the check.

### 2.5 Rules

- **Rule:** the automation is copied unchanged from the standard. The project's own values are never
  written into its files: the board is identified by the preflight and stored in a repository variable.
- **Rule:** the automation's tests are part of the repository and are run before any change to it (see the
  guide on working and committing, section 3).
- **Rule:** the preflight runs first, before any other step of the automation.
- **Recommendation:** when the standard's automation changes, copy the new version into the project and run
  the check script, and run the check when unsure whether the files still match.

**Why.** If every project edits its own copy, the copies drift apart and none of them matches the guides.
Keeping project values out of the files, and checking the files against a manifest, makes drift visible.
The preflight turns a vague failure later ("the board did not update") into a clear one at the start.

> **In GitHub.** The board is a GitHub Project, linked to the repository. Its number is stored in a
> repository variable. The manifest is a file in `.github/`, and the check script sits beside the
> automation's scripts.


---

## 3. Repository settings

### 3.1 The settings

- **Merge methods:** only *merge commit* is allowed. Squash merging and rebase merging are disabled.
- **Automatically delete head branches:** off.
- **Default branch:** `main`.
- **Branch protection on `main`,** where the plan offers it: require a pull request before merging, and
  require the branch to be up to date. Leave the administrator bypass open (do not tick "do not allow
  bypassing the above settings").
- **Actions:** enabled. The workflow declares the permissions it needs (write access to contents, issues and
  pull requests) in its own file, so the repository's default token permission may stay read-only, and an
  organization may require it to be.
- **Issues and projects:** enabled, and the board is linked to the repository.
- **Wiki:** enabled and initialized (by creating a first page) if the wiki sync is used. It may not be
  offered for private repositories on every plan.
- **Collaborators and roles:** the administrator role has admin access, and developers have write access.

### 3.2 Rules

- **Rule:** only merge commits are allowed, and head branches are not deleted automatically.
- **Rule:** the default branch is `main`, Actions is enabled, and the workflow declares the permissions it
  needs.
- **Rule:** the board is linked to the repository, so that the preflight can identify it.
- **Rule:** the preflight also reads these settings and reports any that do not match.
- **Recommendation:** use branch protection where it is available, with the administrator bypass left open.

**Why.**

- *Merge commits only* keeps every tested commit as it was.
- *No automatic branch deletion* keeps the rule that a branch is tagged first and deleted second.
- *The administrator bypass stays open* because a bypass is allowed, with an Alert as its record (see the
  guide on branching and merging, section 6).
- *The board linked to the repository* is how the automation finds it.
- *The preflight checks the settings* so that this part of the bootstrap is verified and not just trusted,
  and so that a setting changed later is noticed.

> **In GitHub.** The merge methods and the head-branch setting are under the repository's general
> settings, in the pull request section. Branch protection is under branches or rules. The default
> token permission is under Actions, in general settings, and an organization policy may fix it to read-only. The board is linked from the project's settings or
> from the repository's projects tab.


---

## 4. The project token

### 4.1 What it is and why it is needed

The automation writes to the board: it sets Delivery, Version, Build, the dates and the Attention flags,
advances a ticket from *ToDo* or *OnDeck* to *InProgress*, and it creates and closes Version tickets. The credential a workflow gets by default cannot write to an organization's board,
so the project keeps its own token, stored as a secret. The same token lets the preflight store the board's
number in a repository variable. Without it the automation still versions, and only the board steps are
skipped, with a clear message.

### 4.2 The steps

1. **Create the token** under an account that has access to the board and administrator access to the
   repository. At present that is a classic personal access token with the `project` and `repo` scopes. A
   fine-grained token can replace it once it covers the same needs.
2. **Store it as a repository secret** named `PROJECT_TOKEN`.
3. **Note when it expires** and renew it before then.
4. **Run the preflight** to check that it works.

### 4.3 Rules

- **Rule:** the token is stored only as a secret. It never goes in a file, a ticket, a comment, a commit or
  a chat, and an assistant never reads or prints it.
- **Rule:** the token belongs to an account holding the administrator role.
- **Rule:** a lost or exposed token is revoked and replaced at once.
- **Rule:** the preflight reads the token's expiry date and warns when it is close to expiring.
- **Recommendation:** give the token an expiry, and record when it expires so it is renewed in time.
- **Recommendation:** give it only the access the automation needs.

**Why.** A token that can write to the repository and the board is a powerful credential, so where it is
kept and who owns it matter more than how convenient it is. An expiry limits the damage if it leaks, and
the preflight's warning means the board does not stop updating without notice.

> **In GitHub.** The token is created under the account's developer settings. The secret is added under the
> repository's settings, in the secrets section for Actions, with the name `PROJECT_TOKEN`.


---

## 5. Issue types and labels

### 5.1 Issue types

- **Rule:** the eight issue types exist, with these names: *Feature*, *Enhancement*, *Change*, *Bug*,
  *Refactor*, *Task*, *Version* and *Alert*. Each carries its short definition from the *Ticket fields
  reference* as its description.
- **Prerequisite:** the repository belongs to an organization, because issue types are an organization
  feature.

They are set up once, by the administrator, for the organization.

### 5.2 Labels

- **Rule:** the labels are exactly the 14 Area labels: `requirements`, `research`, `design`,
  `implementation`, `assembly`, `testing`, `analysis`, `debugging`, `documentation`, `tool`, `process`,
  `config`, `content` and `build`, plus the marker label `dummy` for throwaway tickets made to test the
  automation (see the *Ticket fields reference*). There are no other labels.
- **Rule:** each label carries its meaning from the *Ticket fields reference* as its description, so the
  meaning shows wherever the label is used.
- **Rule:** the labels a new repository starts with that are not on this list (for example `bug`,
  `enhancement`, `duplicate`, `invalid`, `question`, `wontfix`, `good first issue`, `help wanted` and
  `accessibility`; the set changes over time) are deleted. `documentation` stays, because it is on the list.
  After deleting, check that exactly the 14 Area labels and `dummy` remain.
- **Recommendation:** create the labels with a script, so that every project gets the same list.

**Why.**

- The Type, Resolution, Waiting and Origin fields replace what those default labels were used for, so
  keeping them would record the same fact twice.
- A fixed list is the same in every project, so filtering and reporting by Area works across all of them.
- Allowing only the Area labels, and `dummy` as the one marker, keeps the list from growing into a second,
  unmanaged classification.

> **In GitHub.** Issue types are under the organization's settings, in the planning section. Labels are
> under the repository's issues, in the labels page, and can be created in bulk with the command line.


---

## 6. The board

### 6.1 What to create

A project board linked to the repository, with these fields. The meaning of each value is in the *Ticket
fields reference*.

| Field | Kind | Values |
|---|---|---|
| Status | single select | ToDo, OnDeck, InProgress, Review, Completed, Suspended, Abandoned |
| Origin | single select | Backfilled, Backdated |
| REF | text | |
| Waiting | single select | Needs input |
| Attention | single select | Fine (green), Acknowledged (purple), Watch (yellow), Caution (orange), AtRisk (red) |
| Resolution | single select | Done, Duplicate, Invalid, WontFix, Superseded, Obsolete |
| Delivery | single select | Committed, Pushed, Merged, Implemented, Released, Dropped |
| Priority | single select | Critical, Urgent, High, Normal, Low, Wishlist |
| Size | single select | XS, S, M, L, XL |
| Risk | single select | 1 Very low, 2 Low, 3 Medium, 4 High, 5 Very high |
| Version | text | |
| Build | text | |
| Version# | number | |
| Start date, End date | date | |

Type is the issue type and Area is labels, so neither is a board field. Every field above is a kind that a
script can create.

**Saved views:** All, Backlog, Board, Health and Versions (see the guide on issues and the board in practice,
section 2). They are defined in `.github/views.json` and created with `.github/scripts/views.py`, which is a dry
run until it is given `--apply` and needs the project token; run it once the fields exist.

### 6.2 Rules

- **Rule:** the board has exactly these fields with these values. The built-in Status values of a new
  board are replaced with the ones above.
- **Rule:** Build is a text field, not a number, because a build timestamp is too large for a number
  field.
- **Rule:** the board is linked to the repository, and the preflight checks the fields and their values.
- **Rule:** the saved views are the ones in `.github/views.json`, created by `views.py`, and a view is changed
  by changing the file and running the script again.
- **Recommendation:** create the fields with a script, or start from a template board that already has
  them, so that every project gets the same board.

**Why.** The automation reads and writes these fields by name, so a board that differs breaks it, and a
build timestamp stored in a number field is rejected by the hosting service.

> **In GitHub.** The board is a GitHub Project owned by the organization and linked to the repository. The
> fields are added in the project's settings, and the saved views are views of the project. A new board has
> one default view, and GitHub never deletes a board's last view, so the script creates the new views first and
> then deletes the default one (`--delete-unlisted`).


---

## 7. The first version and the roles

### 7.1 The first version

- The changelog starts with a title line and no version heading (section 1).
- The first change to `main` goes through the normal flow: a branch with a `WIP-Version` heading and its
  entries, and a pull request. Its merge produces version `V0.1.0`. It is not a small change and it is not
  a release, so there is no `released/` tag.
- Versions below 1.0.0 are the project's early life. Moving to `V1.0.0` is a deliberate decision, made with
  the `+V` marker on a later version.

### 7.2 The roles

- **Rule:** the project records who holds each role (developer, project owner and administrator) in
  `AGENTS.md`, so that assistants and people alike know.
- **Rule:** the administrator role has administrator access to the repository and holds the project token.
  Developers have write access. The project owner role triages the board.
- One person may hold several roles, and in a small team usually does.

### 7.3 Rules

- **Rule:** the first merge is a real change, logged and merged by pull request like any other, so that
  the first version comes from the normal flow.
- **Recommendation:** make that first change the initial structure of the project.

**Why.** A first version that comes from the normal flow proves the flow works, and it avoids a bypass
Alert on the very first push. An empty repository starts with a single commit made by the hosting service,
and everything after it follows the process. Recording the roles at the start avoids anyone guessing later
who decides what.


---

## 8. Prove the setup

A full trial through the real repository would use up the first version: the first merge produces
`V0.1.0`, so a trial would become the project's first version, and it would leave test tickets and tags to
clean up. So the setup is proved in two levels, neither of which leaves anything behind.

### 8.1 Level 1: without side effects

1. **Run the preflight.** It confirms the repository, the project token, the board and its fields, and the
   repository settings.
2. **Run the automation's tests.**
3. **Run the finalize step in dry-run mode.** It prints every write it would make, such as the heading
   rename, the ticket updates and the Version ticket, without making any.
4. **Test the hooks with a throwaway commit** on a local branch that is never pushed. Check that the build
   is stamped, that the message is drafted, and that the warnings appear. Then delete the branch.

### 8.2 Level 2: the first real merge

The first real change (the initial structure, by pull request) is the live proof. After it merges, check it
as in the guide on syncing and merging (section 5.2): the heading is renamed to `V0.1.0`, the Version ticket
exists and lists the tickets, and the tickets show Delivery *Merged*.

### 8.3 Rules

- **Rule:** run level 1 before the first real change, and fix every failure it reports.
- **Rule:** check the result of the first merge, as in the guide on syncing and merging (section 5.2).
- **Recommendation:** if something fails on the first real merge, correct the board by hand and fix the
  cause. The version number stays as it is.

**Why.** Level 1 finds nearly every setup mistake with nothing to clean up, and the first merge shows what
only a live run can: whether the automation really writes to the board. Keeping the trial out of the real
repository means the first version is a real one.

> **In GitHub.** The finalize step has a dry-run mode that prints every write instead of making it. The
> preflight is the automation's own first step and can also be started on request from the repository's
> Actions page.


---

## 9. Checklist

A one-page summary of the guide. It adds no new rules.

**Structure** (section 1)

- [ ] The locations exist under the standard names. The changelog has a title and no version, and the
      readme explains the setup and the command that activates the hooks.

**Automation** (section 2)

- [ ] The files are copied unchanged, the hook scripts are executable and activated, the tests pass, the
      workflow is enabled with its permissions, and the manifest is in place and the check passes.

**Repository settings** (section 3)

- [ ] Only merge commits are allowed, and head branches are not deleted automatically.
- [ ] The default branch is `main`, Actions is enabled with the workflow declaring its permissions, and
      issues and projects are enabled with the board linked.
- [ ] The wiki is initialized if it is used. Branch protection is on if the plan offers it, with the
      administrator bypass left open. Access matches the roles.

**The project token** (section 4)

- [ ] It is created under an administrator account with the `project` and `repo` scopes, and stored as
      `PROJECT_TOKEN`. Its expiry is recorded, and it is nowhere else.

**Issue types and labels** (section 5)

- [ ] The eight issue types exist with their descriptions.
- [ ] The 14 Area labels and `dummy` exist with their descriptions, and the default labels not on the list
      are deleted.

**The board** (section 6)

- [ ] The fields and values are exactly the standard's, Build is text, and the built-in Status values are
      replaced.
- [ ] The saved views of `.github/views.json` exist (All, Backlog, Board, Health, Versions) and `views.py`
      reports them up to date.

**The first version and the roles** (section 7)

- [ ] The first change goes by pull request (the initial structure).
- [ ] The roles are recorded in `AGENTS.md`.

**Proof** (section 8)

- [ ] The preflight reports no problems, the tests pass, the dry-run finalize looks right, and a throwaway
      commit shows the hooks working.
- [ ] After the first merge: the heading is `V0.1.0`, the Version ticket lists the tickets, and the tickets
      show Delivery *Merged*.

**In one line:** structure, automation, settings, token, labels, board, roles, proof.
