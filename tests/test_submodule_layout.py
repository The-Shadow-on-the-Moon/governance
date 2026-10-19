import json
import os
import subprocess
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kit_common  # noqa: E402
import check_manifest  # noqa: E402
import survey  # noqa: E402
import upgrade  # noqa: E402
from finalize import Runner  # noqa: E402
from migrations import s01_pin  # noqa: E402

ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.com", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.com"}


def git(folder, *args):
    result = subprocess.run(["git", "-c", "protocol.file.allow=always", *args], cwd=folder, env=ENV, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, (args, result.stderr)
    return result.stdout.strip()


def commit_version(standard, version):
    path = os.path.join(standard, check_manifest.MANIFEST)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"standard": version, "files": {}}, handle)

    git(standard, "add", "-A")
    git(standard, "commit", "-q", "-m", "Finalize " + version)
    return git(standard, "rev-parse", "HEAD")


class Layout:
    """A standard with two finalized versions, and a project that carries it as a submodule pinned at the first."""

    def __init__(self, folder):
        self.standard = os.path.join(folder, "standard")
        self.project = os.path.join(folder, "project")
        os.makedirs(self.standard)
        git(self.standard, "init", "-q")
        os.makedirs(os.path.join(self.standard, "guides"))
        with open(os.path.join(self.standard, "guides", "README.md"), "w") as handle:
            handle.write("x")
        self.first = commit_version(self.standard, "V0.1.0")
        self.second = commit_version(self.standard, "V0.2.0")
        os.makedirs(self.project)
        git(self.project, "init", "-q")
        self.folder = os.path.join(self.project, *survey.EMBEDDED.split("/"))
        git(self.project, "clone", "-q", self.standard, self.folder)  # what `git submodule add` does, without its cost
        git(self.folder, "checkout", "-q", "--detach", self.first)
        git(self.project, "config", "-f", ".gitmodules", "submodule.{}.path".format(survey.EMBEDDED), survey.EMBEDDED)
        git(self.project, "config", "-f", ".gitmodules", "submodule.{}.url".format(survey.EMBEDDED), self.standard)
        git(self.project, "add", ".gitmodules", survey.EMBEDDED)
        git(self.project, "commit", "-q", "-m", "Add the standard")


class SurveyTests(unittest.TestCase):
    def test_a_project_without_the_submodule_has_none(self):
        with tempfile.TemporaryDirectory() as folder:
            git(folder, "init", "-q")
            self.assertEqual(survey.facts_embedded(folder)["present"], False)

    def test_a_plain_copy_of_the_standard_is_reported_to_check_by_hand(self):
        with tempfile.TemporaryDirectory() as folder:
            git(folder, "init", "-q")
            os.makedirs(os.path.join(folder, "doc", "governance", "guides"))
            facts = survey.facts_embedded(folder)
            self.assertFalse(facts["present"])
            self.assertIn("not a git submodule", facts["unknown"][0])

    def test_the_pin_its_version_and_the_checkout_are_read(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            facts = survey.facts_embedded(layout.project)
            self.assertEqual((facts["present"], facts["pinned"], facts["pinned_standard"], facts["checked_out"]),
                             (True, layout.first, "V0.1.0", layout.first))
            self.assertEqual((facts["initialized"], facts["clean"], facts["shallow"], facts["gitmodules_shallow"]), (True, True, False, False))
            self.assertEqual(facts["url"], layout.standard)

    def test_the_pointer_moved_by_the_chain_does_not_make_the_tree_dirty(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            git(layout.folder, "checkout", "-q", "--detach", layout.second)
            self.assertTrue(survey.survey(layout.project, None, None, None, {})["repository"]["clean_tree"])
            with open(os.path.join(layout.project, "mine.txt"), "w") as handle:
                handle.write("x")
            self.assertFalse(survey.survey(layout.project, None, None, None, {})["repository"]["clean_tree"])

    def test_blockers_name_an_uninitialized_shallow_or_unclean_submodule(self):
        base = {"present": True}
        self.assertIn("git submodule update --init", survey.blockers({}, {}, {**base, "initialized": False})[0])
        self.assertIn("fetch --unshallow", survey.blockers({}, {}, {**base, "initialized": True, "shallow": True})[0])
        self.assertIn("fetch --unshallow", survey.blockers({}, {}, {**base, "initialized": True, "gitmodules_shallow": True})[0])
        self.assertIn("uncommitted", survey.blockers({}, {}, {**base, "initialized": True, "clean": False})[0])
        self.assertEqual(survey.blockers({}, {}, {**base, "initialized": True, "clean": True, "shallow": False}), [])
        self.assertEqual(survey.blockers({}, {}, {"present": False}), [])

    def test_the_render_names_the_pin(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            text = survey.render(survey.survey(layout.project, None, None, None, {}))
            self.assertIn("pinned at {} (V0.1.0)".format(layout.first[:8]), text)


class PinStepTests(unittest.TestCase):
    def context(self, layout, standard):
        return types.SimpleNamespace(root=layout.project, standard_root=standard, survey={"embedded": survey.facts_embedded(layout.project)})

    def staged(self, layout):
        return git(layout.project, "ls-files", "-s", "--", survey.EMBEDDED).split()[1]

    def test_the_pin_moves_to_the_commit_of_an_outside_checkout_and_is_staged(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            ctx = self.context(layout, layout.standard)
            self.assertTrue(s01_pin.needed(ctx))
            self.assertIn("move the submodule", s01_pin.plan(ctx)[0])
            s01_pin.apply(ctx, Runner(False))
            self.assertEqual((self.staged(layout), git(layout.folder, "rev-parse", "HEAD")), (layout.second, layout.second))
            self.assertFalse(s01_pin.needed(self.context(layout, layout.standard)))
            self.assertEqual(upgrade.dirty_outside_the_chain(types.SimpleNamespace(root=layout.project, standard_root=layout.standard, table=None)), [])

    def test_run_from_the_submodule_itself_only_stages_the_pointer(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            git(layout.folder, "checkout", "-q", "--detach", layout.second)
            ctx = self.context(layout, layout.folder)
            self.assertEqual(len(s01_pin.plan(ctx)), 1)
            s01_pin.apply(ctx, Runner(False))
            self.assertEqual(self.staged(layout), layout.second)

    def test_a_dry_run_moves_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            run = Runner(True)
            s01_pin.apply(self.context(layout, layout.standard), run)
            self.assertEqual((self.staged(layout), git(layout.folder, "rev-parse", "HEAD")), (layout.first, layout.first))
            self.assertEqual(len(run.log), 2)

    def test_there_is_no_step_without_the_submodule_or_when_the_pin_is_the_target(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            self.assertFalse(s01_pin.needed(types.SimpleNamespace(root=layout.project, standard_root=layout.standard, survey={})))
            self.assertFalse(s01_pin.needed(types.SimpleNamespace(root=layout.project, standard_root=layout.standard,
                                                                  survey={"embedded": {"present": False}})))
            git(layout.folder, "checkout", "-q", "--detach", layout.second)
            git(layout.project, "add", survey.EMBEDDED)
            self.assertFalse(s01_pin.needed(self.context(layout, layout.folder)))

    def test_a_failing_git_command_is_a_refusal(self):
        with tempfile.TemporaryDirectory() as folder:
            layout = Layout(folder)
            with self.assertRaises(kit_common.KitError):
                s01_pin.git(layout.project, "checkout", "--detach", "0" * 40)


if __name__ == "__main__":
    unittest.main()
