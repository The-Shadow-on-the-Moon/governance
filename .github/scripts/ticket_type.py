"""Where the Type of a ticket comes from.

A project owned by an organization keeps the Type in the native issue type. A project owned by a personal
account has no issue types, and keeps it in a single-select board field named Kind, with the same eight
values. The repository variable TYPE_SOURCE says which (`issue-type` or `field`); when it is not set, the
source is `issue-type` for an organization and `field` for a personal account (the owner of the repository).
See the guide on the new-project bootstrap, section 5.1.

Reading never needs the variable: the issue type is used when the issue has one, and the Kind of its board
item otherwise. The variable decides what the preflight requires (the field Kind on the board), what
`fields.py` creates and how the Version and Alert tickets get their Type.
"""
from github_api import GitHubError

VARIABLE = "TYPE_SOURCE"
FIELD = "Kind"
ISSUE_TYPE, FIELD_SOURCE = "issue-type", "field"
SOURCES = (ISSUE_TYPE, FIELD_SOURCE)
VALUES = ["Feature", "Enhancement", "Change", "Bug", "Refactor", "Task", "Version", "Alert"]
# The colors and descriptions of the options of Kind (appendix C, the Type table), for fields.py.
COLORS = {"Feature": "PURPLE", "Enhancement": "GREEN", "Change": "BLUE", "Bug": "PINK", "Refactor": "ORANGE",
          "Task": "YELLOW", "Version": "GRAY", "Alert": "RED"}
DESCRIPTIONS = {
    "Feature": "New capability that did not exist before.",
    "Enhancement": "An improvement to something that already works: better performance, smarter behavior, easier use.",
    "Change": "A change to existing behavior that is neither an improvement nor a fix: a new default, a different threshold, "
              "an adjustment someone asked for.",
    "Bug": "Something that behaves differently from what was intended, and the fix for it.",
    "Refactor": "Internal restructuring with no change in what the product does.",
    "Task": "Work that does not change the product's behavior: testing, analyzing, building, releasing, writing documentation, "
            "and creating a new tool.",
    "Version": "Bookkeeping ticket for one version. It does no work and never counts toward a bump.",
    "Alert": "An automatic check that needs a person to review something, such as a detected bypass or a stale planned "
             "version. It never counts toward a bump.",
}
# GraphQL for the Kind of a board item, to add to the selection of an item.
SELECTION = 'kind:fieldValueByName(name:"Kind"){... on ProjectV2ItemFieldSingleSelectValue{name}} '


def of_node(node, content):
    """The Type of a board item: the issue type of its issue, or else its Kind."""
    return (content.get("issueType") or {}).get("name") or (node.get("kind") or {}).get("name")


def source(repository, client=None):
    """`issue-type` or `field`: the variable if it holds a valid value, else decided by the owner of the repository.

    `repository` is what GET /repos/{repo} returned (None when unknown, which means an organization)."""
    value = None
    if client is not None:
        try:
            value = (client.get_variable(VARIABLE) or "").strip()
        except GitHubError:
            value = None
    if value in SOURCES:
        return value
    owner_type = ((repository or {}).get("owner") or {}).get("type")
    return FIELD_SOURCE if owner_type == "User" else ISSUE_TYPE


def field_mode(client):
    """True when the Type of a ticket lives in the field Kind (the preflight gave the client a reader)."""
    return getattr(client, "kind_reader", None) is not None


def type_filter(client, issue_type):
    """The issues query for an issue type. With the field Kind there are no issue types and the filter would be refused:
    the caller picks the issues by their title."""
    return "" if field_mode(client) else f"&type={issue_type}"


def set_kind(run, project_client, board, item_id, kind, label):
    """Set the field Kind of a board item (a ticket the automation created, since a personal account has no issue types)."""
    run.do(f"{label}: set {FIELD} to {kind}", project_client.set_project_field, board.id, item_id,
           board.fields[FIELD]["id"], {"singleSelectOptionId": board.fields[FIELD]["options"][kind]})


def required_fields(source_name, select):
    """The board field the field source needs, in the form of preflight.REQUIRED_FIELDS."""
    return {FIELD: (select, list(VALUES))} if source_name == FIELD_SOURCE else {}


def reader(project_client):
    """A function number -> Kind of that issue's board item (None when there is none), for Client.issue_type."""
    owner, name = project_client.repo.split("/", 1)
    query = ("query($o:String!,$n:String!,$i:Int!){repository(owner:$o,name:$n){issue(number:$i){"
             "projectItems(first:20){nodes{" + SELECTION + "}}}}}")

    def read(number):
        data = project_client.graphql(query, {"o": owner, "n": name, "i": number})
        for item in (((data.get("repository") or {}).get("issue") or {}).get("projectItems") or {}).get("nodes") or []:
            value = (item.get("kind") or {}).get("name")
            if value:
                return value
        return None

    return read
