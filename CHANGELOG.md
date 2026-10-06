# Changelog

## WIP-Version
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
