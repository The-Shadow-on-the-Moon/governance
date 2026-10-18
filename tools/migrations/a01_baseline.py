"""A1: the installation baseline (V0.3.0): a board linked to the repository with the fields of the standard, the issue
types, the labels. Uses the install module, which creates only what is missing."""
import install

ID, SINCE, TITLE, GATE = "A1", "V0.3.0", "the board, the labels and the issue types", None


def needed(ctx):
    return "A1" in ctx.gap_ids and not ctx.survey.get("board", {}).get("found")


def plan(ctx):
    return ["install what is missing: labels, issue types, the board with its fields and views (tools/install.py)"]


def apply(ctx, run):
    run.log.extend(install.install(ctx.repo_client, ctx.project_client, ctx.repo, run.dry_run).log)
