# Combined evaluation of the guides and the project

Date: 2026-10-08. Sources: `Claude-eval.md`, `Gemini-eval.md`, `Copilot-eval.md`. Every finding below was checked against the guides, the code or the live GitHub state where possible. Analysis only: nothing has been changed.

## How the three evaluations compare

| | Scope | Verdict | Quality |
|---|---|---|---|
| Claude | Guides (all files) and the project: tests, repo settings, board, tickets, pull requests, history | Several real contradictions and gaps; the project follows the guides closely, with a few deviations | Concrete and checked against code and live data |
| Gemini | Combined guide file only | "High / Very High" | Two real gaps. Most other findings are "check that…" prompts that turned out fine |
| Copilot | Combined guide file only | "Strong", no major contradictions | Generic. Mostly editorial or out of scope. The "no contradictions" verdict is wrong |

Neither Gemini nor Copilot looked at the project, so only Claude's evaluation covers whether the project follows its own guides.

## 1. Address: guide defects (confirmed)

Ordered by importance. "Fix" says what to change; each fix is a small documentation edit unless stated.

| # | Finding | Source | Fix |
|---|---|---|---|
| G1 | **Test-result rule contradicts itself.** 05 §4.2 says "nothing more is prescribed", 05 §4.3 makes recording a Rule, the file location is only a Recommendation, yet checklists 05 §8 and 06 §2.1 treat the file as mandatory. "Recorded test result" is never defined. | Claude | Decide the intent, then make every place say it. Suggested: results are required only when the person verifies or reviews a ticket and when a release is verified (08 §1.1); routine unit-test runs need no stored file. Define "recorded result". Make `tests/results/` a Rule only for those cases, and align 05 §4.2, 05 §4.3, 05 §8, 06 §2.1, 07 §3 and 03 §2.1. |
| G2 | **Alert causes listed as three, automation raises four.** The changelog-error Alert (02 §3.3, `alerts.changelog_error_alert`) is missing from 03 §5.3 and §5.4, Appendix E §5, guide 07 §5 and Appendix C. | Claude | Add the fourth cause to those places, with its assignee rule and triage steps ("correct `CHANGELOG.md`, then re-run finalize", from the Alert's own text). |
| G3 | **Scheduled run is never defined.** Version#, the Implemented attach, Watch flags and field rules all depend on it. Only Appendix C says "three a day". 03 and 07 use the term undefined; bootstrap 10 §2.1 doesn't list the schedule or the `reenable-schedule.yml` workflow (needed because GitHub disables schedules after 60 days of inactivity); the glossary has no entry. | Claude | Add a short "scheduled run" section in guide 03 (what it does, how often, why it exists), a glossary entry in guide 01, and add the schedule and the re-enable workflow to the bootstrap guide's list and checklist. |
| G4 | **Guide 01 says the only labels are the 14 Area labels.** The standard also requires `dummy` (10 §5.2, Appendix C, 07 §7.1). | Claude | Reword guide 01 §8: "the 14 Area labels plus the `dummy` marker label". |
| G5 | **Five-minute versus two-hour wait.** 03 §4.3 says five minutes with no exception; 03 §4.4 and Appendix C say two hours for the Delivery and Version rules. | Claude | State both in 03 §4.3: five minutes by default, two hours for the Delivery and Version rules. |
| G6 | **`WIP-Build` must be re-added before every commit.** The hook only stamps an existing placeholder. Guide 04 introduces it once; guide 05 never says to add a fresh one for each later commit. | Gemini (confirmed in `hooks.py`) | In 05 §1/§2 and checklist 05 §8: "before each commit that logs a change, add a `### WIP-Build` block under the open version". Add one line to Appendix A. |
| G7 | **Assistant and merging is ambiguous.** 09 §3.1 requires approval for any "merge", but syncing `main` into a branch is a merge that guides 04 and 06 treat as routine. 09 §3.2 implies syncing is gated. | Claude | In 09 §2.1 list "syncing `main` into the person's branch" as routine, and keep merging into `main` as ask-first. Align 09 §3.2. |
| G8 | **Appendix C: "Critical needs a comment"**, but automation-created Alerts and hotfix tickets are Critical. | Claude | Add "except Alerts, which the automation creates as Critical". |
| G9 | **Hotfix version assignment.** Guide 01 §1 says a version is assigned "when a branch merges into main"; a hotfix version is assigned at finish. | Claude | Add "or, for a hotfix, when it is finished". |
| G10 | **Wrong cross-reference in Appendix B** for the skipped-hooks fallback ("Working and committing §5"). It's in guide 04 §5.1. | Claude | Change the "See" column. `xref_check` can't catch this because the section exists. |
| G11 | **Root contents table is incomplete.** 03 §2.2 says the root holds only what the table lists; `LICENSE*` and `.gitattributes` aren't in it. | Claude | Add rows for licence files and for `.gitattributes`. |
| G12 | **Bootstrap omits `.gitattributes`.** Windows line endings broke the hooks and parser once (ticket #14). | Claude | Add `.gitattributes` with `* text=auto eol=lf` to guide 10 §1 and the checklist. |
| G13 | **Trialling automation changes isn't a procedure.** The DUMMY-ticket convention is only in Appendix C and `AGENTS.md`. | Claude | Add a short subsection to guide 05 §3.2 (or 10 §8) covering the title, label, closing as Invalid, and tagging branches before deleting. |
| G14 | **Build blocks within a version: order is not stated.** | Claude | Add "newest build first" to 03 §7.3. |
| G15 | **Push rejected on a shared branch.** Guide 06 doesn't say to merge `origin/<branch>` and never rebase. | Gemini | Add a note to 06 §1: fetch, merge the remote branch, rebuild, push. |
| G16 | **`AUTO-REF` after a new-block triage.** Only implied that it stays. | Gemini (partly covered) | One sentence in 03 §7.4: the generated entry stays as the record, same as `REF`. |
| G17 | **Template for personal assistant-preference files.** 09 §6.1 only says they exist. | Copilot | Add a short optional template to 09 §6, flagged as optional. |
| G18 | **Smaller edits.** Fix guide 01 §5's heading ("Branches and tags' words"). Add Appendix D and the individual guides to the wiki Home. Add a note about tool-attribution trailers to `AGENTS.md`. | Claude | Direct edits. |

### Structural recommendation (the root cause of G2, G5 and G8)

Each Attention, Delivery and Version rule is restated in 4–6 places (03, Appendix C, Appendix E, guide 07, the wiki `Automation.md`, the changelog). Ticket #104 had to edit five files for two rules. Copilot made a related point about the Version field.

Fix: keep one canonical location per rule (the fields reference, Appendix C, is the natural one). Elsewhere, link to it and keep only a one-line summary. Add a test in `tests/test_tools.py` for any value that appears in several places (the idle thresholds, the wait times, the Alert causes, the label list), so drift fails the build. The existing tests already do this for the wiki page and `views.json`.

## 2. Address: project deviations (confirmed)

| # | Finding | Fix |
|---|---|---|
| P1 | **No test results stored** (`tests/results/` missing). 45 of 60 Completed work tickets have no comment naming a build. | Settle G1 first. Then either start recording results in the cases G1 defines, or accept the lighter rule. The comment-naming-a-build point is only a Recommendation, so no retrofit is needed. |
| P2 | **Changelog entries describe board actions**, not file changes (#70, #72, #82, #99, #100, #101). | Under the guides' own rule, earlier entries aren't edited except for a critical correction, so leave history alone. Keep such statements in ticket comments from now on. |
| P3 | **Collaborator `claudia-tsom` (read access) isn't in `Roles-and-Access.md` or `AGENTS.md`.** | Confirm who it is. Either add a "read-only" line to the roles page or remove the access. |
| P4 | **Leftover registered workflow "Ubuntu 26.04 trial"** (file gone, shown as active). Local tags `released/V9.9.9` and `-HF1` exist only locally. | Run `git fetch --prune --prune-tags` for the tags. The workflow entry disappears from the Actions list once its runs are deleted or GitHub ages it out; this is housekeeping. Ask first before deleting anything on the remote. |
| P5 | **Label and type descriptions drift** from Appendix C (`config` loses "service definitions"; US versus UK spelling). | Update the `config` label description. Pick one spelling for the issue types and match Appendix C. |
| P6 | **Untracked `.anchor` file.** | Add `.anchor` to `.gitignore` (personal or tool file). |

## 3. Irrelevant or incorrect findings (and why)

| Finding | Source | Why it doesn't need action |
|---|---|---|
| Version ticket title inconsistency (with or without `V`) | Gemini | The guides state the rule explicitly and apply it consistently: title `Version 2.4.1`, field `V2.4.1`. |
| Attention thresholds might differ across guides | Gemini | Checked. They match in guides 03 and 07, Appendix C and `watch.py` (7 days, 30, 182, 14). It was a "please verify", not a defect. |
| Internal anchor links might be wrong | Gemini | The combined file has 96 links. Three end in `-1`, which is GitHub's suffix for duplicate headings, so they work. |
| Hook lifecycle (`pre-commit` versus `prepare-commit-msg`) is blurry | Gemini | A nitpick. The guides say what each hook does and don't misstate it. |
| `AtRisk` is "reserved", which confuses readers | Copilot | Intentional and documented in 03 §4.3 and Appendix C. It is a design choice, not a defect. Revisit only if you want to give it a rule. |
| "No major contradictions or process dead ends" | Copilot | Incorrect. G1–G5 are contradictions and gaps. |
| "Scaling beyond one team", broader secrets guidance, beginner setup help | Copilot | Out of scope: the standard targets a small team on one repository. A scaling section would need real input first. |
| Reduce repeated role-collapsing text; "see above" wording | Copilot | Role-collapsing is explained once in 03 §10.6. The guides use precise section references. |
| "Exceptionally rigorous / very high completeness" | Gemini | Generous. Several of the gaps above were visible only by checking against the code and the live repository. |

## 4. Suggested order of work

1. **Tickets first** (the project's own rule): one ticket per group below, each with a Size, and each logged in the open changelog.
2. **Group A (content, one ticket):** G1 (decide the intent first, because it changes P1), then G2, G4, G5, G8, G9.
3. **Group B (one ticket):** G3, G12, G13, G14 (the bootstrap and scheduled-run gaps).
4. **Group C (one ticket):** G6, G7, G10, G11, G15–G18.
5. **Group D (structural, one ticket):** the single-source-of-truth refactor plus the drift tests. This is the largest piece and the one that prevents G2/G5-type bugs coming back. It can wait.
6. **Housekeeping tickets:** P3–P6.
7. After each guide edit: `python tools/combine.py`, `python tools/xref_check.py` (expect `problems: 0`) and `python -m unittest discover -s tests`. Guides aren't automation files, so the manifest isn't affected.

Decision needed from you first: **G1**, because it determines whether the project (P1) is non-compliant or the rule is simply too strict.
