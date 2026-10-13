# Appendix F: Board views, columns and sorting

What each saved view of the board shows, column by column: the fields displayed, the sort order and the
grouping (the swimlanes of a board view, the row groups of a table). The layout is defined in
`.github/views.json` (`visible_fields`, in the order they are meant to appear). Which tickets each view
lists, and why, is in *Issues and the board in practice*, section 2.2; the filters are in the same file and
in the wiki page Board views.

---

## 1. Table views

The number is the position of the column in the view; "·" means the view does not show it.

| Field | All | Decide | Follow up | Fix | Versions |
|---|---|---|---|---|---|
| Title | 1 | 1 | 1 | 1 | 1 |
| Assignees | 2 | 2 | 2 | 2 | 5 |
| Status | 3 | 3 | 3 | 4 | 2 |
| Type | 4 | 4 | 4 | 5 | 3 |
| Labels | 5 | 5 | 5 | 6 | 4 |
| Priority | 6 | 7 | 7 | 7 | 6 |
| Size | 7 | · | 8 | · | 7 |
| Risk | 8 | · | 9 | · | · |
| Waiting | 9 | 8 | 6 | · | · |
| Attention | 10 | 6 | · | · | · |
| Fix | 11 | · | · | 3 | · |
| Resolution | 12 | · | 10 | 8 | 9 |
| Delivery | 13 | 9 | 11 | 9 | 8 |
| Origin | 14 | · | · | · | · |
| REF | 15 | · | · | 13 | · |
| Version | 16 | 10 | 12 | 10 | 10 |
| Build | 17 | · | · | 11 | 11 |
| Start date | 18 | · | · | · | · |
| End date | 19 | · | · | 12 | · |
| **Sort** | Created, ascending | Priority, ascending | Priority, ascending | Priority, ascending | Version, ascending, then Priority, ascending |
| **Group** | none | none | none | none | Parent issue (the Version ticket) |

Version is written in the board form (`V000.010.001`), which sorts as text in version order, so the Versions view sorts by it and its groups (the Version tickets, titled `Version 000.010.001`) come out in version order.

## 2. Board views

A board view has columns (one per value of a field) and, optionally, rows (swimlanes, one per value of a
second field). The fields below are the ones drawn on each card.

| View | Layout | Columns | Rows | Fields on the card | Sort within a cell |
|---|---|---|---|---|---|
| **Backlog** | board | Status | none | Assignees, Priority, Size, Risk, Version | Priority, ascending |
| **Board** | board | Status | Version | Assignees, Waiting, Attention, Priority, Size | Priority, ascending |

## 3. Why these columns

- Every table view starts with the same five columns (Title, Assignees, Status, Type, Labels), so a ticket
  reads the same wherever it is listed. All is the complete list: every field.
- The short views add what their job needs: Attention and Waiting to decide, Waiting, Size, Risk and
  Resolution to follow up, Fix and the rule columns to fix, Delivery, Resolution and Build to see what a
  version holds. Delivery and Version are on all of them, to tell at a glance whether the work is merged or
  released without opening the ticket.

## 4. Notes

- **Type** is the issue type, not a board field. The API does not report it among a view's visible fields,
  so `views.py` does not compare it. When the Type source is the field Kind, the column is *Kind*, a board
  field like the others, and the filters use `kind:` where the views use `type:`. The order of the columns is
  not compared either (only which fields are shown).
- The sort and grouping of a view can only be set when it is created (see *Issues and the board in
  practice*, section 2.3), so changing them recreates the view. Recreating All also loses its two hand-made
  settings (sort by Created, ascending, and *Show hierarchy* off).
