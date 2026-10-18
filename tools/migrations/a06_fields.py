"""A6: the field Fix and the values of Priority, Size and Risk (V0.10.0), and the field Kind (V0.13.0): fields the
board lacks are created, options a field lacks are added with every ticket's value kept."""
import fields
import migrations
import preflight

ID, SINCE, TITLE, GATE = "A6", "V0.10.0", "the fields and the values of the board", None


def required(ctx):
    return preflight.required_fields(ctx.type_source or "issue-type")


def options_lacking(ctx):
    found = {}

    for name, (kind, values) in required(ctx).items():
        have = ctx.board.fields.get(name)

        if have and have["type"] == kind and values:
            absent = [v for v in values if v not in have["options"]]

            if absent and name != "Status":
                found[name] = absent

    return found


def needed(ctx):
    if ctx.board is None:
        return False

    missing, _ = fields.plan(ctx.board, required(ctx))
    return bool(missing or options_lacking(ctx))


def plan(ctx):
    missing, _ = fields.plan(ctx.board, required(ctx))
    return ["create the field {} ({})".format(name, kind) for name, kind, _ in missing] + \
           ["add the values {} to {}".format(", ".join(v), n) for n, v in options_lacking(ctx).items()]


def apply(ctx, run):
    missing, _ = fields.plan(ctx.board, required(ctx))
    fields.create(run, ctx.project_client, ctx.board, missing)

    for name, absent in options_lacking(ctx).items():
        migrations.add_options(ctx, run, name, absent)
