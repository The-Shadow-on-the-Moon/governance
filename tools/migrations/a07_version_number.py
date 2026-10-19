"""A7, removal of the field Version# (V0.11.0). Run after the views no longer use it, and only with the flag
`delete_version_number`, because a deleted field cannot be restored: its values are saved in the state folder first."""
import json

import kit_common

ID, SINCE, TITLE, GATE = "A7b", "V0.11.0", "the removal of the field Version#", "delete_version_number"
DELETE = "mutation($f:ID!){deleteProjectV2Field(input:{fieldId:$f}){clientMutationId}}"
VALUES = ("query($id:ID!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){pageInfo{hasNextPage endCursor} "
          "nodes{id v:fieldValueByName(name:\"Version#\"){... on ProjectV2ItemFieldNumberValue{number} "
          "... on ProjectV2ItemFieldTextValue{text}}}}}}}")


def needed(ctx):
    return ctx.board is not None and "Version#" in ctx.board.fields


def plan(ctx):
    return ["save the values of Version# and delete the field"]


def export(ctx):
    found, after = {}, None

    while True:
        page = ctx.project_client.graphql(VALUES, {"id": ctx.board.id, "after": after})["node"]["items"]

        for node in page["nodes"]:
            if node.get("v"):
                found[node["id"]] = node["v"]

        if not page["pageInfo"]["hasNextPage"]:
            return found

        after = page["pageInfo"]["endCursor"]


def apply(ctx, run):
    if not run.dry_run:
        with open(kit_common.state_path(ctx.root, "restore-Version-number.json"), "w", encoding="utf-8", newline="\n") as handle:
            json.dump(export(ctx), handle, indent=1)
            handle.write("\n")

    run.do("delete the field Version#", ctx.project_client.graphql, DELETE, {"f": ctx.board.fields["Version#"]["id"]})
