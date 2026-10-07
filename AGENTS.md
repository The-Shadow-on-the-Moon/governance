# Instructions for assistants

Follow the process guides in [`guides/`](guides/README.md), also published as one file in
[`guides/Developer-Guides-Complete.md`](guides/Developer-Guides-Complete.md). Work from the checklist at the
end of each guide. This repository is the standard itself, so the guides are both the rules and the content.

This project
- Build: `python tools/combine.py` (rebuilds the combined copy; run it after editing any guide).
- Tests: `python tools/xref_check.py` (expect `problems: 0`) and `python -m unittest discover -s tests`
  (expect `OK`).
- Hooks: activate them once per clone with `git config core.hooksPath .githooks`.
- Automation files (hooks, `.github/scripts/`, the versioning workflow, the pull request template and the
  automation's tests) are listed in `.github/automation-manifest.json`. After a change to one, run
  `python .github/scripts/check_manifest.py --update --standard <version>`, then the tests. `<version>` is the version the
  open version will become; the marker or the ticket Types can change it at merge, so after the finalize check it against
  the changelog and correct it through a ticket if it differs.
- A release, a hotfix finish and a branch retirement are done only by the workflow's manual runs (see the wiki page
  on the automation), never by hand with git, and only when the administrator or developer asks: run the dry run
  first and say what it would do.
- Flag comments (they start with `<!-- attention:`) and commits whose message starts with `Finalize `,
  `Flag bypass` or `Fill in a build heading` are written by the automation, which recognises them: do not edit
  or reuse them.
- Tests of the automation use throwaway tickets and branches, titled DUMMY and labelled `dummy`, closed as
  Invalid (Abandoned), with their branches tagged before they are deleted.
- Roles: Damian Bucovsky holds the administrator, project owner and developer roles. Pablo holds the
  developer role, with write access. More in [`doc/wiki/Roles-and-Access.md`](doc/wiki/Roles-and-Access.md).
- Durable authorizations: none.
- Out of bounds: `guides/Developer-Guides-Complete.md` is generated, so change the separate guide files and
  rebuild it, never edit it by hand. The automation files change only through a ticket, and the manifest is
  rewritten with them. Repository, organization and board settings change only when the
  administrator asks.
