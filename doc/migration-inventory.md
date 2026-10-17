# Migration inventory: V0.1.0 to V0.14.0

Which versions of the standard need a project to do something besides copying files, what, and how a tool can tell whether it is done. It is the input of the migration chain (#217), the survey (#218) and the `Upgrading` page (#231). Written for ticket #216 on 2026-10-16.

## How it was derived

- Every `CHANGELOG.md` entry of the 22 finalized versions, V0.1.0 to V0.14.0, read for changes to the board, the repository, the organization, the workflow and the tickets' data.
- For the board and the workflow, the facts were taken from the files at each version's `Finalize` commit (`git show <commit>:<file>`), not from the entries alone: the required fields and options of `preflight.py`, and the events, modes, schedules, secrets and permissions of `versioning.yml`. Every version has a `Finalize Vx.y.z` commit (found with `git log`), which is also what the fingerprints (#215) will use.
- Not derived from the `standard` field of old manifests: they were sometimes a guess corrected later (V0.7.1 never existed: #85; corrections #144, #195).

## Principle: the state decides, not the version label

A project's files can be from one version and its board from another, so a step is needed when the project lacks the thing, never because of a version number. Each action below has a **detect** (what the survey reads) and an **apply** (what the chain does). Where the actions interact, the order matters (see the last section).

## Summary

| Version | Date | Project action | What |
|---|---|---|---|
| V0.1.0 | 2026-10-05 | none | Guides and the two tools of this repository (files only) |
| V0.2.0 | 2026-10-05 | none | Pull request template, `AGENTS.md`, roles, licence (files only); the saved views were created by hand, replaced by A5 |
| **V0.3.0** | 2026-10-05 | **A1** | The automation: hooks, library, preflight, finalize, advisory check, bypass, workflow, manifest. The installation baseline |
| V0.3.1 | 2026-10-06 | none | Preflight fix |
| **V0.4.0** | 2026-10-06 | **A2** | Delivery option *Implemented* |
| V0.5.0 | 2026-10-06 | check | Push step, date sweep, Watch and Caution flags, schedule, skipped-hooks fallback: workflow and scripts; the fields were in A1 |
| V0.6.0 | 2026-10-06 | check | Release, hotfix and retire as manual runs: workflow and scripts |
| **V0.7.0** | 2026-10-06 | **A4** | The label `dummy` |
| **V0.8.0** | 2026-10-07 | **A5** | Saved views (`views.json`, `views.py`), pull requests on the board |
| V0.8.1, V0.8.2, V0.8.3 | 2026-10-07/08 | none | Fixes (files only; the workflow's checkout action) |
| V0.9.0 | 2026-10-08 | check | Rules for Delivery and Version, three scheduled runs a day, mode renamed `daily` to `scheduled`, the re-enabler workflow: files; Actions must be on |
| **V0.10.0** | 2026-10-09 | **A6** | The field *Fix*, the Decide, Follow up and Fix views, settings checks, condition comments |
| V0.10.1 | 2026-10-09 | none | Workflow job for the team's own events (files only) |
| **V0.11.0** | 2026-10-11 | **A7** | Version written `V000.010.001`, the field *Version#* removed, view columns and sorts, standard colors |
| V0.11.1 | 2026-10-11 | none | Manifest correction |
| V0.12.0 | 2026-10-11 | none | Audit tools (`tools/` is not copied to projects) |
| **V0.13.0** | 2026-10-13 | **A8** (personal accounts only) | The Type in the board field *Kind*; the variable `TYPE_SOURCE` |
| V0.13.1, V0.13.2 | 2026-10-15 | none | Manifest and licence |
| V0.14.0 | 2026-10-15 | none | The manifest placeholder `WIP-Version` (files; see #226 for what an adopting project must not do) |

"check" means no change of the board or the repository, but the survey verifies it (Actions enabled, the workflow on the default branch).

## The actions

### A1: the installation baseline (V0.3.0)

- **What.** A board linked to the repository with these 15 fields: Status, Origin, Waiting, Attention, Resolution, Delivery, Priority, Size, Risk, REF, Version, Build, *Version#*, Start date, End date (single selects with the guide's values, text and date fields as in the guide). The secret `PROJECT_TOKEN` (an administrator's token with the project scope) and the repository variable `BOARD_NUMBER` (the preflight stores it, or asks the administrator when no board or several are linked). The workflow declares `contents`, `issues` and `pull-requests` write itself. The issue types of the standard in an organization (finalize decides the bump from them). The hooks are activated in every clone: `git config core.hooksPath .githooks`. The wiki-sync workflow is optional.
- **Detect.** Fields and options by GraphQL; the secret by name and the variable by name through the API; the issue types through `orgs/{owner}/issue-types`. The hooks path can be read only in a clone: the survey reports it as `unknown`, with the command, when it runs elsewhere.
- **Apply.** Guide 10 sections 3 to 6; since V0.10.0 `fields.py --apply` creates missing fields; the install module (#233) covers a project with none of it.
- **Who.** Administrator (token, secret, board), developer (hooks, files).
- **Reversible.** Yes (fields, variable and secret can be removed); nothing here destroys data.

### A2: the Delivery option *Implemented* (V0.4.0)

- **What.** Delivery had `Committed`, `Pushed`, `Merged`, `Released`, `Dropped`; V0.4.0 adds `Implemented` and the preflight requires it.
- **Detect.** The options of the field Delivery.
- **Apply.** Add the option without changing the ids of the others, so no ticket's value is lost. `fields.py` never changes a field that exists, so this is done through `updateProjectV2Field` with the existing option ids (the same technique as the colors in V0.11.0, #135, which kept the ids), or in the web interface. To be proven in the rehearsal (#224): existing values must survive.
- **Who.** Administrator. **Reversible.** Yes.

### A3: nothing new on the board in V0.5.0 and V0.6.0

The push step, the date sweep, the Watch and Caution flags, the schedule (one run a day at 06:17 UTC), the manual modes (`finalize`, `daily`, `release`, `hotfix`, `retire`) and the skipped-hooks fallback use the fields of A1 (Attention, Start date, End date, Build, Delivery including `Dropped`, which already existed in V0.3.0). The workflow and scripts are replaced by copying; the survey checks that Actions is enabled and that `versioning.yml` is on the default branch (a schedule runs only there).

### A4: the label `dummy` (V0.7.0)

- **What.** A marker label for throwaway tickets made to test the automation; the views exclude it. The label list becomes the 14 Area labels plus `dummy`.
- **Detect.** The label list of the repository. **Apply.** Create the label with its color and description (the install module, #233). **Who.** Administrator or developer. **Reversible.** Yes.

### A5: the saved views (V0.8.0)

- **What.** `.github/views.json` and `views.py` define the board's views; the administrator runs `views.py --apply`. Pull requests are put on the board so the All view has no gaps (`board_pull_requests.py --all`, a one-time backfill, optional). Manual settings the API cannot reach: *Show hierarchy* off in the All view and the sort by Created (printed as a reminder by the script).
- **Detect.** `views.py` dry run (differences between the board's views and `views.json`).
- **Apply.** `views.py --apply` when the administrator asks; the manual steps by hand.
- **Who.** Administrator. **Reversible.** Yes: a changed view is created again and the old one deleted; the old definition is in git history.
- **Note.** Replaced and extended by A6 and A7, so a chain from far back goes straight to the latest `views.json`.

### A6: the field Fix and the new views (V0.10.0)

- **What.**
  - The 16th field, *Fix* (text); `fields.py --apply` creates it. Priority, Size and Risk carry all their values (the preflight of V0.3.0 required only the value `Critical` for Priority and no values for Size and Risk): verify the options and add the missing ones.
  - The views Decide, Follow up and Fix replace Health: `views.py --apply` and deleting Health (`--delete Health`, or `--delete-unlisted`).
  - Repository settings the preflight now warns about: merge commits allowed, squash and rebase merging off, head branches not deleted automatically, default branch `main`, branch protection (a pull request and an up-to-date branch), and the wiki enabled and initialized when the wiki-sync workflow exists. These are warnings, set by the administrator.
  - The refresh writes the Fix field and the comments of the conditions, and stamps the board's description with the time it was last checked (needs the project token's project write access).
- **Effect on old data.** The first refresh lists every ticket that breaks a rule (for example Completed without Resolution *Done*): a burst of Fix entries and, after a wait, comments. The survey previews the count (#218).
- **Detect.** The field and its options; the views; the settings through the repository API. **Who.** Administrator. **Reversible.** Yes.

### A7: the Version form and the removal of *Version#* (V0.11.0)

- **What.** The board writes a version with three digits for each part (`V000.010.001`, a hotfix `V001.025.000-HF1`) so that text sorting equals version sorting. `version_format.py` (the scheduled run) rewrites the Version field of every ticket in the new form. The field *Version#* is removed (the board sorts by Version itself). The Version tickets' titles took the form `Version 000.010.001`, but no tool renames the old ones (the conversion in #213 replaces that). The views were created again (columns and sorts). Optional: the standard colors and descriptions of the options and the 15 label colors.
- **Detect.** Version values not in the board form; the field *Version#* present; the views.
- **Apply, in this order.** Copy the new files, let the scheduled run (or `version_format.py`) rewrite the values, run `views.py --apply`, and only then delete *Version#* by GraphQL or by hand. The old files still require the field, so deleting it first would break their runs (the pattern recorded for ticket #139).
- **Who.** Administrator (field, views), automation (values). **Reversible.** Mostly: values can be rewritten back; a deleted field and its data cannot be restored, so export first.

### A8: the Type in the field Kind (V0.13.0, personal accounts only)

- **What.** A project owned by a personal account has no issue types; the Type is a board field *Kind* with the standard values, and the repository variable `TYPE_SOURCE` names the source (`issue-type` or `field`; without the variable the owner of the repository decides). Views use `kind:` filters, translated by `views.py`.
- **Detect.** The owner type; the variable; the field Kind and its values. **Apply.** `fields.py --apply` creates Kind; set the variable if the default is wrong. **Who.** Administrator. **Reversible.** Yes. An organization project needs nothing.

### Forecast: the 0.15 series (not part of this inventory)

Views Versions and Plan (A5 again); conversion of the legacy Version tickets (#213); Resolution *Done* filled and cleared by the refresh (#232); the first refresh flags stale plans (#208); in an adopting project the manifest keeps the standard's version (#226). These are the chain's last steps.

## Order of the steps for a project with files from one version and a board from another

1. A1 (the baseline), then A2, A4.
2. A6 fields, then the files of the target version, then A5/A6/A7 views (`views.py` reads `views.json` of the target).
3. A7 in its internal order: files, values, views, then the removal of *Version#*.
4. A8 anywhere after A1 for a personal account.
5. The 0.15 series last.

A project older than V0.3.0 (no automation) is not a migration: it is an adoption (guide 11), and the survey calls it `none` or `unsupported`.

## What is not yet known

- Whether adding an option to an existing field keeps the values of the tickets for every field type (A2): to be proven in the rehearsal.
- Whether a board at an intermediate state (some of A1 done by hand, with a different order of options) matches `preflight.py` in every detail: the survey reports the differences instead of assuming.
- The behavior of a project whose files are a mix of versions: the fingerprints (#215) say which file is which version, and the chain acts on the state of the board either way.
- Settings the token cannot read (some protection details, the wiki being initialized): listed as manual checks.
