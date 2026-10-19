# Ticket model

How a ticket is built: the questions it answers, the field that answers each, and how a ticket moves from creation to release. The full text, with the reasons behind each choice, is [Appendix E: Ticket model](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-e-ticket-model.md). The values of every field are in [Appendix C: ticket fields](https://github.com/The-Shadow-on-the-Moon/governance/blob/main/guides/appendix-c-ticket-fields-reference.md), with the standard color of each value and of each Area label: a recommendation, which a project may change for its own board.

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
| **Resolution** | How did it end? | a person (the automation fills *Done* with *Completed*) |
| **Delivery** | Where is the delivered work? | the automation (a person sets *Committed* and *Implemented*) |
| **Priority**, **Size**, **Risk** | How urgent, how big, how risky? | a person |
| **Version**, **Build** | Which version and build? | a person may aim it, the automation sets the real values |
| **Start date**, **End date** | When did the work actually start and end? | the automation |
| **Fix** | Which of the rules that span fields do its fields break? | the automation |

Type lives in the native issue type, or, for a project owned by a personal account (which has no issue types), in the board field **Kind** with the same seven values. Judgment belongs to people and facts belong to the automation.

## The life of a work ticket

| Step | Progress | Delivery |
|---|---|---|
| Created | ToDo | blank |
| Chosen next | OnDeck | blank |
| Started | InProgress | blank |
| First push | InProgress | Pushed |
| Work done | Review | Pushed |
| Merged | Review | Merged |
| Verified by a human | Completed (issue closed; Resolution Done follows) | Merged |
| Release cut | Completed | Released |

Side paths: Waiting (*Needs input*) at any open step, sent back from Review to InProgress, Suspended, Abandoned (with a Resolution reason), Attention flags when something looks wrong, and Delivery *Implemented* for work that changes no file.

## Special tickets

- **Version tickets** are gone: a version has no ticket. Its changelog entry, the Version field of its tickets (the Versions view groups by it) and, for a release, its tag are the record. A ticket that still has the legacy type *Version* is converted into a closed record before the upgrade (`tools/convert_legacy.py`): the automation no longer knows the type.
- **Plans:** a Version on a ticket that is open and has not shipped is a plan, and it is advisory; the Plan view lists them, and one that was passed (at or below the highest finalized version) is listed in Fix.
- **Umbrella ticket:** an ordinary work ticket that groups the tickets of one piece of work as its sub-issues.
- **Alert ticket:** a check a person must do, raised for a bypass, a merge without changelog entries, or a changelog the automation could not read. It is Critical and every move is manual.

See also [Automation](Automation) for what the automation writes and when.
