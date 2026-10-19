"""A5: the saved views (V0.8.0, changed in V0.10.0, V0.11.0 and V0.15.0), made to match `.github/views.json`. The views
of a board are the administrator's, so this runs only with the flag `views`; a view not in the file is kept."""
import views

ID, SINCE, TITLE, GATE = "A5", "V0.8.0", "the saved views of the board", "views"


def needed(ctx):
    return "A5" in ctx.gap_ids


def plan(ctx):
    board = ctx.survey.get("board", {}).get("views", {})
    return ["create or replace the views (missing: {}; different: {})".format(", ".join(board.get("missing", [])) or "none",
                                                                             ", ".join(board.get("different", [])) or "none")]


def apply(ctx, run):
    definition = views.for_source(views.load_definition(), ctx.type_source or "issue-type")
    run.log.extend(views.sync(ctx.project_client, ctx.board, definition, dry_run=run.dry_run).log)
