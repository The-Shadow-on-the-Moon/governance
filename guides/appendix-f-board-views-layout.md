# Appendix F: Board views, columns and sorting

What each saved view of the board shows, column by column: the fields displayed, the sort order and the
grouping (the swimlanes of a board view, the row groups of a table). It records the views as they are, so a
change to them can be judged against it. Which tickets each view lists, and why, is in *Issues and the board
in practice*, section 2.2; the filters are in `.github/views.json` and in the wiki page Board views.

**Read as of 2026-10-11,** from the Governance board (project 7) through the API, and compared with
`.github/views.json`. Every view also shows the ticket **Title**, which is not repeated in the lists below.

---

## 1. Table views

| View | Columns, in the order the board reports them | Sort | Groups |
|---|---|---|---|
| **All** | Assignees, Status, Labels, Origin, Waiting, Attention, Resolution, Delivery, Priority, Size, Risk, REF, Version, Build, Version#, Start date, End date | Created, ascending (ticket-number order) | none |
| **Decide** | Assignees, Status, Attention, Priority | Priority, ascending | none |
| **Follow up** | Assignees, Status, Waiting, Priority | Priority, ascending | none |
| **Fix** | Assignees, Status, Resolution, Delivery, Priority, REF, Version, End date, Fix | Priority, ascending | none |
| **Versions** | Status, Resolution, Delivery, Priority, Version, Build | Version#, ascending, then Priority, ascending | Parent issue (the Version ticket) |

## 2. Board views

A board view has columns (one per value of a field) and, optionally, rows (swimlanes, one per value of a
second field). The fields below are the ones drawn on each card.

| View | Layout | Columns | Rows | Fields on the card | Sort within a cell |
|---|---|---|---|---|---|
| **Backlog** | board | Status | none | Assignees, Priority, Size, Risk, Version | Priority, ascending |
| **Board** | board | Status | Version | Assignees, Waiting, Attention, Priority, Size | Priority, ascending |

## 3. Where the board and the file differ

`.github/views.json` asks for more columns than the board reports for each view:

- **Type** is requested by All, Backlog, Board, Decide, Follow up, Fix and Versions, and the board reports it
  for none. Type is the issue type, not a board field, and the API may leave it out of this list although
  the column is shown. Check it on the screen.
- **Order.** The board reports the columns in the order of its fields (REF comes after Risk), while the file
  lists them in the order they are meant to appear (REF after Origin). Which order the screen shows is
  checked by looking at it, not by this table.

## 4. Notes

- All is the view the owner finds right for working through many tickets: every field is shown, and the
  order is the ticket number. The other table views show little, which is enough for one or two tickets
  (open the ticket for the rest) and not enough when many are listed.
- The sort and grouping of a view can only be set when it is created (see *Issues and the board in
  practice*, section 2.3), so changing them recreates the view.
- This appendix is documentation of the present state. Choosing the columns each view should show is
  decided separately, and the result replaces sections 1 and 2.
