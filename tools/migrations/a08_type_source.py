"""A8: the Type in the field Kind for a personal account (V0.13.0): the variable TYPE_SOURCE is set to `field`.
The field Kind itself is made with the other fields (A6)."""
import install
import ticket_type

ID, SINCE, TITLE, GATE = "A8", "V0.13.0", "the Type source of a personal account", None


def needed(ctx):
    repository = ctx.survey.get("repository", {})
    return bool(repository.get("owner_type") and repository["owner_type"] != "Organization"
                and ticket_type.VARIABLE not in (ctx.survey.get("settings", {}).get("variables") or []))


def plan(ctx):
    return ["set the variable {} to {}".format(ticket_type.VARIABLE, ticket_type.FIELD_SOURCE)]


def apply(ctx, run):
    install.ensure_types(run, ctx.repo_client, ctx.survey["repository"]["owner"], ctx.survey["repository"]["owner_type"])
