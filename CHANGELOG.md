# Changelog

## WIP-Version
### Build 20261008230718 (branch project-views)
#### #113 — Keep each rule in one place in the guides, with tests against drift
- A sweep of every guide, the appendices, the wiki and the readmes for rules stated in more than one place (a scan of repeated passages, a scan of repeated numbers and counts, and a check that every cross-reference points at a section about the topic named).
- guides/appendix-c-ticket-fields-reference.md: the Progress, Waiting and Resolution paragraphs no longer repeat the rules of Project structure, section 4.3; they point to it.
- guides/08-releases-hotfixes-and-retiring-branches.md (section 2.4): the hotfix rules that Branching and merging sections 1.3 and 2.2 already set out are replaced by a pointer; the rules that belong to the procedure stay. guides/06-syncing-and-merging.md (sections 6.3, 7.1): the bypass and branch-retirement rules point to Branching and merging, sections 6.5 and 1.5. guides/04-starting-work.md (section 3.2) and guides/03-project-structure.md (section 8.1): the hotfix branch name points to Branching and merging, section 2.1. guides/03-project-structure.md (section 7.3), guides/05-working-and-committing.md (sections 1, 7.2) and guides/01-concepts-and-vocabulary.md (section 1): the rules on entries and on the build block, the Attention advice and the test-result sentence point to their one home.
- guides/appendix-e-ticket-model.md and doc/wiki/Ticket-Model.md: the questions of the Attention and Origin fields are worded as in Project structure, section 4.2 (the test found them different).
- doc/wiki/Automation.md: the date sweep runs on every scheduled run (it said "every day"); a release treats Implemented tickets like merged ones (it said "will"); the release step records the result as a strong recommendation; bypass detection includes the changelog-error Alert.
- tests/test_tools.py: 2 new tests, the field questions of Project structure, Appendix E and the wiki page Ticket-Model are identical, and the line-endings rule quotes the project's own `.gitattributes`; 9 tests in `GuideValueTests`.
- guides/Developer-Guides-Complete.md rebuilt; `xref_check` reports 0 problems.
### Build 20261008225021 (branch project-views)
#### #113 — Keep each rule in one place in the guides, with tests against drift
- guides/README.md: new section "Where a rule lives", a table that names the one place each rule is set out.
- guides/appendix-c-ticket-fields-reference.md: the Attention causes, idle times, waits and re-raise rules and the Delivery rules paragraph are replaced by a pointer to Project structure, sections 4.3, 4.4 and 5.2 (the values tables stay). guides/03-project-structure.md (section 4.3): the rules that only the reference had are moved there (*Committed* is overwritten by *Pushed*, a suspended branch keeps *Pushed*, hotfix and release Delivery); section 5.2: a scheduled run attaches a blank Version to the latest finalized version; section 8.2: the tag table is replaced by a pointer to Branching and merging, section 2.2.
- guides/appendix-e-ticket-model.md: the restatements of the Caution rule, the cross-field table, the Version and Alert ticket stages and the bump rules are shortened to a summary and a pointer.
- guides/04-starting-work.md (section 5): the restatement of the Caution rule is replaced by a pointer to project structure, section 4.3.
- tests/test_tools.py: added `GuideValueTests`, 7 tests that fail when the guides and the automation disagree: the idle thresholds and the waits before a flag (against `watch.py` and `field_rules.py`, in Project structure), that the fields reference does not repeat them, the Alert kinds, the Area labels, the board values of the bootstrap against the fields reference, and the bump per Type in Appendix C against the table in Branching and merging.
- guides/Developer-Guides-Complete.md rebuilt; `xref_check` reports 0 problems.
### Build 20261008223645 (branch project-views)
#### #109 — Fix contradictions and stale statements in the guides
- guides/01-concepts-and-vocabulary.md, 05-working-and-committing.md (sections 4.2, 4.3, checklists), 06-syncing-and-merging.md (section 2.1), 07-issues-and-the-board-in-practice.md (section 3), 08-releases-hotfixes-and-retiring-branches.md (section 1.1 and the checklist), 03-project-structure.md (section 2.1), appendix-a-cheat-sheet-daily-flow.md: recording test results is now a strong recommendation everywhere, releases and hotfixes included; "recorded result" is defined (previously a rule in 05 section 4.3, a recommendation for the file, and mandatory in two checklists).
- guides/03-project-structure.md (sections 5.3, 5.4), 07-issues-and-the-board-in-practice.md (section 5), appendix-e-ticket-model.md (section 5), appendix-c-ticket-fields-reference.md (Assignee row): the fourth Alert, "Changelog error on main: no version finalized", is described next to the other three, with its assignee and triage steps.
- guides/01-concepts-and-vocabulary.md: the labels are the 14 Area labels and `dummy` (section 8); a hotfix version is assigned when the hotfix is finished (section 1); the heading of section 5 reads "The words for branches and tags".
- guides/03-project-structure.md (section 4.3): the two-hour wait of the Delivery and Version rules next to the five-minute wait. guides/appendix-c-ticket-fields-reference.md: Alerts are Critical without a comment. guides/appendix-b-cheat-sheet-if-then.md: the skipped-hooks row points at Starting work, section 5.1. guides/03-project-structure.md (section 7.4): the placeholder stays when the change is described in a new block.
- doc/wiki/Home.md: Appendix D and the ten guides are linked. AGENTS.md: commit messages and pull request descriptions carry no assistant attribution.
#### #111 — Let an assistant sync main into the person's own branch without asking
- guides/09-working-with-an-ai-assistant.md (sections 2.1, 3.1, 3.2 and the checklist), guides/appendix-b-cheat-sheet-if-then.md: syncing `main` into the person's own work branch is routine; "merge" in the ask-first rule means a merge into `main` or a shared branch; "syncing" is no longer something a durable authorization covers.
#### #110 — Add missing guidance to the guides
- guides/03-project-structure.md (new section 2.3), guides/01-concepts-and-vocabulary.md (glossary), guides/10-new-project-bootstrap.md (sections 2.1, 2.2 and the checklist): the scheduled run is defined, and the schedule and the re-enabler workflow are part of the bootstrap.
- guides/03-project-structure.md (section 2.1, 2.2), guides/10-new-project-bootstrap.md (section 1 and the checklist): `.gitattributes` with `* text=auto eol=lf` is a rule, and the licence files are in the root table.
- guides/05-working-and-committing.md (section 5.1, checklist), guides/appendix-a-cheat-sheet-daily-flow.md: a fresh `### WIP-Build` is added before each commit. guides/03-project-structure.md (section 7.3): builds in a version are newest first.
- guides/05-working-and-committing.md (new section 4.4 and the automation row of section 3.2), guides/10-new-project-bootstrap.md (section 8.3): the procedure for trying an automation change with throwaway tickets.
- guides/06-syncing-and-merging.md (new section 1.4 and the checklist), guides/appendix-b-cheat-sheet-if-then.md: what to do when a push to a shared branch is rejected.
- guides/09-working-with-an-ai-assistant.md (new section 6.5): a template for a personal preferences file.
#### #112 — Housekeeping found by the guidelines analysis
- .gitignore: `.anchor` added.
- guides/appendix-c-ticket-fields-reference.md: the descriptions of the labels `config` and `content` and of the Types Task, Enhancement and Change now read exactly as they do on GitHub (US spelling in those three, and the colon style; `config` no longer lists "service definitions"), so the guide and the repository agree.
- guides/Developer-Guides-Complete.md rebuilt.
- doc/wiki/Roles-and-Access.md, AGENTS.md: other members of the organization can read the repository through the organization's default permission; reading is not a role (the account `claudia-tsom` has no grant on the repository).### Build 20261008215441 (branch project-views)
#### #108 — Analyze Guidelines
- doc/Evaluation/Combined-eval.md: added section 5, how the tickets #109 to #113 address the findings: the decisions taken, a map from each finding to its ticket, the findings with no ticket and why, and the order of work.
### Build 20261008211150 (branch project-views)
#### #108 — Analyze Guidelines
- doc/Evaluation/Claude-eval.md, Gemini-eval.md, Copilot-eval.md: added; three independent evaluations of the guides for coherence, consistency and completeness (the Claude one also checks the project against the guides).
- doc/Evaluation/Combined-eval.md: added; the three compared, with what to address, what is irrelevant or incorrect (and why), and how to fix each item.

## V0.9.0 — 2026-10-08 20:36 UTC
### Build 20261008202952 (branch project-views)
#### #104 — Document that Completed work has a Delivery and shipped work has a Version
- guides/03-project-structure.md (section 4.4: three rows, and the Caution causes), guides/07-issues-and-the-board-in-practice.md (section 6.1 on Implemented tickets and a blank Version, the board review item 4, and a checklist line before Completed), guides/appendix-c-ticket-fields-reference.md (the two-hour wait of the Delivery and Version rules; the Delivery section: the sweep runs at every scheduled run, and the two gaps are flagged), guides/appendix-e-ticket-model.md (two rows): a Completed work ticket has a Delivery, shipped work has a Version, pure analysis is Implemented and never blank.
- doc/wiki/Automation.md: the two rules, their two-hour wait and why they run after the sweeps; the sweep gives a blank Version the latest finalized version at a scheduled run.
- guides/Developer-Guides-Complete.md rebuilt; `xref_check` reports 0 problems.
### Build 20261008202143 (branch project-views)
#### #99 — Flag a Completed work ticket that has no Delivery
- .github/scripts/field_rules.py: added the rule `completed-without-delivery` (Status Completed, Delivery blank; Version and Alert tickets exempt); the Caution comment says to set Implemented if no file changed, Merged if files did, or Abandoned with a reason. The board query now reads Delivery. A rule can wait longer than the usual five minutes: `WAIT` gives this one two hours (a person may be in the middle of completing the ticket); a rule still inside its wait is left out of the flag, and the others in the same sweep are flagged as before.
- tests/test_field_rules.py: 4 new tests (the rule, its exemptions, the two-hour wait, a quick rule flagged while the slow one waits); the ticket helper gives a Completed ticket Delivery Merged unless a test says otherwise. A dry run against the board reports no flag.
- .github/automation-manifest.json: regenerated for `field_rules.py`.
#### #100 — Flag shipped work that still has no Version
- .github/scripts/field_rules.py: added the rule `shipped-without-version` (Delivery Merged, Implemented or Released and a blank Version; Version and Alert tickets and Abandoned tickets are left out, because the sweeps never attach those). It waits two hours since the ticket's last change (`WAIT`), and runs after the Implemented sweep and the finalize step in the same run, so a ticket they attach is not flagged. A ticket with a Version, even one aimed at a version that is not finalized yet, is not flagged (the passed-version Caution covers the other case). The board query now reads Version.
- tests/test_field_rules.py: 4 new tests (the rule and its exemptions, the aimed-at-a-future-version case, the two-hour wait and the flag text); 27 tests. A dry run against the board reports no flag.
- .github/automation-manifest.json: regenerated for `field_rules.py`.
#### #101 — Show unversioned finished work in the Health view
- .github/views.json: the Health filter gains two clauses, `(status:Completed no:delivery AND -type:Version AND -type:Alert)` (a Completed work ticket with no Delivery) and `(delivery:Implemented,Merged no:version)` (shipped work with no Version), and the view shows the Version field after Delivery. The filter is now 468 characters (the longest one tried on the board before was 357); a dry run of `views.py --only Health` plans to recreate the view, and it has not been applied.
- tests/test_views.py: 3 new tests on the real definition file (both clauses and the Version column).
- doc/wiki/Board-Views.md: the Health row and the table of what Health catches describe the two clauses.
- .github/automation-manifest.json: regenerated for `views.json`.
#### #102 — Run the scheduled job three times a day and stop it overlapping a merge
- .github/workflows/versioning.yml: the schedule is three runs a day, 08:17, 16:17 and 20:17 UTC (4am, noon and 4pm ET in summer time; an hour earlier in winter, because cron has no time zone). The `main` job (a push to main) and the `daily` job now share one concurrency group, `versioning-board` (they were `versioning-main` and `versioning-daily`, so a merge and a scheduled run could attach a ticket or post a comment twice), with `cancel-in-progress: false`. The `main` job also runs the Version# sweep, after the stale-version check and before the date sweep (it ran only in the daily job). The header comment describes all of it.
- tests/test_workflow.py: the three times, the shared group, and the order of the new step in the main job.
- doc/wiki/Automation.md: the table rows and the paragraph on the scheduled job. Not done here: the guides that say "every day" or "once a day" (appendix E, guide 03, appendix C) are left to the documentation ticket #104.
- .github/automation-manifest.json: regenerated for the workflow.
#### #103 — Rename the daily job and mode to scheduled
- .github/workflows/versioning.yml: the job `daily` and the manual mode `daily` are now `scheduled` (the job runs three times a day and on request); the header comment says so. A manual start now uses mode `scheduled`; the old name is gone.
- .github/scripts/implemented.py: `daily_sweep` is now `scheduled_sweep`, and the comment on a passed version says "the next scheduled run". .github/scripts/version_numbers.py: its docstring says "the scheduled run". tests/test_workflow.py and tests/test_implemented.py follow (the test names too).
- doc/wiki/Automation.md (the table rows, the section "The scheduled run", the script and job tables), README.md, guides 03 (section 5.2), appendix C and appendix E: "daily" and "every day" became "scheduled" and "on every scheduled run". Left as they are, because they mean something else: "the daily flow" (appendix A), "the daily board" and "daily handling" (guide 07, the guide README, Home).
- guides/Developer-Guides-Complete.md rebuilt; .github/automation-manifest.json regenerated.
### Build 20261008200831 (branch project-views)
#### #105 — Re-enable the scheduled workflow after GitHub disables it for inactivity
- .github/scripts/reenable_schedule.py: added; reads the state of `versioning.yml` and enables it only when it is `disabled_inactivity` (switched off by GitHub after 60 days without repository activity); `disabled_manually` and every other state are left alone; `--dry-run` only reports; a failure to enable fails the run.
- .github/workflows/reenable-schedule.yml: added; no schedule (so GitHub never disables it), runs on a push to any branch (not only `main`, so the first activity after a long pause wakes the schedule) and on request; permission `actions: write` only.
- tests/test_reenable_schedule.py: 12 tests (the decision, the calls made, dry run, a refused enable, and the structure of the workflow file).
- doc/wiki/Automation.md: describes it.
- .github/automation-manifest.json: regenerated for the three new files (standard V0.9.0 is provisional: an Enhancement bumps the sub version; check it against the changelog after the finalize).
## V0.8.3 — 2026-10-08 13:15 UTC
### Build 20261008013731 (branch project-views)
#### #96 — Two files are opened without being closed (ResourceWarning on Python 3.14)
- tools/xref_check.py: fixed; `load()` read the ten guide files with `open(...).read()` and never closed them (ten unclosed files per call, about 20 `ResourceWarning` lines per test run); it now reads each file with a `with` statement.
- tests/test_checks.py: fixed; the bypass test read `CHANGELOG.md` the same way and now closes it.
- .github/automation-manifest.json: regenerated for `tests/test_checks.py` (standard V0.8.3, a mod bump after V0.8.2).
## V0.8.2 — 2026-10-07 19:08 UTC
### Build 20261007183941 (branch project-views)
#### #90 — Move actions/checkout to a Node 24 release in the workflows
- .github/workflows/versioning.yml and .github/workflows/wiki-sync.yml: every `actions/checkout@v4` (seven and two) is now `actions/checkout@v7`. v4 targets Node 20, which GitHub removed from the runners on 2026-09-23, so it ran only because the runner forced it onto Node 24 (the warning on every run). The extras (persist-credentials, SHA pinning, Dependabot) are not part of this change.
- tests/test_tools.py: added a test that every `actions/checkout` use in the workflows names one release and that it is v5 or later (the first Node 24 release).
- guides/10-new-project-bootstrap.md: a recommendation to keep the workflows' actions on a supported runtime and to prove the git pushes when moving.
- .github/automation-manifest.json: regenerated for the changed workflow (standard V0.8.2).
## V0.8.1 — 2026-10-07 15:19 UTC
### Build 20261007150026 (branch project-views)
#### #86 — An Implemented ticket aimed at a version that was passed waits for ever without a flag
- .github/scripts/implemented.py: an Implemented ticket aimed at a version that is not finalized while a higher version is (the number was passed and can no longer happen) now gets Attention Caution and one comment (marker `<!-- attention:caution passed=V0.7.1 -->`), once per passed version and not when a Caution or AtRisk is already open; it is still never moved or attached by itself. A version above the latest finalized one still waits quietly. tests/test_implemented.py: 6 new tests.
- guides/07-issues-and-the-board-in-practice.md (section 6.1: leave the Version of an Implemented ticket blank until the version is finalized, and what the flag means), guides/03-project-structure.md and guides/appendix-c-ticket-fields-reference.md (the causes of Caution), doc/wiki/Automation.md.
#### #85 — The manifest names a version that never existed
- .github/automation-manifest.json: `standard` is the version these changes ship in (V0.8.1), regenerated after the code and tests of this version; it said V0.7.1, which never existed (the merge produced V0.8.0).
- AGENTS.md: `--standard` is the version the open version will become; after the finalize it is checked against the changelog and corrected through a ticket if the marker or the Types changed it.
## V0.8.0 — 2026-10-07 14:40 UTC
### Build 20261007143643 (branch project-views)
#### #77 — Update the guides and the wiki for the new views
- CHANGELOG.md: the open version is marked `+s` (a sub bump), because the version adds the views script, the Version# step and the pull request step.
### Build 20261007142146 (branch project-views)
#### #80 — Set Version# for tickets that only have a target Version
- .github/scripts/version_numbers.py: added; a daily step that sets Version# from Version on every work ticket that has a Version (also one only aimed at a version) when Version# is blank or different (Version# is `Version.number()`); it changes nothing else, skips Version and Alert tickets and reports text that is not a version. A dry run only reports.
- .github/workflows/versioning.yml: the daily job runs it after attaching the Implemented tickets and before the date sweep. tests/test_version_numbers.py: 13 tests; tests/test_workflow.py: the order of the daily steps.
- guides/appendix-c-ticket-fields-reference.md, guides/03-project-structure.md, guides/appendix-e-ticket-model.md, doc/wiki/Automation.md: Version# is also set every day for a ticket that has a Version; manifest covers the new files.
#### #81 — Recommend aiming tickets with the Version field instead of planned Version tickets
- guides/07-issues-and-the-board-in-practice.md: section 6.2 says to aim tickets with the Version field and leave the Version tickets to the automation, and that creating one ahead of time is allowed but not recommended (the Versions view orders its groups by the order the Version tickets were created in, so a ticket made early for a later version would sort ahead of a version that ships first; a planned number is also a guess); section 6.3 has the recommendation and the rule now covers a ticket made anyway; the Why and the checklist agree.
- guides/03-project-structure.md (section 5.2 stage table and recommendation) and guides/appendix-e-ticket-model.md (the stage table and the note): the planned stage is optional and not recommended.
#### #82 — Add pull requests to the board so the All view has no gaps in the numbers
- .github/scripts/board_pull_requests.py: added; puts a pull request on the board as an item with no field set (`PULL_REQUEST` and `PULL_REQUEST_NODE_ID`, as the workflow does when one is opened or reopened), or with `--all` every pull request that is not on it yet (a one-time backfill); whether one is already on the board is asked of the pull request itself, because the board's own list of items does not show the pull requests added to it; it never fails a pull request run. tests/test_board_pull_requests.py: 13 tests.
- .github/workflows/versioning.yml: the pull request job runs it before the advisory check, with continue-on-error, so a failure there never fails the check. tests/test_workflow.py: a test of that step.
- .github/scripts/views.py, .github/views.json: every view except All now ends with `AND is:issue AND -label:dummy` (the new entry key `include_pull_requests`, set only on All); the five views were created again; tests/test_views.py: 42 tests.
- tests/test_pull_request_items.py: added; the date, Watch, field-rule, Implemented and Version# sweeps skip a board item that is a pull request or a draft.
- guides/03-project-structure.md (section 6.2), guides/07-issues-and-the-board-in-practice.md (section 2.2), doc/wiki/Automation.md and doc/wiki/Board-Views.md: describe it; the 8 existing pull requests (#2, #10, #23, #26, #32, #53, #64, #68) were added to the board.
### Build 20261007042123 (branch project-views)
#### #72 — Create the All view
- .github/views.json: the `All` view now lists every ticket and hides nothing (no filter, so the test tickets are in it too), has no grouping, and is meant to be in ticket-number order (sort by Created, ascending).
- .github/scripts/views.py: an entry can say `"include_test_tickets": true` so its filter is not given ` AND -label:dummy`; a sort by Created, Updated or Closed can be written in an entry, but the API cannot set it when a view is created, so the script leaves it out of the request and out of the comparison and says to set it by hand (this replaces the earlier refusal). tests/test_views.py: 38 tests.
- .github/scripts/views.py, .github/views.json: an entry may list `manual_steps` (settings the API cannot reach); All lists turning off "Show hierarchy" and the script prints a reminder of the manual sorts and steps at the end of every run. tests/test_views.py: 41 tests.
- doc/wiki/Board-Views.md, guides/07-issues-and-the-board-in-practice.md, guides/appendix-c-ticket-fields-reference.md: describe All as the complete list, why the pull request numbers are missing from it, and the sort and the hierarchy setting to make by hand; guides/10-new-project-bootstrap.md: the same in section 6 and a checklist line.
#### #76 — Create the Versions view
- .github/views.json: the Versions view is now grouped by Parent issue (the Version ticket, so a group reads "Version 0.7.0" and the groups follow the order the Version tickets were created in) and sorted by Version#, then Priority. Grouping by Version# had unreadable headers (70000) and grouping by the Version text sorts alphabetically (V0.10.0 before V0.9.0).
- doc/wiki/Board-Views.md, guides/07-issues-and-the-board-in-practice.md: describe the grouping; tickets only aimed at a version are in the "No parent issue" group (their Version# comes with #80).
### Build 20261007033120 (branch project-views)
#### #70 — Add a script that creates and removes board views from a definition file
- .github/scripts/views.py: added; reads the board's views, compares them with `.github/views.json` and creates, recreates (create the new view, then delete the old one, because GitHub never deletes the last view of a board; grouping and sorting can only be set at creation) or deletes views: `--only NAME`, `--delete NAME`, `--delete-unlisted`, `--show`, `--definition PATH`; a dry run unless `--apply`; every filter gets ` AND -label:dummy`; field names are resolved to the numeric ids REST needs (GraphQL and REST are both read, because each lacks some fields); every field name is checked before anything changes; once a view changes the ones listed after it are recreated so the tabs keep the file's order; it refuses to delete a board's last view.
- .github/views.json: added, with an empty list of views (each view has its own ticket).
- .github/scripts/github_api.py: added `project_views`, `view_field_ids`, `create_view` and `delete_view`.
- tests/test_views.py: added; 34 tests (filter rule, definition checks, request bodies, reading a view, each sync case, deletion by name, the client calls).
- .github/scripts/check_manifest.py, doc/wiki/Automation.md: the manifest covers the new files; the script is described. Checked on the real board: a view with an `OR` filter, grouping, board columns, sorting and visible fields was created and read back (a 357-character filter, the whole Health filter, is accepted), then deleted.
- .github/scripts/views.py: found while applying the first view: the API cannot sort a new view by Created, Updated or Closed (the script refuses with a reason), and GraphQL does not report the Type field among a view's visible fields (it is left out of the comparison, so a view showing it is not seen as changed).
#### #72 — Create the All view
- .github/views.json: added the `All` view: a table of every ticket except the test ones, with all the fields, sorted by Version# (latest first) then Priority. The ticket asked for newest-updated first, but the API cannot sort a new view by Updated.
#### #73 — Create the Backlog view
- .github/views.json: added the `Backlog` view: a board with the columns ToDo, OnDeck and Suspended (filter `status:ToDo,OnDeck,Suspended`), sorted by Priority (Critical first), showing Priority, Size, Risk, Version, Assignees and Type.
#### #74 — Create the Board view
- .github/views.json: added the `Board` view: a board with the columns OnDeck, InProgress and Review and a row per Version (filter `is:open AND -type:Version AND -status:ToDo,Suspended`), sorted by Priority, showing Priority, Size, Assignees, Waiting, Attention and Type.
#### #75 — Create the Health view
- .github/views.json: added the `Health` view: one table of everything that needs a person (Attention Watch, Caution or AtRisk, Waiting for input, Review, open Alerts) or whose fields break a rule (Completed with no Resolution, open with a Resolution or an End date, Waiting on a closed ticket, Backfilled with no REF, an open issue at Completed or Abandoned, a closed issue at any other Progress except Version tickets), sorted by Priority, showing Attention, Waiting, Resolution, Delivery, End date, REF, Status, Type and Priority. It replaces the Attention, Waiting, Review, Alerts and consistency views, and adds the check that an issue is closed only at Completed or Abandoned.
#### #76 — Create the Versions view
- .github/views.json: added the `Versions` view: a table of the work tickets that have a Version (not the Version tickets), grouped by Version#, sorted by Priority within a group, showing Status, Type, Delivery, Build, Resolution, Version and Priority.
#### #77 — Update the guides and the wiki for the new views
- guides/07-issues-and-the-board-in-practice.md: section 2.2 describes the five saved views (All, Backlog, Board, Health, Versions) and that they are created from a file by a script; the Health view is where a work session starts; section 7.1 and 7.2: the Health view lists the field-consistency checks, replacing the recommendation to make them into views; the "In GitHub" notes cover `AND`/`OR` filters and that grouping and sorting are set only at creation; checklist updated.
- guides/10-new-project-bootstrap.md: the automation includes the views file and script; section 6 lists the five views, the rule that they come from `.github/views.json`, the one default view of a new board, and the checklist line; guide 01 ("View"), guide 03 (the administrator creates the views from a file) and appendix C (every view excludes `dummy`).
- doc/wiki/Board-Views.md: rewritten from the definition file (the five views with layout, filter, grouping and sorting, what Health catches, notes, the planned Roadmap); the wrong statement that the API cannot create views and the stale filter `has:"end date"` are gone.
- tests/test_tools.py: added tests that the wiki page lists every view and filter of `.github/views.json` and that no guide or the page says views cannot be scripted.
## V0.7.0 — 2026-10-06 21:50 UTC
### Build 20261006214642 (branch apply-governance-to-itself)
#### #65 — Raise the new-work Caution only when an earlier Build is recorded
- .github/scripts/push_step.py: fixed; the new-work Caution trusted Delivery alone, so a Delivery written by hand just before the push step ran (or the same push handled twice) made a Review ticket's first push look like new work. It now needs a recorded Build, a 14-digit stamp, older than the build being pushed; Delivery Implemented, which has no Build, still counts as earlier work.
- tests/test_push_step.py: existing cases get an earlier Build; added a hand-set Delivery with no Build, a Build equal to or newer than the pushed one, a Build that is not a stamp, and an Implemented ticket with no Build.
- guides/03-project-structure.md, guides/04-starting-work.md, guides/appendix-c-ticket-fields-reference.md, guides/appendix-e-ticket-model.md, doc/wiki/Automation.md: say that earlier work is recognised by the recorded Build.
#### #66 — Dummy versions and tickets cause confusion
- guides/appendix-c-ticket-fields-reference.md: described the `dummy` label (a marker for throwaway tickets and Version tickets made to test the automation, not an Area; working views exclude it with `-label:dummy`).
- guides/10-new-project-bootstrap.md, guides/07-issues-and-the-board-in-practice.md: the label list is the 14 Area labels plus `dummy`; the saved views leave test tickets out.
- doc/wiki/Board-Views.md, AGENTS.md: the test-ticket convention and the view filter.
- repository labels: created `dummy` and put it on the 15 DUMMY tickets and the two DUMMY Version tickets (#46 to #52, #54 to #63).
#### #67 — Ticket Model Design
- guides/appendix-e-ticket-model.md: added; the design of a ticket as a whole (the questions and fields, why each is separate, the life of a work ticket, the Version and Alert tickets, how the model drives the automation), written from the current implementation and the earlier design notes.
- doc/wiki/Ticket-Model.md, doc/wiki/Home.md: added a wiki page that summarises the model and links to the appendix.
- guides/README.md, guides/01-concepts-and-vocabulary.md, guides/03-project-structure.md, guides/appendix-c-ticket-fields-reference.md, README.md, HANDOFF-governance.md: refer to the new appendix.
- tools/combine.py, tests/test_tools.py: the combined file and its test now include appendix E; the combined file is rebuilt.
## V0.6.0 — 2026-10-06 03:35 UTC
### Build 20261006032529 (branch apply-governance-to-itself)
#### #44 — Document and prove merge C2
- README.md: the automation section lists the steps a person starts by hand (release, hotfix finish, branch retire), and the status says that anything still open is tracked in a ticket.
- AGENTS.md: a release, a hotfix finish and a branch retirement are done only by the workflow's manual runs, only when asked, with a dry run first.
### Build 20261006031532 (branch apply-governance-to-itself)
#### #43 — Add the manual inputs for release, hotfix and retire to the workflow
- .github/workflows/versioning.yml: fixed; the new checkout step name had a colon followed by a space, which made the file invalid YAML (GitHub reported a workflow file issue and could not start the workflow). The name is reworded.
- tests/test_workflow.py: added a test that no unquoted step name contains a colon followed by a space.
### Build 20261006031446 (branch apply-governance-to-itself)
#### #43 — Add the manual inputs for release, hotfix and retire to the workflow
- .github/workflows/versioning.yml: fixed; the `release` and `retire` jobs checked out `main`, so a manual start from a branch ran main's scripts and could not try a change. They now check out the ref the run was started from (start them from `main`, or from a branch to try a change).
- tests/test_workflow.py, doc/wiki/Automation.md: updated to match.
### Build 20261006031406 (branch apply-governance-to-itself)
#### #43 — Add the manual inputs for release, hotfix and retire to the workflow
- .github/workflows/versioning.yml: the manual start now has the modes `release`, `hotfix` and `retire` besides `finalize` and `daily`, with the inputs `version`, `branch`, `outcome`, `confirm` and `comment` (the dry run stays on by default). Three new jobs run the preflight and then the step: `release` (checks out main; `version` empty means the latest), `hotfix` (checks out the branch the workflow was started from, with its tags, sets the commit author, and takes the hotfix version from `version`; it only runs for a branch) and `retire` (checks out main; takes `branch`, `outcome`, `confirm` and `comment`). None of the others touches git.
- tests/test_workflow.py: the modes, the inputs reaching the scripts, which branch each job runs on, that only the hotfix job commits, and that the default stays a dry run of finalize; the daily job's checks now look only at that job.
- doc/wiki/Automation.md: how to start the three steps by hand.
### Build 20261006031245 (branch apply-governance-to-itself)
#### #42 — Add the retire step (tag, delete branch, Dropped on abandon)
- .github/scripts/retire.py: added; given a branch, an outcome (archived, suspended or abandoned) and the branch name typed again as a confirmation, it tags the branch's last commit `<outcome>/<yyyy-mm-dd>_<branch>[_<comment>]` (the UTC date of that commit, an optional kebab-case comment) and only then deletes the remote branch; for an abandoned branch it sets the Delivery of the tickets in the branch's changelog entries to Dropped. It refuses main, a wrong confirmation, a tag name that exists, an archived branch whose last commit is not on main, and a suspended or abandoned branch with an open pull request; a finished hotfix branch (its tip carries a hotfix release tag) is deleted without a retirement tag. `--dry-run` only reports.
- .github/scripts/github_api.py: added `delete_ref`.
- tests/test_retire.py: added; 18 tests on real temporary repositories with a bare remote (each outcome, the UTC date, tag before delete, the Dropped tickets, a finished hotfix, each refusal, dry run).
- doc/wiki/Automation.md: described the retire step.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
### Build 20261006030809 (branch apply-governance-to-itself)
#### #41 — Add the hotfix-finalize step
- .github/scripts/hotfix.py: added; run on a hotfix branch with the version (for example V1.25.0-HF1, via `VERSION` and `BRANCH` in the environment), it renames the open WIP-Version heading to that version in a commit of its own on the branch and pushes it, tags that commit `released/V1.25.0-HF1`, creates and closes the Version ticket (Delivery Released), and sets the tickets' Delivery straight to Released with the hotfix version, Version# and Build (never Merged). It refuses a hotfix number outside 1 to 9, a branch not named `hotfix-v<major>-<sub>-<mod>-<description>` for the release, a marker on the heading, an open version with no ticket entry, a version already finalized or already tagged, a base tag (the release, or the previous hotfix) missing from the clone, and a branch that does not contain it. `--dry-run` only reports.
- .github/scripts/finalize.py: the ticket and Version ticket updates take the Delivery value to set (Merged by default) and the Version ticket description can name its source, so the hotfix step reuses them.
- tests/test_hotfix.py: added; 12 tests on real temporary repositories with a bare remote (the whole finish, Released and not Merged, a second hotfix from the first, each refusal, dry run, no board).
- doc/wiki/Automation.md: described the hotfix-finalize step.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.
### Build 20261006030117 (branch apply-governance-to-itself)
#### #40 — Add the release step (tag, Version ticket and tickets Released, including Implemented)
- .github/scripts/release.py: added; given a finalized version (by default the latest) it tags the commit where that version's heading first appears (where it was finalized, not the tip of main) as `released/V<major>.<sub>.<mod>`, sets the Version ticket to Delivery Released and comments with the date and the tag, and sets to Released every ticket whose Delivery is Merged or Implemented and whose version is at or below the released one (a ticket with newer work, Delivery Pushed, keeps it; Version and Alert tickets, and other deliveries, are left alone). It refuses a version that is not finalized, one that already has a release tag, and one with no finalized Version ticket. `--dry-run` only reports; `VERSION` in the environment picks the version.
- tests/test_release.py: added; 12 tests (each rule, the refusals, an earlier version, dry run, no board, paging, and the finalize commit in a real repository).
- doc/wiki/Automation.md: described the release step.
- .github/scripts/check_manifest.py: the manifest now also covers the new test file.

## V0.5.0 — 2026-10-06 02:52 UTC
### Build 20261006025104 (branch apply-governance-to-itself)
#### #39 — Document and prove merge C1
- doc/wiki/Automation.md: added how to read a flag (the hidden markers, how to close one), a table of the scripts, how to start a run by hand, and fixed the date sweep text (it now runs daily).
- README.md: the automation section lists what the workflow does on each kind of push and the daily run, and the status says what is still to come (the release, hotfix and retire steps).
- AGENTS.md: the automation's flag comments and commit messages are not to be edited or reused; tests of the automation use throwaway tickets and branches titled DUMMY, closed as Invalid and with their branches tagged before deletion.
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
