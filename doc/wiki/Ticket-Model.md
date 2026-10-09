# Ticket model

How a ticket is built: the questions it answers, the field that answers each, and how a ticket moves from creation to release. The full text, with the reasons behind each choice, is [Appendix E: Ticket model](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-e-ticket-model.md). The values of every field are in [Appendix C: ticket fields](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md).

## The fields

Each field answers one question, and the fields are kept separate on purpose.

| Field | Question | Set by |
|---|---|---|
| **Type** | What sort of ticket is this, and why is the change being made? | a person (the automation for Version and Alert tickets) |
| **Area** | What kind of work does it involve? | a person |
| **Origin**, **REF** | Was the ticket created after the work, and which placeholder did it replace? | a person |
| **Progress** | Where is the work? | a person (the automation only advances *ToDo* and *OnDeck* to *InProgress*) |
| **Waiting** | Is it waiting for someone's input? | a person |
| **Attention** | Has the ticket's state been looked at, and is it sound? | the automation raises flags, a person closes them |
| **Resolution** | How did it end? | a person |
| **Delivery** | Where is the delivered work? | the automation (a person sets *Committed*, *Implemented* and *Dropped* on a planned Version ticket) |
| **Priority**, **Size**, **Risk** | How urgent, how big, how risky? | a person |
| **Version**, **Build**, **Version#** | Which version and build? | a person may aim it, the automation sets the real values |
| **Start date**, **End date** | When did the work actually start and end? | the automation |
| **Fix** | Which of the rules that span fields do its fields break? | the automation |

Judgment belongs to people and facts belong to the automation.

## The life of a work ticket

| Step | Progress | Delivery |
|---|---|---|
| Created | ToDo | blank |
| Chosen next | OnDeck | blank |
| Started | InProgress | blank |
| First push | InProgress | Pushed |
| Work done | Review | Pushed |
| Merged | Review | Merged |
| Verified by a human | Completed (Resolution Done, issue closed) | Merged |
| Release cut | Completed | Released |

Side paths: Waiting (*Needs input*) at any open step, sent back from Review to InProgress, Suspended, Abandoned (with a Resolution reason), Attention flags when something looks wrong, and Delivery *Implemented* for work that changes no file.

## Special tickets

- **Version ticket:** a bookkeeping record for one version, with no Progress. Its Delivery goes Merged, then Released (or Dropped for a planned version that never happened).
- **Alert ticket:** a check a person must do, raised for a bypass, a merge without changelog entries, or stale planned versions. It is Critical and every move is manual.

See also [Automation](Automation) for what the automation writes and when.
