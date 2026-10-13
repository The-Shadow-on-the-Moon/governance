# Walkthrough: one change from ticket to release, and a hotfix

One invented change followed from start to finish: "Add CSV export to the reports page", ticket #201. Every
name, number and date is made up. The page adds no rule; each step says which guide holds it. The numbers
below are only an example of how the pieces fit together.

The project is at version V2.3.2 and has a release tag `released/V2.3.2`. Sam is the developer; the project
owner triages the board.

## 1. The ticket exists first

The project owner (or Sam) creates the issue before any work starts. It needs a Title, a Type, a Description
and a Size; the rest can be proposed.

| Field | Value |
|---|---|
| Title | Add CSV export to the reports page |
| Type | Feature |
| Size | M |
| Priority | Normal |
| Risk | 2 (Low) |
| Progress | ToDo |

The full description is the first example of guide 03, section 3. See *Starting work*, section 2, and
*Issues and the board in practice*, section 1.

## 2. Sam starts it

1. Triage puts #201 in **OnDeck**; Sam picks it up and sets Progress to **InProgress**, with Sam as assignee.
2. Sam updates `main` and creates a branch from it, in kebab-case with no ticket number: `csv-export`.
3. Sam opens the changelog entry at the top of `CHANGELOG.md`, with the ticket's exact title:

```
## WIP-Version
### WIP-Build
#### #201 — Add CSV export to the reports page
```

The hooks are active in the clone (once per clone: `git config core.hooksPath .githooks`). See *Starting
work*, sections 1 to 4.

## 3. Work, log, commit

Sam builds and tests, then logs each change as a specific bullet. A small typo in a help text turns up on
the way: it has no ticket, so Sam logs it as a `REF` with a UTC token instead of stopping to create one.

```
## WIP-Version
### WIP-Build
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
- tests: added a test that compares the exported file with the page for three reports.
#### REF 20261006091500 — no ticket yet (typo in the settings help text)
- settings help text: fixed the spelling of "authentication".
```

Sam commits through the editor. The commit hook turns `### WIP-Build` into `### Build 20261006091200 (branch
csv-export)`, and the commit message is drafted from the entries. See *Working and committing*, sections 1
to 5.

## 4. First push

Sam pushes. The automation sets #201 to Delivery **Pushed** and fills its Build. Nothing else on the ticket
changes by itself: Progress stays with Sam. See *Starting work*, section 5.

## 5. Main moved: sync

Another change landed on `main` and renamed the date column used by the export. Sam merges `main` into
`csv-export` (never rebases), resolves the conflict, rebuilds, retests, and logs it under #201 because Sam
had to change something:

```
#### #201 — Add CSV export to the reports page
- Merged `main` into `csv-export` and resolved a conflict in the report query: `main` had renamed the date
  column, and the export now uses the new name. Rebuilt and retested.
```

See *Syncing and merging*, section 1.

## 6. Get ready, then the pull request

- The `REF` is backfilled: Sam creates #206 ("Fix the spelling of "authentication" in the settings help
  text", Bug, Origin **Backfilled**, REF `20261006091500`) and replaces the placeholder in place:

```
#### #206 — Fix the spelling of "authentication" in the settings help text
- settings help text: fixed the spelling of "authentication".
```

- #201 and #206 go to **Review**, with Risk revised.
- Sam opens a pull request `csv-export` into `main`, titled with the purpose, with the changelog entries of the
  open version pasted in, the tested build, and the sync line. No closing keyword anywhere: tickets are closed by
  a person after verification.

See *Syncing and merging*, sections 2 and 3.

## 7. The merge

Sam merges with a merge commit and keeps the branch. The versioning workflow runs on `main`:

- The heading is renamed. The tickets are a Feature and a Bug, and the highest Type wins, so the bump is
  **sub**: V2.3.2 becomes V2.4.0.
- The Version ticket "Version 002.004.000" is created, with #201 and #206 as sub-issues.
- #201 and #206 get Delivery **Merged**, Version `V002.004.000` and their Build.

```
## V2.4.0 — 2026-10-07 16:20 UTC
### Build 20261006091200 (branch csv-export)
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
- tests: added a test that compares the exported file with the page for three reports.
#### #206 — Fix the spelling of "authentication" in the settings help text
- settings help text: fixed the spelling of "authentication".

## V2.3.2 — 2026-10-02 11:05 UTC
### Build 20261002101500 (branch report-fixes)
#### #198 — Report totals ignore the last day of the month
- report totals: the last day of the month is now included in the sum.
```

Sam pulls `main` and checks the heading, the Version ticket and the Delivery of both tickets. See *Syncing and
merging*, section 5, and *Project structure*, section 5.

## 8. Verification and closing

A person (Sam or the project owner) checks that the export does what the ticket's "Done when" asks. Then, in one
move, Resolution becomes **Done**, Progress **Completed**, and the issue is closed. The automation never does
this. See *Issues and the board in practice*, section 3.

## 9. The release

Every merge made a version; a release is a deliberate choice. Sam runs the regression checks on V2.4.0 and
records the result with the build, then starts the release step of the workflow with the version. The tag
`released/V2.4.0` goes on the commit where V2.4.0 was finalized, the Version ticket becomes **Released**
with a comment, and so do the tickets whose Delivery was **Merged**. See *Releases, hotfixes and retiring
branches*, section 1.

## 10. A critical problem in V2.4.0: the hotfix

Support reports that the export breaks accented names. It cannot wait for the next version, and `main` has
moved on, so it is fixed in V2.4.0 itself.

1. Sam creates #240 (Bug, Priority Critical) and sets it InProgress.
2. Sam creates the branch **from the release tag**, not from `main`: `hotfix-v2-4-0-export-encoding`.
3. The changelog gets `## WIP-Version` with **no marker** (markers are not allowed on a hotfix), and Sam works as
   usual.
4. Sam verifies the fix, then runs the hotfix step of the workflow **from that branch** with the explicit
   version `V2.4.0-HF1`. It renames the heading, tags `released/V2.4.0-HF1`, creates the Version ticket and sets
   #240 straight to **Released** (a hotfix is never merged, so it skips Merged).

```
## V2.4.0-HF1 — 2026-10-13 09:40 UTC
### Build 20261013093100 (branch hotfix-v2-4-0-export-encoding)
#### #240 — Export breaks accented names
- reports page: the exported file is now written in UTF-8 with a byte order mark.

## V2.4.0 — 2026-10-07 16:20 UTC
### Build 20261006091200 (branch csv-export)
#### #201 — Add CSV export to the reports page
- reports page: added an Export button that downloads the current report as CSV.
```

5. The same fix reaches `main` separately, as an ordinary branch and pull request with its own ticket (#241, "Forward-port of
   #240"), and gets whatever version `main` is at, say V2.4.1.
6. The hotfix branch is deleted without a retirement tag: its release tag keeps its history.

If the release being fixed was made before the project adopted the standard, the hotfix branch starts with
one extra commit, the overlay: see [[Adopting-the-Standard]].

## Where to read more

- [Appendix A](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-a-cheat-sheet-daily-flow.md): the same flow on one page.
- [Ticket model](Ticket-Model): the life of a ticket and its fields.
- [Automation](Automation): what the workflow does at each step.
