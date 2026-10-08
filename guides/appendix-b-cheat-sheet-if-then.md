# Appendix B: Cheat sheet, if this then that

Situations, what to do, and where to read more. It adds no new rules. "Branching" means the guide on
branching and merging.

## While working

| If… | Then… | See |
|---|---|---|
| I changed something and have no ticket | Start a `REF` block with a UTC token, and backfill it before the pull request. | Starting work, section 4; Working and committing, section 6 |
| a change serves several tickets | Describe it in full under one, mention the others, and give each of the others a block that points to it. | Working and committing, section 2.4 |
| the hook did not stamp my commit, or I skipped the hooks | The automation fills in the build heading with the commit's hash and adds a note. Skipping is allowed but not hidden. | Starting work, section 5.1 |
| an existing test fails and it is not my change | Raise a Bug ticket, mention it in my ticket, and do not hide or delete the test. | Working and committing, section 4 |
| an earlier changelog entry is critically wrong | Create a correction ticket, log it in the current version, comment on the original ticket, and correct the old entry with a note. | Working and committing, section 2.5 |
| I need an answer before I can go on | Set Waiting with a comment saying what is needed and from whom. | Working and committing, section 7 |
| the work is bigger or smaller than its Size | Correct the Size and say why in a comment. | Working and committing, section 7 |

## Landing

| If… | Then… | See |
|---|---|---|
| my branch is behind `main` | Merge `main` into it, recompile, and retest in proportion. | Syncing and merging, section 1 |
| `main` has nothing my branch lacks | No sync is needed. | Syncing and merging, section 1.1 |
| I got a conflict while syncing | Resolve it on the branch, log it under my ticket, put the details in a comment, and rebuild and retest. | Syncing and merging, section 1.2 |
| the conflict is in `CHANGELOG.md`, at the top, because another branch landed first | Keep my open `WIP-Version` on top and `main`'s finalized versions below it, unchanged. No entry is needed. | Syncing and merging, section 1.2 |
| `main` moved after my sync | Sync again. | Syncing and merging, section 1.2 |
| my push was rejected because someone else pushed to the branch | Fetch and merge `origin/<branch>`, resolve any conflict on the branch, rebuild, push. Never rebase or force. | Syncing and merging, section 1.4 |
| I want to force a different version bump | Add `+V`, `+s` or `+m` after `WIP-Version` (never on a hotfix). | Branching, section 3.3 |
| the advisory check is red | Sync again before merging. | Syncing and merging, section 4 |
| I need to bypass a rule | Do it deliberately, say why, expect the Alert, then pull `main` and build and test it. | Syncing and merging, section 6 |
| the version came out wrong | Note it on the Version ticket and fix the ticket's Type. The number is never changed. | Syncing and merging, section 5.4 |
| the board was not updated after the merge | Re-run the finalize step or correct the fields by hand. | Syncing and merging, section 5.2 |

## Tickets

| If… | Then… | See |
|---|---|---|
| a review fails and the ticket's own work is wrong | Send it back to *InProgress* with a comment. | Project structure, section 3.4 |
| a review finds a separate problem | Create a new Bug that mentions the original as "introduced by #123". | Project structure, section 3.4 |
| a ticket needs more work after it is *Completed* | Reopen it only if its own scope is unmet. Otherwise create a new ticket and link the two. | Issues and the board in practice, section 4.3 |
| work is set aside to resume later | Suspend the ticket, with a comment, and the branch too. | Issues and the board in practice, section 4.1 |
| work is being dropped | Abandon it with a Resolution and a comment, and the branch too. | Issues and the board in practice, section 4.2 |
| an Alert is assigned to me | Triage it before other work. | Issues and the board in practice, section 5 |
| the automation flagged my ticket (*Watch*, *Caution* or *AtRisk*) | Read its comment, decide, act, and set *Fine*, or *Acknowledged* if it is handled elsewhere. | Issues and the board in practice, section 2.4 |
| an Alert was raised in error | Abandon it with Resolution *Invalid* and a comment, and raise a Bug against the automation. | Issues and the board in practice, section 5 |
| a planned version will not happen | Mark it *Dropped*, close it, and comment what replaced it. | Issues and the board in practice, section 6 |

## Branches and releases

| If… | Then… | See |
|---|---|---|
| my branch is merged and the work is done | Retire it, tagging it first (archived). | Releases, hotfixes and retiring branches, section 3 |
| a hotfix is finished and released | Delete the hotfix branch: its release tag keeps its history. | Releases, hotfixes and retiring branches, section 2 |
| I want to keep working on a merged branch | Sync `main` into it first, then open a new `WIP-Version` heading. | Starting work, section 3.3 |
| I want to restart a suspended or abandoned branch | Recreate it from its tag, and sync `main` first. | Starting work, section 3.4 |
| a critical problem is found in a released version | Start a hotfix from the release tag. | Releases, hotfixes and retiring branches, section 2 |
| I want to declare a version a release | Verify it, run the release step, and tell the project owner. | Releases, hotfixes and retiring branches, section 1 |
| a release was declared by mistake | Delete the tag and put the Version ticket and its tickets back to *Merged*. | Releases, hotfixes and retiring branches, section 1.1 |

## Assistants and new projects

| If… | Then… | See |
|---|---|---|
| I am an assistant and the action is risky, outward-facing, or a commit, push or merge into `main` or a shared branch | Ask first, and propose the commit message. Syncing `main` into the person's own branch is routine. | Working with an assistant, section 3 |
| I am an assistant and there is a real choice to make | Present the options with a recommendation and ask. | Working with an assistant, section 3 |
| I am starting a new project | Follow the bootstrap checklist. | New-project bootstrap, section 9 |
