# Appendix C: Ticket fields reference

Every ticket field with its values, what they mean, who sets them and when. The idea behind each field,
and the rules that tie the fields together, are in section 4 of *Project structure*. How the fields work
together over a ticket's life is in *Appendix E: Ticket model*.

**Where each field lives (GitHub).** Type is the native issue type, Area is a set of labels, and every
other field is a board field.

---

## Type

One value per ticket. Says what sort of ticket it is and why the change is made.

| Value | Meaning | Version bump |
|---|---|---|
| **Feature** | New capability that did not exist before. | sub |
| **Enhancement** | An improvement to something that already works: better performance, smarter behaviour, easier use. | sub |
| **Change** | A change to existing behaviour that is neither an improvement nor a fix: a new default, a different threshold, an adjustment someone asked for. | mod |
| **Bug** | Something that behaves differently from what was intended, and the fix for it. | mod |
| **Refactor** | Internal restructuring with no change in what the product does. | mod |
| **Task** | Work that does not change the product's behaviour: testing, analysing, building, releasing, writing documentation, and creating a new tool. | mod |
| **Version** | Bookkeeping ticket for one version. It does no work and never counts toward a bump. | none |
| **Alert** | An automatic check that needs a person to review something, such as a detected bypass or a stale planned version. It never counts toward a bump. | none |

Set by a person when the ticket is created; the automation sets it on Version and Alert tickets.

## Area

Several values per ticket. Says what kind of work the ticket involves. Descriptive only: it never affects
version numbers or any automation. At least one is suggested on a work ticket; none is allowed.

| Value | Meaning |
|---|---|
| `requirements` | Working out what is needed, with the people who need it. |
| `research` | Investigating options or unknowns: technologies, parts, approaches. |
| `design` | Deciding how it will be built, before building it (software, hardware, mechanical). |
| `implementation` | Producing the thing itself: code, circuit, enclosure, configuration of the product. |
| `assembly` | Putting physical parts together: electronics, mechanical parts, enclosures. |
| `testing` | Unit, functional and acceptance or QA testing. |
| `analysis` | Examining existing behaviour or data to understand it, without necessarily fixing it. |
| `debugging` | Finding and fixing the cause of a fault. |
| `documentation` | Wiki, readme, guides, comments and other written documentation. |
| `tool` | Developer tooling and scripts that support the work. |
| `process` | How the team works: git, changelog, versioning, hooks, the board, repository settings. |
| `config` | Settings that tune how the product behaves (feature flags, pin assignments, service definitions, intervals). |
| `content` | Data the product or its tests use (test fixtures, sample data, lookup tables, a database seed). |
| `build` | Build system, toolchain, compiling and releasing. |

The list is the same for every project. Adding a value is a change to the standard, not something a
project does on its own. Set by a person.

## The `dummy` label

Not an Area. A marker for a throwaway ticket or Version ticket made to test the automation (a trial of a
new step, a test of a rule). It is the only label besides the 14 Area labels.

| Label | Meaning |
|---|---|
| `dummy` | A throwaway ticket or version made to test the automation; left out of the board's working views. |

Set by a person when the test ticket is created. A test ticket is titled `DUMMY ...` and is closed as
*Abandoned*, with Resolution *Invalid*, when the test is over. Every saved view of the board except All excludes the
label (`-label:dummy`), so test tickets never appear among real work. It never affects version numbers or
any automation, and it is not part of Area.

## Origin and REF

**Origin** is blank for a ticket created in the normal flow.

| Value | Meaning | Example |
|---|---|---|
| *(blank)* | Created before or while the work was done. | Most tickets. |
| **Backfilled** | Created after the work was done, to replace a ticket-less placeholder in the changelog. | A quick fix logged as a placeholder and ticketed afterwards. |
| **Backdated** | Created to document history from before the process existed. | Tickets written when a project adopted the ticket system, covering earlier development. |

**REF** is a text field. For a Backfilled ticket it holds the placeholder token or tokens (separated by
commas, if one ticket replaces several entries) from the changelog. Blank otherwise. Both are set by a
person.

## Progress (Status)

Where the work is.

| Value | Meaning | Who sets it |
|---|---|---|
| **ToDo** | Accepted, not scheduled. | the person creating the ticket |
| **OnDeck** | Chosen to be worked on next. | a person |
| **InProgress** | Work has started. | a person; the automation also moves a ticket here when code for it is pushed (or merged) and it was still *ToDo* or *OnDeck* |
| **Review** | The developer (or an assistant) believes the work is done and wants it checked. May be a real review or a formality. | a person, never the automation |
| **Completed** | A human has verified the result. | a human only |
| **Suspended** | Set aside, expected to resume. | a person |
| **Abandoned** | Dropped, not expected to return. | a person |

The path is *ToDo, OnDeck, InProgress, Review, Completed*. *Suspended* and *Abandoned* are exits from any
open state. A reviewer may send work back from *Review* to *InProgress*. The automation never sets
*Review* or *Completed*, and never moves a ticket out of *Review*, *Completed*, *Abandoned* or
*Suspended*: it raises Attention instead. An assistant may set *Review* when work is done and
never *Completed*. The GitHub issue is closed only at *Completed* or *Abandoned*, by a person.

## Waiting

Blank by default.

| Value | Meaning |
|---|---|
| **Needs input** | The ticket is waiting for someone's feedback, an answer to a question, or a verification. |

Set by a person together with a comment that says what is needed and from whom. Applies to open tickets
only. Cleared when the answer arrives, and always when the ticket becomes *Completed* or *Abandoned*.

## Attention

Whether a work ticket's state has been looked at and is sound. Blank by default: nothing has affected it.
Version and Alert tickets have no Attention.

| Value | Colour | Meaning | Set by |
|---|---|---|---|
| *(blank)* | none | Nothing has affected it. | n/a |
| **Fine** | green | Looked at: nothing is wrong, or it was put right. | a person |
| **Acknowledged** | purple | Looked at: something has to be done, and it is handled elsewhere (another ticket, or this ticket moved back to *ToDo*, *OnDeck*, *InProgress* or *Suspended*). The comment says where. | a person |
| **Watch** | yellow | An open flag, the lowest level. | the automation |
| **Caution** | orange | An open flag, the middle level. | the automation |
| **AtRisk** | red | An open flag, the highest level. Reserved: no rule uses it yet. | the automation |

A level says how serious something looks, not what it is. The comment the automation adds says why.
These are the causes it uses today, with the level each starts at:

| Level | Raised when |
|---|---|
| **Caution** | New work arrives on a ticket that is *Completed*, *Abandoned*, *Review* or *Suspended* and whose earlier work was already pushed or delivered, recognised by a recorded Build older than the one being pushed (or by Delivery *Implemented*; never for its first push), or a field rule is broken (for example *Completed* without Resolution *Done*, an open ticket with a Resolution or an End date, Waiting on a closed ticket, a backfilled ticket with no REF, or an issue open or closed in the wrong state), or an *Implemented* ticket is aimed at a version that was passed (not finalized while a higher version is, so it could never be attached). |
| **Watch** | A ticket has had no activity at *Review* for a week, at *OnDeck* or *InProgress* for a month, or at *Suspended* for six months, or has been waiting for input for two weeks. |

Activity means a comment, a change to a field, or a new build that mentions the ticket; the automation's
own flag comments do not count.

A broken field rule is raised only if the ticket, meaning its issue or its board fields, has not changed
for five minutes, because fixing one takes several edits (two hours for the Delivery and Version rules, which a
person may be in the middle of completing).

The automation sets an open flag only on a ticket that is blank, *Fine* or *Acknowledged*, or that has a
lower open flag, and a higher level replaces a lower one. It never sets *Fine* or *Acknowledged* and never
lowers a level. A person may set any value by hand. Each raise adds one comment saying why (and which
build, for new work). A flag is raised when a situation begins and not again while it goes on: time
alone never raises it a second time. After a person closed it, it is raised again only if the situation
reappears (new work with a later build; a change of Progress followed by the ticket becoming stale there;
or a broken rule put right and then broken again). Setting the field changes nothing else on the ticket.

## Resolution

How a ticket ended. Blank while the ticket is open.

| Value | Meaning | Used with |
|---|---|---|
| **Done** | The work was done and verified. | *Completed* |
| **Duplicate** | The same as another ticket, which the comment links. | *Abandoned* |
| **Invalid** | Not a real problem, or based on a misunderstanding; includes a fault that cannot be reproduced. | *Abandoned* |
| **WontFix** | A valid request or fault that was decided not to act on. | *Abandoned* |
| **Superseded** | Replaced by a different approach or ticket: the work was real, but something else took its place. | *Abandoned* |
| **Obsolete** | No longer relevant because the thing it was about changed or was removed. | *Abandoned* |

Set by the person making the move to *Completed* or *Abandoned*. An abandoned ticket also gets a comment
that links any related ticket. Cleared when the ticket becomes open again.

## Delivery

Where the ticket's delivered work is: a fact about the work, independent of Progress and Resolution.

| Value | Meaning | Set by |
|---|---|---|
| *(blank)* | No code for this ticket exists on the hosting service, and its work is not yet in effect. | n/a |
| **Committed** | Optional personal marker: the work is committed locally and not yet pushed. | the developer, by hand only |
| **Pushed** | Code for the ticket is on a branch on the hosting service, not yet merged. | the automation, when a push contains a changelog entry for the ticket |
| **Merged** | The work is on `main`, in a finalized version. | the automation, at finalize |
| **Implemented** | The work is in effect and involved no file change (a setting, a secret, a check that was run). | a person, with the Version it belongs to; the automation then attaches the ticket to that version's ticket |
| **Released** | The version containing it has been declared a release. | the automation, when a release is cut |
| **Dropped** | The code or version was planned or pushed but will never be delivered. | the automation when a branch is abandoned; a person for a planned version |

Rules: *Committed* is never required and is overwritten by *Pushed* at the next push; nobody else can see a
local commit, so the team cannot rely on it. Delivery can move back: new work pushed on a ticket that is
*Merged*, *Implemented*, *Released* or *Dropped* returns it to *Pushed*. Hotfix tickets skip *Merged* and go straight to
*Released* when the hotfix is finished. When a release is cut, every ticket merged up to and including that
version becomes *Released* (a ticket merged or implemented), whatever its Progress or Resolution, unless newer work has moved its Delivery back to *Pushed*. A suspended branch is not dropped: its code
is kept, so *Pushed* stays. A ticket that produces no file change stays blank until its work is in effect. Then a person
sets *Implemented* and its Version. At every finalize and every scheduled run (three a day), and on a manual run, the automation attaches
*Implemented* tickets that no Version ticket has yet: a blank Version gets the version being finalized (at a scheduled run, the
latest finalized version), a finalized version is kept, and a later version waits. It never sets *Merged* or a Build on such a ticket.
A *Completed* work ticket must have a Delivery (*Merged* if files changed, *Implemented* if none did), and a ticket whose Delivery is
*Merged*, *Implemented* or *Released* must have a Version; the automation flags either gap with *Caution*. Version and Alert tickets
are not work tickets.

## Priority

How urgent, by consequence rather than by deadline. A ticket with no priority is treated as *Normal*. The
creator proposes it and the owner can change it at any time; *Critical* needs a comment saying why.

| Value | Meaning |
|---|---|
| **Critical** | Act now: a fault in released software, or an unverified bypass. Every Alert ticket is Critical. |
| **Urgent** | Must be in the current or next version; it blocks other work or a release. |
| **High** | Important; planned for the next few versions. |
| **Normal** | The default for ordinary work. |
| **Low** | Nice to have; do it when convenient. |
| **Wishlist** | An idea or backlog item with no commitment to do it. |

## Size

Estimated developer effort, from starting the work to moving it to *Review*, including testing and
documentation. It is effort, not calendar time, and it is not risk. A day means eight hours of effort.
Every work ticket gets a Size when it is created, and a Size can be corrected as understanding improves.

| Value | Estimated effort |
|---|---|
| **XS** | up to 1 hour |
| **S** | up to 4 hours |
| **M** | up to 2 days |
| **L** | up to 2 weeks |
| **XL** | more than 2 weeks |

## Risk

How likely the work is to go wrong. Size assumes the work succeeds; Risk says how likely that estimate is to
be badly wrong. Proposed by the creator and revised by the developer before the ticket moves to *Review*.
Informational only: it drives no rule or automation.

| Value | Meaning |
|---|---|
| **1 Very low** | Nothing depends on it. |
| **2 Low** | Isolated and easy to undo. |
| **3 Medium** | Some uncertainty. |
| **4 High** | Likely to go wrong: critical failure or major delay. |
| **5 Very high** | May not be feasible. |

## Version, Build and Version#

| Field | Holds | Set by |
|---|---|---|
| **Version** (text) | The version a ticket is aimed at and, once it ships, the version it really shipped in (`V2.1.0`, or `V2.1.0-HF1` for a hotfix). | a person may set it ahead of time; the automation overwrites it with the real version (for a backfilled ticket, the version where its placeholder appears). On an *Implemented* ticket the person's value stays |
| **Build** (text) | The latest build of the ticket: the most recent build stamp among the build blocks that mention it. | the automation |
| **Version#** (number) | A number derived from Version, used only to sort versions. It keeps a digit for the hotfix number. | the automation: at finalize, and on every scheduled run for any ticket that has a Version (also one that is only aimed at a version) and a blank or different Version# |

## Start date and End date

Dates the automation noticed, never planned ones. Set by the automation; a person may correct one by hand.

| Field | Set when | Rules |
|---|---|---|
| **Start date** | The automation first sees the ticket at *InProgress* or beyond. | Set only if blank: never overwritten, whether set earlier or by a person. |
| **End date** | The automation first sees the ticket *Completed* or *Abandoned*. | Set only if blank. Cleared by the automation when it sees the ticket open again, and set again the next time it ends. |

The automation cannot be told when a person changes Progress, so the dates are found by a sweep on every
run and a scheduled run; a date is accurate to the day it was noticed, in UTC. Version and Alert
tickets have no dates.

---

## Which fields apply to which tickets

| Field | Work ticket | Version ticket | Alert ticket |
|---|---|---|---|
| Type | the work Type | Version | Alert |
| Area | suggested | none | `process` |
| Origin, REF | as needed | none (Origin may stay Backdated on old ones) | blank |
| Progress | yes | none | yes, all moves manual |
| Waiting | yes | none | as for any ticket |
| Attention | yes | none | none |
| Resolution | yes | none | as for any ticket |
| Delivery | yes | *Merged*, *Released* or *Dropped* | none |
| Priority | Normal by default | none | Critical, always |
| Size | required at creation | none | set by the person who takes it |
| Risk | proposed by the creator | none | set by the person who takes it |
| Version, Build, Version# | yes | its own version; its last build | the version in which it was raised |
| Start date, End date | yes | none | none |
| Assignee | assigned to the person who starts the work | none | the person who pushed, for a bypass or a merge without changelog entries; none for stale planned versions |
