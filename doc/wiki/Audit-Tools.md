# Audit tools

Scripts that look at an existing project and report which rules and recommendations of the guides it already
follows. They are a first step before adopting the standard: they show what differs, and change nothing. The route from an audit report to a compliant project is in
[Adopting the standard in an existing project](Adopting-the-Standard).

They live in `tools/` of this repository and use only Python 3 and, for the GitHub parts, the
[`gh` command line tool](https://cli.github.com/) signed in to an account that can read the repository.

## Running them

```
python tools/audit.py <project-path>                  # all four audits
python tools/audit.py <project-path> --offline        # only the files and git audits (no gh, no network)
python tools/audit.py <project-path> --json audit.json
```

| Option | Meaning |
|---|---|
| `--offline` | Skip the GitHub and board audits. |
| `--repo owner/name` | The GitHub repository, when the project's `origin` remote is not it (or there is none). |
| `--board <number>` | The board, when the repository links more than one. The first one is used otherwise. |
| `--baseline <file>` | The file of accepted deviations, instead of `.github/audit-baseline.json` in the project. |
| `--since <date or commit>` | Judge the history only from a cut-over (see below). |
| `--verbose` | Also list the checks that passed, with what each examined (screen, Markdown and JSON). Off by default. |
| `--md <file>` | Write the Markdown report here instead of `audit-report.md`. |
| `--json <file>` | Also write the whole result to a JSON file. |

Each audit can also be run alone, with the same project path and the `--json` option:
`audit_files.py`, `audit_git.py`, `audit_github.py` (`--repo`) and `audit_board.py` (`--repo`, `--board`).

The exit code is `1` when a rule fails, `2` for bad arguments, and `0` otherwise. A failed recommendation, or a
check that could not be made, never fails the run.

## Judging the history from a cut-over

A project that adopts the standard has a past that cannot change: commits on `main` that are not merges, `fix:`
subjects, old tags. `--since` limits the history checks to what came after a cut-over: a UTC date (`2026-10-01`, or
`2026-10-01 14:30`) or a commit (a hash, or a tag). It applies to these checks:

- `git.history.merge-commits`: only the commits on `main`'s first-parent line made after the cut-over;
- `git.message.no-type-prefix` and `git.message.no-assistant-attribution`: only the commits made after it, on any
  branch;
- `git.tag.names`, `git.tag.released-on-main` and `git.tag.released-in-changelog`: only the tags that point at such
  commits.

Everything else looks at the present state and is not affected (branch names, files, GitHub settings, the board).
The screen, the Markdown report and the JSON file say which cut-over was used (`History judged from`, and a `since`
key). A date after the year 2100 is not understood by git; a value that is neither a date nor a commit of the
project is a bad argument (exit code `2`). The single script `audit_git.py` takes the same option.

## Accepting known deviations: the baseline

Some failures cannot be fixed (the past) or do not apply to the project (a feature its hosting plan lacks). They are
recorded, with a reason, in `.github/audit-baseline.json` in the audited project, and `audit.py` then shows them as
**accepted**: counted apart, listed with the reason, and never a failure or a cause of exit code `1`.

```
{"accepted": [
  {"check": "git.history.merge-commits",
   "reason": "history before the cut-over; it cannot be rewritten",
   "date": "2026-10-12",
   "agreed_by": "the project owner",
   "items": ["82e13d9", "0e4cf26"]}
]}
```

- `check`, `reason`, `date` and `agreed_by` are required; a file that lacks one, or is not valid, is a bad argument
  (exit code `2`).
- `items` is optional. Without it the entry accepts the whole check. With it, the entry accepts only the detail lines
  of the check that start with one of the items (a commit hash, a branch or tag name, `line 12`); if other lines
  remain, the check stays a failure for those, and says how many items the baseline accepted.
- An entry that accepts nothing now (the check passes, or its items are gone) is reported by the check
  `baseline.stale`, a recommendation, so the file does not collect dead entries.
- Only the failures of the files, git, GitHub and board audits can be accepted; a check that was *not-checkable* is
  not touched. The single-audit scripts do not read the baseline.

Use it together with `--since` (guide 11, section 3): `--since` leaves the old history out, the baseline records what
is left.

## The adoption plan

After the checks, `audit.py` groups the open findings by the stage of guide 11 that deals with them, in the order of
the stages, so the report also says what to do first. Each finding shows its strength, its usual class (fix now,
convert, history, not applicable), the role that makes the change and whether the change can be undone. All of it is
read from the tables of appendix G, the guide's own list of every finding, so the plan and the guide cannot differ.

- Only failed checks are planned. A finding that appendix G does not list goes under *not part of a stage*; the checks
  that *could not be made* are listed apart, under *to confirm*.
- Accepted deviations (the baseline) and passes are not in the plan.
- The plan is on the screen, in the Markdown report (the section *Adoption plan*, a table per stage) and in the JSON
  file (the key `plan`: the stages, each with its findings). A project with nothing open has no plan.

## Where the report goes

`audit.py` prints the report to the screen and also writes it as a Markdown file: `audit-report.md` in the directory
you run the command from (never in the audited project), or the file named with `--md <file>`. The file lists **every**
check, passes included, in one table per audit (result, id, strength, guide section, check, detail and fix), after the
date, the project and the totals; under each table the failed and not-checkable checks list every offender as bullets
(with `--verbose`, the passed checks list what they examined too). It is overwritten on every run; copy or rename it to keep an earlier one. The screen
shows only what is not a pass. `--json <file>` additionally writes the same result as JSON, and the four single-audit
scripts (`audit_files.py` and the others) print to the screen only.

## Step by step

1. **Get the standard.** Clone this repository; the scripts are in `tools/` and need only Python 3.
2. **Prepare the project to audit.** Have a clone of it, and run `git fetch` in it so the remote branches and tags are
   seen (the audits never fetch).
3. **For the GitHub and board audits,** sign in with `gh auth login`, then `gh auth refresh -s project` (the board needs
   the `project` scope). Use an account with administration access, or protection and secrets will be not-checkable.
   Skip this step with `--offline`.
4. **Run it:** `python tools/audit.py <project-path>`, adding `--repo owner/name` if the project has no GitHub
   `origin`, and `--board <number>` if the repository links several boards.
5. **Read the result** on the screen or in `audit-report.md` (see below): fix the failed rules first, then the recommendations.
6. **Run it again** to confirm; add `--md before.md --json before.json` (then `after`) and compare the check ids to follow
   progress. The exit code is `0` when no rule fails, so the command can also gate a script or a workflow.

## What each audit checks

| Audit | Looks at | Needs |
|---|---|---|
| **Files** (`audit_files.py`) | The places every project has (readme, `CHANGELOG.md`, `doc/wiki/`, `.githooks/`, `.github/`, `AGENTS.md`, `.gitignore`, `.gitattributes`, license); the `* text=auto eol=lf` line; the changelog (Unix line endings, no *Known bugs* or *Planned* sections, one open `WIP-Version` heading on top with a valid marker, version headings and their order, build and ticket headings); the hooks and whether they are active in the clone; the wiki (`Home.md`, page names); the workflow, pull request template, manifest and tests; that `AGENTS.md` points to the guides. | A clone. |
| **Git** (`audit_git.py`) | `main` exists and is the only integration line; branch names are kebab-case without `/` (or the hotfix form); tag names follow the namespaces; release tags are on `main` and name a changelog version; work reaches `main` through merge commits; no `fix:` or `feat:` subject prefix; no assistant co-author or "generated with" line. | A clone. Run `git fetch` first to include the remote branches. |
| **GitHub** (`audit_github.py`) | Merge methods, automatic branch deletion, default branch, issues, projects and wiki; that the owner is an organization (or the Type is kept in the field Kind) and the variable `TYPE_SOURCE` is valid; protection of `main` and the administrator bypass; Actions; the secret `PROJECT_TOKEN` and the variable `BOARD_NUMBER`; the labels (the 14 Area labels and `dummy`, described, standard colors); the eight issue types. | `gh`; administration access for protection and secrets. |
| **Board** (`audit_board.py`) | The board linked to the repository; every field with its kind, values and colors; the saved views against `.github/views.json`; the tickets (issue type, Size, Status against open or closed, Resolution, Origin and REF, the board form of Version, Version tickets, Alerts, Area labels). Throwaway (`dummy`) tickets and pull requests are skipped. | `gh` with the `project` scope (`gh auth refresh -s project`). |

The tables the audits compare with are not copied: the fields, their values and colors come from
`.github/scripts/preflight.py`, the views from `.github/views.json`, and the labels and issue types from
[Appendix C](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md),
so the audits follow the standard when it changes.

## Reading the report

Only checks that are not a pass are listed:

```
[FAIL] files.changelog.no-bug-plan-sections (rule, guide 03 section 7): the changelog has no 'Known bugs' or 'Planned' sections
    2 such heading(s)
      - line 12: ### Known bugs
      - line 20: ### Planned
    fix: move known bugs and planned work to tickets
```

The message counts the offenders and the bullets list **every** one of them: each commit (full hash and subject),
branch, tag, label, ticket (number, title and what is wrong), changelog line, or board view setting (what the board
has and what `views.json` wants, and the columns that are missing or extra). Nothing is cut to "for example".

- **pass, fail, not-checkable.** *Not-checkable* means the audit could not tell: `gh` is missing or not signed in, the
  data needs more access, or the project is not a clone. It is not a failure.
- **rule or recommendation** is the strength the guide gives the statement; the guide section is named so you can read
  the reason.
- The report ends with a total of rules and of recommendations, counted apart.
- **`--verbose`** (off by default) also lists the checks that passed, each with what it examined and found right (for
  example the 29 commits looked at, or the three hooks found). Use it when you need to show evidence, not just the
  problems.

The JSON file holds the same: `summary` (counts by strength and result) and `audits`, each with its `area`, `counts`
and every check (`id`, `guide`, `strength`, `title`, `result`, `message`, `hint`, `details`). `details` holds the
offenders of a failed check and, with `--verbose`, what a passed check examined (empty otherwise). The ids are stable, so two runs can
be compared to follow progress.

## Every check

One row per thing verified. **Id** is the stable id in the report and the JSON file; **Strength** is *rule* (R, a
failure makes the exit code `1`) or *recommendation* (r, reported but never fails the run); **Guide** is the section of
the guides that holds the reason. A check is *not-checkable* instead of failed when its source cannot be read, as noted.
When a check does not pass, the report lists every offender (see *Reading the report*), not a sample.

### `audit_files.py` — the working tree

| Id | Strength | Guide | What is verified |
|---|---|---|---|
| `files.location.README.md` | r | 03 §2.1 | A file `README.md` exists in the project root. |
| `files.location.CHANGELOG.md` | R | 03 §2.1 | A file `CHANGELOG.md` exists in the root. |
| `files.location.doc` | R | 03 §2.1 | A folder `doc/` exists. |
| `files.location.doc.wiki` | R | 03 §2.1 | A folder `doc/wiki/` exists. |
| `files.location.githooks` | R | 03 §2.1 | A folder `.githooks/` exists. |
| `files.location.github` | R | 03 §2.1 | A folder `.github/` exists. |
| `files.location.AGENTS.md` | R | 03 §2.1 | A file `AGENTS.md` (shared assistant instructions) exists. |
| `files.location.gitignore` | r | 03 §2.1 | A file `.gitignore` exists. |
| `files.location.gitattributes` | R | 03 §2.1 | A file `.gitattributes` exists. |
| `files.location.license` | r | 03 §2.1 | A file whose name starts with `LICENSE` or `LICENCE` (any case) exists in the root. |
| `files.gitattributes.eol` | R | 03 §2.2 | `.gitattributes` contains the exact line `* text=auto eol=lf`. Not-checkable if the file cannot be read. |
| `files.changelog.readable` | R | 03 §7 | `CHANGELOG.md` can be read. When it cannot, this is the only changelog check made. |
| `files.changelog.eol` | R | 03 §2.2 | The changelog contains no carriage return (Unix line endings). |
| `files.changelog.no-bug-plan-sections` | R | 03 §7 | No heading of level 2 to 4 starts with "Known bugs" or "Planned" (any case); those belong to tickets. Lists the line numbers. |
| `files.changelog.wip-heading` | R | 02 §3 | Every `## WIP-Version` heading is exactly that, optionally followed by one marker ` +V`, ` +s` or ` +m` and nothing else. |
| `files.changelog.one-wip` | R | 04 §4.1 | At most one `## WIP-Version` heading is open. |
| `files.changelog.version-heading` | R | 03 §7 | Every other `## V<digit>…` heading has the form `## V<V>.<s>.<m> — yyyy-mm-dd hh:mm UTC` (a hotfix may end the version with `-HF<n>`). |
| `files.changelog.has-version` | R | 02 §3 | At least one finalized version heading exists. |
| `files.changelog.newest-first` | R | 03 §7 | The finalized versions (hotfix headings excluded) are in descending order of V, s, m. |
| `files.changelog.wip-on-top` | R | 04 §4.1 | When a `WIP-Version` heading is open, it is the first version heading of the file. |
| `files.changelog.headings` | R | 03 §7 | Under a version, every `###` heading is `### WIP-Build` or `### Build <14 digits> (branch <name>[, commit <hash>])`, and every `####` heading is `#### #<n> — <title>`, `#### REF <14 digits> — <reason>` or `#### AUTO-REF <14 digits> (tracked as #<n>)`. |
| `files.hooks.present` | R | 03 §2.2 | The files `pre-commit`, `pre-push` and `prepare-commit-msg` exist in `.githooks/`. Names the missing ones. |
| `files.hooks.active` | R | 04 §1 | `git config core.hooksPath` is `.githooks` in this clone. Not-checkable when the folder has no `.git`. |
| `files.wiki.home` | R | 03 §9.2 | `doc/wiki/Home.md` exists (fails too when `doc/wiki/` is missing). |
| `files.wiki.names` | R | 03 §9.2 | Every file in `doc/wiki/` ends in `.md` and has no space or underscore in its name (words are joined by hyphens). |
| `files.automation.workflow` | R | 03 §2.2 | At least one `.yml` or `.yaml` file exists in `.github/workflows/`. |
| `files.automation.pr-template` | r | 06 §3 | `.github/pull_request_template.md` exists. |
| `files.automation.manifest` | r | 03 §2.2 | `.github/automation-manifest.json` exists. |
| `files.automation.tests` | R | 03 §2.2 | When `.github/scripts/` exists, a `tests/` folder exists too; a project without its own scripts passes. |
| `files.agents.guides` | R | 09 §6 | `AGENTS.md` mentions the word "guides" (any case), that is, it sends the assistant to the guides. Not-checkable if the file cannot be read. |

### `audit_git.py` — branches, tags and commits (local clone only)

If the folder is not a git repository, the only check is `git.repository` (R, 03 §1), which fails; nothing else runs.
Remote branches appear only after `git fetch`.

| Id | Strength | Guide | What is verified |
|---|---|---|---|
| `git.branch.main` | R | 02 §1.1 | A branch named `main` exists, locally or on a remote. |
| `git.branch.single-line` | R | 02 §1.1 | No branch is named `develop`, `development`, `dev`, `staging`, `stage` or `release`. |
| `git.branch.no-slash` | R | 02 §2.1 | No branch name contains `/`. |
| `git.branch.kebab-case` | R | 02 §2.1 | Every branch other than `main` is lowercase words and digits joined by hyphens, or has the hotfix form `hotfix-v<V>-<s>-<m>-<words>`. |
| `git.tag.names` | R | 02 §2.2 | Every tag is `released/V<V>.<s>.<m>` (optionally `-HF<1-9>`) or `archived/`, `suspended/` or `abandoned/` followed by `yyyy-mm-dd_<branch>[_<detail>]`; each may carry a `test/` prefix. |
| `git.tag.released-on-main` | R | 02 §1.1 | Every non-test, non-hotfix `released/` tag is an ancestor of `main`. Skipped when there is no `main`. |
| `git.history.merge-commits` | R | 06 §4.1 | On `main`'s first-parent line every commit is a merge, except the first commit and the automation's own commits (subjects starting `Finalize `, `Flag bypass` or `Fill in a build heading`). So no direct, squashed or rebased commit. Skipped when there is no `main`. |
| `git.message.no-type-prefix` | R | 05 §5.2 | No commit on any branch has a subject starting `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `style:`, `perf:`, `build:` or `ci:` (with an optional scope or `!`). |
| `git.message.no-assistant-attribution` | R | 09 §4.2 | No commit message has a `Co-authored-by:` trailer naming an assistant (Claude, Anthropic, Codex, OpenAI, Copilot, Gemini, Cursor, ChatGPT) or a "generated with/by …" line. |
| `git.tag.released-in-changelog` | R | 03 §7 | Every non-test `released/` tag matches a finalized `## V… —` heading of `CHANGELOG.md` (hotfix suffix included). Not-checkable when the changelog cannot be read. |

### `audit_github.py` — repository settings (through `gh api`)

If the repository cannot be read, the only check is `github.repository` (R, 10 §3), reported as not-checkable.

| Id | Strength | Guide | What is verified |
|---|---|---|---|
| `github.setting.allow_merge_commit` | R | 10 §3 | Merge commits are allowed. |
| `github.setting.allow_squash_merge` | R | 10 §3 | Squash merging is off. |
| `github.setting.allow_rebase_merge` | R | 10 §3 | Rebase merging is off. |
| `github.setting.delete_branch_on_merge` | R | 10 §3 | Head branches are not deleted automatically after a merge (the branch is retired with a tag first). |
| `github.setting.has_issues` | R | 10 §3 | Issues are enabled. |
| `github.setting.has_projects` | R | 10 §3 | Projects are enabled. |
| `github.setting.has_wiki` | r | 10 §3 | The wiki is enabled. |
| `github.setting.default_branch` | R | 10 §3 | The default branch is `main`. |
| `github.setting.owner-type` | R | 10 §5.1 | The owner is an organization (issue types exist only there), or the Type is kept in the board field Kind. |
| `github.type-source` | R | 10 §5.1 | The repository variable `TYPE_SOURCE`, if it is set, is `issue-type` or `field`. When it is not set, the source is `issue-type` for an organization and `field` for a personal account. The other checks follow the source. |
| `github.protection.pull-request` | r | 10 §3 | `main` requires a pull request or status checks, through branch protection or an active branch ruleset. Not-checkable when neither can be read. |
| `github.protection.up-to-date` | r | 10 §3 | Branch protection requires branches to be up to date before merging. |
| `github.protection.admin-bypass` | r | 10 §3 | The protection does not apply to administrators (the bypass is left open). |
| `github.actions.enabled` | R | 10 §3 | Actions is enabled. Not-checkable if unreadable. |
| `github.token.secret` | R | 10 §4 | The Actions secret `PROJECT_TOKEN` exists (only its name is read). Not-checkable without administration access. |
| `github.board.variable` | r | 10 §2.3 | The Actions variable `BOARD_NUMBER` is set. |
| `github.labels.exact` | R | 10 §5.2 | The repository's labels are exactly the 14 Area labels and `dummy` of Appendix C: none extra, none missing. |
| `github.labels.descriptions` | R | 10 §5.2 | Each of those labels has a non-empty description. |
| `github.labels.colors` | r | 10 §5.2 | Each of those labels has its Appendix C color. |
| `github.issue-types.exact` | R | 10 §5.1 | The organization has all eight issue types of Appendix C (Feature, Enhancement, Change, Bug, Refactor, Task, Version, Alert), enabled. With the source `field` it is passed as not needed, and the next two checks are not made. |
| `github.issue-types.descriptions` | R | 10 §5.1 | Each issue type has a non-empty description. |
| `github.issue-types.colors` | r | 10 §5.2 | Each issue type has its Appendix C color. |

### `audit_board.py` — the project board (through `gh api graphql`)

If the repository's boards cannot be read, the only check is `board.linked` (R, 10 §6.2), not-checkable. If the fields,
views or tickets cannot be read, one not-checkable check (`board.fields`, `board.views` or `board.tickets`) stands for
that group. Each field of the bootstrap table in `preflight.py` (Status, Origin, REF, Waiting, Attention, Resolution,
Delivery, Priority, Size, Risk, Version, Build, Start date, End date, Fix) gets the first two field rows (the second
only when the field exists), and each single-select field also the next two; `<field>` is its lowercase name (spaces
become hyphens).

| Id | Strength | Guide | What is verified |
|---|---|---|---|
| `board.linked` | R | 10 §6.2 | A board is linked to the repository (the one given by `--board`, else the first). Nothing else runs without it. |
| `board.field.<field>` | R | 10 §6.2 | The field exists on the board. With the source `field`, Kind is one of the fields, with the eight values of the Type. |
| `board.field.<field>.type` | R | 10 §6.2 | The field is of the right kind: single select, text or date (Build and Version must be text, not number). |
| `board.field.<field>.values` | R | 10 §6.2 | A single-select field has exactly the values of the table: none missing, none extra. |
| `board.field.<field>.colors` | r | Appendix C | Each value that has a standard color has it. |
| `board.views.present` | R | 10 §6.2 | Every view named in `.github/views.json` exists on the board. |
| `board.views.no-extra` | r | 10 §6.2 | The board has no view that `views.json` does not name. |
| `board.views.match` | R | 10 §6.2 | Each view equals its definition: layout, filter, grouping, sorting and visible columns. Names the view and the differing keys. |
| `board.ticket.type` | R | 03 §4.3 | Every ticket has a Type: an issue type, or a value in the field Kind. |
| `board.ticket.size` | R | 03 §3 | Every work ticket (not Version or Alert) has a Size. |
| `board.ticket.closed-status` | R | 03 §4.3 | A closed work ticket has Status *Completed* or *Abandoned*. |
| `board.ticket.open-status` | R | 03 §4.3 | An open work ticket does not have Status *Completed* or *Abandoned*. |
| `board.ticket.resolution` | R | 03 §4.3 | Resolution is set exactly when the work ticket is *Completed* or *Abandoned*. |
| `board.ticket.backfilled-ref` | R | 03 §4.3 | A work ticket with Origin *Backfilled* has its REF filled in. |
| `board.ticket.version-form` | r | 03 §4.3 | A Version value matches the board form `V000.010.001` (with an optional `-HF<n>`). |
| `board.ticket.version-title` | R | 03 §5.2 | A ticket of type Version is titled `Version 000.010.001` (optional `-HF<n>`). |
| `board.ticket.alert-priority` | R | 03 §5.3 | A ticket of type Alert has Priority *Critical*. |
| `board.ticket.area` | r | 03 §4.3 | A work ticket has at least one label (Area). |

Ticket checks skip pull requests, drafts and tickets labeled `dummy`; a failure lists every ticket with its number, title
and what is wrong with it.

## Limits

- The audits read facts. What needs judgment (is a ticket well written, is a changelog entry accurate, is the
  documentation current) is left to people.
- The history check looks at the first-parent line of `main`: commits made by the automation (`Finalize`, `Flag
  bypass`, `Fill in a build heading`) are allowed there.
- A project that adopts the standard late will fail rules about its past (old tags, old commit messages). The report
  says what, and the hint says what to do from now on; history is not rewritten.
