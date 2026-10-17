import json
import os
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))

import check_manifest as cm  # noqa: E402


def write(root, relative, text):
    path = os.path.join(root, *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name
        write(self.root, ".githooks/pre-commit", "hook\n")
        write(self.root, ".github/scripts/a.py", "a = 1\n")
        write(self.root, ".github/workflows/versioning.yml", "name: v\n")
        write(self.root, ".github/workflows/wiki-sync.yml", "name: wiki\n")  # not automation
        write(self.root, "README.md", "readme\n")  # not automation

    def test_build_lists_only_the_automation_files(self):
        manifest = cm.build(self.root, "V0.3.0")
        self.assertEqual(manifest["standard"], "V0.3.0")
        self.assertEqual(sorted(manifest["files"]), [".githooks/pre-commit", ".github/scripts/a.py", ".github/workflows/versioning.yml"])

    def test_everything_unchanged(self):
        states = cm.check(self.root, cm.build(self.root, "V0.3.0"))
        self.assertEqual(set(states.values()), {cm.UNCHANGED})

    def test_an_edited_and_a_missing_file(self):
        manifest = cm.build(self.root, "V0.3.0")
        write(self.root, ".github/scripts/a.py", "a = 2\n")
        os.remove(os.path.join(self.root, ".githooks", "pre-commit"))
        states = cm.check(self.root, manifest)
        self.assertEqual(states[".github/scripts/a.py"], cm.EDITED)
        self.assertEqual(states[".githooks/pre-commit"], cm.MISSING)

    def test_line_endings_do_not_matter(self):
        manifest = cm.build(self.root, "V0.3.0")
        write(self.root, ".github/scripts/a.py", "a = 1\r\n")
        self.assertEqual(cm.check(self.root, manifest)[".github/scripts/a.py"], cm.UNCHANGED)

    def test_against_a_newer_manifest(self):
        old = cm.build(self.root, "V0.3.0")
        newer = json.loads(json.dumps(old))
        newer["standard"] = "V0.4.0"
        newer["files"][".github/scripts/a.py"] = "0" * 64  # the standard changed this file
        newer["files"][".githooks/pre-commit"] = cm.file_hash(os.path.join(self.root, ".githooks", "pre-commit"))
        newer["files"][".github/new.py"] = "1" * 64  # a file the project does not have in its manifest
        write(self.root, ".githooks/pre-commit", "hook, edited here\n")
        states = cm.check(self.root, old, newer)
        self.assertEqual(states[".github/scripts/a.py"], cm.OLDER)
        self.assertEqual(states[".githooks/pre-commit"], cm.EDITED)
        self.assertEqual(states[".github/new.py"], cm.NEW)  # in the standard, not here yet
        self.assertEqual(states[".github/workflows/versioning.yml"], cm.UNCHANGED)

    def test_render_and_exit_summary(self):
        text = cm.render({"a": cm.UNCHANGED, "b": cm.EDITED}, "V0.3.0")
        self.assertIn("1 file(s) differ", text)
        self.assertIn("edited locally", text)
        self.assertIn("all files unchanged", cm.render({"a": cm.UNCHANGED}, "V0.3.0"))

    def test_a_standard_flag_without_a_version_is_refused(self):
        self.assertEqual(cm.main(["--update", "--standard"]), 1)

    def test_the_placeholder_is_replaced_once_by_the_version(self):
        cm.write(self.root, cm.build(self.root, cm.PLACEHOLDER))
        self.assertTrue(cm.stamp_pending(self.root))
        self.assertTrue(cm.set_standard(self.root, "V0.4.0"))
        manifest = cm.load(os.path.join(self.root, cm.MANIFEST))
        self.assertEqual(manifest["standard"], "V0.4.0")
        self.assertEqual(manifest["files"], cm.build(self.root, "x")["files"])  # the hashes are untouched
        self.assertFalse(cm.stamp_pending(self.root))
        self.assertFalse(cm.set_standard(self.root, "V0.5.0"))  # a real version is left as it is
        self.assertEqual(cm.load(os.path.join(self.root, cm.MANIFEST))["standard"], "V0.4.0")

    def update(self, *args):
        return cm.main(["--update", *args], self.root)

    def standard(self):
        return cm.load(os.path.join(self.root, cm.MANIFEST))["standard"]

    def test_an_update_keeps_the_standard_the_manifest_names(self):
        cm.write(self.root, cm.build(self.root, "V0.4.0"))
        write(self.root, ".github/scripts/a.py", "a = 2\n")
        self.assertEqual(self.update(), 0)
        self.assertEqual(self.standard(), "V0.4.0")
        self.assertEqual(cm.check(self.root, cm.load(os.path.join(self.root, cm.MANIFEST)))[".github/scripts/a.py"], cm.UNCHANGED)

    def test_an_update_keeps_the_placeholder_too(self):
        cm.write(self.root, cm.build(self.root, cm.PLACEHOLDER))
        self.assertEqual(self.update(), 0)
        self.assertEqual(self.standard(), cm.PLACEHOLDER)

    def test_an_update_with_no_manifest_needs_the_version_stated(self):
        self.assertEqual(self.update(), 1)
        self.assertFalse(os.path.exists(os.path.join(self.root, cm.MANIFEST)))
        self.assertEqual(self.update("--standard", "V0.4.0"), 0)
        self.assertEqual(self.standard(), "V0.4.0")

    def test_pending_writes_the_placeholder_over_a_real_version(self):
        cm.write(self.root, cm.build(self.root, "V0.4.0"))
        self.assertEqual(self.update("--pending"), 0)
        self.assertEqual(self.standard(), cm.PLACEHOLDER)

    def test_standard_states_the_version_over_the_current_one(self):
        cm.write(self.root, cm.build(self.root, "V0.4.0"))
        self.assertEqual(self.update("--standard", "V0.5.0"), 0)
        self.assertEqual(self.standard(), "V0.5.0")

    def test_pending_with_a_version_is_refused(self):
        self.assertEqual(self.update("--pending", "--standard", "V0.4.0"), 1)

    def test_a_standard_flag_followed_by_another_flag_is_refused(self):
        self.assertEqual(self.update("--standard", "--pending"), 1)
        self.assertEqual(self.update("--standard"), 1)

    def test_no_manifest_means_nothing_to_stamp(self):
        self.assertFalse(cm.stamp_pending(self.root))
        self.assertFalse(cm.set_standard(self.root, "V0.4.0"))


class RepositoryManifestTests(unittest.TestCase):
    def test_the_projects_manifest_matches_its_files(self):
        """Fails when an automation file was edited without rewriting the manifest (or the reverse)."""
        manifest = cm.load(os.path.join(ROOT, cm.MANIFEST))
        states = cm.check(ROOT, manifest)
        self.assertEqual({p: s for p, s in states.items() if s != cm.UNCHANGED}, {})
        self.assertEqual(sorted(manifest["files"]), cm.automation_files(ROOT))


if __name__ == "__main__":
    unittest.main()
