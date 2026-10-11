import copy
import os
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_common  # noqa: E402
import audit_github  # noqa: E402

REPO = "org/proj"
LABELS, TYPES = audit_common.appendix_c()

GOOD = {
    "repos/org/proj": {"allow_merge_commit": True, "allow_squash_merge": False, "allow_rebase_merge": False,
                       "delete_branch_on_merge": False, "has_issues": True, "has_projects": True, "has_wiki": True,
                       "default_branch": "main", "owner": {"type": "Organization"}},
    "repos/org/proj/branches/main/protection": {"required_pull_request_reviews": {},
                                                "required_status_checks": {"strict": True},
                                                "enforce_admins": {"enabled": False}},
    "repos/org/proj/actions/permissions": {"enabled": True},
    "repos/org/proj/actions/secrets": {"secrets": [{"name": "PROJECT_TOKEN"}]},
    "repos/org/proj/actions/variables": {"variables": [{"name": "BOARD_NUMBER"}]},
    "repos/org/proj/labels?per_page=100": [{"name": n, "description": "d", "color": c.lower()}
                                           for n, (c, _) in LABELS.items()],
    "orgs/org/issue-types": [{"name": n, "description": "d", "color": c.lower(), "is_enabled": True}
                             for n, (c, _) in TYPES.items()],
}


def fake(data, status=None):
    status = status or {}

    def gh(path, *args):
        if path in status:
            return status[path], None

        if path in data:
            return 200, copy.deepcopy(data[path])

        return 404, None

    return gh


def failed(report):
    return {c.id for c in report.checks if c.result == audit_common.FAIL}


def unknown(report):
    return {c.id for c in report.checks if c.result == audit_common.NOT_CHECKABLE}


class AuditGithubTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(GOOD)

    def audit(self, status=None):
        return audit_github.audit(REPO, fake(self.data, status))

    def test_the_standard_tables_were_read(self):
        self.assertEqual(len(LABELS), 15)
        self.assertEqual(len(TYPES), 8)

    def test_a_conforming_repository_passes(self):
        report = self.audit()
        self.assertEqual(failed(report), set())
        self.assertEqual(unknown(report), set())

    def test_unreachable_repository(self):
        report = audit_github.audit(REPO, fake({}, {"repos/org/proj": 0}))
        self.assertEqual(unknown(report), {"github.repository"})

    def test_merge_methods_and_branch_deletion(self):
        info = self.data["repos/org/proj"]
        info.update(allow_squash_merge=True, allow_rebase_merge=True, delete_branch_on_merge=True,
                    default_branch="master")
        bad = failed(self.audit())
        self.assertTrue({"github.setting.allow_squash_merge", "github.setting.allow_rebase_merge",
                         "github.setting.delete_branch_on_merge", "github.setting.default_branch"} <= bad)

    def test_personal_account_owner(self):
        self.data["repos/org/proj"]["owner"] = {"type": "User"}
        self.assertIn("github.setting.owner-type", failed(self.audit()))

    def test_protection_details(self):
        protection = self.data["repos/org/proj/branches/main/protection"]
        protection["required_status_checks"]["strict"] = False
        protection["enforce_admins"]["enabled"] = True
        bad = failed(self.audit())
        self.assertTrue({"github.protection.up-to-date", "github.protection.admin-bypass"} <= bad)

    def test_no_protection_and_no_ruleset(self):
        del self.data["repos/org/proj/branches/main/protection"]
        self.data["repos/org/proj/rulesets"] = []
        self.assertIn("github.protection.pull-request", failed(self.audit()))

    def test_an_active_ruleset_counts_as_protection(self):
        del self.data["repos/org/proj/branches/main/protection"]
        self.data["repos/org/proj/rulesets"] = [{"target": "branch", "enforcement": "active"}]
        self.assertNotIn("github.protection.pull-request", failed(self.audit()))

    def test_unreadable_secrets_are_not_checkable(self):
        report = self.audit({"repos/org/proj/actions/secrets": 403, "repos/org/proj/actions/variables": 403})
        self.assertTrue({"github.token.secret", "github.board.variable"} <= unknown(report))

    def test_missing_secret_and_variable(self):
        self.data["repos/org/proj/actions/secrets"] = {"secrets": []}
        self.data["repos/org/proj/actions/variables"] = {"variables": []}
        bad = failed(self.audit())
        self.assertTrue({"github.token.secret", "github.board.variable"} <= bad)

    def test_labels(self):
        labels = self.data["repos/org/proj/labels?per_page=100"]
        labels.append({"name": "bug", "description": "", "color": "ff0000"})
        labels[:] = [l for l in labels if l["name"] != "tool"]
        labels[0]["description"] = ""
        labels[1]["color"] = "000000"
        bad = failed(self.audit())
        self.assertTrue({"github.labels.exact", "github.labels.descriptions", "github.labels.colors"} <= bad)

    def test_issue_types(self):
        types = self.data["orgs/org/issue-types"]
        types[:] = [t for t in types if t["name"] != "Alert"]
        types[0]["description"] = ""
        types[1]["color"] = "black"
        bad = failed(self.audit())
        self.assertTrue({"github.issue-types.exact", "github.issue-types.descriptions",
                         "github.issue-types.colors"} <= bad)

    def test_main_without_a_remote_or_arguments(self):
        self.assertEqual(audit_github.main(["audit_github.py"]), 2)
        self.assertEqual(audit_github.main(["audit_github.py", os.path.dirname(os.path.abspath(__file__)),
                                            "--repo", REPO], gh=fake(self.data)), 0)
        self.data["repos/org/proj"]["allow_squash_merge"] = True
        self.assertEqual(audit_github.main(["audit_github.py", ROOT, "--repo", REPO], gh=fake(self.data)), 1)


if __name__ == "__main__":
    unittest.main()
