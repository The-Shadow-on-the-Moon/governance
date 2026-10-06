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
| A pull request | The advisory check: fails and comments once when the branch is behind `main`, and lists merges with a manual conflict resolution. |
| A push to `main` | The preflight, then bypass detection (an Alert and an `AUTO-REF` entry), then the finalize step, then the check for stale planned Version tickets. |
| A push to another branch | The preflight; then the fallback for skipped hooks (a pushed changelog that still has `### WIP-Build` gets its build heading filled in with the commit's time and hash, a note in the first entry, and a commit on the branch); then the push step: for each ticket in the changelog entries the push added, Delivery becomes *Pushed* and Build the ticket's latest build, *ToDo* and *OnDeck* tickets become *InProgress*, and a ticket that is *Completed*, *Abandoned*, *Review* or *Suspended* and already had work pushed or delivered gets a *Caution* flag with a comment naming the build (not on its first push, and not again while a *Caution* or *AtRisk* is open). |
| On request | The preflight and the finalize step, as a dry run unless told otherwise. Safe to repeat. |

The preflight checks that the repository is reachable (the workflow's own token does not report its rights, so write access is confirmed through the project token), that `PROJECT_TOKEN` works (and warns two weeks before it expires), which board belongs to the repository (its number is kept in the repository variable `BOARD_NUMBER`) and that the board has every field and value the automation needs.

The finalize step decides the bump from the tickets' Types or the marker, renames the open `WIP-Version` heading in a commit of its own, sets Delivery, Version, Build and Version# on each ticket, and creates and closes the Version ticket with the tickets as sub-issues. If the board cannot be updated, the version is still finalized.

## Tickets with no file change

A ticket that changed no file (a setting, a secret, a check that was run) has nothing in the changelog for the automation to find. When its work is in effect, a person sets its Delivery to *Implemented* and its Version to the version it belongs to. At every finalize, and on a manual run of the workflow (dry run off), the automation attaches each *Implemented* ticket that is not yet a sub-issue of any Version ticket: a blank Version gets the version being finalized, an already finalized Version is kept and the ticket goes to that version's ticket, and a later Version waits. The ticket keeps Delivery *Implemented* and gets no Build, and a comment on the Version ticket says which tickets were added. Releases will treat *Implemented* tickets like merged ones.

## Checking the files

`python .github/scripts/check_manifest.py` reports each automation file as unchanged, edited locally or missing. With `--against <newer manifest>` it also reports files from an older version and files new in the standard. `--update --standard <version>` rewrites the manifest after a deliberate change.

## Running the tests

```
python -m unittest discover -s tests
```

The workflow itself can only be proven by a real run: start it by hand from the Actions tab (a dry run by default).

## Token

The workflow needs the secret `PROJECT_TOKEN`, a classic token with the `project` and `repo` scopes under an administrator account. It is stored only as a repository secret and renewed before it expires.
