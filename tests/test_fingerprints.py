import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import build_fingerprints as bf  # noqa: E402
import check_manifest  # noqa: E402


def git(root, *args, env=None):
    subprocess.run(["git", "-c", "user.name=T", "-c", "user.email=t@example.com", "-c", "commit.gpgsign=false",
                    "-c", "core.autocrlf=false", *args], cwd=root, check=True, capture_output=True, text=True,
                   env=dict(os.environ, **(env or {})))


def write(root, relative, data):
    path = os.path.join(root, *relative.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "wb") as handle:
        handle.write(data if isinstance(data, bytes) else data.encode("utf-8"))


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def changelog_text(*versions):
    """A changelog with the given finalized versions, newest first."""
    lines = ["# Changelog", ""]

    for version in versions:
        lines += ["## {} — 2026-10-0{} 10:00 UTC".format(version, version[-1]), "### Build 20261001100000 (branch a)",
                  "#### #1 — Thing", "- x.", ""]

    return "\n".join(lines)


class Repo:
    """A temporary repository standing in for the standard."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        git(self.root, "init", "-b", "main")

    def commit(self, subject, files=None, manifest=None, changelog=None):
        for relative, data in (files or {}).items():
            write(self.root, relative, data)

        if changelog is not None:
            write(self.root, "CHANGELOG.md", changelog)

        if manifest is not None:
            check_manifest.write(self.root, check_manifest.build(self.root, manifest))

        git(self.root, "add", "-A")
        git(self.root, "commit", "-q", "--allow-empty", "-m", subject)

    def cleanup(self):
        self.tmp.cleanup()


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.root = self.repo.root

    def two_versions(self):
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 1\n", ".githooks/pre-commit": "hook\n"}, "V0.1.0",
                         changelog_text("V0.1.0"))
        self.repo.commit("Finalize V0.2.0", {".github/scripts/a.py": "a = 2\n"}, "V0.2.0", changelog_text("V0.2.0", "V0.1.0"))

    def test_each_finalized_version_is_found_by_its_commit_with_the_hash_of_its_files(self):
        self.two_versions()
        versions = bf.build(self.root)["versions"]
        self.assertEqual(sorted(versions), ["V0.1.0", "V0.2.0"])
        self.assertEqual(versions["V0.1.0"]["method"], "finalize-commit")
        self.assertEqual(versions["V0.1.0"]["files"][".github/scripts/a.py"], sha("a = 1\n"))
        self.assertEqual(versions["V0.2.0"]["files"][".github/scripts/a.py"], sha("a = 2\n"))
        self.assertEqual(versions["V0.2.0"]["files"][".githooks/pre-commit"], sha("hook\n"))
        self.assertEqual(versions["V0.2.0"]["stale_manifest"], [])

    def test_a_subject_that_only_looks_like_a_finalize_is_ignored(self):
        self.two_versions()
        self.repo.commit("Finalize writes the manifest standard; manual finalize comment")
        self.repo.commit("Finalize V0.3.0 by hand")
        self.assertEqual(sorted(bf.finalize_commits(self.root)), ["V0.1.0", "V0.2.0"])

    def test_the_oldest_commit_of_a_version_wins(self):
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 1\n"}, "V0.1.0", changelog_text("V0.1.0"))
        first = bf.finalize_commits(self.root)["V0.1.0"]
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 9\n"})
        self.assertEqual(bf.finalize_commits(self.root)["V0.1.0"], first)

    def test_line_endings_do_not_change_a_hash(self):
        crlf = "a = 1" + chr(13) + chr(10)
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": crlf.encode("utf-8")}, "V0.1.0", changelog_text("V0.1.0"))
        entry = bf.build(self.root)["versions"]["V0.1.0"]
        self.assertEqual(entry["files"][".github/scripts/a.py"], sha("a = 1\n"))
        self.assertEqual(entry["files"][".github/scripts/a.py"], check_manifest.file_hash(os.path.join(self.root, ".github/scripts/a.py")))

    def test_the_standard_a_manifest_names_is_recorded_but_not_trusted(self):
        self.repo.commit("Finalize V0.8.0", {".github/scripts/a.py": "a = 1\n"}, "V0.7.1", changelog_text("V0.8.0"))
        versions = bf.build(self.root)["versions"]
        self.assertEqual(list(versions), ["V0.8.0"])
        self.assertEqual(versions["V0.8.0"]["manifest_standard"], "V0.7.1")

    def test_a_manifest_hash_that_does_not_match_the_file_is_reported(self):
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 1\n"}, "V0.1.0", changelog_text("V0.1.0"))
        manifest = check_manifest.load(os.path.join(self.root, check_manifest.MANIFEST))
        manifest["files"][".github/scripts/a.py"] = "0" * 64
        check_manifest.write(self.root, manifest)
        self.repo.commit("Finalize V0.2.0", {}, None, changelog_text("V0.2.0", "V0.1.0"))
        self.assertEqual(bf.build(self.root)["versions"]["V0.2.0"]["stale_manifest"], [".github/scripts/a.py"])

    def test_a_file_the_manifest_lists_but_the_commit_lacks_is_reported_missing(self):
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 1\n"}, "V0.1.0", changelog_text("V0.1.0"))
        manifest = check_manifest.load(os.path.join(self.root, check_manifest.MANIFEST))
        manifest["files"][".github/scripts/gone.py"] = "1" * 64
        check_manifest.write(self.root, manifest)
        self.repo.commit("Finalize V0.2.0", {}, None, changelog_text("V0.2.0", "V0.1.0"))
        self.assertEqual(bf.build(self.root)["versions"]["V0.2.0"]["missing"], [".github/scripts/gone.py"])

    def test_a_version_without_a_manifest_is_judged_by_the_patterns(self):
        self.repo.commit("Finalize V0.2.0", {".github/pull_request_template.md": "t\n", "README.md": "r\n"}, None, changelog_text("V0.2.0"))
        entry = bf.build(self.root)["versions"]["V0.2.0"]
        self.assertEqual(list(entry["files"]), [".github/pull_request_template.md"])
        self.assertIsNone(entry["manifest_standard"])

    def test_a_version_finalized_by_hand_is_found_by_its_heading(self):
        self.repo.commit("Start", {".github/scripts/a.py": "a = 1\n"}, "V0.1.0", changelog_text("V0.1.0"))
        self.repo.commit("Release the first version by hand")
        versions = bf.build(self.root)["versions"]
        self.assertEqual(versions["V0.1.0"]["method"], "changelog-heading")
        self.assertEqual(versions["V0.1.0"]["files"][".github/scripts/a.py"], sha("a = 1\n"))

    def test_a_hotfix_counts_once_it_has_its_released_tag(self):
        self.repo.commit("Finalize V1.0.0", {".github/scripts/a.py": "a = 1\n"}, "V1.0.0", changelog_text("V1.0.0"))
        git(self.root, "switch", "-c", "hotfix-v1-0-0-fix")
        self.repo.commit("Finalize V1.0.0-HF1", {".github/scripts/a.py": "a = 1.1\n"}, "V1.0.0-HF1")
        git(self.root, "switch", "main")
        self.assertEqual(list(bf.build(self.root)["versions"]), ["V1.0.0"])
        git(self.root, "tag", "released/V1.0.0-HF1", "hotfix-v1-0-0-fix")
        versions = bf.build(self.root)["versions"]
        self.assertEqual(list(versions), ["V1.0.0", "V1.0.0-HF1"])
        self.assertEqual(versions["V1.0.0-HF1"]["files"][".github/scripts/a.py"], sha("a = 1.1\n"))

    def test_a_trial_hotfix_is_not_a_version(self):
        self.repo.commit("Finalize V1.0.0", {".github/scripts/a.py": "a = 1\n"}, "V1.0.0", changelog_text("V1.0.0"))
        git(self.root, "switch", "-c", "hotfix-v9-9-9-trial")
        self.repo.commit("Finalize V9.9.9-HF1", {}, "V1.0.0")
        git(self.root, "tag", "test/released/V9.9.9-HF1")
        git(self.root, "switch", "main")
        self.assertEqual(list(bf.build(self.root)["versions"]), ["V1.0.0"])

    def test_a_shallow_clone_is_refused(self):
        self.two_versions()
        clone = tempfile.TemporaryDirectory()
        self.addCleanup(clone.cleanup)
        subprocess.run(["git", "clone", "-q", "--depth", "1", "file://" + self.root.replace(os.sep, "/"), clone.name],
                       check=True, capture_output=True, text=True)

        with self.assertRaises(bf.FingerprintError):
            bf.build(clone.name)

        self.assertEqual(bf.main(["--repo", clone.name]), 2)

    def test_the_cache_is_used_while_head_has_not_moved(self):
        self.two_versions()
        cache = os.path.join(self.root, "..", "fingerprint-cache-{}.json".format(os.getpid()))
        self.addCleanup(lambda: os.path.exists(cache) and os.remove(cache))
        first = bf.load_or_build(self.root, cache)
        with open(cache, encoding="utf-8") as handle:
            stored = json.load(handle)

        stored["versions"]["V0.1.0"]["method"] = "from the cache"

        with open(cache, "w", encoding="utf-8") as handle:
            json.dump(stored, handle)

        self.assertEqual(bf.load_or_build(self.root, cache)["versions"]["V0.1.0"]["method"], "from the cache")
        self.repo.commit("Another commit")
        self.assertEqual(bf.load_or_build(self.root, cache)["versions"]["V0.1.0"]["method"], first["versions"]["V0.1.0"]["method"])

    def test_option_errors(self):
        self.assertEqual(bf.main(["--repo"]), 2)
        self.assertEqual(bf.main(["--identify", "--json"]), 2)


class IdentifyTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.cleanup)
        self.repo.commit("Finalize V0.1.0", {".github/scripts/a.py": "a = 1\n", ".githooks/pre-commit": "hook\n"}, "V0.1.0",
                         changelog_text("V0.1.0"))
        self.repo.commit("Finalize V0.2.0", {".github/scripts/a.py": "a = 2\n"}, "V0.2.0", changelog_text("V0.2.0", "V0.1.0"))
        self.repo.commit("Finalize V0.3.0", {".githooks/pre-commit": "hook 2\n"}, "V0.3.0", changelog_text("V0.3.0", "V0.2.0", "V0.1.0"))
        self.repo.commit("Finalize V0.3.1", {}, "V0.3.1", changelog_text("V0.3.1", "V0.3.0", "V0.2.0", "V0.1.0"))
        self.table = bf.build(self.repo.root)
        self.project = tempfile.TemporaryDirectory()
        self.addCleanup(self.project.cleanup)

    def put(self, files):
        for relative, text in files.items():
            write(self.project.name, relative, text)

    def test_a_project_with_no_automation_file(self):
        self.assertEqual(bf.identify(self.project.name, self.table)["state"], "none")

    def test_the_files_of_one_version_match_it(self):
        self.put({".github/scripts/a.py": "a = 2\n", ".githooks/pre-commit": "hook\n"})
        result = bf.identify(self.project.name, self.table)
        self.assertEqual((result["state"], result["versions"]), ("match", ["V0.2.0"]))

    def test_versions_that_changed_no_automation_file_are_indistinguishable(self):
        self.put({".github/scripts/a.py": "a = 2\n", ".githooks/pre-commit": "hook 2\n"})
        result = bf.identify(self.project.name, self.table)
        self.assertEqual((result["state"], result["versions"]), ("match", ["V0.3.0", "V0.3.1"]))

    def test_files_from_two_versions_are_mixed(self):
        self.put({".github/scripts/a.py": "a = 1\n", ".githooks/pre-commit": "hook 2\n"})
        result = bf.identify(self.project.name, self.table)
        self.assertEqual(result["state"], "mixed")
        self.assertEqual(result["files"][".github/scripts/a.py"], ["V0.1.0"])
        self.assertEqual(result["files"][".githooks/pre-commit"], ["V0.3.0", "V0.3.1"])

    def test_an_edited_file_is_modified_and_the_closest_versions_are_named(self):
        self.put({".github/scripts/a.py": "a = 2 # edited\n", ".githooks/pre-commit": "hook\n"})
        result = bf.identify(self.project.name, self.table)
        self.assertEqual(result["state"], "modified")
        self.assertEqual(result["files"][".github/scripts/a.py"], [])
        self.assertEqual(result["closest"], ["V0.1.0", "V0.2.0"])

    def test_a_missing_file_is_not_a_match(self):
        self.put({".github/scripts/a.py": "a = 2\n"})
        result = bf.identify(self.project.name, self.table)
        self.assertEqual(result["state"], "mixed" if all(result["files"].values()) else "modified")
        self.assertEqual(result["versions"], [])


class RealHistoryTests(unittest.TestCase):
    def setUp(self):
        if bf.is_shallow(ROOT):
            self.skipTest("the history of this clone is shallow")

    def test_every_version_of_the_changelog_is_fingerprinted(self):
        table = bf.build(ROOT)["versions"]
        finals = bf.changelog_versions(ROOT, "HEAD")
        self.assertTrue(set(finals) <= set(table))
        self.assertTrue(all(table[v]["commit"] for v in finals))
        self.assertNotIn("V9.9.8-HF1", table)  # a trial hotfix of the automation's own tests

    def test_the_first_automation_has_the_23_files_the_changelog_names(self):
        self.assertEqual(len(bf.build(ROOT)["versions"]["V0.3.0"]["files"]), 23)

    def test_no_manifest_of_the_history_disagrees_with_its_files(self):
        table = bf.build(ROOT)["versions"]
        self.assertEqual({v: e["stale_manifest"] for v, e in table.items() if e["stale_manifest"]}, {})


if __name__ == "__main__":
    unittest.main()
