# Board views

The saved views of the [Governance board](https://github.com/orgs/The-Shadow-on-the-Moon/projects/7), from the standard's guide on tickets and the board (sections 2.2 and 7.1). They are defined in `.github/views.json` and created by `.github/scripts/views.py` (see [Automation](Automation)), so every project has the same ones. To change a view, change the file and run the script; keep this page in step with the file (a test checks that every view and filter in the file is on this page).

Every view also ends with `AND -label:dummy`, which the script adds, so throwaway tickets and Version tickets made to test the automation (label `dummy`, described in the standard's ticket fields reference) never show among real work.

## The views, in tab order

| View | Layout | Filter | Grouping and sorting | Shows |
|---|---|---|---|---|
| All | table | none | sorted by Version# (latest first), then Priority | Every ticket with all its fields, for finding anything and for audit. |
| Backlog | board | `status:ToDo,OnDeck,Suspended` | columns by Status; sorted by Priority | The waiting and set-aside work, the most urgent first. |
| Board | board | `is:open AND -type:Version AND -status:ToDo,Suspended` | columns by Status, rows by Version; sorted by Priority | The active work (OnDeck, InProgress, Review) with a row for each Version. |
| Health | table | `attention:Watch,Caution,AtRisk OR waiting:"Needs input" OR status:Review OR (type:Alert AND is:open) OR (status:Completed no:resolution) OR (is:open has:resolution) OR (is:open has:end-date) OR (is:closed has:waiting) OR (origin:Backfilled no:ref) OR (status:Completed,Abandoned AND is:open) OR (is:closed AND -status:Completed,Abandoned AND -type:Version)` | sorted by Priority | Everything that needs a person, and every ticket whose fields break a rule. |
| Versions | table | `has:version AND -type:Version` | grouped by Version#; sorted by Priority | What each version holds, with Delivery, Build and Resolution. |

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

## Notes

- A filter may join fields with `AND`, `OR` and parentheses. If a filter is rejected, rebuild it with the board's filter suggestions (type the field name and pick from the list) and correct it in the file.
- A view's grouping, columns and rows, and sorting can only be set when it is created, and the API cannot sort a new view by Created, Updated or Closed. So `views.py` creates a changed view again and then deletes the old one; GitHub never deletes the last view of a board.
- Planned, not yet created: a **Roadmap** view (a timeline from Start date to End date, actual dates only), kept in a ticket at *ToDo*.
