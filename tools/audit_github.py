"""Audit the GitHub repository settings of an existing project against the guides.

Reads, through the `gh` command line tool, the repository's merge methods, default branch, features, branch protection,
Actions, secret and variable names, labels and the organization's issue types (not needed when the Type is kept in the board field Kind, see the variable
TYPE_SOURCE). Read-only. It needs `gh` signed in with
enough access (administration to read protection and secrets); what it cannot read is reported as not-checkable.

Usage:
    python tools/audit_github.py <project-path> [--verbose] [--repo owner/name] [--json <file>]

The repository is the origin remote of the project unless --repo says otherwise.
Prints the checks that are not a pass (every check with --verbose), each with all its detail lines, and exits 1 when
a rule fails.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_common import (Report, RULE, RECOMMENDATION, Variables, gh_api, remote_repo, appendix_c, format_report)  # noqa: E402
import ticket_type  # noqa: E402

GUIDE = "10 section 3"
SETTINGS = (
    ("allow_merge_commit", True, "merge commits are allowed", RULE),
    ("allow_squash_merge", False, "squash merging is off", RULE),
    ("allow_rebase_merge", False, "rebase merging is off", RULE),
    ("delete_branch_on_merge", False, "head branches are not deleted automatically", RULE),
    ("has_issues", True, "issues are enabled", RULE),
    ("has_projects", True, "projects are enabled", RULE),
    ("has_wiki", True, "the wiki is enabled", RECOMMENDATION),
)


def audit(repo, gh=gh_api):
    report = Report("github")
    status, info = gh("repos/{}".format(repo))

    if status != 200 or not isinstance(info, dict):
        report.add("github.repository", GUIDE, RULE, "the repository can be read with `gh`", None,
                   "cannot read {} (status {}): `gh` is missing, not signed in, or has no access".format(repo, status),
                   "run `gh auth login` and use an account with access", ["gh api repos/{} returned status {}".format(repo, status)])
        return report

    source = check_type_source(report, repo, gh, info)
    check_settings(report, info, source)
    check_protection(report, repo, gh)
    check_actions(report, repo, gh)
    check_token_and_board(report, repo, gh)
    check_labels(report, repo, gh)
    check_issue_types(report, repo, gh, source)
    return report


def check_type_source(report, repo, gh, info):
    """Check the variable TYPE_SOURCE (if it is set it must name a source) and return the source that applies."""
    status, data = gh("repos/{}/actions/variables/{}".format(repo, ticket_type.VARIABLE))
    source = ticket_type.source(info, Variables(repo, gh))
    value = data.get("value") if status == 200 and isinstance(data, dict) else None

    if status not in (200, 404):
        report.add("github.type-source", "10 section 5.1", RULE, "the Type source is `issue-type` or `field`", None,
                   "the variable {} could not be read (status {})".format(ticket_type.VARIABLE, status), "",
                   ["gh api repos/{}/actions/variables/{} returned status {}".format(repo, ticket_type.VARIABLE, status)])
    else:
        report.add("github.type-source", "10 section 5.1", RULE, "the Type source is `issue-type` or `field`",
                   value is None or value.strip() in ticket_type.SOURCES,
                   "{} is {!r}".format(ticket_type.VARIABLE, value),
                   "set the repository variable {} to `issue-type` or `field`, or delete it".format(ticket_type.VARIABLE),
                   ["{} = {}".format(ticket_type.VARIABLE, value) if value is not None
                    else "{} is not set: the source is {} (the owner is {})".format(
                        ticket_type.VARIABLE, source, (info.get("owner") or {}).get("type"))])

    return source


def check_settings(report, info, source=ticket_type.ISSUE_TYPE):
    for key, wanted, title, strength in SETTINGS:
        value = info.get(key)
        report.add("github.setting." + key, GUIDE, strength, title, None if value is None else value == wanted,
                   "{} is {}".format(key, value), "change it in the repository's settings",
                   ["{} = {} (wanted {})".format(key, value, wanted)])

    branch = info.get("default_branch")
    report.add("github.setting.default_branch", GUIDE, RULE, "the default branch is `main`", branch == "main",
               "the default branch is {!r}".format(branch), "rename it to `main` and make it the default",
               ["default_branch = {}".format(branch)])
    report.add("github.setting.owner-type", "10 section 5.1", RULE,
               "the repository belongs to an organization (issue types need one), or the Type is kept in the field Kind",
               (info.get("owner") or {}).get("type") == "Organization" or source == ticket_type.FIELD_SOURCE,
               "the owner is {!r}".format((info.get("owner") or {}).get("type")),
               "move the repository to an organization, or keep the Type in the field Kind (variable TYPE_SOURCE = field)",
               ["owner {} is of type {}".format((info.get("owner") or {}).get("login"),
                                                (info.get("owner") or {}).get("type"))])


def check_protection(report, repo, gh):
    status, protection = gh("repos/{}/branches/main/protection".format(repo))
    title = "`main` requires a pull request before merging"

    if status == 404:
        status2, rulesets = gh("repos/{}/rulesets".format(repo))
        covered = status2 == 200 and any(r.get("target") == "branch" and r.get("enforcement") == "active"
                                         for r in rulesets or [])
        report.add("github.protection.pull-request", GUIDE, RECOMMENDATION, title, covered if status2 == 200 else None,
                   "no branch protection and no active ruleset on `main`",
                   "protect `main` where the plan offers it (leave the administrator bypass open)",
                   ["branch protection of main: none (status 404)",
                    "active branch rulesets: {}".format(
                        ", ".join(r.get("name", "?") for r in rulesets or []
                                  if r.get("target") == "branch" and r.get("enforcement") == "active") or "none")])
        return

    if status != 200 or not isinstance(protection, dict):
        report.add("github.protection.pull-request", GUIDE, RECOMMENDATION, title, None,
                   "branch protection could not be read (status {})".format(status), "",
                   ["gh api branches/main/protection returned status {}".format(status)])
        return

    report.add("github.protection.pull-request", GUIDE, RECOMMENDATION, title,
               bool(protection.get("required_pull_request_reviews") is not None
                    or protection.get("required_status_checks") is not None),
               "no pull request requirement on `main`", "require a pull request before merging",
               ["required_pull_request_reviews: {}".format(
                   "set" if protection.get("required_pull_request_reviews") is not None else "not set"),
                "required_status_checks: {}".format(
                    "set" if protection.get("required_status_checks") is not None else "not set")])
    strict = (protection.get("required_status_checks") or {}).get("strict")
    report.add("github.protection.up-to-date", GUIDE, RECOMMENDATION, "`main` requires the branch to be up to date",
               bool(strict), "the up-to-date requirement is off", "require branches to be up to date before merging",
               ["required_status_checks.strict = {}".format(strict)])
    enforce = (protection.get("enforce_admins") or {}).get("enabled")
    report.add("github.protection.admin-bypass", GUIDE, RECOMMENDATION, "the administrator bypass is left open",
               enforce is False, "the protection also applies to administrators",
               "untick \"do not allow bypassing the above settings\"",
               ["enforce_admins.enabled = {}".format(enforce)])


def check_actions(report, repo, gh):
    status, actions = gh("repos/{}/actions/permissions".format(repo))
    report.add("github.actions.enabled", GUIDE, RULE, "Actions is enabled",
               None if status != 200 or not isinstance(actions, dict) else bool(actions.get("enabled")),
               "Actions is disabled or could not be read", "enable Actions for the repository",
               ["gh api actions/permissions returned status {}".format(status)] +
               (["enabled = {}".format(actions.get("enabled"))] if status == 200 and isinstance(actions, dict) else []))


def check_token_and_board(report, repo, gh):
    status, secrets = gh("repos/{}/actions/secrets".format(repo))
    names = [s.get("name") for s in (secrets or {}).get("secrets", [])] if status == 200 else None
    report.add("github.token.secret", "10 section 4", RULE, "the secret PROJECT_TOKEN exists",
               None if names is None else "PROJECT_TOKEN" in names, "no secret PROJECT_TOKEN",
               "store the project token as the Actions secret PROJECT_TOKEN",
               ["secrets found: {}".format(", ".join(names) or "none")] if names is not None
               else ["secrets could not be read (status {})".format(status)])

    status, variables = gh("repos/{}/actions/variables".format(repo))
    names = [v.get("name") for v in (variables or {}).get("variables", [])] if status == 200 else None
    report.add("github.board.variable", "10 section 2.3", RECOMMENDATION, "the variable BOARD_NUMBER is set",
               None if names is None else "BOARD_NUMBER" in names, "no variable BOARD_NUMBER",
               "run the preflight, which stores the board number",
               ["variables found: {}".format(", ".join(names) or "none")] if names is not None
               else ["variables could not be read (status {})".format(status)])


def check_labels(report, repo, gh):
    wanted, _ = appendix_c()
    status, labels = gh("repos/{}/labels?per_page=100".format(repo), "--paginate")

    if status != 200 or not isinstance(labels, list):
        report.add("github.labels.exact", "10 section 5.2", RULE, "the labels are the 14 Area labels and `dummy`", None,
                   "labels could not be read (status {})".format(status), "",
                   ["gh api labels returned status {}".format(status)])
        return

    found = {l["name"]: l for l in labels}
    extra = sorted(set(found) - set(wanted))
    missing = sorted(set(wanted) - set(found))
    report.add("github.labels.exact", "10 section 5.2", RULE, "the labels are the 14 Area labels and `dummy`, no others",
               not extra and not missing,
               "extra: {}; missing: {}".format(", ".join(extra) or "none", ", ".join(missing) or "none"),
               "delete the extra labels and create the missing ones",
               ["extra: " + n for n in extra] + ["missing: " + n for n in missing]
               or ["{} labels, all expected: {}".format(len(found), ", ".join(sorted(found)))])
    nodesc = sorted(n for n in wanted if n in found and not (found[n].get("description") or "").strip())
    report.add("github.labels.descriptions", "10 section 5.2", RULE, "each label carries a description", not nodesc,
               "{} label(s) without a description".format(len(nodesc)), "give each label its meaning from Appendix C",
               ["no description: " + n for n in nodesc]
               or ["{}: {}".format(n, found[n].get("description")) for n in sorted(wanted) if n in found])
    wrong = sorted(n for n in wanted if n in found and (found[n].get("color") or "").upper() != wanted[n][0])
    report.add("github.labels.colors", "10 section 5.2", RECOMMENDATION, "each label has its standard color", not wrong,
               "{} label(s) with another color".format(len(wrong)), "use the hex colors of Appendix C",
               ["{}: color {}, expected {}".format(n, (found[n].get("color") or "").upper(), wanted[n][0])
                for n in wrong] or ["{}: {}".format(n, wanted[n][0]) for n in sorted(wanted) if n in found])


def check_issue_types(report, repo, gh, source=ticket_type.ISSUE_TYPE):
    if source == ticket_type.FIELD_SOURCE:
        report.add("github.issue-types.exact", "10 section 5.1", RULE, "the eight issue types exist", True, "",
                   "", ["not needed: the Type is kept in the board field {}".format(ticket_type.FIELD)])
        return

    _, wanted = appendix_c()
    owner = repo.split("/")[0]
    status, types = gh("orgs/{}/issue-types".format(owner))

    if status != 200 or not isinstance(types, list):
        report.add("github.issue-types.exact", "10 section 5.1", RULE, "the eight issue types exist", None,
                   "issue types could not be read (status {})".format(status), "",
                   ["gh api orgs/{}/issue-types returned status {}".format(owner, status)])
        return

    found = {t["name"]: t for t in types if t.get("is_enabled", True)}
    missing = sorted(set(wanted) - set(found))
    report.add("github.issue-types.exact", "10 section 5.1", RULE, "the eight issue types exist", not missing,
               "{} issue type(s) missing".format(len(missing)), "create them in the organization's settings",
               ["missing: " + n for n in missing] or ["found: " + n for n in sorted(wanted)])
    nodesc = sorted(n for n in wanted if n in found and not (found[n].get("description") or "").strip())
    report.add("github.issue-types.descriptions", "10 section 5.1", RULE, "each issue type carries a description",
               not nodesc, "{} issue type(s) without a description".format(len(nodesc)),
               "give each type its definition from Appendix C",
               ["no description: " + n for n in nodesc]
               or ["{}: {}".format(n, found[n].get("description")) for n in sorted(wanted) if n in found])
    wrong = sorted(n for n in wanted if n in found and (found[n].get("color") or "").upper() != wanted[n][0])
    report.add("github.issue-types.colors", "10 section 5.2", RECOMMENDATION, "each issue type has its standard color",
               not wrong, "{} issue type(s) with another color".format(len(wrong)), "use the colors of Appendix C",
               ["{}: color {}, expected {}".format(n, (found[n].get("color") or "").upper(), wanted[n][0])
                for n in wrong] or ["{}: {}".format(n, wanted[n][0]) for n in sorted(wanted) if n in found])


def main(argv, gh=gh_api):
    args = argv[1:]
    options = {}
    verbose = "--verbose" in args

    if verbose:
        args.remove("--verbose")

    for flag in ("--repo", "--json"):
        if flag in args:
            i = args.index(flag)
            options[flag] = args[i + 1] if i + 1 < len(args) else None
            del args[i:i + 2]

    if len(args) != 1 or not os.path.isdir(args[0]):
        print(__doc__)
        return 2

    repo = options.get("--repo") or remote_repo(args[0])

    if not repo:
        report = Report("github")
        report.add("github.remote", "03 section 1", RULE, "the project has a GitHub remote", None,
                   "no github.com origin remote; pass --repo owner/name", "")
    else:
        report = audit(repo, gh)

    print(format_report(report, verbose))

    if options.get("--json"):
        with open(options["--json"], "w", encoding="utf-8") as f:
            json.dump(report.as_dict(verbose), f, indent=2)

    return 1 if report.failures(RULE) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
