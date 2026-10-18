"""L1: the legacy Version tickets (V0.15.0), converted into closed records (guide 03, section 5.2). Only with the flag
`convert_legacy`. A ticket that needs a decision is reported and left alone, so the step can still be needed after it
ran: the runner then lists `ctx.decisions` instead of treating it as a failure."""
import convert_legacy

ID, SINCE, TITLE, GATE = "L1", "V0.15.0", "the legacy Version tickets", "convert_legacy"


def needed(ctx):
    return "L1" in ctx.gap_ids


def plan(ctx):
    return ["convert the {} legacy Version ticket(s)".format(ctx.survey.get("board", {}).get("legacy_version_tickets", {}).get("total", 0))]


def apply(ctx, run):
    inner, decisions = convert_legacy.convert(ctx.repo_client, ctx.project_client, ctx.board, ctx.tickets, ctx.type_source or "issue-type",
                                              ctx.root, run.dry_run, include_open="include_open" in ctx.flags)
    run.log.extend(inner.log)
    ctx.decisions = decisions
