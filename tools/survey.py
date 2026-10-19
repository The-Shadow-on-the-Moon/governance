"""Survey a project: read its real state, change nothing, assume nothing.

The first step of an adoption or an upgrade. It gathers the facts the plan is built from, and anything it cannot read is
recorded as `unknown` with the manual check for the administrator instead of being guessed:

- the repository: remote, default branch, visibility, owner, branches, tags by namespace, the history shape, open pull
  requests, the clean state of the tree;
- the files: which version of the standard each automation file comes from (the fingerprints of the standard's own
  history), the standard the manifest claims, a placeholder in a project that is not the standard's repository, the hooks,
  the workflows, the project's own `AGENTS.md`, the changelog;
- the settings the token can read: Actions, rulesets, protection, variables and secrets by name (never a value);
- the organization: its issue types and its other repositories with the standard they follow;
- the board: fields and options, views against `.github/views.json`, tickets by type, the legacy Version tickets, the
  forms of Version, and what the first refresh of the new files would do (stale plans, Resolution *Done* to fill);
- an open hotfix branch, a running workflow, or anything else that blocks an upgrade.

From these it names the detected state (none, a version, mixed, modified or unsupported) and the gaps: what a project at
that state lacks, each tied to the version that introduced it (`doc/migration-inventory.md`). The output goes to the
state folder of the project (`survey.json` and `survey.md`), never into the repository.

    python tools/survey.py <project-path> [--repo owner/name] [--no-fleet] [--offline]

`--offline` reads only the files and git (no `gh`, no network). Needs the full history of the standard it runs from.
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kit_common  # noqa: E402
from kit_common import KitError  # noqa: E402

import audit_common  # noqa: E402
import build_fingerprints  # noqa: E402
import changelog  # noqa: E402
import check_manifest  # noqa: E402
import conditions  # noqa: E402
import preflight  # noqa: E402
import ticket_type  # noqa: E402
import versions  # noqa: E402
import views  # noqa: E402
from github_api import GitHubError  # noqa: E402

KIT_FILES = ("ADOPT-OR-UPDATE-GOVERNANCE.md", "doc/adoption-plan.md")  # files of the kit itself, never a reason to block
EMBEDDED = "doc/governance"  # where a project carries the standard: a git submodule (only the standard's own repository does not)
BOARD_FORM = re.compile(r"^V\d{3}\.\d{3}\.\d{3}(-HF\d)?$")
SHORT_FORM = re.compile(r"^V\d+\.\d+\.\d+(-HF\d)?$")
NAMESPACES = ("archived", "suspended", "abandoned", "released", "test")
HOOK_MANAGERS = (".husky", ".pre-commit-config.yaml", "lefthook.yml", ".lefthook.yml")
ORIGINAL_FIELDS = ("Status", "Origin", "Waiting", "Attention", "Resolution", "Delivery", "Priority", "Size", "Risk", "REF",
                   "Version", "Build", "Start date", "End date")  # the fields of V0.3.0, without the later Fix and the removed Version#


def git(root, *args):
    return audit_common.git(root, *args)


def facts_repository(root, repo, gh):
    facts = {"repo": repo, "unknown": []}
    code, branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    facts["current_branch"] = branch if code == 0 else None
    code, status = git(root, "status", "--porcelain", "-uall")
    changed = [line for line in status.splitlines() if line[3:].strip().strip('"') not in KIT_FILES + (EMBEDDED,)] if code == 0 else []
    facts["clean_tree"] = not changed if code == 0 else None  # the instruction file, the plan and the pin of the submodule are the kit's own, not changes
    code, shallow = git(root, "rev-parse", "--is-shallow-repository")
    facts["shallow"] = shallow == "true" if code == 0 else None
    code, out = git(root, "for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes")
    refs = out.split("\n") if code == 0 and out else []
    branches = sorted({r.split("/", 3)[-1] if r.startswith("refs/remotes/") else r[len("refs/heads/"):] for r in refs
                       if not r.endswith("/HEAD")} - {"HEAD"})
    facts["branches"] = branches
    facts["hotfix_branches"] = [b for b in branches if b.startswith("hotfix-")]
    code, out = git(root, "tag")
    tags = out.split("\n") if code == 0 and out else []
    facts["tags"] = {space: sum(1 for t in tags if t.startswith(space + "/")) for space in NAMESPACES}
    facts["tags"]["other"] = sum(1 for t in tags if t.split("/")[0] not in NAMESPACES)
    facts["released_tags"] = sorted(t for t in tags if t.startswith("released/"))
    code, out = git(root, "log", "--first-parent", "--format=%P", "-n", "400")
    parents = out.split("\n") if code == 0 and out else []
    facts["history"] = {"commits_examined": len(parents), "merge_commits": sum(1 for p in parents if len(p.split()) > 1)}
    code, out = git(root, "log", "--format=%s", "-n", "400")
    subjects = out.split("\n") if code == 0 and out else []
    facts["history"]["type_prefixes"] = sum(1 for s in subjects if re.match(r"^(feat|fix|chore|docs|refactor|test)(\(.*\))?!?:", s))

    if gh is None:
        facts["unknown"].append("the repository settings were not read (offline)")
        return facts

    status, info = gh("repos/{}".format(repo))

    if status != 200 or not isinstance(info, dict):
        facts["unknown"].append("the repository {} could not be read (status {}): sign in with `gh auth login`".format(repo, status))
        return facts

    facts.update({"default_branch": info.get("default_branch"), "private": info.get("private"), "owner": (info.get("owner") or {}).get("login"),
                  "owner_type": (info.get("owner") or {}).get("type"), "archived": info.get("archived"), "has_wiki": info.get("has_wiki"),
                  "merge_commit_allowed": info.get("allow_merge_commit"), "squash_allowed": info.get("allow_squash_merge"),
                  "rebase_allowed": info.get("allow_rebase_merge")})
    status, pulls = gh("repos/{}/pulls?state=open&per_page=100".format(repo))
    facts["open_pull_requests"] = len(pulls) if status == 200 and isinstance(pulls, list) else None
    return facts


def facts_embedded(root):
    """The standard carried by the project as a submodule at `doc/governance`: whether it is there, its pinned commit and
    version, the commit that is checked out, a shallow or unclean checkout, and whether the pin and the manifest agree."""
    facts = {"path": EMBEDDED, "present": False, "unknown": []}
    code, out = git(root, "ls-files", "-s", "--", EMBEDDED)
    line = out.splitlines()[0] if code == 0 and out else ""
    folder = os.path.join(root, *EMBEDDED.split("/"))

    if not line.startswith("160000"):
        if os.path.isdir(os.path.join(folder, "guides")):
            facts["unknown"].append("{} holds a copy of the standard that is not a git submodule: make it one (git submodule add) so the "
                                    "pin can be moved".format(EMBEDDED))

        return facts

    facts.update({"present": True, "pinned": line.split()[1]})
    code, out = git(root, "config", "-f", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$")
    name = next((entry.split()[0][len("submodule."):-len(".path")] for entry in out.splitlines() if entry.split()[-1:] == [EMBEDDED]), None) if code == 0 else None

    if name:
        code, url = git(root, "config", "-f", ".gitmodules", "--get", "submodule.{}.url".format(name))
        facts["url"] = url if code == 0 else None
        code, shallow = git(root, "config", "-f", ".gitmodules", "--get", "submodule.{}.shallow".format(name))
        facts["gitmodules_shallow"] = code == 0 and shallow == "true"

    facts["initialized"] = os.path.exists(os.path.join(folder, ".git"))

    if not facts["initialized"]:
        return facts

    code, out = git(folder, "rev-parse", "HEAD")
    facts["checked_out"] = out if code == 0 else None
    code, out = git(folder, "rev-parse", "--is-shallow-repository")
    facts["shallow"] = out == "true" if code == 0 else None
    code, out = git(folder, "status", "--porcelain")
    facts["clean"] = not out if code == 0 else None
    code, out = git(folder, "show", "{}:{}".format(facts["pinned"], check_manifest.MANIFEST.replace(os.sep, "/")))

    try:
        facts["pinned_standard"] = json.loads(out).get("standard") if code == 0 else None
    except ValueError:
        facts["pinned_standard"] = None

    if facts["pinned_standard"] is None:
        facts["unknown"].append("the version of the pinned commit {} of {} could not be read (is it fetched?)".format(facts["pinned"][:8], EMBEDDED))

    return facts


def facts_files(root, table):
    facts = {"unknown": []}
    exists = lambda *parts: os.path.exists(os.path.join(root, *parts))  # noqa: E731
    manifest_path = os.path.join(root, check_manifest.MANIFEST)
    manifest = None

    if os.path.isfile(manifest_path):
        try:
            manifest = check_manifest.load(manifest_path)
        except (OSError, ValueError):
            facts["unknown"].append("the manifest cannot be read")

    facts["manifest_standard"] = (manifest or {}).get("standard")
    facts["manifest_files"] = len((manifest or {}).get("files", {}))
    is_standard = os.path.abspath(root) == os.path.abspath(kit_common.STANDARD)
    facts["placeholder_in_a_project"] = bool(facts["manifest_standard"] == check_manifest.PLACEHOLDER and not is_standard)

    if table is None:
        facts["identity"] = {"state": "unknown", "versions": [], "closest": []}
        facts["unknown"].append("the fingerprints of the standard could not be built (needs its full history)")
    else:
        found = build_fingerprints.identify(root, table)
        facts["identity"] = {"state": found["state"], "versions": found["versions"], "closest": found["closest"],
                             "files": found["files"]}

    facts.update({"agents": exists("AGENTS.md"), "changelog": exists("CHANGELOG.md"), "doc_wiki": exists("doc", "wiki"),
                  "githooks": exists(".githooks"), "versioning_workflow": exists(".github", "workflows", "versioning.yml"),
                  "reenable_workflow": exists(".github", "workflows", "reenable-schedule.yml"),
                  "wiki_sync_workflow": exists(".github", "workflows", "wiki-sync.yml"),
                  "views_file": exists(".github", "views.json"), "hook_managers": [m for m in HOOK_MANAGERS if exists(m)]})
    code, hooks = git(root, "config", "core.hooksPath")
    facts["hooks_path"] = hooks.strip() if code == 0 and hooks.strip() else None
    text = ""

    if facts["agents"]:
        with open(os.path.join(root, "AGENTS.md"), encoding="utf-8", errors="replace") as handle:
            text = handle.read()

    facts["agents_lines"] = len(text.splitlines())
    facts["changelog_state"] = None

    if facts["changelog"]:
        try:
            with open(os.path.join(root, "CHANGELOG.md"), encoding="utf-8") as handle:
                sections = changelog.parse(handle.read())
            finals = [s.version for s in sections if s.kind == "final"]
            facts["changelog_state"] = {"finalized": len(finals), "highest": str(max(finals, key=lambda v: v.number())) if finals else None,
                                        "open_heading": any(s.kind == "wip" for s in sections)}
        except (ValueError, OSError) as error:
            facts["changelog_state"] = {"error": str(error)}

    return facts


def facts_settings(repo, gh):
    facts = {"unknown": []}

    if gh is None:
        facts["unknown"].append("the settings were not read (offline)")
        return facts

    def read(path):
        status, data = gh("repos/{}/{}".format(repo, path))
        return data if status == 200 else None

    actions = read("actions/permissions")
    facts["actions_enabled"] = actions.get("enabled") if isinstance(actions, dict) else None
    workflow = read("actions/permissions/workflow")
    facts["workflow_default_permission"] = workflow.get("default_workflow_permissions") if isinstance(workflow, dict) else None
    secrets = read("actions/secrets")
    facts["secrets"] = sorted(s.get("name") for s in secrets.get("secrets", [])) if isinstance(secrets, dict) else None
    variables = read("actions/variables")
    facts["variables"] = sorted(v.get("name") for v in variables.get("variables", [])) if isinstance(variables, dict) else None
    rulesets = read("rulesets")
    facts["rulesets"] = [r.get("name") for r in rulesets] if isinstance(rulesets, list) else None
    status, protection = gh("repos/{}/branches/main/protection".format(repo))
    facts["main_protected"] = True if status == 200 else (False if status == 404 else None)

    for key, label in (("actions_enabled", "Actions"), ("secrets", "the secrets"), ("variables", "the variables"),
                       ("rulesets", "the rulesets")):
        if facts[key] is None:
            facts["unknown"].append("{} could not be read: check it by hand (needs administration access)".format(label))

    facts["unknown"].append("the built-in workflows of the board (guide 10, section 6.1) cannot be read: check them by hand")
    return facts


def facts_organization(owner, owner_type, gh, fleet=True):
    facts = {"unknown": [], "issue_types": None, "repositories": None}

    if gh is None or owner_type != "Organization":
        return facts

    status, found = gh("orgs/{}/issue-types".format(owner))
    facts["issue_types"] = sorted(t.get("name") for t in found) if status == 200 and isinstance(found, list) else None

    if facts["issue_types"] is None:
        facts["unknown"].append("the organization's issue types could not be read")

    if not fleet:
        return facts

    status, repos = gh("orgs/{}/repos?per_page=100&type=all".format(owner))

    if status != 200 or not isinstance(repos, list):
        facts["unknown"].append("the organization's repositories could not be listed")
        return facts

    facts["repositories"] = []

    for item in repos[:60]:
        status, data = gh("repos/{}/contents/{}".format(item["full_name"], check_manifest.MANIFEST.replace(os.sep, "/")))
        standard = None

        if status == 200 and isinstance(data, dict) and data.get("encoding") == "base64":
            import base64
            try:
                standard = json.loads(base64.b64decode(data["content"]).decode("utf-8")).get("standard")
            except (ValueError, KeyError):
                standard = "unreadable"

        facts["repositories"].append({"name": item["full_name"], "standard": standard, "archived": item.get("archived", False)})

    return facts


def classify_version(text):
    text = (text or "").strip()

    if not text:
        return "blank"

    return "board" if BOARD_FORM.match(text) else "short" if SHORT_FORM.match(text) else "other"


def facts_board(source, highest):
    """The board facts from `source` (see `default_board_source`)."""
    facts = {"unknown": [], "found": False}

    if source is None:
        facts["unknown"].append("the board was not read (offline)")
        return facts

    data = source()

    if data.get("error"):
        facts["unknown"].append(data["error"])
        return facts

    if not data.get("board"):
        return facts

    tickets = data.get("tickets", [])
    board = data["board"]
    fields = board.get("fields", {})
    facts.update({"found": True, "number": board.get("number"), "title": board.get("title"), "type_source": data.get("type_source"),
                  "fields": {name: {"type": f["type"], "options": sorted(f.get("options", {}))} for name, f in fields.items()}})
    by_type = {}

    for ticket in tickets:
        by_type[ticket["type"] or "none"] = by_type.get(ticket["type"] or "none", 0) + 1

    facts["tickets"] = {"total": len(tickets), "by_type": by_type}
    facts["version_forms"] = {}

    for ticket in tickets:
        form = classify_version(ticket["version"])
        facts["version_forms"][form] = facts["version_forms"].get(form, 0) + 1

    legacy = [t for t in tickets if t["type"] == "Version"]
    facts["legacy_version_tickets"] = {"total": len(legacy), "open": sum(1 for t in legacy if t["state"] == "OPEN"),
                                       "open_without_delivery": sum(1 for t in legacy if t["state"] == "OPEN" and not t["delivery"])}
    stale = 0

    if highest is not None:
        stale = sum(1 for t in tickets if conditions.stale_plan(t, highest))

    facts["preview"] = {
        "stale_plans": stale,
        "stale_plans_checked": highest is not None,
        "resolution_done_to_fill": sum(1 for t in tickets if t["status"] == "Completed" and not t["resolution"]),
        "resolution_done_to_clear": sum(1 for t in tickets if t["status"] and t["status"] != "Completed" and t["resolution"] == "Done"),
        "fix_flags_now": sum(1 for t in tickets if t["fix"]),
    }
    definition = views.for_source(views.load_definition(), data.get("type_source") or ticket_type.ISSUE_TYPE)
    current = {v["name"]: v for v in data.get("views", [])}
    facts["views"] = {"expected": [e["name"] for e in definition], "missing": [e["name"] for e in definition if e["name"] not in current],
                      "different": [e["name"] for e in definition if e["name"] in current
                                    and views.differences(views.desired_state(e), current[e["name"]])]}
    facts["views"]["extra"] = sorted(set(current) - {e["name"] for e in definition})
    return facts


def gaps(files, board, labels_have_dummy, owner_type):
    """What a project at this state lacks, each tied to the version that introduced it (doc/migration-inventory.md).
    [{"id", "since", "text"}], in the order of the inventory."""
    found = []
    fields = (board or {}).get("fields", {})
    has_board = bool((board or {}).get("found"))

    def add(ident, since, text):
        found.append({"id": ident, "since": since, "text": text})

    if not has_board:
        add("A1", "V0.3.0", "there is no board linked to the repository, or it could not be read")
    else:
        missing = [name for name in ORIGINAL_FIELDS if name not in fields]

        if missing:
            add("A1", "V0.3.0", "the board lacks the fields {}".format(", ".join(missing)))

        if "Implemented" not in fields.get("Delivery", {}).get("options", ["Implemented"]):
            add("A2", "V0.4.0", "the field Delivery lacks the option Implemented")

        if "Fix" not in fields:
            add("A6", "V0.10.0", "the board lacks the field Fix")

        for name, wanted in (("Priority", preflight.REQUIRED_FIELDS["Priority"][1]), ("Size", preflight.REQUIRED_FIELDS["Size"][1]),
                             ("Risk", preflight.REQUIRED_FIELDS["Risk"][1])):
            have = fields.get(name, {}).get("options")

            if have is not None and [v for v in wanted if v not in have]:
                add("A6", "V0.10.0", "the field {} lacks the values {}".format(name, ", ".join(v for v in wanted if v not in have)))

        forms = board.get("version_forms", {})

        if "Version#" in fields:
            add("A7", "V0.11.0", "the board still has the field Version#")

        if forms.get("short") or forms.get("other"):
            add("A7", "V0.11.0", "{} ticket(s) have a Version that is not in the board form V000.010.001".format(
                forms.get("short", 0) + forms.get("other", 0)))

        if board.get("type_source") == ticket_type.FIELD_SOURCE and ticket_type.FIELD not in fields:
            add("A8", "V0.13.0", "the Type is kept in the field Kind and the board lacks it")

        v = board.get("views", {})

        if v.get("missing") or v.get("different"):
            add("A5", "V0.8.0", "the views differ from .github/views.json (missing: {}; different: {})".format(
                ", ".join(v.get("missing", [])) or "none", ", ".join(v.get("different", [])) or "none"))

        legacy = board.get("legacy_version_tickets", {}).get("total", 0)

        if legacy:
            add("L1", "V0.15.0", "{} legacy Version ticket(s) to convert".format(legacy))

    if labels_have_dummy is False:
        add("A4", "V0.7.0", "the label dummy does not exist")

    if files.get("placeholder_in_a_project"):
        add("M1", "V0.15.0", "the manifest names the placeholder WIP-Version in a project that is not the standard's repository: "
            "state the standard's version")

    return found


def detect_state(files):
    identity = files.get("identity", {})
    state = identity.get("state")

    if state == "match":
        return {"detected": "version", "versions": identity["versions"]}

    if state == "mixed":
        return {"detected": "mixed", "closest": identity.get("closest", [])}

    if state == "modified":
        return {"detected": "unsupported" if not identity.get("closest") else "modified", "closest": identity.get("closest", [])}

    if state == "none":
        return {"detected": "none"}

    return {"detected": "unknown"}


def blockers(repository, board, embedded=None):
    found = []
    embedded = embedded or {}

    if embedded.get("present") and not embedded.get("initialized"):
        found.append("the submodule {} is not checked out: run `git submodule update --init {}`".format(EMBEDDED, EMBEDDED))

    if embedded.get("shallow") or embedded.get("gitmodules_shallow"):
        found.append("the submodule {} is shallow and the fingerprints need its full history: run `git -C {} fetch --unshallow` and "
                     "remove `shallow = true` from .gitmodules".format(EMBEDDED, EMBEDDED))

    if embedded.get("clean") is False:
        found.append("the submodule {} has uncommitted changes: the files copied from it would not be the standard's".format(EMBEDDED))

    if repository.get("hotfix_branches"):
        found.append("hotfix branches exist ({}): finish or retire them first".format(", ".join(repository["hotfix_branches"])))

    if repository.get("clean_tree") is False:
        found.append("the working tree has uncommitted changes")

    if repository.get("shallow"):
        found.append("the clone of the project is shallow")

    if repository.get("open_pull_requests"):
        found.append("{} open pull request(s): settle them or accept that they merge after the cut-over".format(repository["open_pull_requests"]))

    return found


def survey(root, repo=None, gh=None, board_source=None, table=None, fleet=True, now=None):
    """The whole survey as a dict. `gh(path)` -> (status, data) reads REST (None: offline), `board_source()` the board."""
    now = now or datetime.now(timezone.utc)
    repository = facts_repository(root, repo, gh)
    files = facts_files(root, table)
    embedded = facts_embedded(root)
    settings = facts_settings(repo, gh) if repo else {"unknown": ["no GitHub repository: the settings were not read"]}
    organization = facts_organization(repository.get("owner"), repository.get("owner_type"), gh, fleet)
    highest = None
    state = files.get("changelog_state") or {}

    if state.get("highest"):
        highest = versions.Version.parse(state["highest"])

    board = facts_board(board_source, highest)
    labels_have_dummy = None

    if gh is not None and repo:
        status, labels = gh("repos/{}/labels?per_page=100".format(repo), "--paginate")

        if status == 200 and isinstance(labels, list):
            labels_have_dummy = any(l.get("name") == "dummy" for l in labels)

    detected = detect_state(files)
    result = {"tool": "survey", "when": now.strftime("%Y-%m-%d %H:%M UTC"), "project": os.path.abspath(root), "repo": repo,
              "repository": repository, "files": files, "embedded": embedded, "settings": settings, "organization": organization, "board": board,
              "state": detected, "gaps": gaps(files, board, labels_have_dummy, repository.get("owner_type")),
              "blockers": blockers(repository, board, embedded)}
    result["manual"] = [item for section in (repository, files, embedded, settings, organization, board) for item in section.get("unknown", [])]
    return result


def render(result):
    """The survey as Markdown."""
    lines = ["# Survey of {}".format(result["repo"] or result["project"]), "", "{} UTC".format(result["when"].replace(" UTC", "")), ""]
    state = result["state"]
    lines += ["## Detected state", "", "- **{}**{}".format(state["detected"], ": " + ", ".join(state.get("versions", state.get("closest", []))) if state.get("versions") or state.get("closest") else ""), ""]
    lines += ["## Gaps", ""] + (["- {} ({}): {}".format(g["id"], g["since"], g["text"]) for g in result["gaps"]] or ["- none found"]) + [""]
    lines += ["## Blockers", ""] + (["- " + b for b in result["blockers"]] or ["- none found"]) + [""]
    board = result["board"]

    if board.get("found"):
        lines += ["## Board", "", "- #{} {}; {} tickets; by type {}".format(board["number"], board["title"], board["tickets"]["total"], board["tickets"]["by_type"]),
                  "- legacy Version tickets: {}".format(board["legacy_version_tickets"]),
                  "- the first refresh of the new files would: flag {} stale plan(s), fill Resolution Done on {} ticket(s), clear it on {}".format(
                      board["preview"]["stale_plans"], board["preview"]["resolution_done_to_fill"], board["preview"]["resolution_done_to_clear"]),
                  "- views: missing {}, different {}".format(board["views"]["missing"], board["views"]["different"]), ""]

    files = result["files"]
    lines += ["## Files", "", "- the standard the manifest names: {}".format(files.get("manifest_standard")),
              "- identity of the automation files: {} {}".format(files["identity"]["state"], files["identity"].get("versions") or files["identity"].get("closest")),
              "- hooks path: {}; hook managers: {}".format(files.get("hooks_path"), files.get("hook_managers") or "none"), ""]
    embedded = result.get("embedded", {})

    if embedded.get("present"):
        lines += ["## The standard in the project", "", "- submodule {} pinned at {} ({}); checked out {}{}".format(
            embedded["path"], (embedded.get("pinned") or "")[:8], embedded.get("pinned_standard") or "version unknown",
            (embedded.get("checked_out") or "not checked out")[:8], "; shallow" if embedded.get("shallow") else ""),
            "- the manifest of the project names {}".format(files.get("manifest_standard")), ""]

    lines += ["## To check by hand", ""] + (["- " + item for item in result["manual"]] or ["- nothing"]) + [""]
    return "\n".join(lines)


def default_board_source(repo):
    """The board through the automation's own modules, with the token of `gh`. Returns a callable for `survey`."""
    def source():
        try:
            repo_client, project_client = kit_common.connect(repo)
            report = preflight.run(repo_client, project_client, store=False)
            board = report.board or report.candidate

            if board is None:
                return {"board": None}

            tickets = conditions.board_tickets(project_client, board)
            nodes = project_client.project_views(board.id)
            return {"board": {"number": board.number, "title": board.title, "fields": board.fields}, "type_source": report.type_source,
                    "tickets": tickets, "views": [views.current_state(n) for n in nodes]}
        except (GitHubError, KitError) as error:
            return {"error": "the board could not be read: {}".format(error)}

    return source


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])

    try:
        if not args or args[0].startswith("--"):
            raise KitError("usage: python tools/survey.py <project-path> [--repo owner/name] [--no-fleet] [--offline]")

        root = os.path.abspath(args[0])
        offline = "--offline" in args
        repo = kit_common.option(args, "--repo") or audit_common.remote_repo(root)

        try:
            table = build_fingerprints.load_or_build(kit_common.STANDARD)
        except build_fingerprints.FingerprintError as error:
            print("warning: {}".format(error))
            table = None

        result = survey(root, repo, None if offline else audit_common.gh_api, None if offline or not repo else default_board_source(repo),
                        table, "--no-fleet" not in args)
    except KitError as error:
        print("survey refused: {}".format(error))
        return 1

    folder = kit_common.state_path(root)
    with open(os.path.join(folder, "survey.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=1, default=str)
        handle.write("\n")
    with open(os.path.join(folder, "survey.md"), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render(result))

    print(render(result))
    print("written to {}".format(folder))
    return 0


if __name__ == "__main__":
    sys.exit(main())
