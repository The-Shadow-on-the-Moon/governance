# Board views

The saved views of the [Governance board](https://github.com/orgs/The-Shadow-on-the-Moon/projects/7), from the standard's guide on tickets and the board (sections 2.2 and 7.1). The API cannot create views, so the administrator creates them in the web interface (the board's view tabs, then the filter box). Keep this page in step with the board.

## Test tickets

Throwaway tickets and Version tickets made to test the automation carry the label `dummy`, and every working view below ends with `-label:dummy` so they never show among real work. The label is described in the standard's ticket fields reference. An optional view `label:dummy` lists only them.

## Daily views

| View | Filter | Shows |
|---|---|---|
| Mine | `assignee:@me` | Tickets assigned to me. |
| Alerts | `type:Alert -status:Completed,Abandoned` | Alerts not completed. |
| Attention | `attention:Watch,Caution,AtRisk` | Tickets flagged Watch, Caution or AtRisk. |
| Review | `status:Review` | Tickets awaiting verification. |
| Waiting | `waiting:"Needs input"` | Tickets marked Needs input. |

## Consistency views (for the regular board review)

| View | Filter | Problem it catches |
|---|---|---|
| Completed with no Resolution | `status:Completed no:resolution` | Completed must have Resolution Done. |
| Open with a Resolution | `is:open has:resolution` | Open tickets have no Resolution. |
| Open with an End date | `is:open has:"end date"` | Open tickets have no End date. |
| Waiting on a closed ticket | `is:closed has:waiting` | Waiting is only on open tickets. |
| Backfilled with no REF | `origin:Backfilled no:ref` | A backfilled ticket has its REF. |

If a filter is rejected, rebuild it with the board's filter suggestions (type the field name and pick from the list) and correct it here.
