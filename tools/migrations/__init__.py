"""The migration chain: one module for each thing a project must do to follow a newer version of the standard.

`doc/migration-inventory.md` lists the actions (A1 to A8, then the 0.15 series) and how to tell whether each is done.
A step is needed when the project *lacks the thing*, never because of a version label, so the chain works the same for a
project that follows one version, a mix of versions, or none. Each module has:

- `ID`, `SINCE` (the version of the standard that introduced the action), `TITLE`;
- `GATE`: None, or the name of a flag the person must give for the step to run, because the step changes something that
  cannot be undone with a restore file or that the administrator decides (the views, the removal of a field, the
  conversion of tickets); without the flag the step is only listed;
- `needed(ctx)`: True when the project lacks what the step brings (read from the survey, never guessed);
- `plan(ctx)`: the lines that say what the step would do;
- `apply(ctx, run)`: does it through `run.do`, so a dry run only logs; every destructive write keeps a restore file in
  the state folder first.

After a step is applied the runner reads the project again and the step must no longer be needed, or the chain stops.
"""
import importlib
import json
import os

import kit_common

ORDER = ("a01_baseline", "a02_delivery", "a04_label", "a06_fields", "f01_files", "m01_manifest", "a05_views",
         "a07_version_form", "a07_version_number", "a08_type_source", "l01_legacy")

OPTIONS = ("query($id:ID!,$n:String!){node(id:$id){... on ProjectV2{field(name:$n){"
           "... on ProjectV2SingleSelectField{id options{id name color description}}}}}}")
VALUES = ("query($id:ID!,$n:String!,$after:String){node(id:$id){... on ProjectV2{items(first:100,after:$after){"
          "pageInfo{hasNextPage endCursor} nodes{id v:fieldValueByName(name:$n){"
          "... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}")
SET_OPTIONS = ("mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){updateProjectV2Field("
               "input:{fieldId:$f,singleSelectOptions:$o}){projectV2Field{... on ProjectV2SingleSelectField{id}}}}")


class Context:
    """What a step reads and uses: the project, the clients, the board as the last read left it, the survey."""

    def __init__(self, root, repo, repo_client, project_client, standard_root, target, flags=(), survey_fn=None, board_fn=None):
        self.root, self.repo, self.repo_client, self.project_client = root, repo, repo_client, project_client
        self.standard_root, self.target, self.flags = standard_root, target, set(flags)
        self.survey_fn, self.board_fn = survey_fn, board_fn
        self.survey, self.board, self.type_source, self._tickets = {}, None, None, None
        self.table = None  # the fingerprints of the standard, set by the caller that has them
        self.refresh()

    def refresh(self):
        """Read the project again."""
        self.survey = self.survey_fn() if self.survey_fn else {}

        if self.board_fn:
            self.board, self.type_source = self.board_fn()

        self._tickets = None

    @property
    def gap_ids(self):
        return {gap["id"] for gap in self.survey.get("gaps", [])}

    @property
    def tickets(self):
        if self._tickets is None:
            import conditions
            self._tickets = conditions.board_tickets(self.project_client, self.board)

        return self._tickets


def steps():
    """The step modules in the order of the chain."""
    return [importlib.import_module("migrations." + name) for name in ORDER]


def item_values(ctx, name):
    """{item id: option name} of a single select field for every item of the board."""
    found, after = {}, None

    while True:
        page = ctx.project_client.graphql(VALUES, {"id": ctx.board.id, "n": name, "after": after})["node"]["items"]

        for node in page["nodes"]:
            if node.get("v"):
                found[node["id"]] = node["v"]["name"]

        if not page["pageInfo"]["hasNextPage"]:
            return found

        after = page["pageInfo"]["endCursor"]


def add_options(ctx, run, name, wanted):
    """Add the options of `wanted` that the single select field `name` lacks.

    GitHub gives every option a new id when the option list is written, which clears the value of every ticket. So the
    value of every item is read first and kept in a restore file, the list is written (the existing options with their
    color and description, then the new ones), and every value is set again by name with the new ids. Returns the
    names added."""
    field = ctx.board.fields[name]
    missing = [value for value in wanted if value not in field["options"]]

    if not missing:
        return []

    import preflight

    run.log.append("{}: add the options {} (the value of every ticket is kept and set again)".format(name, ", ".join(missing)))

    if run.dry_run:
        return missing

    before = item_values(ctx, name)

    with open(kit_common.state_path(ctx.root, "restore-{}.json".format(name)), "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"field": name, "values": before}, handle, indent=1)
        handle.write("\n")

    node = ctx.project_client.graphql(OPTIONS, {"id": ctx.board.id, "n": name})["node"]["field"]
    options = [{"name": o["name"], "color": o.get("color") or "GRAY", "description": o.get("description") or ""} for o in node["options"]]
    options += [{"name": v, "color": preflight.OPTION_COLORS.get(v, "GRAY"), "description": preflight.OPTION_DESCRIPTIONS.get(v, "")}
                for v in missing]
    ctx.project_client.graphql(SET_OPTIONS, {"f": node["id"], "o": options})
    ctx.refresh()
    new = ctx.board.fields[name]

    for item, value in before.items():
        ctx.project_client.set_project_field(ctx.board.id, item, new["id"], {"singleSelectOptionId": new["options"][value]})

    after = item_values(ctx, name)

    if after != before:
        raise kit_common.KitError("the values of {} were not all restored ({} before, {} after): the restore file is in the state folder"
                                  .format(name, len(before), len(after)))

    return missing
