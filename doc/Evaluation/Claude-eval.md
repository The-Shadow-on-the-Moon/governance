# Governance review: guides and project adherence

Date: 2026-10-08. Analysis only: nothing in the repository was changed. `combine.py` was run and produced no diff; GitHub state was read with read-only `gh` calls.

## Verified results

- `xref_check.py`: 212 references, 0 problems.
- 408 unit tests passed (about 3m48s).
- `combine.py --check`: the combined copy is current.
- Manifest check: all files unchanged.

## Part 1: the guides

### Contradictions and inconsistencies

1. **Labels.** Guide 01 §8 says "The only labels are the 14 Area labels." Guide 10 §5.2, Appendix C and guide 07 §7.1 add `dummy`, and the repo has 15 labels. Fix guide 01.
2. **Test results.** The guides contradict each other on whether results must be recorded.
   - 05 §4.2 says "Nothing more is prescribed". 05 §4.3 makes recording a **Rule**.
   - The `tests/results/` location is only a Recommendation, but checklists 05 §8 and 06 §2.1 treat it as mandatory.
   - "Recorded test result" is never defined, so nobody can tell when a result has to be recorded.
3. **Alert causes.** The automation raises four kinds of Alert. 02 §3.3 describes the changelog-error Alert ("Changelog error on main: no version finalized"). 03 §5.3 and §5.4, Appendix E §5, guide 07 §5 and Appendix C list only three.
4. **Wait before a broken-rule flag.** 03 §4.3 says five minutes with no exception. 03 §4.4 and Appendix C say two hours for the Delivery and Version rules.
5. **Hotfix versions.** Guide 01 §1 says a version is assigned "when a branch merges into main". A hotfix version is assigned at hotfix finish and is never merged.
6. **Critical priority.** Appendix C says Critical "needs a comment saying why". Every automation-created Alert is Critical, and the automation writes no such comment. Hotfix tickets are Critical too.
7. **Assistant and merging.** 09 §3.1 requires approval for any "merge". Syncing `main` into a branch is a merge, yet guides 04 and 06 present it as routine. 09 §3.2 treats "syncing branches" as something a durable authorization can cover, which implies it is gated.
8. **Skipped-hooks pointer.** Appendix B points to "Working and committing §5" for the skipped-hooks fallback. That text is in guide 04 §5.1, with a mention in 03 §7.2.
9. **Root contents.** 03 §2.2 says the root holds "only what the table lists". The table omits `LICENSE*` and `.gitattributes`, which this repo has. The table needs a "licence" row and an "other root config" row.
10. **Smaller points.** Guide 01 §5's heading, "Branches and tags' words", is ungrammatical. The wiki Home lists Appendices A, B, C and E but not D, and links no individual guides.

### Gaps (incomplete)

- **Scheduled run.** The three-a-day scheduled run is a core mechanism. Version#, the Implemented attach, Watch flags and the field rules all depend on it. The only definition is a parenthesis in Appendix C ("three a day").
  - Guides 03 and 07 use the term without defining it.
  - The bootstrap guide (10 §2.1) doesn't list the schedule or the `reenable-schedule.yml` workflow. The latter exists because GitHub disables schedules after 60 days of inactivity.
  - The glossary (guide 01) has no entry for "scheduled run" or "sweep".
- **Line endings.** Bootstrap omits `.gitattributes`. Windows line endings broke the hooks and parser once (ticket #14, commits `f252bb7` and `d74d99d`, which rewrote the whole changelog).
- **Build order.** Nothing says builds inside a version are newest first. Only "newest version first" is stated.
- **Trialling automation.** The DUMMY-ticket convention (title `DUMMY`, label, close as Invalid, tag branches before deleting) lives only in Appendix C and `AGENTS.md`. Nothing in 05 §3.2's "Hooks, automation, process rules" row or the bootstrap trial (10 §8) says to use it.
- **Tool attribution.** 09 §4.2 forbids naming the tool in commit messages. Assistant tooling often appends a co-author trailer. `AGENTS.md` could say explicitly that the trailer is suppressed.

### Structural risk

Each Attention, Delivery and Version rule is restated in 4–6 places: 03 §4.3 and §4.4, Appendix C, Appendix E, guide 07, the wiki `Automation.md` and the changelog. Ticket #104 had to edit five files for two rules. Items 3 and 4 above are already drift from this. `xref_check` only checks that section numbers exist. It can't catch a rule that differs between two places. Consider one canonical location per rule, with the others linking to it.

### What is solid

- Every section reference in the glossary tables points to the right topic.
- The Rule / Recommendation / In GitHub markers are applied uniformly.
- Every procedural guide has a checklist.
- The role and responsibility model is consistent across guides.
- The enforcement stance is stated plainly: warn, allow a bypass, record it.

## Part 2: does the project follow the guides?

### Adheres (checked against live data)

- **Repository settings.** Only merge commits are allowed. Auto-delete of branches is off. `main` is protected with a required pull request, a required `advisory` check and strict up-to-date, and admin enforcement is off. The default token is read-only, and `PROJECT_TOKEN` and `BOARD_NUMBER` exist.
- **Issue types and labels.** All 8 issue types exist. There are exactly 14 Area labels plus `dummy`.
- **Board.** It has exactly the 15 specified fields and values. All 93 issues are on the board along with 14 pull requests.
- **History of `main`.** First-parent history is only pull request merges plus `Finalize` commits, with no direct pushes.
- **Pull requests.** All 12 real pull requests have no closing keywords, a "Tested on build" line and ticket blocks. #106's 7 blocks match V0.9.0.
- **Changelog and commits.** The changelog is newest first. Every real commit that changed files logged an entry, and build stamps match the commit's UTC time. Changelog ticket titles match the issue titles exactly (checked for every ticket). Versions and builds on the board match the changelog.
- **Tickets.** No non-dummy ticket breaks a cross-field rule: Size, Type, Resolution, Delivery or Version, closed state, Waiting or REF. No Attention flags are open. The 13 Version tickets for real versions match the changelog headings.
- **Hooks, manifest, assistant file.** The hook scripts are executable, the manifest is unchanged, and no tool names appear in committed files. `AGENTS.md` follows guide 09 §6.2.
- **Wiki.** The wiki-sync workflow matches the user's template, apart from `checkout@v7`.

### Deviations

1. **No test results are stored.** `tests/results/` doesn't exist, and nothing in the repo records a result naming a build.
   - 45 of 60 Completed work tickets have no comment naming a build. That is only a Recommendation, so it is a soft miss.
   - Whether the Rule is breached depends on what "recorded" means (guide item 2).
2. **Non-file statements in the changelog.** The guides say the changelog records changes to files and nothing else.
   - #82 says the 8 existing pull requests "were added to the board".
   - #72 says "the five views were created again".
   - #70 describes creating, reading back and deleting a view on the real board.
   - #99 and #100 say "a dry run against the board reports no flag".
   - #101 says the change "has not been applied".
3. **Undocumented collaborator.** `claudia-tsom` has read access. `Roles-and-Access.md` and `AGENTS.md` don't list them. They may be intentional, since read isn't a role, but guide 10's checklist says "Access matches the roles".
4. **Leftovers from dummy trials.**
   - A workflow named "Ubuntu 26.04 trial" (`ubuntu-26-trial.yml`) is still registered and shows active, but the file isn't on any branch.
   - Local tags `released/V9.9.9` and `released/V9.9.9-HF1` don't exist on the remote. `git fetch --prune --prune-tags` should drop them.
5. **Label description.** The `config` label drops "service definitions" from Appendix C's text. Issue-type descriptions use US spelling where Appendix C uses UK.
6. **Untracked `.anchor` file.** It isn't in `.gitignore`.
7. **Release and hotfix flows.** They have only been exercised with DUMMY tickets, never a real release. That is allowed.

### Not verified

The live saved views against `views.json`, the token's expiry date, and the `advisory` check's behaviour on a fresh pull request.

## Notes outside the review

- **Global preferences conflict with the standard here.** The user's global `CLAUDE.md` changelog format has "Known bugs" and "Planned" sections. The standard (03 §7.3) forbids them, and the repo follows the standard, as the handoff note says.
- **Other evaluation files.** `doc/Evaluation/Copilot-eval.md` and `Gemini-eval.md` appeared untracked during the session. They were not read, so this review is independent of them.
