# Board views

The saved views of the [Governance board](https://github.com/orgs/The-Shadow-on-the-Moon/projects/7), from the standard's guide on tickets and the board (sections 2.2 and 7.1). They are defined in `.github/views.json` and created by `.github/scripts/views.py` (see [Automation](Automation)), so every project has the same ones. To change a view, change the file and run the script; keep this page in step with the file (a test checks that every view and filter in the file is on this page).

Every view except All also ends with `AND is:issue AND -label:dummy`, which the script adds: `is:issue` leaves out the pull requests (the automation puts each one on the board so that All has no gap in the numbers), and `-label:dummy` leaves out the throwaway tickets and Version tickets made to test the automation (label `dummy`, described in the standard's ticket fields reference). All is the complete list and hides nothing.

## The views, in tab order

| View | Layout | Filter | Grouping and sorting | Shows |
|---|---|---|---|---|
| All | table | none (neither the test tickets nor the pull requests are left out) | no grouping; in ticket-number order (see the notes) | Every item on the board, test tickets and pull requests included, with all its fields, for finding anything and for audit. |
| Backlog | board | `status:ToDo,OnDeck,Suspended` | columns by Status; sorted by Priority | The waiting and set-aside work, the most urgent first. |
| Board | board | `is:open AND -type:Version AND -status:ToDo,Suspended` | columns by Status, rows by Version; sorted by Priority | The active work (OnDeck, InProgress, Review) with a row for each Version. |
| Health | table | `attention:Watch,Caution,AtRisk OR waiting:"Needs input" OR status:Review OR (type:Alert AND is:open) OR (status:Completed no:resolution) OR (is:open has:resolution) OR (is:open has:end-date) OR (is:closed has:waiting) OR (origin:Backfilled no:ref) OR (status:Completed,Abandoned AND is:open) OR (is:closed AND -status:Completed,Abandoned AND -type:Version) OR (status:Completed no:delivery AND -type:Version AND -type:Alert) OR (delivery:Implemented,Merged,Released no:version AND -status:Abandoned)` | sorted by Priority | Everything that needs a person, and every ticket whose fields break a rule. |
| Versions | table | `has:version AND -type:Version` | grouped by Parent issue (the Version ticket, so a group reads "Version 0.7.0"); sorted by Version#, then Priority | What each version holds, with Delivery, Build and Resolution. Tickets only aimed at a version (no Version ticket yet) are in the "No parent issue" group, ordered by their Version#. |

## What Health catches

The first four conditions are the work that waits for a person: an open Attention flag, a ticket marked *Needs input*, a ticket at *Review*, and an open Alert. The rest are the cross-field rules of the standard (the guide on project structure, section 4.4), which the automation also flags:

| Condition | Rule it catches |
|---|---|
| `status:Completed no:resolution` | *Completed* has Resolution *Done*. |
| `is:open has:resolution` | An open ticket has no Resolution. |
| `is:open has:end-date` | An open ticket has no End date. |
| `is:closed has:waiting` | Waiting is only on open tickets. |
| `origin:Backfilled no:ref` | A backfilled ticket has its REF. |
| `status:Completed,Abandoned AND is:open` | A *Completed* or *Abandoned* ticket has its issue closed. |
| `is:closed AND -status:Completed,Abandoned AND -type:Version` | An issue is closed only at *Completed* or *Abandoned* (Version tickets are closed by the automation and have no Progress, so they are left out). |
| `status:Completed no:delivery AND -type:Version AND -type:Alert` | A *Completed* work ticket has a Delivery (*Merged* if files changed, *Implemented* if none did). Version and Alert tickets are not work tickets. |
| `delivery:Implemented,Merged,Released no:version AND -status:Abandoned` | Shipped work has a Version. The scheduled run gives a blank Version to an *Implemented* ticket, and the finalize step to a *Merged* one, so this row shows the gap until that happens, or a step that failed. An *Abandoned* ticket is left out, as the field rule leaves it out: the sweeps never attach it. |

## Notes

- A filter may join fields with `AND`, `OR` and parentheses. If a filter is rejected, rebuild it with the board's filter suggestions (type the field name and pick from the list) and correct it in the file.
- A view's grouping, columns and rows, and sorting can only be set when it is created, and the API cannot sort a new view by Created, Updated or Closed. So `views.py` creates a changed view again and then deletes the old one; GitHub never deletes the last view of a board.
- **By hand, once, when All is created:** set its sort to *Created, ascending* and turn *Show hierarchy* off (otherwise tickets are listed inside their Version ticket). The API cannot do either, `views.py` prints a reminder at the end of every run, and a view that is created again loses them.
- All lists the board's items in the order they were added, which is the ticket-number order. The API cannot set a sort by Created, Updated or Closed on a new view, so to make the order certain set the sort **Created, ascending** on All by hand in the web interface (the script ignores a sort by Created when it compares, and says so when it creates the view). A pull request takes a ticket number too: the automation puts it on the board as an item (`board_pull_requests.py`) so that All has no gap in the numbers, and the other views leave it out with `is:issue`.
- Planned, not yet created: a **Roadmap** view (a timeline from Start date to End date, actual dates only), kept in a ticket at *ToDo*.
