# Combined evaluation of the guides

Date: 2026-10-11. Ticket #165. Subject: guides 01 to 11 and appendices A to G as they are now (the combined file, 6,466 lines).
Sources: my own evaluation (part 1), `Copilot-eval.md` and `Gemini-eval.md` (part 2), both redone against the latest guides.
This is a new analysis and rests on no earlier evaluation. Analysis only: nothing in the guides was changed.

**How it was done.** I read the whole combined file, then checked every claim against the guides themselves, the tools and tests, and the live files:
`xref_check.py` (280 references, 0 problems), `combine.py --check` (the combined file is current), a comparison of Appendix F with `.github/views.json`
and of Appendix G with the checks the audit scripts report, and a search of the guides for each term and value in question.
The unit tests (`python -m unittest discover -s tests`) pass: 612 tests, `OK`, run on the working tree with the uncommitted changes of the open version. The tests therefore show that the guides, tools and automation agree where they are tied together; the findings below fall where no test looks.

## 1. My evaluation

### Verdict

| | Verdict | Why |
|---|---|---|
| **Coherence** | Strong | One model runs through everything: ticket → branch → commits → pull request → version → release. Judgment belongs to people, facts to the automation. Every procedural guide has Rule / Recommendation / In GitHub markers and a checklist. The README's "Where a rule lives" table gives each rule one home, and tests in `tests/test_tools.py` hold the values that repeat (idle times, Alert kinds, labels, the bump per Type, board fields and colors, the conditions table). |
| **Consistency** | Good, with a short list of real slips | No contradiction in a rule. The slips are in the tables that list what exists (files, stages), a stale word, and one rule that is restated in three places. |
| **Completeness** | Good for the stated scope | The normal flow, exceptions, bootstrap, adoption, audit and assistants are all covered. The gaps are at the edges: a release made before adoption, the limits of scope, and one failure case. |

### Findings, most important first

Each is a small documentation edit unless stated. Type: **C** consistency, **M** completeness (missing), **H** coherence.

| # | Type | Finding | Suggested fix |
|---|---|---|---|
| E1 | C | **The file tables are incomplete.** Guide 03 §2.2 says the repository holds "only what the table lists", but guide 11 §4.2 has the project add `.git-blame-ignore-revs` to the root, and guide 11 §3 and Appendix G put `.github/audit-baseline.json` in `.github/`. `.github/automation-manifest.json` and `.github/views.json` are named only in guides 07 and 10. None of these is in guide 03 §2.1, whose `.github/` row names only "workflows and their scripts, and the pull request template". | Extend the `.github/` row (manifest, saved views, audit baseline) and add a root row for `.git-blame-ignore-revs` ("present only after a line-endings commit"). Check that guide 10 §1 and the audit's `files.location.*` checks still agree. |
| E2 | C | **A stale term.** Appendix E §1 (Planning row) says "a person, except Build, **Version#**, the real Version and the dates". No guide or board field called Version# exists. | Delete "Version#,". |
| E3 | C/H | **Alert triage is stated in three places and has no home in the table.** Guide 02 §6.3, guide 05 §6.2 and guide 07 §5.2 each say what to do with an Alert. Guide 03 §7.4 sends the reader to guide 07, guide 07 sends them to guide 05 §6.2, and the README's "Where a rule lives" has no row for it. The README promises "each rule is set out in one place". | Give triage one home (guide 07 §5.2 is the natural one, since it already covers every Alert kind), reduce 05 §6.2 to the AUTO-REF documenting step, make 02 §6.3 and 06 §5.2 / §6.2 point to it, and add the row. Consequence: guide 06 and Appendix A/B references change, and the combined file is rebuilt. |
| E4 | M | **The guides do not say how to hotfix a release made before the cut-over.** Details below. | A decision is needed (see §4). The points to correct are listed under "E4 in detail". |
| E5 | M | **Scope limits are not stated.** The standard is silent on several repositories that must release together, and on several maintained lines (`release-1.x`, `release-2.x`). Guide 02 §1.1 forbids long-lived integration branches, and a hotfix from the release tag (up to nine per release) is in practice the answer for old lines, but no sentence says so. | Add two lines to "What the standard assumes" in the README: coordination across repositories is out of scope, and an old release is maintained by hotfixes from its tag. |
| E6 | M | **A release that was declared correctly and turned out bad is not named.** Guide 08 §1.1 covers a *mistaken tag* (delete it and redo). It says nothing about a real release found defective: the tag stays, a hotfix or a newer version replaces it. | Two sentences in guide 08 §1.1 and a row in Appendix B. |
| E7 | C | **"Seven stages" is stage 0 plus seven.** The README, guide 11 and the wiki say "the seven stages" while the guide numbers 0 to 7. | Say "stage 0 and seven stages" everywhere, or number the stages 1 to 8. |
| E8 | M | **The end of a converted tag is not defined.** Guide 11 §4.4 adds the standard tag and "keeps the old tag until everybody has moved", then stops. The audit check `git.tag.names` flags the old tag as long as it exists. | State the end: the administrator deletes the old tag once everyone has moved (the commit stays reachable under the new one), or the old tag is recorded as accepted history. |
| E9 | C | **Tool names outside "In GitHub" blocks.** The README says only two places name GitHub or its tooling outside the blocks. Guide 03 §4.3 (Fix) and guide 07 §2.2 and §2.5 name `conditions.py`, `views.json`, `views.py` and the workflow mode `conditions` in the main text. | Move those names into "In GitHub" blocks, or widen the README's statement. |
| E10 | C | **Appendix F is hand-kept.** Each column position and sort in it is correct today (I compared every view with `views.json`), but no test guards it, unlike the wiki's board-views page. | Add a test that reads Appendix F's table and compares it with `views.json`. |
| E11 | M | **The coherence of the delivery states has to be assembled.** The moves of Delivery (Pushed ↔ Merged ↔ Released, Implemented, Dropped, back to Pushed on new work) are spread over guide 03 §4.3, Appendix C and Appendix E §3's side paths. | One small "from → to → caused by" table in Appendix E §3. |
| E12 | H | **No single walkthrough.** The invented ticket #201 (CSV export) appears in guides 03, 04, 05 and 06, but nobody follows it from ticket to release in one piece. | Optional. A worked example as a *wiki page*, not a guide (guides and cheat sheets add no rules, and a copy of the rules would drift). Its changelog snippets can be checked by the existing test of the examples. |
| E13 | C | A typo: "analyzes and investigations" in guide 03 §9.1 (should be "analyses"). | Direct edit. |

### E4 in detail

**What the guides say today.**
- A hotfix branch starts from a `released/V…` tag, never from `main` (guide 02 §1.3, guide 04 §3.2, guide 08 §2.1 step 2).
- Guide 11 §5.2 says a release that really happened is tagged `released/V…` on its commit when that commit is known, and left untagged otherwise.
- Guide 08 §2.1 steps 3 and 4 add a `## WIP-Version` heading (no marker) and work with the hooks. Step 7 runs the hotfix-finalize step with an explicit version.

**Why that fails for an old release.** I checked the automation:
- The hotfix step is the workflow's `hotfix` mode. It runs only when started from a branch (`versioning.yml`, `github.ref_type == 'branch'`), and it checks out that branch and runs `.github/scripts/hotfix.py` from it. So the workflow file and the script must exist on the hotfix branch.
- `hotfix.py` stops with "the changelog has no open WIP-Version heading to finalize" unless the branch changelog has the standard heading.
- A commit from before the adoption has none of this: no `.github/`, no `.githooks/`, and a changelog in another format (guide 11 §4.2 keeps the old one in `doc/`).
- Guide 11 §1 forbids rewriting history and moving tags, so the old commit cannot be given these files.

**What is undecided, and so what a correction has to settle.**
1. Whether the standard supports a hotfix of a pre-adoption release at all.
2. If not (option a, recommended): which versions have a hotfix lineage. Say that `-HF` numbering and the `released/` hotfix tags start with the first release made after the cut-over, and that a defect in an older release is fixed on a normal branch from `main` and released as a newer version (consistent with guide 02 §2.2, "a release that needs that many fixes should be replaced").
3. If so (option b): how the branch gets the automation and a changelog. It would have to be copied onto a branch started from the old tag, with a fresh changelog and baseline heading, and the guide would have to say that branch is allowed to differ from the tag in those files only.

**Places to change, for either option.**

| File | Change |
|---|---|
| `guides/11-adopting-the-standard-in-an-existing-project.md` §5.2 | State the rule (point 2 or 3 above). Say that tagging an old release does not make it hotfixable. |
| `guides/08-releases-hotfixes-and-retiring-branches.md` §2 | A rule that a hotfix is only for a release made after the cut-over (or the extra steps of option b), and a line in the checklist (§4). |
| `guides/02-branching-and-merging-strategy.md` §1.3 | One line pointing to the above, so the branch rules are not read as covering every tag. |
| `guides/appendix-b-cheat-sheet-if-then.md` | A row: "a critical problem is found in a release from before the adoption". The existing row "a critical problem is found in a released version" should say "made after the adoption". |
| `doc/wiki/Adopting-the-Standard.md` | Same statement in the wiki page. |
| `tests/test_tools.py` | Nothing is needed for option a. For option b, add a test that the steps agree between guides 08 and 11. |
| After editing | `python tools/combine.py`, `python tools/xref_check.py` (expect `problems: 0`) and the unit tests. No automation file changes, so the manifest is unaffected. |

**Side effects to keep in mind.** Option a changes no code and no tests. Option b means the automation would run on a branch that does not descend from the project's current `main`, which the finalize and preflight steps were not built for (they read `main`); it needs trial runs on a throwaway tag (guide 05 §4.4).

### What I checked and found sound

- **Cross-references**: 280, none broken, and I found no pointer to the wrong guide or section among those I followed (Appendices A and B, the glossary tables).
- **Appendix G is complete**: it has a row for every check the audit scripts can report (87 ids), and a test fails if one is missing.
- **Appendix F matches `views.json`**, view by view and column by column (E10 is only about keeping it so).
- **The padded and short forms of a version** are used correctly: three-digit on the board and in Version ticket titles, short in the changelog, tags and branch names (guide 01 §1, guide 03 §4.3, Appendix C).
- **Roles, the Rule / Recommendation split, and the enforcement stance** (warn, allow a bypass, record it) are the same in every guide.
- **Checklists** add no rules, and the ones I compared with their guides match.
- **The assistant rules** (guide 09) agree with guides 03 §10 and 04 on who sets what.

## 2. The Copilot and Gemini evaluations, checked

### Copilot

Copilot's overall ratings (coherence 9.5, consistency 9.5, completeness 9.5, "no significant contradictions") are generous but not far off; I find no contradiction of a rule, only the slips above. Each of its findings:

| Copilot finding | Verdict | Evidence |
|---|---|---|
| "Where a rule lives" is the strongest part | **Right, with a qualification.** | It is, and tests back it. Alert triage (E3) is an exception to "each rule in one place". |
| Implemented / Merged / Released are hard to tell apart; add a lifecycle diagram | **Partly right.** | The moves are scattered (E11), so a transitions table is worth adding. Copilot's own sketch cannot be used as written: it leaves out *Committed*, *Dropped*, the return to *Pushed* on new work, and *OnDeck*, *Suspended* and *Abandoned*. |
| Backfilled vs Backdated is easy to miss; add a comparison table | **Not needed.** | Appendix C's Origin table already contrasts them with an example each, and guide 01 §4, guide 03 §4.3 and guide 11 §4.5 define them. Copilot's wording of the difference ("during the process" vs "before adoption") is looser than the guides'. |
| Why are pull requests on the board? Rationale appears late | **Wrong.** | Guide 03 §6.2, the first place pull requests are described, gives the reason (they share their numbers with tickets, so *All* would have gaps) and guide 07 §2.2 repeats it. |
| No scenario for a release found bad | **Right, small** (E6). | Only a mistaken tag is covered. |
| Multi-repository coordination is not addressed | **Right** (E5). | No mention anywhere. |
| Several maintained support lines are not addressed | **Right, but the answer exists** (E5). | Hotfix from the release tag covers it; it is not said. |
| Guide 01 is very large | **Wrong.** | Guide 01 is 303 lines, one of the shortest. The large one is guide 03 (1,094 lines, 17% of the guides). I would not split it: the section numbers it carries are referenced from every other guide and from the "Where a rule lives" table. |
| REF, AUTO-REF and Alert tickets appear before they are explained; add a "for now" note | **Adequate as is.** | The glossary gives each a one-line meaning and a "See" column. A note would add words without adding a rule. |
| Add one end-to-end example | **Right, as an option** (E12). | Best as a wiki page. |
| "About 14k lines" | **Wrong.** | The guides are about 6,300 lines. |
| "No significant contradictions" | **Right.** | I found none in a rule. |

### Gemini

Gemini's summary says there are internal contradictions and minor formatting discrepancies. I could confirm none of the four as a contradiction.

| Gemini finding | Verdict | Evidence |
|---|---|---|
| Priority: guide 03 §4.3 says it defaults to *Normal*, but guide 03 §10 and Appendix C say the creator proposes and the project owner sets it | **Not a contradiction.** | A default, a proposal and a decision are different steps, and guides 03, 04, 07 and Appendix C agree (Normal by default, proposed at creation, the owner can change it at any time). A clause in 03 §4.3 ("the project owner can change it") would only repeat 07 §1. |
| Padded version numbers are mixed with unpadded in guides 02 and 03 outside the board | **Not found.** | Guide 02 §2.2 and §3.1 are unpadded, as are tags and branch names. Padded forms in guide 03 §5.2 and §5.4 appear only in board contexts (the Version field, Version ticket titles). I read every example. |
| Progress: automation advances to *InProgress* (03 §4.3) vs the person sets it (04 §2.1) | **Not a contradiction.** | Setting it is the rule (guide 04 §2.1, guide 07 §7, Appendix C); the automation's advance is the safety net, and guide 03 §4.3 says so ("the only change it makes"). The guides could say "safety net" in 03 §4.3; I do not count it a defect. |
| Guide 03 "§2.4" mentions the manifest hashes | **Wrong citation.** | Guide 03 has no §2.4 (it stops at §2.3). The manifest is in guide 10 §2.4. |
| Guide 03 §2.1's layout table omits `.github/automation-manifest.json` | **Right, and broader** (E1). | The table omits the manifest, the views file and the audit baseline. |
| Verify that guide 07 §2.2's views match Appendix F | **Right to ask, and they match** (E10). | I compared them. No test guards it. |
| Rating "complete" for the stated scope | **Fair**, but see E4 to E6. | |

### Comparison of the three

| | Mine | Copilot | Gemini |
|---|---|---|---|
| Read | the whole guides, the tools, the live files | the guides, structure and samples | the guides |
| Findings that stand | 13 | 4 clearly (E5, E6, E11, E12), 1 partly (E3 via "single source") | 2 (E1, E10) |
| Findings that fail | | 5 (PR rationale, size of guide 01, Backfilled/Backdated, REF note, line count) | 3 contradictions, and 1 citation to a section that does not exist |
| Strength | evidence for each | the right questions about scope and onboarding | pointing at the layout table and Appendix F |
| Weakness | not an outside reader's first impression | some claims not checked against the text | claimed contradictions that are not |

## 3. Suggested order of work

1. **Group A, consistency (E1, E2, E7, E9, E13)**: direct edits, one ticket, size S. Then `python tools/combine.py`, `python tools/xref_check.py` and the unit tests.
2. **Group B, completeness (E4, E5, E6, E8, E11)**: new text, one ticket, size M. E4 needs a decision first.
3. **Group C, structure (E3, E10)**: moving the Alert triage text and a new test, one ticket, size M. It changes references in guides 02, 05, 06 and 07 and Appendices A and B.
4. **Optional (E12)**: the walkthrough as a wiki page.

## 4. Decisions needed

- **E4**: how a release from before the cut-over is fixed. (a) A normal branch released as a newer version, and hotfix numbering from the first release after the cut-over (recommended: it needs no new mechanism, and old changelogs stay untouched). (b) Define a hotfix on an old tag: it needs the automation on that branch, which means editing history or copying files onto an old commit.
- **E3**: which guide owns Alert triage. I recommend guide 07.
- **E12**: whether to write the walkthrough, and as a wiki page (recommended) or an appendix.

## 5. Status of the findings (added 2026-10-13)

The sections above are the evaluation as it was made on 2026-10-11 and are not rewritten. This table records what became of each finding.

| Finding | Ticket | Outcome |
|---|---|---|
| E1 file tables incomplete | #166 | Guide 03 section 2.1 extended (manifest, saved views, audit baseline, `.git-blame-ignore-revs`). |
| E2 stale term Version# | #167 | Removed from appendix E. |
| E3 Alert triage in three places | #168 | Guide 07 section 5.2 owns the triage; guides 02, 05 and 06, the appendices and the README point to it. |
| E4 hotfix of a release from before the cut-over | #170, #174, #175 | Decision changed from option (a) to a hotfix with an overlay commit (guide 08, section 2.1); proven by a trial (#174), which also found the pre-push warning fixed in #175. |
| E5 scope limits | #171 | Two lines in the README. |
| E6 defective release | #171 | Guide 08 section 1.1 and a row in appendix B. |
| E7 "seven stages" | #167 | "Stage 0 and the seven stages" in the README (the wiki and guide 11 did not use the phrase). |
| E8 end of a converted tag | #170 | Guide 11 section 4.4. |
| E9 tool names outside In GitHub blocks | #166 | Moved into In GitHub blocks in guides 03 and 07. |
| E10 appendix F not guarded | #169 | `AppendixFTests` in `tests/test_tools.py`. |
| E11 delivery transitions | #172 | "Delivery moves" table in appendix E section 3. |
| E12 walkthrough | #173 | Wiki page Walkthrough-CSV-Export. |
| E13 typo | #167 | Corrected in guide 03 section 9.1. |

Found afterwards: the invented examples of the guides disagreed with the rules and with each other (#178), and the README and Automation page were stale (#179, guarded by the tests of #181).
