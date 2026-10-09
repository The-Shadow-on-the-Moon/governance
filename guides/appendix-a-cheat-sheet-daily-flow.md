# Appendix A: Cheat sheet, the daily flow

The whole flow on one page, from starting work to a verified result. Each step names the guide section that
explains it. It adds no new rules.

## Once per clone

- [ ] Clone the repository, follow the readme's setup, and activate the hooks (*Starting work*, section 1).

## Start

1. **Find or create the ticket.** Search first. A new ticket needs a Title, Type, Description and Size, or
   start with a `REF` (*Starting work*, section 2).
2. **Assign it to yourself and set it to *InProgress*.**
3. **Update `main` and create the branch** from it: kebab-case, no `/`. A hotfix starts from the release tag
   (*Starting work*, section 3).
4. **Open the changelog entry:** a `## WIP-Version` heading, a `### WIP-Build` placeholder, and the ticket
   block with the ticket's exact title (*Starting work*, section 4).

## Work

5. **Change, build, test, log, commit.** Build locally before every commit, add a fresh `### WIP-Build`
   under the open version for each commit, log each change as a specific bullet, and commit through the editor so the message is drafted from the changelog (*Working and
   committing*, sections 1, 2, 4 and 5).
6. **Update what the change affects:** find the row for each change in the checklist (*Working and
   committing*, section 3).
7. **Keep the ticket current:** Progress, Waiting, comments, Size and Risk (*Working and committing*,
   section 7).
8. **Push.** Delivery becomes *Pushed* (*Starting work*, section 5).

## Land

9. **Sync `main` into the branch** by merging, never by rebasing. Recompile, and retest in proportion
   (*Syncing and merging*, section 1).
10. **Get ready:** tickets at *Review* with Risk revised, every `REF` backfilled (strongly recommended), test results worth keeping recorded
    (strongly recommended), documentation updated (*Syncing and merging*, section 2).
11. **Open the pull request:** a title that states the purpose, and a description that pastes the open
    version's changelog entries plus the tested build and the sync line (*Syncing and merging*, section 3).
12. **Merge with a merge commit.** Do not delete the branch and do not close the tickets (*Syncing and
    merging*, section 4).

## After

13. **Pull `main` and check:** the heading is renamed to the expected version, the Version ticket lists your
    tickets, and they show Delivery *Merged* (*Syncing and merging*, section 5).
14. **Triage any Alert** assigned to you (*Issues and the board in practice*, section 5), and decide any
    Attention flag on your tickets (*Issues and the board in practice*, section 2.4).
15. **Verify** (a person), before or after the merge: set Resolution *Done* and Progress *Completed*
    together, and close the issue
    (*Issues and the board in practice*, section 3).
16. **Continue the branch or retire it** (*Syncing and merging*, section 7; *Releases, hotfixes and retiring
    branches*, section 3).

## Never

- Never rebase, squash, or amend a commit that others have built on.
- Never use a closing keyword (*Closes*, *Fixes*, *Resolves*) in a pull request.
- Never edit an earlier changelog entry, except to replace a placeholder or to correct a critical mistake.
- Never commit without building.
- Never bypass a rule silently: say why, and expect the Alert.

**In one line:** ticket, branch, entry, build, commit, push, sync, pull request, merge, check, verify.
