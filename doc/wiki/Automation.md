# Automation

The repository applies its own guides with three pieces of automation. All of it is Python 3, standard library only. Every automation file is listed in the [manifest](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/.github/automation-manifest.json) with a fingerprint; a test fails when a file and the manifest disagree.

## Local hooks

Activate once per clone: `git config core.hooksPath .githooks`. The hooks warn and never block.

| Hook | What it does |
|---|---|
| `pre-commit` | Replaces `### WIP-Build` in the staged changelog with `### Build <UTC stamp> (branch <name>)`. Warns about a commit with no changelog entry, a merge that needs a rebuild, or a conflict resolved by hand. |
| `prepare-commit-msg` | Drafts the commit message from the new changelog entries: the ticket title, or "Multiple tickets", or the first bullet for a `REF`, then a block per ticket. |
| `pre-push` | Warns when the branch is behind `main`, when a pushed changelog still has its placeholder, or when the push carries a merge. |

## The versioning workflow

`.github/workflows/versioning.yml`; its logic is in `.github/scripts/`.

| When | What runs |
|---|---|
| A pull request | The pull request is put on the board as an item with no field set (so the All view has no gap in the numbers; a failure there never fails the run), then the advisory check: it fails and comments once when the branch is behind `main`, and lists merges with a manual conflict resolution. |
| A push to `main` | The preflight, then bypass detection (an Alert and an `AUTO-REF` entry), then the finalize step, then the check for stale planned Version tickets, then the date sweep, then the Watch flags, then the Caution flags for field rules. |
| A push to another branch | The preflight; then the fallback for skipped hooks (a pushed changelog that still has `### WIP-Build` gets its build heading filled in with the commit's time and hash, a note in the first entry, and a commit on the branch); then the push step: for each ticket in the changelog entries the push added, Delivery becomes *Pushed* and Build the ticket's latest build, *ToDo* and *OnDeck* tickets become *InProgress*, and a ticket that is *Completed*, *Abandoned*, *Review* or *Suspended* and already had work pushed or delivered (recognised by its recorded Build being older than the pushed one, or by Delivery *Implemented*, which has no Build) gets a *Caution* flag with a comment naming the build (not on its first push, not when the Delivery was only set by hand, and not again while a *Caution* or *AtRisk* is open). |
| Every day at 06:17 UTC, or on request with mode `daily` | The preflight, then attaching *Implemented* tickets to their versions, setting Version# from Version, the date sweep, the Watch flags and the Caution flags for field rules. It never commits. |
| On request with mode `finalize` | The preflight and the finalize step, as a dry run unless told otherwise. Safe to repeat. |

The preflight checks that the repository is reachable (the workflow's own token does not report its rights, so write access is confirmed through the project token), that `PROJECT_TOKEN` works (and warns two weeks before it expires), which board belongs to the repository (its number is kept in the repository variable `BOARD_NUMBER`) and that the board has every field and value the automation needs.

The finalize step decides the bump from the tickets' Types or the marker, renames the open `WIP-Version` heading in a commit of its own, sets Delivery, Version, Build and Version# on each ticket, and creates and closes the Version ticket with the tickets as sub-issues. If the board cannot be updated, the version is still finalized.

## The daily run

The checks that depend on time rather than on a push run from a `daily` job, started by a schedule (06:17 UTC) and by hand from the Actions tab (run the *Versioning* workflow with mode `daily`; a dry run is the default for a manual start). Scheduled runs only start from the default branch, so the schedule works once this workflow is on `main`, and GitHub stops scheduled runs of a repository that has had no activity for 60 days: a manual run starts them again.

## The date sweep

Start date and End date are the days the automation noticed a ticket start and end (UTC). The sweep looks at every ticket on the board: Start date is set the first time a ticket is seen at *InProgress* or beyond (anything but *ToDo* and *OnDeck*), End date the first time it is seen *Completed* or *Abandoned*, each only when blank and never overwritten; End date is cleared when a ticket is seen open again and set again when it next ends. Version and Alert tickets have no dates. It runs after each finalize and every day; a person may still correct a date by hand.

## The Watch flags

A ticket left alone gets Attention *Watch* with one comment: no activity at *Review* for a week, at *OnDeck* or *InProgress* for a month, at *Suspended* for six months, or waiting for input for two weeks. Activity is a comment, a change on the board, or a new build; the automation's own flag comments do not count. A flag is set only on a ticket that is blank, *Fine* or *Acknowledged*, and never lowers a level. It is raised once per situation, meaning the stage together with the latest build, remembered in a hidden marker in the comment: after a person closes the flag it comes back only when the stage changes or new work arrives. One limit follows from that: a ticket that moves away and back to the same stage with no new build counts as the same situation. Version and Alert tickets have no flags.

## The Caution flags for field rules

The rules that span fields are checked on every ticket: *Completed* has Resolution *Done*; *Abandoned* has one of the abandon reasons; an open ticket has no Resolution and no End date; Waiting is only on open tickets; a Backfilled ticket has its REF; the issue is closed only at *Completed* or *Abandoned*. A broken rule raises *Caution* with one comment naming it, but only when neither the issue nor the board item has changed for five minutes (fixing one takes several edits). It is raised once for a set of broken rules, remembered in a hidden marker in the comment: after a person closes the flag it comes back only when a rule not named before is broken. One limit follows: a rule put right and later broken again, with the flag closed in between, is not seen as new. Version and Alert tickets have no flags.

## Tickets with no file change

A ticket that changed no file (a setting, a secret, a check that was run) has nothing in the changelog for the automation to find. When its work is in effect, a person sets its Delivery to *Implemented* and its Version to the version it belongs to. At every finalize, and on a manual run of the workflow (dry run off), the automation attaches each *Implemented* ticket that is not yet a sub-issue of any Version ticket: a blank Version gets the version being finalized, an already finalized Version is kept and the ticket goes to that version's ticket, and a later Version waits (when a higher version is already finalized, the aimed number was passed and will never exist: the ticket gets Attention *Caution* with one comment and a person decides, so it does not wait for ever). The ticket keeps Delivery *Implemented* and gets no Build, and a comment on the Version ticket says which tickets were added. Releases will treat *Implemented* tickets like merged ones.

## Reading a flag

Every flag the automation raises is one comment that starts with a hidden marker (`<!-- attention:watch ... -->` or `<!-- attention:caution ... -->`). The marker is how the automation recognises its own flag comments (they do not count as activity) and remembers which situation or which broken rules it already flagged, so do not edit or delete these comments. To close a flag, decide what is true, act, and set Attention to *Fine* (nothing is wrong, or it was put right) or *Acknowledged* (something has to be done and it is handled elsewhere), with a comment saying which.

## The scripts

All in `.github/scripts/`, with a test file for each in `tests/`. Each can be run by hand with `--dry-run` (it needs `GITHUB_REPOSITORY`, `GITHUB_TOKEN` and `PROJECT_TOKEN` in the environment) except where noted.

| Script | What it does |
|---|---|
| `preflight.py` | The first step of every run: repository, token, board and its fields. |
| `finalize.py` | The finalize step, and the sweep of *Implemented* tickets that goes with it. |
| `bypass.py` | Bypass detection after a push to `main`, and the stale-version check (`stale`). |
| `advisory.py` | The advisory check on a pull request. |
| `push_step.py`, `skipped_hooks.py` | The push step and the fallback for skipped hooks. |
| `implemented.py` | Attaching *Implemented* tickets (the daily entry). |
| `board_pull_requests.py` | Puts a pull request on the board (`PULL_REQUEST`, as the workflow does), or with `--all` every pull request that is not on it yet (a one-time backfill). It sets no field, and it never fails a pull request run. |
| `version_numbers.py` | Sets Version# from Version on every work ticket that has a Version and a blank or different Version# (so an aimed ticket sorts by version). Changes nothing else. |
| `dates.py`, `watch.py`, `field_rules.py` | The date sweep, the Watch flags and the Caution flags for field rules. |
| `views.py` | Creates, recreates and removes the board's saved views from `.github/views.json` (grouping and sorting can only be set when a view is created, so a changed view is created again and the old one deleted after it; GitHub never deletes the last view of a board). By hand only, with `PROJECT_TOKEN`; it is a dry run unless `--apply` is given: `--only NAME`, `--delete NAME`, `--delete-unlisted`, `--show` (prints the board's views in the file's format), `--definition PATH`. Board settings are the administrator's, so it is run only when the administrator asks. |
| `check_manifest.py` | The manifest check and its rewrite (no tokens needed). |
| `changelog.py`, `versions.py`, `github_api.py`, `checks.py`, `alerts.py` | The shared library: changelog parsing, version rules, the GitHub client, git analysis, Alert tickets. |

## Starting a run by hand

In the Actions tab, run the *Versioning* workflow with a mode and the dry run on or off (it is on by default; a dry run only reports):

| Mode | Start it from | Inputs |
|---|---|---|
| `finalize` | `main` (or a branch, to try a change) | none: repeat or dry-run a finalize |
| `daily` | `main` | none: the daily checks |
| `release` | `main` (or a branch, to try a change) | `version`: a finalized version, or empty for the latest |
| `hotfix` | the hotfix branch itself | `version`: the hotfix version, for example `V1.25.0-HF1` |
| `retire` | `main` (or a branch, to try a change) | `branch`, `outcome` (archived, suspended or abandoned), `confirm` (the branch name again) and an optional `comment` for the tag |

The same from the command line: `gh workflow run versioning.yml --ref <branch> -f mode=release -f dry_run=false`.

## The release step

Declaring a finalized version a release is a deliberate step, started by hand (the developer verifies the version first and records the result). `release.py` tags the commit where the version was finalized, not the tip of `main`, as `released/V<major>.<sub>.<mod>`; sets the Version ticket to Delivery *Released* with a comment giving the date and the tag; and sets to *Released* every ticket that is *Merged* or *Implemented* with a version at or below the released one. A ticket with newer work pushed keeps *Pushed*. It refuses a version that is not finalized, one that already has a release tag, and one without a finalized Version ticket. A mistaken release tag may be deleted and the step run again, after putting the Version ticket and its tickets back to *Merged*.

## The hotfix-finalize step

A hotfix starts from a release tag, never from `main`, and is never merged, so its version is stated explicitly (`V1.25.0-HF1`, a single digit from 1 to 9 per release). Run on the hotfix branch (named `hotfix-v<major>-<sub>-<mod>-<description>`), `hotfix.py` renames the open `WIP-Version` heading to that version in a commit of its own on the branch, tags that commit `released/V1.25.0-HF1`, creates the Version ticket, and sets the tickets straight to *Released*. It refuses a marker on the heading, a branch that does not contain the release tag (or the previous hotfix's tag), and a version that already has its tag. Afterwards the branch is deleted without a retirement tag, and the fix reaches `main` separately through an ordinary branch and pull request.

## The retire step

Retiring a branch means tagging it and then deleting it. `retire.py` takes the branch, the outcome (*archived*, *suspended* or *abandoned*) and the branch name typed again as a confirmation. It tags the branch's last commit `<outcome>/<yyyy-mm-dd>_<branch>[_<comment>]` (the UTC date of that commit; the comment is optional and in kebab-case) and only then deletes the remote branch. It refuses `main`, a tag name that already exists, an *archived* branch that is not fully merged into `main`, and a *suspended* or *abandoned* branch that still has an open pull request (close it with a comment first). For an *abandoned* branch it sets the Delivery of the tickets in the branch's changelog entries to *Dropped*; moving tickets to *Suspended* or *Abandoned* stays a person's step. A finished hotfix branch is deleted without a retirement tag, because its release tag keeps its history.

## Checking the files

`python .github/scripts/check_manifest.py` reports each automation file as unchanged, edited locally or missing. With `--against <newer manifest>` it also reports files from an older version and files new in the standard. `--update --standard <version>` rewrites the manifest after a deliberate change.

## Running the tests

```
python -m unittest discover -s tests
```

The workflow itself can only be proven by a real run: start it by hand from the Actions tab (a dry run by default).

## Token

The workflow needs the secret `PROJECT_TOKEN`, a classic token with the `project` and `repo` scopes under an administrator account. It is stored only as a repository secret and renewed before it expires.
