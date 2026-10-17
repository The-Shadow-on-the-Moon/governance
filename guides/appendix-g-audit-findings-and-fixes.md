# Appendix G: Audit findings and how to fix them

The audit tools (see the wiki page on them) report findings by check id. This appendix lists every check the
audits can report, with what the finding means and how to deal with it when a project adopts the standard (guide
11). Use it as the work list: take the audit report finding by finding, find its id here, and do what the row says
in the stage it names.

**How to read the tables.**

- **Id** is the id in the report and in the JSON file. A placeholder in angle brackets (`<field>`) stands for
  each of the values it can take.
- **Class** is the usual triage class (guide 11, section 3): *Fix* (fix now), *Convert* (change existing
  material once), *History* (the past, accepted and recorded), *N/A* (not applicable, recorded with a reason).
  A row names two when it depends on the project.
- **Stage** is the stage of guide 11, section 4, that deals with it: 1 GitHub settings, 2 adoption branch (files
  and automation), 3 token, board and preflight, 4 git names, 5 tickets, 6 land and prove, 7 keep it. A dash
  means the finding is not fixed by a stage.
- **Role** is who makes the change: **Admin** (administrator), **Owner** (project owner), **Dev** (developer).
- **Undo** says whether the change can be undone: *Yes*, *With care* (it affects clones or links), or *No* (the
  past cannot be changed).
- A check that reports *not-checkable* is not a finding. Its row says what to provide so the audit can tell.

Strength (rule or recommendation) and the guide section behind each check are in the audit report itself and in
the wiki page on the audit tools; the rows here say what to do. Nothing here adds a rule.

---

## 1. Files (`audit_files.py`)

| Id | Class | Stage | Role | Undo | What it means and what to do |
|---|---|---|---|---|---|
| `files.location.README.md` | Fix | 2 | Dev | Yes | There is no `README.md` in the root. Write one that says what the project is and how to set it up, including the command that activates the hooks. |
| `files.location.CHANGELOG.md` | Convert | 2 | Dev | Yes | There is no `CHANGELOG.md`. Keep the project's old changelog (if any) in `doc/` under a name that says it is earlier history, and start a new `CHANGELOG.md` with a baseline heading (guide 11, section 4.2). |
| `files.location.doc` | Fix | 2 | Dev | Yes | There is no `doc/` folder. Create it; the project's documentation goes there. |
| `files.location.doc.wiki` | Fix | 2 | Dev | Yes | There is no `doc/wiki/` folder. Create it with a `Home.md` and move the project's wiki pages in, one Markdown file per page. |
| `files.location.githooks` | Fix | 2 | Dev | Yes | There is no `.githooks/` folder. Copy the hooks from the standard unchanged. |
| `files.location.github` | Fix | 2 | Dev | Yes | There is no `.github/` folder. It is created with the workflow, scripts, template and manifest. |
| `files.location.AGENTS.md` | Fix | 2 | Dev | Yes | There is no `AGENTS.md`. Create it: the roles, the pointer to the guides, what the project's build and tests are. |
| `files.location.gitignore` | Fix | 2 | Dev | Yes | There is no `.gitignore`. Add one for the project's tools and build output. |
| `files.location.gitattributes` | Fix | 2 | Dev | Yes | There is no `.gitattributes`. Add it with the line `* text=auto eol=lf` (see `files.gitattributes.eol`). |
| `files.location.license` | Fix / N/A | 2 | Owner | Yes | There is no license file. Add the project's license, or record that the project has none on purpose. |
| `files.gitattributes.eol` | Convert | 2 | Dev | With care | The line `* text=auto eol=lf` is missing. Add it, then renormalize the files in a commit of its own and list that commit in `.git-blame-ignore-revs` (guide 11, section 4.2). Do it when no branch is waiting to merge: it touches every line of the files whose endings change. |
| `files.changelog.readable` | Fix | 2 | Dev | Yes | The audit cannot read `CHANGELOG.md`. Create it (see `files.location.CHANGELOG.md`). |
| `files.changelog.eol` | Convert | 2 | Dev | Yes | The changelog has Windows line endings. Convert it with the renormalizing commit of `files.gitattributes.eol`. |
| `files.changelog.no-bug-plan-sections` | Convert | 2 | Dev | Yes | The changelog has *Known bugs* or *Planned* sections. Move each item into a ticket and delete the sections. The changelog records changes to files and nothing else. |
| `files.changelog.wip-heading` | Fix | 2 | Dev | Yes | A `WIP-Version` heading has text after it other than one `+V`, `+s` or `+m`. Remove the extra text. |
| `files.changelog.one-wip` | Fix | 2 | Dev | Yes | More than one `WIP-Version` heading is open. Keep one, at the top, and merge the entries of the others into it. |
| `files.changelog.version-heading` | Convert | 2 | Dev | Yes | A version heading is not `## V<major>.<sub>.<mod> — yyyy-mm-dd hh:mm UTC`. For an old changelog kept as history, leave it in its file in `doc/` and start the new one with the baseline heading; for the live changelog, rewrite the heading (UTC, no padding). |
| `files.changelog.has-version` | Fix | 2 | Dev | Yes | The changelog has no finalized version. Write the baseline heading for the version the project continues from (guide 11, section 4.2). |
| `files.changelog.newest-first` | Convert | 2 | Dev | Yes | Versions are not in descending order. Reorder them, or start the new changelog with the baseline. |
| `files.changelog.wip-on-top` | Fix | 2 | Dev | Yes | The `WIP-Version` heading is below a finalized version. Move it to the top. |
| `files.changelog.headings` | Convert | 2 | Dev | Yes | A build or ticket heading is not in the forms of the guide (`### Build <stamp> (branch <name>)`, `#### #<n> — <title>`, `#### REF <token> — <reason>`). Do not invent stamps for old entries: keep the old changelog as history and start the new one in the standard form. |
| `files.hooks.present` | Fix | 2 | Dev | Yes | One of `pre-commit`, `pre-push`, `prepare-commit-msg` is missing from `.githooks/`. Copy it from the standard; keep it executable. |
| `files.hooks.active` | Fix | 2 | Dev | Yes | This clone does not use the hooks. Run `git config core.hooksPath .githooks`. Every developer does this once per clone. Not-checkable when the folder has no `.git`. |
| `files.wiki.home` | Fix | 2 | Dev | Yes | `doc/wiki/Home.md` is missing. Add it as the index of the wiki. |
| `files.wiki.names` | Convert | 2 | Dev | Yes | A wiki file is not a Markdown file named by its title with hyphens. Rename it (for example `Getting-Started.md`) and update the links to it. |
| `files.automation.workflow` | Fix | 2 | Admin | Yes | There is no workflow in `.github/workflows/`. Copy the workflow and its scripts from the standard unchanged. |
| `files.automation.pr-template` | Fix | 2 | Dev | Yes | There is no `.github/pull_request_template.md`. Copy it from the standard. |
| `files.automation.manifest` | Fix | 2 | Dev | Yes | There is no `.github/automation-manifest.json`. Copy it with the files, or generate it with the manifest script, stating the version of the standard (`--update --standard`). |
| `files.automation.tests` | Fix | 2 | Dev | Yes | The project has its own automation scripts but no `tests/`. Copy the tests that come with the scripts. |
| `files.agents.guides` | Fix | 2 | Dev | Yes | `AGENTS.md` does not mention the guides. Add the pointer: the assistant follows the guides and works from their checklists. Not-checkable when `AGENTS.md` is missing. |

---

## 2. Git (`audit_git.py`)

Branches and tags are read from the local clone: run `git fetch` first to include the remote ones.

| Id | Class | Stage | Role | Undo | What it means and what to do |
|---|---|---|---|---|---|
| `git.repository` | Fix | — | Dev | Yes | The folder is not a git repository. Point the audit at a clone. |
| `git.branch.main` | Convert | 4 | Admin | With care | No branch is called `main`. Rename the integration branch to `main` and make it the default (guide 11, section 5.1). |
| `git.branch.single-line` | Convert | 4 | Owner | With care | A long-lived `develop`, `staging` or `release` branch exists. Merge it into `main` with a merge commit and retire it as *archived* (guide 11, section 5.1). |
| `git.branch.no-slash` | Convert | 4 | Dev | With care | A branch name contains `/`. Create the branch again with hyphens, push it, move its pull request, and retire the old name. |
| `git.branch.kebab-case` | Convert | 4 | Dev | With care | A branch is not in lowercase words with hyphens (or the hotfix form). Rename it as above; branches nobody will resume are retired instead (guide on releases, hotfixes and retiring branches, section 3). |
| `git.tag.names` | Convert / History | 4 | Dev | With care | A tag is not in the standard form. For a tag that marks a real release, add `released/V<major>.<sub>.<mod>` on the same commit and keep the old tag until everybody has moved. A tag with no use is left alone and recorded as history. Never move a tag. |
| `git.tag.released-on-main` | History | 4 | Dev | No | A `released/` tag is on a commit that `main` does not contain. If it is a mistake, add the right tag; otherwise record it as history. |
| `git.history.merge-commits` | History | 6 | Owner | No | Commits on `main` are not merges (direct, squashed or rebased). History cannot be rewritten: record it as history, and use the audit's judging from the cut-over when the tools offer it. After the cut-over, every change lands by pull request and a merge commit. |
| `git.message.no-type-prefix` | History | 6 | Owner | No | Commit subjects with a prefix such as `fix:` or `feat:`. The past stays; from the cut-over the subject is the ticket's title. |
| `git.message.no-assistant-attribution` | History | 6 | Owner | No | Commit messages with an assistant's co-author or "generated with" line. The past stays; from the cut-over leave the line out. |
| `git.tag.released-in-changelog` | Convert | 2 | Dev | Yes | A `released/` tag names a version that has no heading in the changelog. Add the version to the baseline heading, or tag the right version. Not-checkable when the changelog cannot be read. |

---

## 3. GitHub (`audit_github.py`)

The audit reads the settings with `gh`, signed in to an account that can read the repository; protection and
secrets need administration access. A refused read is *not-checkable*, not a failure.

| Id | Class | Stage | Role | Undo | What it means and what to do |
|---|---|---|---|---|---|
| `github.remote` | Fix | — | Dev | Yes | The project has no `github.com` origin remote, so the GitHub and board audits did not run. Give the remote, or pass `--repo owner/name`. |
| `github.repository` | Fix | — | Admin | Yes | `gh` cannot read the repository: it is missing, not signed in, or the account has no access. Run `gh auth login`. |
| `github.setting.allow_merge_commit` | Fix | 1 | Admin | Yes | Merge commits are not allowed. Turn them on: they are the only way work lands. |
| `github.setting.allow_squash_merge` | Fix | 1 | Admin | Yes | Squash merging is on. Turn it off. Tell the team first: open pull requests will need a merge commit. |
| `github.setting.allow_rebase_merge` | Fix | 1 | Admin | Yes | Rebase merging is on. Turn it off, with the same warning. |
| `github.setting.delete_branch_on_merge` | Fix | 1 | Admin | Yes | Head branches are deleted automatically. Turn it off: a branch is tagged first and deleted second. |
| `github.setting.has_issues` | Fix | 1 | Admin | Yes | Issues are off. Turn them on: tickets are issues. |
| `github.setting.has_projects` | Fix | 1 | Admin | Yes | Projects are off. Turn them on: the board is a project. |
| `github.setting.has_wiki` | Fix / N/A | 1 | Admin | Yes | The wiki is off. Turn it on and create a first page, or record that the plan does not offer it for the repository. |
| `github.setting.default_branch` | Convert | 1 | Admin | With care | The default branch is not `main`. Create or rename `main` and make it the default (guide 11, section 5.1). |
| `github.setting.owner-type` | Convert | 1 | Admin | With care | The repository belongs to a person and the Type is not kept in the field Kind. Either transfer it to an organization (issue types exist only there; clones must update their remote), or keep it and set the variable `TYPE_SOURCE` to `field`, so that the Type lives in the board field Kind. |
| `github.type-source` | Fix | 1 | Admin | Yes | The repository variable `TYPE_SOURCE` is neither `issue-type` nor `field`. Set it to one of them, or delete it: the source is then `issue-type` for an organization and `field` for a person. Not-checkable when the variable cannot be read. |
| `github.protection.pull-request` | Fix / N/A | 6 | Admin | Yes | `main` does not require a pull request. Turn on protection (or a ruleset) after the first compliant merge, where the plan offers it. Not-checkable when protection cannot be read. |
| `github.protection.up-to-date` | Fix / N/A | 6 | Admin | Yes | `main` does not require branches to be up to date. Turn it on with the protection. |
| `github.protection.admin-bypass` | Fix | 6 | Admin | Yes | The protection also applies to administrators. Leave the administrator bypass open: a bypass is allowed, with an Alert as its record. |
| `github.actions.enabled` | Fix | 1 | Admin | Yes | Actions is off. Turn it on: the automation runs there. |
| `github.token.secret` | Fix | 3 | Admin | Yes | The secret `PROJECT_TOKEN` does not exist. Create the token and store it (guide on new-project bootstrap, section 4). Not-checkable without administration access. |
| `github.board.variable` | Fix | 3 | Admin | Yes | The variable `BOARD_NUMBER` is not set. Run the preflight, which stores it. |
| `github.labels.exact` | Convert | 1 | Admin | With care | The repository's labels are not exactly the 14 Area labels and `dummy`. Move the issues from each extra label to the Area label that replaces it, then delete it, because deleting a label removes it from its issues. Create the missing ones. |
| `github.labels.descriptions` | Fix | 1 | Admin | Yes | A label has no description. Give each its meaning from Appendix C. |
| `github.labels.colors` | Fix | 1 | Admin | Yes | A label has another color than the standard. Use the colors of Appendix C. |
| `github.issue-types.exact` | Fix | 1 | Admin | Yes | An issue type is missing in the organization. Create the eight types (Feature, Enhancement, Change, Bug, Refactor, Task, Version, Alert). Not needed, and passed, when the Type is kept in the field Kind. Not-checkable when the types cannot be read. |
| `github.issue-types.descriptions` | Fix | 1 | Admin | Yes | A type has no description. Give it the definition of Appendix C. |
| `github.issue-types.colors` | Fix | 1 | Admin | Yes | A type has another color than the standard. Use the colors of Appendix C. |

---

## 4. Board (`audit_board.py`)

The audit reads the board linked to the repository with `gh` and the `project` scope (`gh auth refresh -s
project`). Tickets labeled `dummy` and pull requests are skipped.

| Id | Class | Stage | Role | Undo | What it means and what to do |
|---|---|---|---|---|---|
| `board.remote` | Fix | — | Dev | Yes | No `github.com` remote, so the board audit did not run. Give the remote, or pass `--repo owner/name`. |
| `board.linked` | Fix | 3 | Admin | Yes | No board is linked to the repository. Create the board and link it (guide on new-project bootstrap, section 6). Not-checkable when the boards cannot be read. |
| `board.fields` | Fix | 3 | Admin | Yes | The board's fields could not be read. Check the `project` scope of `gh`. |
| `board.field.<field>` | Fix | 3 | Admin | Yes | The board lacks the field. Create it with `fields.py`. |
| `board.field.<field>.type` | Fix | 3 | Admin | With care | The field is of the wrong kind (Build and Version must be text). Delete and create it again: the values of the old field are lost, so copy them first. |
| `board.field.<field>.values` | Fix | 3 | Admin | With care | The field's values are not exactly the standard's. Add the missing ones and remove the extra ones by hand; move the tickets off an extra value first (for example the built-in Status values). |
| `board.field.<field>.colors` | Fix | 3 | Admin | Yes | A value has another color than the standard. Use the colors of Appendix C. |
| `board.views` | Fix | 3 | Admin | Yes | The board's views could not be read, or the definition file `.github/views.json` is missing or invalid. Copy the file from the standard. |
| `board.views.present` | Fix | 3 | Admin | Yes | A view of `.github/views.json` is missing. Run `views.py --apply`. |
| `board.views.no-extra` | Fix / N/A | 3 | Owner | Yes | The board has a view that `views.json` does not list. Delete it (`views.py --delete-unlisted`), or add it to the file. |
| `board.views.match` | Fix | 3 | Admin | Yes | A view differs from its definition: the report names the view and the setting. Run `views.py --apply` (it creates the view again) or correct `views.json`. |
| `board.tickets` | Fix | 5 | Admin | Yes | The board's tickets could not be read. Check the `project` scope. |
| `board.ticket.type` | Fix | 5 | Owner | Yes | A ticket has no Type (no issue type, or no value in the field Kind). Set it. For many old issues, set the type through the API in one pass. |
| `board.ticket.size` | Fix | 5 | Owner | Yes | A work ticket has no Size. Estimate it and set the Size. |
| `board.ticket.closed-status` | Convert | 5 | Owner | Yes | A closed work ticket is not *Completed* or *Abandoned*. Set the Status to match (or reopen the ticket if it is not done). |
| `board.ticket.open-status` | Convert | 5 | Owner | Yes | An open work ticket is *Completed* or *Abandoned*. Close the issue or move the Status back. |
| `board.ticket.resolution` | Convert | 5 | Owner | Yes | Resolution is not set exactly when the ticket is *Completed* or *Abandoned*. Set it on finished tickets (*Done* for finished work) and clear it on open ones. |
| `board.ticket.backfilled-ref` | Fix | 5 | Owner | Yes | A ticket with Origin *Backfilled* has no REF. Set the REF to the token of the placeholder it replaced, or change the Origin to *Backdated* if it documents older work. |
| `board.ticket.version-form` | Fix | 5 | Owner | Yes | A Version value is not in the board form (`V000.010.001`). The scheduled run rewrites it, or type the three-digit form. |
| `board.ticket.version-title` | Fix | 5 | Owner | Yes | A Version ticket is not titled `Version 000.010.001`. Retitle it in the board form. |
| `board.ticket.alert-priority` | Fix | 5 | Owner | Yes | An Alert does not have Priority *Critical*. Set it. |
| `board.ticket.area` | Fix | 5 | Owner | Yes | A work ticket has no Area label. Add one. |

---

## 5. The baseline (`audit.py`)

`audit.py` reads the accepted deviations from `.github/audit-baseline.json` in the audited project (or the file
given with `--baseline`) and shows the failures they accept as *accepted*. It adds one check of its own.

| Id | Class | Stage | Role | Undo | What it means and what to do |
|---|---|---|---|---|---|
| `baseline.stale` | Fix | 7 | Owner | Yes | An entry of the baseline accepts nothing now: the check passes, or the items it names are gone. Remove the entry, so the file lists only what is still deviating. |
