"""A2: the Delivery option Implemented (V0.4.0). The value of every ticket is kept (see `add_options`)."""
import migrations

ID, SINCE, TITLE, GATE = "A2", "V0.4.0", "the Delivery option Implemented", None


def needed(ctx):
    return "A2" in ctx.gap_ids


def plan(ctx):
    return ["add the option Implemented to the field Delivery"]


def apply(ctx, run):
    migrations.add_options(ctx, run, "Delivery", ["Implemented"])
