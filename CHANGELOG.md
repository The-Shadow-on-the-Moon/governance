# Changelog

## WIP-Version
### Build 20261006024537 (branch apply-governance-to-itself)
#### #38 — Add the daily schedule to the workflow
- .github/workflows/versioning.yml: added a `daily` job, run every day at 06:17 UTC and on request with the new input `mode` set to `daily` (the other mode, `finalize`, is the existing manual finalize run, so a manual start runs exactly one of them): the preflight, the attaching of Implemented tickets, the date sweep, the Watch flags and the Caution flags for field rules, each a dry run for a manual dry run. It never commits or pushes, so it cannot loop and writes nothing to a branch; the `main` job now runs on a manual start only for mode `finalize`. The dry-run input text now says it covers the steps.
- .github/scripts/implemented.py: added `daily_sweep` and a command line entry (`--dry-run`): judges the Implemented tickets by the finalized versions in the changelog, and gives a blank Version the latest one; it does nothing if there is no finalized version or no Version ticket for the latest. An Abandoned ticket is never attached (it never shipped).
- tests/test_workflow.py: the schedule, the input, the job's steps and order, and that it has no git commands; tests/test_implemented.py: the daily sweep and the Abandoned case.
- doc/wiki/Automation.md: described the daily run.
### Build 20261006023919 (branch apply-governance-to-itself)
#### #37 — Add the Caution flags for broken field rules
- .github/scripts/field_rules.py: added; checks the rules that span fields on every ticket on the board and raises Attention *Caution*, with one comment naming what is broken, for: Completed without Resolution Done; Abandoned without one of the abandon reasons; an open ticket with a Resolution or an End date; Waiting on a Completed or Abandoned ticket; a Backfilled ticket with no REF; an issue open at Completed or Abandoned, or closed at any other stage. Only when neither the issue nor the board item has changed for five minutes; only on a ticket that is blank, Fine, Acknowledged or Watch (never lowering a level); once per set of broken rules (kept in a hidden marker in the comment): after a person closed the flag it comes back only when a rule not named before is broken. Version and Alert tickets are skipped; reads every page of the board; `--dry-run` only reports.
- .github/workflows/versioning.yml: the `main` job runs it after the Watch sweep (a dry run for a manual dry run).
- tests/test_field_rules.py: added; 19 tests (each rule, the quiet period, open and closed flags, the same and different rules, skipped types, paging, dry run); tests/test_workflow.py: the step order.
- doc/wiki/Automation.md: described the flags.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
### Build 20261006023458 (branch apply-governance-to-itself)
#### #36 — Add the Watch flags for stale tickets
- .github/scripts/watch.py: added; raises Attention *Watch*, with one comment, when a ticket has had no activity at Review for a week, at OnDeck or InProgress for a month, at Suspended for six months, or has been waiting for input for two weeks. Activity is a comment, a board change, or a new build; the automation's own flag comments do not count. It flags only a ticket that is blank, Fine or Acknowledged (never lowering a level), skips Version and Alert tickets, and raises it once per situation (the Progress with the latest build, kept in a hidden marker in the comment): a flag a person closed is raised again only when the stage changes or new work arrives. Reads every page of the board; `--dry-run` only reports.
- .github/scripts/push_step.py: its Caution comment now starts with the same hidden marker, so flag comments are recognised and do not count as activity.
- .github/workflows/versioning.yml: the `main` job runs the Watch sweep after the date sweep (a dry run for a manual dry run); the daily schedule is its own ticket.
- tests/test_watch.py: added; 17 tests (each limit, waiting, activity, open and closed flags, the same stage, a changed stage, new work, skipped types, paging, dry run); tests/test_workflow.py: the step order.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
#### #35 — Add the daily sweep for Start and End dates
- .github/scripts/dates.py: added; looks at every ticket on the board and sets Start date the first time it is seen at InProgress or beyond (anything but ToDo and OnDeck) and End date the first time it is seen Completed or Abandoned, only when blank and never overwriting; clears End date when a ticket is seen open again, so it is set again at the next end; Version and Alert tickets and draft items are skipped; reads every page of the board; dates are UTC; `--dry-run` only reports.
- .github/scripts/github_api.py: added `clear_project_field`.
- .github/workflows/versioning.yml: the `main` job runs the sweep after the stale-version check (a dry run for a manual dry run); the daily schedule comes with its own ticket.
- tests/test_dates.py: added; 12 tests (each status, existing dates kept, clearing and setting again, skipped types, paging, dry run); tests/test_workflow.py: the step order.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
### Build 20261006021728 (branch apply-governance-to-itself)
#### #34 — Add the fallback for skipped hooks: fill in the build heading with the commit and add a note
- .github/scripts/skipped_hooks.py: added; on a push to a branch, when the pushed changelog still has `### WIP-Build` (a commit made without the hooks), fills the heading in with the commit's own UTC time and the start of its hash (`### Build <stamp> (branch <name>, commit <hash>)`), adds a note to the first entry under it saying the hooks were skipped and the message was not drafted from the entries, commits that on the branch and pushes it. A placeholder that was already in the branch before the push is left alone; a push that cannot be fast-forwarded is reported; `--dry-run` only reports.
- .github/scripts/changelog.py: reads the new heading form (`Build.commit`), `stamp_wip_build` takes an optional commit, and `add_note` adds a bullet under a build's first entry.
- .github/workflows/versioning.yml: the `branch` job sets the commit author and runs the fallback before the push step, which then reads the repaired changelog.
- guides/03-project-structure.md, guides/Developer-Guides-Complete.md: the changelog structure shows the heading form the automation writes.
- tests/test_skipped_hooks.py: added; 10 tests on real temporary repositories with a bare remote; tests/test_workflow.py: the order of the branch job's steps.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
### Build 20261006015801 (branch apply-governance-to-itself)
#### #29 — Make finalize attach Implemented tickets
- .github/scripts/implemented.py: added; at every finalize and manual run, finds the board tickets with Delivery *Implemented* that are not sub-issues of any ticket and attaches each to a Version ticket by its Version (blank: the version being finalized and the field is filled in; an already finalized version: kept, attached to that version's closed ticket; a later or unreadable version: left alone), sets Version#, leaves Delivery and Build alone, and comments once per Version ticket on which tickets were added. Reads every page of the board.
- .github/scripts/finalize.py: runs that sweep after the Version ticket is recorded (and when a version is re-checked), with the existing dry run; the Version ticket lookup now shares the sweep's code.
- tests/test_implemented.py: added; 12 tests for each case of the sweep, the comments, the paging and the call from finalize.
- tests/test_finalize.py: the fake board answers the sweep's query.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
- doc/wiki/Automation.md: described the sweep.
- .github/automation-manifest.json: rewritten for the changed and new files (standard V0.5.0).
#### #33 — Add the push step: Delivery Pushed, InProgress, and a Caution when new work reaches a finished ticket
- .github/scripts/push_step.py: added; on a push to a branch, for each ticket in the open version's changelog entries that the push added (a sync that brings in finalized versions from main is ignored; a new branch is compared with main), sets Delivery to Pushed and Build to the ticket's latest build, moves ToDo and OnDeck to InProgress, and raises Caution with one comment naming the build when the ticket is Completed, Abandoned, Review or Suspended and its earlier work was already pushed or delivered (never on a ticket's first push, since a ticket moved to Review before its first push has no earlier work; not again while a Caution or AtRisk is open, never moving the ticket out of its state). Adds a ticket missing from the board; `--dry-run` only reports.
- .github/scripts/finalize.py: the ticket query also reads Attention.
- .github/workflows/versioning.yml: runs on pushes to every branch; a new `branch` job runs the preflight and the push step (not for main, not for a deleted branch), and the `main` job now only runs for main.
- guides/03-project-structure.md, 04-starting-work.md, 06-syncing-and-merging.md, appendix-c-ticket-fields-reference.md, Developer-Guides-Complete.md: the Caution for new work now says it needs earlier pushed or delivered work, and that a ticket's first push never raises it (the push step as first written would have flagged every ticket moved to Review before its first push).
- tests/test_push_step.py: added; 18 tests on real temporary repositories and fake clients (each state, an open flag, a closed flag, a new branch, a later push, a sync, a ticket not on the board, dry run).
- tests/test_workflow.py: tests for the new job and the main-only condition.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.

## V0.4.0 — 2026-10-06 00:47 UTC
### Build 20261006004523 (branch apply-governance-to-itself)
#### #28 — Add the Implemented Delivery value for tickets with no file change
- guides/appendix-c-ticket-fields-reference.md: added the Delivery value *Implemented* (set by a person, with the Version it belongs to, on a ticket with no file change), the rules for how finalize attaches such tickets and how a release treats them, and that a person's Version stays on them; Delivery is now "where the delivered work is".
- guides/01-concepts-and-vocabulary.md, 03-project-structure.md, 05-working-and-committing.md, 06-syncing-and-merging.md, 07-issues-and-the-board-in-practice.md, 08-releases-hotfixes-and-retiring-branches.md, 09-working-with-an-ai-assistant.md, 10-new-project-bootstrap.md: updated to match (the field table and rules, the Version ticket rules, the settings row of the update checklist, what the automation does and the step for work with no file change, target versions, releases, what an assistant may set, and the board's Delivery values).
- guides/Developer-Guides-Complete.md: rebuilt.
- .github/scripts/preflight.py: the board check now also requires the Delivery value *Implemented*.
- doc/wiki/Automation.md: added a section on tickets with no file change.
- .github/automation-manifest.json: rewritten for the changed script (standard V0.4.0).

## V0.3.1 — 2026-10-06 00:04 UTC
### Build 20261006000318 (branch apply-governance-to-itself)
#### #24 — Fix the preflight's write-access check for the workflow's token, and finalize V0.3.0 by hand
- .github/scripts/preflight.py: fixed; the repository check no longer fails on the workflow's own token, which GitHub does not report push rights for. It confirms the repository is reachable with that token and write access through the project token, and fails naming the case when neither token (or no project token) can confirm it.
- .github/scripts/finalize.py, .github/scripts/bypass.py: fixed; the automation's commits are pushed with `git push origin HEAD`, so a clone with no upstream branch works.
- .github/scripts/finalize.py: fixed; checking a finalized version again now gives the real bump (for example "sub, from V0.2.0 to V0.3.0") in the Version ticket instead of "recorded earlier".
- tests/test_preflight.py, tests/test_finalize.py: added tests for each of the above.
- CHANGELOG.md: the `V0.3.0` heading was renamed by hand (commit `90a3497`), because the first run of the workflow stopped at the preflight; the ticket records the correction.
- doc/wiki/Automation.md: described how the preflight confirms write access.
- .github/automation-manifest.json: rewritten for the changed automation files (standard V0.3.1).

## V0.3.0 — 2026-10-05 23:32 UTC
### Build 20261005232622 (branch apply-governance-to-itself)
#### #14 — Add the local hooks and their activation command
- .githooks/hooks.py: fixed; the stamped changelog was committed with Windows line endings (found when the hooks ran on the first real commit). Git is now run with bytes in and out, so line endings pass through untouched.
- tests/test_hooks.py: added a test that the staged changelog keeps LF line endings.
#### #12 — Add the automation's shared library (changelog parser, version rules, GitHub client) with tests
- .github/scripts/changelog.py: fixed; a changelog with Windows line endings is now read, stamped and renamed without changing its line endings (the first commit on this branch has such a changelog).
- tests/test_automation_library.py: added a test for it (30 tests).
### Build 20261005232139 (branch apply-governance-to-itself)
#### #12 — Add the automation's shared library (changelog parser, version rules, GitHub client) with tests
- .github/scripts/versions.py: added; the version format, the bump rules (from ticket Types or a marker, mod by default, major never automatic, first version V0.1.0), Version#, and UTC build stamps and heading times.
- .github/scripts/changelog.py: added; reads the changelog into versions, builds and ticket, REF and AUTO-REF blocks, rejects malformed headings, and writes the two edits the automation makes (renaming the open heading, stamping the WIP-Build placeholder).
- .github/scripts/github_api.py: added; a standard-library GitHub client for issues, sub-issues, comments, tags, repository variables and board fields, with the transport replaceable for tests.
- tests/test_automation_library.py: added; 29 tests, including that the repository's own changelog parses with Version# 10000 and 20000.
#### #13 — Add the preflight and the repository variable for the board number
- .github/scripts/preflight.py: added; checks the repository and its permissions, the project token, which board is linked to the repository (storing its number in the repository variable BOARD_NUMBER, or asking the administrator when there are none or several), and the board's 15 fields and their values. A failed check says which one and why, and the checks that depend on it are skipped. `--no-store` leaves the variable alone.
- .github/scripts/preflight.py: also reads the project token's expiry date and warns when it is within 14 days or when the token has none.
- .github/scripts/github_api.py: the client keeps the latest response headers and reports the token's expiry date.
- tests/test_preflight.py: added; 17 tests with the GitHub client faked, covering each failure message and the expiry warnings.
#### #14 — Add the local hooks and their activation command
- .githooks/pre-commit, prepare-commit-msg, pre-push: added; three small entry scripts that find a working Python 3 and call the shared script, and never block a git operation (a missing Python or an error only prints a message). Kept executable.
- .githooks/hooks.py: added; stamps `### WIP-Build` in the staged changelog with the UTC time and branch (and in the working copy, leaving other unstaged edits alone), drafts the commit message from the new entries (ticket title, "Multiple tickets", or the first bullet for a REF, then a block per ticket), warns about a commit with no changelog entry, a merge to recompile and retest, and a hand-resolved conflict, and on push warns when the branch is behind main, when a pushed changelog still has the placeholder, and when a merge is included.
- tests/test_hooks.py: added; 21 tests, including real commits in a temporary repository with the entry scripts active.
- README.md: added a Setup section with the one command that activates the hooks.
#### #15 — Add the finalize step: version bump, heading rename, ticket fields and the Version ticket
- .github/scripts/finalize.py: added; decides the bump from the tickets' issue Types or the marker, renames the open WIP-Version heading to the version with its UTC date and time in a commit of its own (and pushes it), sets Delivery Merged, Version, Build (the ticket's latest build) and Version# on each ticket's board item (moving ToDo and OnDeck to InProgress, never touching a Completed ticket, adding a ticket missing from the board), and creates or reuses the Version ticket with a generated description, the tickets as sub-issues and its board fields, then closes it. Running it again skips what is done; a board error is logged and does not stop the version; `--dry-run` only reports and `--no-push` keeps the commit local.
- .github/scripts/github_api.py: made the repository path helper public (`repo_path`).
- .github/scripts/preflight.py: the command line prints UTF-8.
- tests/test_finalize.py: added; 15 tests with fake clients and a temporary repository with a bare remote, covering the whole step, the advances, markers, the first version, dry run, a second run, a planned Version ticket, board errors and a malformed changelog. A dry run on the changelog as it was at the V0.2.0 merge, against the real board, produces V0.2.0 at 21:24 UTC and finds the board and Version ticket #11 already as they should be.
#### #16 — Add the advisory check and bypass detection (Alerts, AUTO-REF, missing entries)
- .github/scripts/checks.py: added; git-only analysis: how far a branch is behind main, whether a merge is identical to its branch's final state or was resolved by hand (by re-running git's own merge of the two parents), which commits of a push bypassed the flow (a direct push, or a merge that is not identical or was resolved by hand; the automation's own version commit is exempt), and whether files changed with no changelog entries.
- .github/scripts/advisory.py: added; the pull request check: fails and comments once when the branch is behind main, and lists merges with a manual conflict resolution; it fails open if GitHub cannot be reached.
- .github/scripts/alerts.py: added; the texts of the four Alerts (bypass, merge without entries, stale planned Version tickets, unreadable changelog), creating an Alert ticket (Type Alert, Area process, Critical, ToDo, on the board), and writing the AUTO-REF entry, creating the open version when there is none.
- .github/scripts/bypass.py: added; after a push to main, raises one Alert and writes one AUTO-REF entry for the whole push (committed on top), raises the Alert for an unreadable changelog, and raises the stale-planned-versions Alert after a version is finalized; `--dry-run` only reports.
- .github/scripts/finalize.py: the version decision moved into `decide` so the Alert can name the version.
- .github/scripts/preflight.py: the board check now also requires the Priority value Critical.
- tests/test_checks.py: added; 32 tests on real temporary repositories (each merge shape, each flagged case, the entries check) and fake clients. Run over the real history, no bypass is detected in the four pushes so far.
#### #17 — Add the versioning workflow that runs them
- .github/workflows/versioning.yml: added; on a pull request it runs the advisory check; on a push to main it runs the preflight, bypass detection, the finalize step and the stale-version check, in that order (skipping the automation's own "Finalize" and "Flag bypass" commits so it cannot loop); on request it runs the preflight and the finalize step, as a dry run unless told otherwise. It declares its own write permissions for contents, issues and pull requests (the default stays read-only), checks out main with the project token so the automation's commits can be pushed, and runs one push at a time.
- .github/scripts/bypass.py: added the `stale` command that the workflow runs after a finalize.
- tests/test_workflow.py: added; 11 tests checking the workflow's triggers, permissions, step order, loop guard and that every script it runs exists, plus the stale command. The workflow itself is proven by a real run in the level-1 proof ticket.
#### #18 — Add the manifest and the check script
- .github/automation-manifest.json: added; names the version of the standard (V0.3.0) and the SHA-256 fingerprint of each of the 23 automation files (hooks, scripts, workflow, pull request template and the automation's tests; line endings are ignored).
- .github/scripts/check_manifest.py: added; reports each file as unchanged, edited locally or missing; with `--against` a newer manifest it also reports files from an older version and files new in the standard; `--update --standard <version>` rewrites the manifest.
- tests/test_manifest.py: added; 8 tests, including one that fails when an automation file is edited without rewriting the manifest.
#### #22 — Update the readme, wiki and AGENTS.md for the automation
- README.md: added the hooks and the `.github/` folder to the table, an Automation section with the manifest commands, and a Status section saying what is still open (the mandatory up-to-date check and the proof by a real run).
- doc/wiki/Automation.md: added; the hooks, the workflow and when each part runs, the preflight and finalize step, the check script, how to run the tests and the token.
- doc/wiki/Home.md: added the Automation link.
- AGENTS.md: added the hook activation, the manifest rule for automation files, and that they change only through a ticket.

## V0.2.0 — 2026-10-05 21:24 UTC
### Build 20261005211638 (branch apply-governance-to-itself)
#### #4 — Add the pull request template
- .github/pull_request_template.md: added; pre-fills the pull request description with a place for the changelog entries, the tested-build and sync line, and a reminder to reword closing keywords.

#### #5 — Add AGENTS.md with roles and the pointer to the guides
- AGENTS.md: added; points to the guides, gives the build and test commands, states that there are no durable authorizations, and lists what is out of bounds (the generated combined copy, and settings).

#### #7 — Record roles and repository access
- AGENTS.md: roles recorded; Damian Bucovsky is administrator, project owner and developer, and Pablo is developer with write access.
- doc/wiki/Roles-and-Access.md: added; the same roles and access in a table.

#### #6 — Add the dual licence (CC BY 4.0 and MIT)
- LICENSE: added; says which paths are under which licence (documentation under CC BY 4.0, code under MIT; copyright The Shadow on the Moon, Inc.).
- LICENSE-CC-BY-4.0.txt, LICENSE-MIT.txt: added; the full texts.
- README.md: added a Licence section.
- doc/wiki/Home.md: added a Licence section.

#### #8 — Create the board's saved views
- doc/wiki/Board-Views.md: added; the daily and consistency views with their filters, so the board's views can be recreated. The views themselves are created on the board by the administrator.
- doc/wiki/Home.md: added links to the roles and board views pages.

#### #9 — Fix the readme status text
- README.md: reworded the Status section to describe only this repository, with no mention of the project the guides came from or its release number.

## V0.1.0 — 2026-10-05 18:22 UTC
### Build 20261005181657 (branch initial-structure)
#### #1 — Initial structure of the project
- guides/: added the README, guides 01 to 10 and appendices A to D, moved here from the project they were developed in, and the combined copy Developer-Guides-Complete.md.
- tools/combine.py: added; rebuilds the combined copy from the separate guide files, and with --check reports whether it is up to date.
- tools/xref_check.py: added; checks that every cross-reference between the guides points at a section that exists.
- tests/test_tools.py: added; 9 tests for both tools, including that the combined copy is current and that the guides have no broken references.
- README.md: replaced GitHub's placeholder with the repository readme: what the repository holds and how to work on the guides.
- doc/wiki/Home.md: added; the wiki home page, linking to the guides.
- .github/workflows/wiki-sync.yml: added; copies doc/wiki/ to the repository's wiki on a push to main that touches it, and on request.
- .gitignore, .gitattributes: added; ignore generated and system files, and keep line endings as LF.
- CHANGELOG.md: started with this entry.
