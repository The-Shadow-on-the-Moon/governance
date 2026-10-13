import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_common  # noqa: E402
import audit_files  # noqa: E402

GOOD_CHANGELOG = """# Changelog

## WIP-Version
### WIP-Build
#### #5 — Something

## V1.0.1 — 2026-10-05 14:32 UTC
### Build 20261005143000 (branch fix-it)
#### #4 — Fix it
- file: changed.

## V1.0.0 — 2026-10-01 09:00 UTC
### Build 20261001085500 (branch first)
#### REF 20261001085500 — start
- file: added.
"""


def write(root, name, text):
    path = os.path.join(root, *name.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def build_project(root):
    for name in ("README.md", "AGENTS.md", ".gitignore", "LICENSE", "doc/wiki/Home.md",
                 ".github/pull_request_template.md", ".github/automation-manifest.json", ".github/workflows/w.yml",
                 ".githooks/pre-commit", ".githooks/pre-push", ".githooks/prepare-commit-msg"):
        write(root, name, "see the guides\n" if name == "AGENTS.md" else "x\n")

    write(root, ".gitattributes", "* text=auto eol=lf\n")
    write(root, "CHANGELOG.md", GOOD_CHANGELOG)


def failed(report):
    return {c.id for c in report.checks if c.result == audit_common.FAIL}


class AuditFilesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        build_project(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_a_complete_project_has_no_failure(self):
        self.assertEqual(failed(audit_files.audit(self.root)), set())

    def test_empty_folder_fails_the_locations(self):
        with tempfile.TemporaryDirectory() as empty:
            bad = failed(audit_files.audit(empty))

        self.assertIn("files.location.CHANGELOG.md", bad)
        self.assertIn("files.location.doc.wiki", bad)

    def test_gitattributes_line_missing(self):
        write(self.root, ".gitattributes", "* text=auto\n")
        self.assertIn("files.gitattributes.eol", failed(audit_files.audit(self.root)))

    def test_changelog_with_banned_sections(self):
        write(self.root, "CHANGELOG.md", GOOD_CHANGELOG + "\n### Known bugs (not yet fixed)\n- x\n")
        self.assertIn("files.changelog.no-bug-plan-sections", failed(audit_files.audit(self.root)))

    def test_the_details_list_every_offending_line(self):
        write(self.root, "CHANGELOG.md", GOOD_CHANGELOG + "\n### Known bugs\n- x\n### Planned\n- y\n")
        lines = GOOD_CHANGELOG.count("\n") + 2
        check = next(c for c in audit_files.audit(self.root).checks if c.id == "files.changelog.no-bug-plan-sections")
        self.assertEqual(check.details, ["line %d: ### Known bugs" % lines, "line %d: ### Planned" % (lines + 2)])

    def test_the_details_of_a_missing_hook_name_all_three(self):
        os.remove(os.path.join(self.root, ".githooks", "pre-push"))
        check = next(c for c in audit_files.audit(self.root).checks if c.id == "files.hooks.present")
        self.assertEqual(check.details, ["pre-commit: found", "pre-push: missing", "prepare-commit-msg: found"])

    def test_changelog_with_carriage_returns(self):
        write(self.root, "CHANGELOG.md", GOOD_CHANGELOG.replace("\n", "\r\n"))
        self.assertIn("files.changelog.eol", failed(audit_files.audit(self.root)))

    def test_odd_version_heading(self):
        text = GOOD_CHANGELOG.replace("## V1.0.1 — 2026-10-05 14:32 UTC", "## V1.0.1 (2026-10-05)")
        write(self.root, "CHANGELOG.md", text)
        self.assertIn("files.changelog.version-heading", failed(audit_files.audit(self.root)))

    def test_versions_out_of_order(self):
        write(self.root, "CHANGELOG.md", GOOD_CHANGELOG.replace("## V1.0.0 —", "## V1.0.2 —"))
        self.assertIn("files.changelog.newest-first", failed(audit_files.audit(self.root)))

    def test_two_wip_headings_and_a_bad_marker(self):
        write(self.root, "CHANGELOG.md", "## WIP-Version +x\n\n" + GOOD_CHANGELOG)
        bad = failed(audit_files.audit(self.root))
        self.assertIn("files.changelog.wip-heading", bad)
        self.assertIn("files.changelog.one-wip", bad)

    def test_wip_below_a_finalized_version(self):
        write(self.root, "CHANGELOG.md", "# Changelog\n\n## V1.0.0 — 2026-10-01 09:00 UTC\n\n## WIP-Version\n")
        self.assertIn("files.changelog.wip-on-top", failed(audit_files.audit(self.root)))

    def test_bad_build_and_ticket_headings(self):
        write(self.root, "CHANGELOG.md", GOOD_CHANGELOG + "\n### Build today\n#### Fix stuff\n")
        self.assertIn("files.changelog.headings", failed(audit_files.audit(self.root)))

    def test_wiki_names_and_home(self):
        write(self.root, "doc/wiki/Getting Started.md", "x")
        self.assertIn("files.wiki.names", failed(audit_files.audit(self.root)))
        os.remove(os.path.join(self.root, "doc", "wiki", "Home.md"))
        self.assertIn("files.wiki.home", failed(audit_files.audit(self.root)))

    def test_automation_scripts_need_tests(self):
        write(self.root, ".github/scripts/a.py", "x")
        self.assertIn("files.automation.tests", failed(audit_files.audit(self.root)))
        write(self.root, "tests/test_a.py", "x")
        self.assertNotIn("files.automation.tests", failed(audit_files.audit(self.root)))

    def test_agents_without_the_guides(self):
        write(self.root, "AGENTS.md", "hello\n")
        self.assertIn("files.agents.guides", failed(audit_files.audit(self.root)))

    def test_outside_a_clone_the_hooks_check_is_not_checkable(self):
        check = next(c for c in audit_files.audit(self.root).checks if c.id == "files.hooks.active")
        self.assertEqual(check.result, audit_common.NOT_CHECKABLE)

    def test_main_exit_codes_and_json(self):
        self.assertEqual(audit_files.main(["audit_files.py"]), 2)
        out = os.path.join(self.root, "out.json")
        self.assertEqual(audit_files.main(["audit_files.py", self.root, "--json", out]), 0)
        self.assertTrue(os.path.isfile(out))
        os.remove(os.path.join(self.root, "CHANGELOG.md"))
        self.assertEqual(audit_files.main(["audit_files.py", self.root]), 1)


if __name__ == "__main__":
    unittest.main()
