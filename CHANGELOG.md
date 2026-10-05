# Changelog

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
