# Adopting the standard in an existing project

A short walk-through for a developer or administrator who wants a project that already exists, with its history,
branches, tags and issues, to follow the standard. The details are in
[guide 11](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/11-adopting-the-standard-in-an-existing-project.md)
and, for each finding the audit can report, in
[appendix G](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-g-audit-findings-and-fixes.md).
This page is the route through them. The measure is the [audit tools](Audit-Tools). An assistant can do the route
for a project from one instruction file and a set of tools: see the [Adoption kit](Adoption-Kit) and [Upgrading](Upgrading).

## The ideas

- **History is never rewritten.** No rebase, squash, filter or force-push of `main`, and no tag moved. What the
  project did stays; what differs is recorded.
- **The standard applies from a cut-over,** the merge that lands the adoption on `main`. Before it, deviations
  are history.
- **The adoption goes through the normal flow:** a ticket, an adoption branch, a changelog entry, a pull request
  and a merge commit.
- **Work made before the cut-over is history wherever it lands.** A branch that was open at the cut-over keeps its
  old commits as history when it is merged afterwards; the merge that lands it is judged. A commit counts as made when
  it was authored.
- **The audit is the measure,** and the project is adopted when a re-audit shows no failed rule after the cut-over.

## The route

1. **Audit first and keep the report.**
   `python tools/audit.py <project> --md before.md --json before.json`
   (add `--offline` until `gh` is signed in; the board needs `gh auth refresh -s project`).
2. **Decide** the cut-over, the version the project continues from, the roles, and take a backup
   (`git clone --mirror`). Settle the open branches and pull requests.
3. **Triage every finding** into one of four classes: *fix now*, *convert*, *accept as history*, *not applicable*.
   The adoption plan at the end of the report already groups the findings by stage, with their usual class and
   role. Appendix G says what each finding means and how to fix it.
4. **Do the stages in order,** re-running the audit after each:

   | Stage | What | Who |
   |---|---|---|
   | 1 GitHub settings | Organization (or, for a personal account, the Kind field in place of issue types), issue types, labels (map old labels first), merge methods, default branch. | Administrator |
   | 2 Adoption branch | Line endings in a commit of their own, structure, automation, hooks, the old changelog kept and a baseline heading. | Developer |
   | 3 Token, board, preflight | The project token, the board with its fields and views, the preflight. | Administrator |
   | 4 Git names | Retire or rename branches, add standard tags beside the old ones, make `main` the integration line. | Developer, project owner |
   | 5 Tickets | Issues on the board with type, label, Size, Status and Resolution; late tickets marked *Backdated* or *Backfilled*. | Project owner |
   | 6 Land and prove | The trial, the pull request (the cut-over), the first-merge check, protection of `main`, the re-audit. | Developer, administrator |
   | 7 Keep it | Review the accepted deviations at each release and re-audit. | Everyone |

5. **Record what cannot change** in `.github/audit-baseline.json` of the project (check, reason, date, who agreed),
   and run the audit with `--since <cut-over>` so the old history is left out.
6. **Re-audit.** Done when there is no failed rule that is not recorded.

## A critical fix in a release from before the adoption

It is a normal hotfix with one extra commit. Start the hotfix branch from the release's tag (the tag of stage 4;
a release without a tag cannot be fixed this way). The first commit on the branch, the *overlay*, copies from the
current `main` the files the automation manifest lists (with the manifest), `AGENTS.md` and `.gitattributes`, and adds a new
`CHANGELOG.md` with one finalized heading for the release being fixed. Activate the hooks, then fix and finish as
in guide 08, section 2. The overlay never goes into `main`; the forward-port carries the fix alone.
The old tag and the history are not touched.

## Useful commands

```
python tools/audit.py <project> --md report.md            # the first report, with the adoption plan
python tools/audit.py <project> --offline                 # files and git only
python tools/audit.py <project> --since 2026-10-01        # judge the history only from a date or a commit
python tools/audit.py <project> --verbose                 # also detail what passed
```

## Where to read more

- [Audit tools](Audit-Tools): the options, the baseline, the adoption plan and the report formats.
- [Roles and access](Roles-and-Access): who holds which role.
- Guide 10, *New-project bootstrap*: the settings, the automation, the token and the board, which stages 1 to 3 use.
