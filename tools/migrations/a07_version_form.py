"""A7, values: the Version of every ticket in the board form `V000.010.001` (V0.11.0). Done after the files are copied."""
import version_format

ID, SINCE, TITLE, GATE = "A7", "V0.11.0", "the form of the Version of the tickets", None


def needed(ctx):
    forms = ctx.survey.get("board", {}).get("version_forms", {})
    return bool(forms.get("short") or forms.get("other"))


def plan(ctx):
    return ["write the Version of the tickets that are not in the board form"]


def apply(ctx, run):
    version_format.sweep(run, ctx.project_client, ctx.board)
