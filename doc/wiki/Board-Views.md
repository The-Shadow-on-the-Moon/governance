# Board views

The saved views of the [Governance board](https://github.com/orgs/The-Shadow-on-the-Moon/projects/7), from the standard's guide on tickets and the board (sections 2.2 and 7.1). They are defined in `.github/views.json` and created by `.github/scripts/views.py` (see [Automation](Automation)), so every project has the same ones. To change a view, change the file and run the script; keep this page in step with the file (a test checks that every view and filter in the file is on this page).

Every view except All also ends with `AND is:issue AND -label:dummy`, which the script adds: `is:issue` leaves out the pull requests (the automation puts each one on the board so that All has no gap in the numbers), and `-label:dummy` leaves out the throwaway tickets and Version tickets made to test the automation (label `dummy`, described in the standard's ticket fields reference). All is the complete list and hides nothing.

## The views, in tab order

| View | Layout | Filter | Grouping and sorting | Shows |
|---|---|---|---|---|
| All | table | none (neither the test tickets nor the pull requests are left out) | no grouping; in ticket-number order (see the notes) | Every item on the board, test tickets and pull requests included, with all its fields, for finding anything and for audit. |
| Backlog | board | `status:ToDo,OnDeck,Suspended` | columns by Status; sorted by Priority | The waiting and set-aside work, the most urgent first. |
| Board | board | `is:open AND -type:Version AND -status:ToDo,Suspended` | columns by Status, rows by Version; sorted by Priority | The active work (OnDeck, InProgress, Review) with a row for each Version. |
| Decide | table | `attention:Watch,Caution,AtRisk OR (type:Alert AND is:open)` | sorted by Priority | What the automation noticed and a person must judge: an open Attention flag, an open Alert. Start a work session here. |
| Follow up | table | `has:waiting OR status:Review` | sorted by Priority | The ordinary queues: a ticket marked *Needs input*, and a ticket at *Review* awaiting verification. |
| Fix | table | `has:fix` | sorted by Priority | Tickets whose fields contradict each other; the Fix column names the broken rules. |
| Versions | table | `has:version AND -type:Version` | grouped by Parent issue (the Version ticket, so a group reads "Version 0.7.0"); sorted by Version#, then Priority | What each version holds, with Delivery, Build and Resolution. Tickets only aimed at a version (no Version ticket yet) are in the "No parent issue" group, ordered by their Version#. |

## What the condition views show

Everything the board draws attention to is a *condition*, and each of the three natures has its own view: **Decide** (a person must judge it), **Follow up** (a queue) and **Fix** (the fields contradict each other). The conditions are listed once, in the registry `.github/scripts/conditions.py`, and the table of the guide on the board (section 2.5) is checked against it by a test.

Decide and Follow up read fields people and the automation already set (Attention, Waiting, Progress). Fix reads one field, **Fix**, in which the refresh lists the ids of the rules of the standard (the guide on project structure, section 4.4) that a ticket breaks, so that its filter is `has:fix` however many rules there are. Only the automation writes Fix, it clears an id when the rule stops being broken, and a ticket with two broken rules keeps both until both are put right. The old Health view repeated every rule as a filter clause, reached the 512-character limit, and had already drifted from the rules (it did not list an Abandoned ticket without a reason); it was replaced by these three.

## Notes

- A filter may join fields with `AND`, `OR` and parentheses, and GitHub accepts at most 512 characters in the filter a view really gets, which is the one in the file plus the ending the script adds (` AND is:issue AND -label:dummy`). The longest is Decide, at 90; a test fails when any view goes over or comes within 100 characters of it. If a filter is rejected, rebuild it with the board's filter suggestions (type the field name and pick from the list) and correct it in the file.
- A view's grouping, columns and rows, and sorting can only be set when it is created, and the API cannot sort a new view by Created, Updated or Closed. So `views.py` creates a changed view again and then deletes the old one; GitHub never deletes the last view of a board.
- **By hand, once, when All is created:** set its sort to *Created, ascending* and turn *Show hierarchy* off (otherwise tickets are listed inside their Version ticket). The API cannot do either, `views.py` prints a reminder at the end of every run, and a view that is created again loses them.
- All lists the board's items in the order they were added, which is the ticket-number order. The API cannot set a sort by Created, Updated or Closed on a new view, so to make the order certain set the sort **Created, ascending** on All by hand in the web interface (the script ignores a sort by Created when it compares, and says so when it creates the view). A pull request takes a ticket number too: the automation puts it on the board as an item (`board_pull_requests.py`) so that All has no gap in the numbers, and the other views leave it out with `is:issue`.
- Planned, not yet created: a **Roadmap** view (a timeline from Start date to End date, actual dates only), kept in a ticket at *ToDo*.
