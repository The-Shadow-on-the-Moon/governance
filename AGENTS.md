# Instructions for assistants

Follow the process guides in [`guides/`](guides/README.md), also published as one file in
[`guides/Developer-Guides-Complete.md`](guides/Developer-Guides-Complete.md). Work from the checklist at the
end of each guide. This repository is the standard itself, so the guides are both the rules and the content.

This project
- Build: `python tools/combine.py` (rebuilds the combined copy; run it after editing any guide).
- Tests: `python tools/xref_check.py` (expect `problems: 0`) and `python -m unittest discover -s tests`
  (expect `OK`).
- Roles: Damian Bucovsky holds the administrator, project owner and developer roles. Pablo holds the
  developer role, with write access. More in [`doc/wiki/Roles-and-Access.md`](doc/wiki/Roles-and-Access.md).
- Durable authorizations: none.
- Out of bounds: `guides/Developer-Guides-Complete.md` is generated, so change the separate guide files and
  rebuild it, never edit it by hand. Repository, organization and board settings change only when the
  administrator asks.
