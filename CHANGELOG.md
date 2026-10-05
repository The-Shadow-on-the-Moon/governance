# Changelog

## V0.2.0 — 2026-10-05 21:24 UTC
### Build 20261005211638 (branch apply-governance-to-itself)
#### #4 — Add the pull request template
- .github/pull_request_template.md: added; pre-fills the pull request description with a place for the changelog entries, the tested-build and sync line, and a reminder to reword closing keywords.

#### #5 — Add AGENTS.md with roles and the pointer to the guides
- AGENTS.md: added; points to the guides, gives the build and test commands, states that there are no durable authorizations, and lists what is out of bounds (the generated combined copy, and settings).

#### #7 — Record roles and repository access
- AGENTS.md: roles recorded; Damian Bucovsky is administrator, project owner and developer, and Pablo is developer with write access.
- doc/wiki/Roles-and-Access.md: added; the same roles and access in a table.

#### #6 — Add the dual licence (CC BY 4.0 and MIT)
- LICENSE: added; says which paths are under which licence (documentation under CC BY 4.0, code under MIT; copyright The Shadow on the Moon, Inc.).
- LICENSE-CC-BY-4.0.txt, LICENSE-MIT.txt: added; the full texts.
- README.md: added a Licence section.
- doc/wiki/Home.md: added a Licence section.

#### #8 — Create the board's saved views
- doc/wiki/Board-Views.md: added; the daily and consistency views with their filters, so the board's views can be recreated. The views themselves are created on the board by the administrator.
- doc/wiki/Home.md: added links to the roles and board views pages.

#### #9 — Fix the readme status text
- README.md: reworded the Status section to describe only this repository, with no mention of the project the guides came from or its release number.

## V0.1.0 — 2026-10-05 18:22 UTC
### Build 20261005181657 (branch initial-structure)
#### #1 — Initial structure of the project
- guides/: added the README, guides 01 to 10 and appendices A to D, moved here from the project they were developed in, and the combined copy Developer-Guides-Complete.md.
- tools/combine.py: added; rebuilds the combined copy from the separate guide files, and with --check reports whether it is up to date.
- tools/xref_check.py: added; checks that every cross-reference between the guides points at a section that exists.
- tests/test_tools.py: added; 9 tests for both tools, including that the combined copy is current and that the guides have no broken references.
- README.md: replaced GitHub's placeholder with the repository readme: what the repository holds and how to work on the guides.
- doc/wiki/Home.md: added; the wiki home page, linking to the guides.
- .github/workflows/wiki-sync.yml: added; copies doc/wiki/ to the repository's wiki on a push to main that touches it, and on request.
- .gitignore, .gitattributes: added; ignore generated and system files, and keep line endings as LF.
- CHANGELOG.md: started with this entry.
