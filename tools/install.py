"""Install the standard's GitHub objects into a project that has none of them: labels, issue types, the board.

For a new project, or a first adoption (detected state: none). It checks first and creates only what is missing:

- the 14 Area labels and `dummy`, with the colors and descriptions of Appendix C (an existing label that differs is
  corrected; a label that is not on the list is kept unless `--delete-extra-labels` says to delete it, which is the
  person's decision: the labels a new repository starts with are such labels);
- the seven issue types, in an organization (a personal account has none: the Type is kept in the board field *Kind*
  and the variable `TYPE_SOURCE` is set to `field`). Issue types belong to the whole organization, so one that exists is
  never changed, only reported;
- the project board, linked to the repository, with the fields of the standard and its saved views. The options of
  the built-in field Status are written only for a board this run created, because replacing them on a board that
  has tickets could lose their values; for any other board the differences are listed.

Nothing is deleted except the extra labels asked for. It is a dry run unless `--apply` is given, because the
settings of a repository, an organization and a board are the administrator's. The token `PROJECT_TOKEN` (a secret of
the repository) and the repository settings of guide 10, section 3, are not made by this tool: they are listed as
manual steps. What it did is written to the state folder of the project.

    python tools/install.py <project-path> [--repo owner/name] [--apply] [--delete-extra-labels] [--board-title TITLE]
"""
import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kit_common  # noqa: E402
from kit_common import KitError, finalize  # noqa: E402

import audit_common  # noqa: E402
import fields  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402
import views  # noqa: E402
from github_api import GitHubError  # noqa: E402

REPO_IDS = "query($o:String!,$n:String!){repository(owner:$o,name:$n){id owner{id}}}"
CREATE_BOARD = ("mutation($o:ID!,$t:String!){createProjectV2(input:{ownerId:$o,title:$t})"
                "{projectV2{id number title}}}")
LINK_BOARD = "mutation($p:ID!,$r:ID!){linkProjectV2ToRepository(input:{projectId:$p,repositoryId:$r}){repository{id}}}"
STATUS_FIELD = ("query($id:ID!){node(id:$id){... on ProjectV2{field(name:\"Status\"){"
                "... on ProjectV2SingleSelectField{id options{id name}}}}}}")
SET_OPTIONS = ("mutation($f:ID!,$o:[ProjectV2SingleSelectFieldOptionInput!]!){updateProjectV2Field("
               "input:{fieldId:$f,singleSelectOptions:$o}){projectV2Field{... on ProjectV2SingleSelectField{id}}}}")


def listing(client, path):
    """Every item of a paged REST list."""
    found, page = [], 1

    while True:
        batch = client.request("GET", "{}{}per_page=100&page={}".format(path, "&" if "?" in path else "?", page)) or []
        found += batch

        if len(batch) < 100:
            return found

        page += 1


def ensure_labels(run, repo_client, delete_extra=False):
    """The 14 Area labels and `dummy`, as Appendix C says. Returns the names created or corrected."""
    wanted, _ = audit_common.appendix_c()
    found = {label["name"]: label for label in listing(repo_client, repo_client.repo_path("/labels"))}
    touched = []

    for name, (color, meaning) in sorted(wanted.items()):
        label = found.get(name)

        if label is None:
            run.do("create the label {} ({})".format(name, color), repo_client.request, "POST", repo_client.repo_path("/labels"),
                   {"name": name, "color": color, "description": meaning})
            touched.append(name)
        elif (label.get("color") or "").upper() != color or (label.get("description") or "") != meaning:
            run.do("correct the color and description of the label {}".format(name), repo_client.request, "PATCH",
                   repo_client.repo_path("/labels/{}".format(urllib.parse.quote(name, safe=""))),
                   {"color": color, "description": meaning})
            touched.append(name)

    for name in sorted(set(found) - set(wanted)):
        if delete_extra:
            run.do("delete the label {} (it is not on the list)".format(name), repo_client.request, "DELETE",
                   repo_client.repo_path("/labels/{}".format(urllib.parse.quote(name, safe=""))))
        else:
            run.log.append("the label {} is not on the list: kept (add --delete-extra-labels to delete it)".format(name))

    return touched


def ensure_types(run, repo_client, owner, owner_kind):
    """The seven issue types of an organization, or the variable TYPE_SOURCE=field of a personal account. Returns the
    source of the Type: `issue-type` or `field`."""
    if owner_kind != "Organization":
        if repo_client.get_variable(ticket_type.VARIABLE) != ticket_type.FIELD_SOURCE:
            run.do("set the repository variable {} to {} (a personal account has no issue types: the Type is kept in the "
                   "board field Kind)".format(ticket_type.VARIABLE, ticket_type.FIELD_SOURCE), repo_client.set_variable,
                   ticket_type.VARIABLE, ticket_type.FIELD_SOURCE)

        return ticket_type.FIELD_SOURCE

    _, wanted = audit_common.appendix_c()
    found = {item["name"]: item for item in listing(repo_client, "/orgs/{}/issue-types".format(owner))}

    for name in ticket_type.VALUES:
        color, meaning = wanted[name]
        item = found.get(name)

        if item is None:
            run.do("create the issue type {}".format(name), repo_client.request, "POST", "/orgs/{}/issue-types".format(owner),
                   {"name": name, "description": meaning, "color": color.lower(), "is_enabled": True})
        elif (item.get("description") or "") != meaning or (item.get("color") or "").upper() != color or not item.get("is_enabled", True):
            run.log.append("the issue type {} differs from Appendix C: kept, because issue types belong to the whole organization "
                           "(change it by hand if you agree)".format(name))

    extra = sorted(set(found) - set(ticket_type.VALUES))

    if extra:
        run.log.append("the issue types {} are not on the standard's list: kept".format(", ".join(extra)))

    return ticket_type.ISSUE_TYPE


def ensure_board(run, project_client, title):
    """The board linked to the repository, made and linked when there is none. Returns {"id", "number", "created"}
    (the id is None in a dry run that would make it)."""
    owner, name = project_client.repo.split("/", 1)
    nodes = project_client.graphql(preflight.LINKED_BOARDS, {"o": owner, "n": name})["repository"]["projectsV2"]["nodes"]

    if len(nodes) > 1:
        listing_text = ", ".join("#{} {}".format(n["number"], n["title"]) for n in nodes)
        raise KitError("the repository has {} linked boards ({}): choose one by setting the repository variable {}"
                       .format(len(nodes), listing_text, preflight.BOARD_VARIABLE))

    if nodes:
        run.log.append("the board #{} \"{}\" is linked: kept".format(nodes[0]["number"], nodes[0]["title"]))
        return {"id": nodes[0]["id"], "number": nodes[0]["number"], "created": False}

    ids = project_client.graphql(REPO_IDS, {"o": owner, "n": name})["repository"]
    made = run.do("create the board \"{}\" for {}".format(title, owner), project_client.graphql, CREATE_BOARD,
                  {"o": ids["owner"]["id"], "t": title})

    if made is None:
        run.log.append("link the new board to the repository")
        return {"id": None, "number": None, "created": True}

    board = made["createProjectV2"]["projectV2"]
    run.do("link the board #{} to the repository".format(board["number"]), project_client.graphql, LINK_BOARD,
           {"p": board["id"], "r": ids["id"]})
    return {"id": board["id"], "number": board["number"], "created": True}


def set_status_options(run, project_client, board_id):
    """Write the options of the built-in Status field. Only for a board this run made: it has no tickets, so no value
    can be lost. A board where the API refuses is told to the person, who sets them by hand."""
    kind, values = preflight.REQUIRED_FIELDS["Status"]
    options = [{"name": value, "color": preflight.OPTION_COLORS.get(value, "GRAY"), "description": preflight.OPTION_DESCRIPTIONS.get(value, "")}
               for value in values]

    try:
        node = project_client.graphql(STATUS_FIELD, {"id": board_id})["node"]["field"]
        run.do("write the options of the field Status ({})".format(", ".join(values)), project_client.graphql, SET_OPTIONS,
               {"f": node["id"], "o": options})
    except (GitHubError, KeyError, TypeError) as error:
        run.log.append("set the options of the field Status by hand (guide 10, section 6.1): the API refused ({})".format(error))


def default_board_loader(repo_client, project_client, dry_run):
    report = preflight.run(repo_client, project_client, store=not dry_run)
    return report.board or report.candidate, report.type_source  # the candidate is the board whose fields are not all there yet


def install(repo_client, project_client, repo, dry_run=True, delete_extra=False, title=None, load_board=default_board_loader):
    """Install what is missing. Returns the Runner."""
    run = finalize.Runner(dry_run)
    info = repo_client.request("GET", "/repos/{}".format(repo))
    owner = info["owner"]["login"]
    title = title or "Project board ({})".format(repo.split("/", 1)[1])
    ensure_labels(run, repo_client, delete_extra)
    source = ensure_types(run, repo_client, owner, (info.get("owner") or {}).get("type"))
    board_info = ensure_board(run, project_client, title)

    if board_info["id"] is None:
        run.log.append("the fields and the views are made once the board exists: run this again")
    else:
        if board_info["created"]:
            set_status_options(run, project_client, board_info["id"])

        board, source_now = load_board(repo_client, project_client, dry_run)

        if board is None:
            run.log.append("the board could not be read yet: run this again")
        else:
            missing, differing = fields.plan(board, preflight.required_fields(source_now or source))
            fields.create(run, project_client, board, missing)
            run.log.extend("by hand: {}".format(text) for text in differing)
            definition = views.for_source(views.load_definition(), source_now or source)
            synced = views.sync(project_client, board, definition, dry_run=dry_run)
            run.log.extend(synced.log)

    secrets = [s.get("name") for s in (repo_client.request("GET", repo_client.repo_path("/actions/secrets")) or {}).get("secrets", [])]

    if "PROJECT_TOKEN" not in secrets:
        run.log.append("by hand: store the project token as the Actions secret PROJECT_TOKEN (guide 10, section 4)")

    run.log.append("by hand, if not done: the repository settings of guide 10, section 3 (merge methods, branch protection, Actions)")
    return run


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])

    try:
        if not args or args[0].startswith("--"):
            raise KitError("usage: python tools/install.py <project-path> [--repo owner/name] [--apply] [--delete-extra-labels] "
                           "[--board-title TITLE]")

        root = os.path.abspath(args[0])
        repo = kit_common.option(args, "--repo") or audit_common.remote_repo(root)

        if not repo:
            raise KitError("the origin remote of {} is not a GitHub repository: say it with --repo owner/name".format(root))

        repo_client, project_client = kit_common.connect(repo)
        run = install(repo_client, project_client, repo, "--apply" not in args, "--delete-extra-labels" in args,
                      kit_common.option(args, "--board-title"))
    except (KitError, GitHubError) as error:
        print("install refused: {}".format(error))
        return 1

    kit_common.print_run(run)

    if not run.dry_run:
        print("log: {}".format(kit_common.save_log(root, "install", run)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
