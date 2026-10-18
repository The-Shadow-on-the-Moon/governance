"""A4: the label `dummy` (V0.7.0), and the other labels of Appendix C, created or corrected; none is deleted."""
import install

ID, SINCE, TITLE, GATE = "A4", "V0.7.0", "the labels of Appendix C", None


def needed(ctx):
    return "A4" in ctx.gap_ids


def plan(ctx):
    return ["create the label dummy (and any other label of Appendix C that is missing)"]


def apply(ctx, run):
    install.ensure_labels(run, ctx.repo_client)
