# Releases, Hotfixes and Retiring Branches

This guide covers the steps that end or branch off the normal flow: declaring a version a release, fixing a
version that has already been released, and retiring a branch. It is a procedure: each step says what to do
and why, and the commands are in the "In GitHub" blocks. The rules and their reasons are in the guide on
branching and merging; the pieces it refers to (tickets, tags, the Version ticket) are defined in the guide
on project structure.

**How to read it.** Each step states what to do and why. Statements are marked:

- **Rule**: followed always. A rule may be checked or enforced by tooling, or only be a convention.
- **Recommendation**: good practice with reasons, but the developer decides.
- **Strong recommendation**: a recommendation with more weight. Follow it unless there is a reason not to,
  and say why when you do not.
- **In GitHub**: how the step looks with GitHub and plain git. Everything outside these blocks is
  tool-neutral.

**Responsible, not necessarily manual.** Where this guide says "you", it means the person responsible. A
step may be done by hand, by an assistant, or by a script or command that person runs; it is still that
person's action.

---

## 1. Cut a release

A release is a version on `main` that is deliberately declared a release. Every merge makes a version, but
only some versions become releases.

The steps:

1. **Decide which version.** It must already be finalized on `main`.
2. **Verify it** (section 1.1).
3. **Run the release step** with that version. By default it is the latest on `main`.
4. **Check the result.** The tag `released/V<major>.<sub>.<mod>` exists on the commit where that version was
   finalized. The Version ticket shows Delivery *Released* and a comment with the date and the tag. Every
   ticket merged or implemented up to that version shows *Released*, unless newer work on it has been
   pushed since.
5. **Tell the project owner** that the release was made.

### 1.1 Rules

- **Rule:** the developer decides which versions are releases, and tells the project owner. The remote
  automation carries it out.
- **Rule:** verify the version before releasing it: run the regression checks on it.
- **Strong recommendation:** record the results, naming the build (see the guide on working and
  committing, section 4). The regression checks are an ordinary Task: its result file is committed like
  any change and lands in a later version, and the result names the version and build that were tested.
- **Rule:** a release marks as *Released* only the tickets whose Delivery is *Merged* or *Implemented* and
  whose version is at or below the released one. A ticket with newer work pushed keeps *Pushed*.
- **Recommendation:** have the version's tickets completed before releasing it.
- **Rule:** the tag goes on the commit where the version was finalized, not simply on the current tip of
  `main`.
- **Rule:** only a finalized version can be released, and each version has at most one release tag.
- **A mistaken release tag may be deleted and redone.** A release tag is only an indicator that makes a
  version easy to find. Every change that lands on `main` produces its own version, so a version is the
  version whatever any tag says, and a tag on the wrong commit, or on a version that was not meant to be a
  release, harms nothing once it is removed. After deleting it, put the Version ticket and its tickets
  back to *Merged*.

**Why.** A release is a statement that a version is fit to be used, so it has to be verified, and the tag
has to point at exactly what was verified; tagging the tip would be wrong whenever `main` has moved on.
Because the version identifies a position in the history by itself, the tag can be corrected freely.

> **In GitHub.** The release step is a manually started run of the repository's workflow, given the
> version to release. The tag appears under the repository's tags, and a mistaken tag is removed with
> `git push origin --delete <tag-name>` and `git tag -d <tag-name>`; other clones drop it with
> `git fetch --prune --prune-tags`.


---

## 2. Hotfix

A hotfix fixes a version that has already been released, without carrying anything that has happened on
`main` since. The rules are in the guide on branching and merging (section 1.3); this section is the
procedure.

### 2.1 Start

1. **Create a ticket for the fix.** Usually Type *Bug*, with a Priority of *Critical* or *Urgent*. Assign it
   to yourself and set it to *InProgress* (see the guide on starting work, section 2).
2. **Create the hotfix branch from the release tag,** not from `main` (for a further hotfix of the same
   release, from the previous hotfix's tag). Name it
   `hotfix-v<major>-<sub>-<mod>-<description>` (see the guide on starting work, section 3.2).
3. **Add the changelog heading:** a `## WIP-Version` at the top, with no marker, since markers are not
   allowed on a hotfix branch.
4. **Work as usual:** change, build, test, log, commit, push (see the guide on working and committing).
5. **Tell the project owner** that a hotfix has been started.

### 2.2 Finish

6. **Verify the hotfix** the same way as any release (section 1.1).
7. **Run the hotfix-finalize step** with the explicit version, for example `V1.25.0-HF1`. It renames the
   heading to that version, tags `released/V1.25.0-HF1`, creates the Version ticket, and sets the tickets'
   Delivery straight to *Released*, because a hotfix is never merged and so skips *Merged*.
8. **Check the result:** the heading, the tag, the Version ticket and the tickets.
9. **Tell the project owner** that the hotfix has been released.

### 2.3 Forward-port and retire

10. **Reintroduce the fix into `main`** as an ordinary branch and pull request, with its own ticket. The
    ticket's description says it is a forward-port of the hotfix ticket, so the link between them is kept in
    the tickets, not in the changelog. It gets whatever version `main` is at.
11. **Delete the hotfix branch.** Its release tag already keeps its history, so no retirement tag is
    added.

### 2.4 Rules

The rules about what a hotfix is (it starts from a release tag and is never merged, its version lineage
and the single-digit limit on hotfix numbers, how the fix reaches `main`, and that a finished hotfix
branch is deleted without a retirement tag) are in the guide on branching and merging, sections 1.3
and 2.2. The rules for the procedure are these:

- **Rule:** the hotfix version is given explicitly when it is finished, because there is nothing to
  compute it from.
- **Rule:** verify the hotfix before finishing it, as for any release.
- **Rule:** the developer starts and finishes a hotfix, and tells the project owner when it is started and
  when it is released.
- **Recommendation:** keep a hotfix to the fix itself, and nothing else.

**Why.**

- *From the tag, never merged* because a hotfix patches exactly what was released, so it must start from
  exactly that and never carry unrelated work. Its own numbering lineage cannot collide with a version
  `main` has produced or will produce.
- *Developer-driven* because a critical problem in a released version is urgent, and waiting for approval
  would cost time the situation does not have. The project owner is told so that nothing happens without
  their knowledge.
- *A separate forward-port* because the fix still has to be part of `main`'s history, through the normal
  flow, with its own ticket, verification and version.


---

## 3. Retire a branch

Retiring means recording where a branch ended up with a tag and then deleting the branch. The rules are in
the guide on branching and merging (section 1.5); this section is the procedure.

The steps:

1. **Choose the outcome.**
   - **Archived:** the work is done and merged.
   - **Suspended:** the work is set aside and expected to return.
   - **Abandoned:** the work is discarded.
2. **Check the branch.**
   - For *archived*, confirm that all its commits are reachable from `main`. If they are not, it is not
     archived: suspend it or abandon it.
   - For *suspended* or *abandoned*, close any open pull request with a comment saying why.
3. **Update the tickets.**
   - *Archived:* nothing to change.
   - *Suspended:* move the tickets to *Suspended* with a comment. The developer proposes, and the project
     owner decides.
   - *Abandoned:* move the tickets to *Abandoned* with a Resolution and a comment. The automation also sets
     their Delivery to *Dropped*.
4. **Run the retire step** with the branch name and the outcome, and confirm by typing the branch name
   again. It tags the branch's last commit and then deletes the branch.
5. **Check the result.** The tag exists, the branch is gone, and the tickets show what you expect. Delete
   your local copy of the branch.

### 3.1 Rules

- **Rule:** tag first, delete second. The one exception is a finished hotfix branch, whose release tag is
  already its record (section 2).
- **Rule:** the tag is named `<outcome>/<yyyy-mm-dd>_<branch>[_<comment>]`, using the UTC date of the
  branch's last commit.
- **Rule:** if a tag with that name already exists, add a short comment to make it unique. The retire step
  refuses a name that already exists.
- **Rule:** *archived* is only for a branch whose work is fully merged.
- **Recommendation:** for *suspended* and *abandoned*, add a short comment to the tag name saying why, in
  kebab-case. A longer note goes in an annotated tag.
- **To start again from a suspended or abandoned branch,** see the guide on starting work, section 3.4.

**Why.** A tag costs nothing and keeps the branch's history reachable. Three outcomes let a later reader
answer "was this merged", "can we pick it back up" and "did we decide to drop it". Typing the branch name
again before deleting guards against retiring the wrong branch.

> **In GitHub.** The retire step is a manually started run of the repository's workflow, given the
> branch, the outcome and the confirmation. By hand: `git tag <tag> origin/<branch>`,
> `git push origin <tag>`, `git push origin --delete <branch>`, then `git branch -d <branch>` for your
> local copy.


---

## 4. Checklist

A one-page summary of the guide. It adds no new rules.

**Cut a release** (section 1)

- [ ] The version is finalized on `main`.
- [ ] It is verified: the regression checks are run, and the results are recorded with the build (a
      strong recommendation).
- [ ] Its tickets are completed (a recommendation).
- [ ] The release step is run with that version, and the project owner is told.
- [ ] The tag is on the commit where the version was finalized, the Version ticket shows *Released* with
      its comment, and the tickets show *Released*.
- [ ] If the release was a mistake: the tag is deleted, and the Version ticket and its tickets are back to
      *Merged*.

**Hotfix** (section 2)

- [ ] A ticket exists for the fix (Type *Bug*, Priority *Critical* or *Urgent*), assigned to me and
      *InProgress*.
- [ ] The branch is created from the release tag and named `hotfix-v…`.
- [ ] The changelog has a `WIP-Version` heading with no marker.
- [ ] I worked as usual, and the project owner is told it started.
- [ ] The hotfix is verified, and the hotfix-finalize step was run with the explicit version (for example
      `V1.25.0-HF1`).
- [ ] I checked the heading, the tag, the Version ticket and the tickets, and the project owner is told it
      is released.
- [ ] The fix is forward-ported to `main` as its own ticket and pull request, linked to the hotfix ticket.
- [ ] The hotfix branch is deleted; its release tag keeps its history.

**Retire a branch** (section 3)

- [ ] The outcome is chosen: archived, suspended or abandoned.
- [ ] For *archived*, all commits are reachable from `main`. For *suspended* or *abandoned*, any open pull
      request is closed with a comment.
- [ ] The tickets are updated: *Suspended*, or *Abandoned* with a Resolution, and a comment.
- [ ] The retire step is run (tag first, then delete) and confirmed.
- [ ] The tag exists, the branch is gone, and my local copy is deleted.

**In one line:** release, hotfix, retire: verify, tag, check.
