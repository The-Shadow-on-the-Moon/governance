import json
import os
import shutil
import sys
import tempfile
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kit_common  # noqa: E402
import check_manifest  # noqa: E402
import migrations  # noqa: E402
import preflight  # noqa: E402
import upgrade  # noqa: E402
from migrations import f01_files, m01_manifest  # noqa: E402


def fake_step(name, needs, gate=None, fail=False, log=None):
    state = {"needs": needs}

    def apply(ctx, run):
        run.do(name + " applied", lambda: state.update(needs=fail))
        (log if log is not None else []).append(name)

    return types.SimpleNamespace(ID=name, SINCE="V0.1.0", TITLE=name, GATE=gate, needed=lambda ctx: state["needs"],
                                 plan=lambda ctx: ["do " + name], apply=apply)


class FakeContext:
    def __init__(self, flags=()):
        self.flags, self.refreshed = set(flags), 0

    def refresh(self):
        self.refreshed += 1


class ChainTests(unittest.TestCase):
    def test_steps_run_in_order_and_each_is_checked_again(self):
        order = []
        ctx = FakeContext()
        run, report = upgrade.chain(ctx, False, modules=[fake_step("S1", True, log=order), fake_step("S2", False), fake_step("S3", True, log=order)])
        self.assertEqual(order, ["S1", "S3"])
        self.assertEqual([e["status"] for e in report], ["done", "not needed", "done"])
        self.assertEqual(ctx.refreshed, 2)

    def test_a_dry_run_applies_nothing_but_logs_what_it_would(self):
        step = fake_step("S1", True)
        run, report = upgrade.chain(FakeContext(), True, modules=[step])
        self.assertTrue(step.needed(None))
        self.assertEqual(report[0]["status"], "would apply")
        self.assertEqual(report[0]["plan"], ["do S1"])

    def test_a_gated_step_waits_for_its_flag(self):
        order = []
        run, report = upgrade.chain(FakeContext(), False, modules=[fake_step("G", True, gate="views", log=order)])
        self.assertEqual((order, report[0]["status"]), ([], "gated"))
        run, report = upgrade.chain(FakeContext({"views"}), False, modules=[fake_step("G", True, gate="views", log=order)])
        self.assertEqual((order, report[0]["status"]), (["G"], "done"))

    def test_a_step_that_leaves_the_project_lacking_stops_the_chain(self):
        order = []
        run, report = upgrade.chain(FakeContext(), False, modules=[fake_step("S1", True, fail=True, log=order), fake_step("S2", True, log=order)])
        self.assertEqual(order, ["S1"])
        self.assertEqual([e["status"] for e in report], ["failed"])
        self.assertTrue(any("FAILED" in line for line in run.log))

    def test_an_error_of_a_step_stops_the_chain(self):
        def boom(ctx, run):
            raise kit_common.KitError("no")

        step = fake_step("S1", True)
        step.apply = boom
        run, report = upgrade.chain(FakeContext(), False, modules=[step, fake_step("S2", True)])
        self.assertEqual((report[0]["status"], report[0]["error"], len(report)), ("failed", "no", 1))

    def test_only_and_pause(self):
        slept = []
        run, report = upgrade.chain(FakeContext(), False, only="S2", modules=[fake_step("S1", True), fake_step("S2", True)], pause=3,
                                    sleep=slept.append)
        self.assertEqual(([e["id"] for e in report], slept), (["S2"], [3]))

    def test_decisions_left_by_a_step_are_not_a_failure(self):
        ctx = FakeContext()
        step = fake_step("L", True, fail=True)
        original = step.apply

        def apply(c, run):
            original(c, run)
            c.decisions = [{"number": 1}]

        step.apply = apply
        run, report = upgrade.chain(ctx, False, modules=[step])
        self.assertEqual(report[0]["status"], "done")


class RegistryTests(unittest.TestCase):
    def test_every_step_module_has_what_the_runner_needs_and_ids_are_unique(self):
        modules = migrations.steps()
        self.assertEqual(len(modules), len(migrations.ORDER))
        self.assertEqual(len({m.ID for m in modules}), len(modules))
        for m in modules:
            for name in ("ID", "SINCE", "TITLE", "GATE", "needed", "plan", "apply"):
                self.assertTrue(hasattr(m, name), (m.__name__, name))

    def test_every_module_file_is_in_the_order(self):
        names = {n[:-3] for n in os.listdir(os.path.join(ROOT, "tools", "migrations")) if n.endswith(".py") and n != "__init__.py"}
        self.assertEqual(names, set(migrations.ORDER))

    def test_destructive_or_administrative_steps_are_gated(self):
        gates = {m.ID: m.GATE for m in migrations.steps()}
        self.assertEqual({k: v for k, v in gates.items() if v}, {"A5": "views", "A7b": "delete_version_number", "L1": "convert_legacy"})


class FakeBoardClient:
    def __init__(self, values):
        self.values = dict(values)  # item -> option name
        self.options = [{"id": "o1", "name": "Committed", "color": "BLUE", "description": "c"}, {"id": "o2", "name": "Merged", "color": "GREEN", "description": "m"}]
        self.sets = []
        self.generation = 0

    def graphql(self, query, variables=None):
        if "updateProjectV2Field" in query:
            self.generation += 1
            self.options = [dict(o, id="n%d-%d" % (self.generation, i)) for i, o in enumerate(variables["o"])]
            self.values = {}  # GitHub clears the values when the options are written
            self.written = [o["name"] for o in variables["o"]]
            return {}
        if "singleSelectOptions" in query or "options{id name color" in query:
            return {"node": {"field": {"id": "F", "options": self.options}}}
        return {"node": {"items": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                                   "nodes": [{"id": i, "v": {"name": v}} for i, v in self.values.items()]}}}

    def set_project_field(self, project, item, field, value):
        name = next(o["name"] for o in self.options if o["id"] == value["singleSelectOptionId"])
        self.values[item] = name
        self.sets.append((item, name))


class AddOptionsTests(unittest.TestCase):
    def context(self, client, folder):
        board = preflight.Board("P", 1, "b", {"Delivery": {"id": "F", "type": "SINGLE_SELECT", "options": {o["name"]: o["id"] for o in client.options}}})
        ctx = types.SimpleNamespace(project_client=client, board=board, root=folder)

        def refresh():
            ctx.board = preflight.Board("P", 1, "b", {"Delivery": {"id": "F", "type": "SINGLE_SELECT", "options": {o["name"]: o["id"] for o in client.options}}})

        ctx.refresh = refresh
        return ctx

    def test_the_value_of_every_ticket_survives_the_new_option_ids(self):
        client = FakeBoardClient({"i1": "Committed", "i2": "Merged", "i3": "Merged"})
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".git"))
            ctx = self.context(client, folder)
            run = upgrade.finalize.Runner(False)
            added = migrations.add_options(ctx, run, "Delivery", ["Implemented", "Merged"])
            self.assertEqual(added, ["Implemented"])
            self.assertEqual(client.written, ["Committed", "Merged", "Implemented"])
            self.assertEqual(client.values, {"i1": "Committed", "i2": "Merged", "i3": "Merged"})
            with open(os.path.join(folder, kit_common.STATE_FOLDER, "restore-Delivery.json"), encoding="utf-8") as h:
                self.assertEqual(json.load(h)["values"], {"i1": "Committed", "i2": "Merged", "i3": "Merged"})

    def test_a_dry_run_changes_nothing_and_an_existing_option_is_not_added(self):
        client = FakeBoardClient({"i1": "Committed"})
        ctx = self.context(client, tempfile.gettempdir())
        run = upgrade.finalize.Runner(True)
        self.assertEqual(migrations.add_options(ctx, run, "Delivery", ["Implemented"]), ["Implemented"])
        self.assertEqual(client.generation, 0)
        self.assertEqual(migrations.add_options(ctx, run, "Delivery", ["Merged"]), [])

    def test_values_that_do_not_come_back_stop_with_an_error(self):
        client = FakeBoardClient({"i1": "Committed"})
        original = client.set_project_field
        client.set_project_field = lambda *a: None
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".git"))
            with self.assertRaises(kit_common.KitError):
                migrations.add_options(self.context(client, folder), upgrade.finalize.Runner(False), "Delivery", ["Implemented"])
        client.set_project_field = original


class FilesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.standard = os.path.join(self.tmp.name, "standard")
        self.project = os.path.join(self.tmp.name, "project")
        for base in (self.standard, self.project):
            os.makedirs(os.path.join(base, ".githooks"))
            os.makedirs(os.path.join(base, ".git"))
        self.write(self.standard, ".githooks/hooks.py", "new\n")
        self.write(self.standard, ".githooks/pre-commit", "same\n")
        self.write(self.project, ".githooks/pre-commit", "same\n")
        self.write(self.project, ".githooks/old-hook", "obsolete\n")

    def read(self, path):
        with open(path, encoding="utf-8") as h:
            return h.read()

    def write(self, base, rel, text):
        with open(os.path.join(base, rel), "w", encoding="utf-8", newline="") as h:
            h.write(text)

    def ctx(self, flags=(), identity=None):
        survey = {"files": {"identity": {"files": identity or {}}}}
        return types.SimpleNamespace(root=self.project, standard_root=self.standard, target="V9.9.9", flags=set(flags), survey=survey)

    def test_missing_and_different_files_are_copied_and_the_replaced_one_is_saved(self):
        self.write(self.project, ".githooks/hooks.py", "old\n")
        ctx = self.ctx(identity={".githooks/hooks.py": ["V0.1.0"]})
        self.assertEqual(f01_files.differing(ctx), [".githooks/hooks.py"])
        run = upgrade.finalize.Runner(False)
        f01_files.apply(ctx, run)
        self.assertEqual(self.read(os.path.join(self.project, ".githooks", "hooks.py")), "new\n")
        self.assertEqual(self.read(os.path.join(self.project, kit_common.STATE_FOLDER, "backup", ".githooks", "hooks.py")), "old\n")
        self.assertFalse(f01_files.needed(ctx))
        self.assertTrue(any("old-hook, kept" in line or "old-hook" in line for line in run.log))
        self.assertTrue(os.path.exists(os.path.join(self.project, ".githooks", "old-hook")))

    def test_a_file_edited_locally_stops_unless_the_flag_is_given(self):
        self.write(self.project, ".githooks/hooks.py", "mine\n")
        ctx = self.ctx(identity={".githooks/hooks.py": []})
        with self.assertRaises(kit_common.KitError):
            f01_files.apply(ctx, upgrade.finalize.Runner(False))
        self.assertEqual(self.read(os.path.join(self.project, ".githooks", "hooks.py")), "mine\n")
        f01_files.apply(self.ctx(("overwrite_edited",), {".githooks/hooks.py": []}), upgrade.finalize.Runner(False))
        self.assertEqual(self.read(os.path.join(self.project, ".githooks", "hooks.py")), "new\n")

    def test_a_file_an_earlier_version_had_is_removed_with_a_backup_and_an_edited_one_is_kept(self):
        old = "old script" + chr(10)
        os.makedirs(os.path.join(self.project, ".github", "scripts"))
        self.write(self.project, ".github/scripts/gone.py", old)
        self.write(self.project, ".github/scripts/edited.py", "mine" + chr(10))
        self.write(self.project, ".githooks/hooks.py", "new" + chr(10))
        import hashlib
        digest = hashlib.sha256(old.encode()).hexdigest()
        ctx = self.ctx()
        ctx.table = {"versions": {"V0.1.0": {"files": {".github/scripts/gone.py": digest, ".github/scripts/edited.py": "0" * 64}}}}
        self.assertEqual(f01_files.removable(ctx), [".github/scripts/gone.py"])
        self.assertIn(".github/scripts/edited.py", f01_files.obsolete(ctx))
        f01_files.apply(ctx, upgrade.finalize.Runner(False))
        self.assertFalse(os.path.exists(os.path.join(self.project, ".github", "scripts", "gone.py")))
        self.assertEqual(self.read(os.path.join(self.project, kit_common.STATE_FOLDER, "backup", ".github", "scripts", "gone.py")), old)
        self.assertTrue(os.path.exists(os.path.join(self.project, ".github", "scripts", "edited.py")))

    def test_a_dry_run_copies_nothing(self):
        f01_files.apply(self.ctx(), upgrade.finalize.Runner(True))
        self.assertFalse(os.path.exists(os.path.join(self.project, ".githooks", "hooks.py")))
        self.assertFalse(os.path.exists(os.path.join(self.project, kit_common.STATE_FOLDER)))

    def test_the_manifest_is_written_with_the_target_version(self):
        ctx = self.ctx()
        f01_files.apply(ctx, upgrade.finalize.Runner(False))
        self.assertTrue(m01_manifest.needed(ctx))
        m01_manifest.apply(ctx, upgrade.finalize.Runner(False))
        written = check_manifest.load(os.path.join(self.project, check_manifest.MANIFEST))
        self.assertEqual(written["standard"], "V9.9.9")
        self.assertIn(".githooks/hooks.py", written["files"])
        self.assertFalse(m01_manifest.needed(ctx))


class DirtyTreeTests(unittest.TestCase):
    def test_what_the_chain_wrote_does_not_block_its_next_step_but_other_changes_do(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            project, standard = os.path.join(folder, "p"), os.path.join(folder, "s")
            for base in (project, standard):
                os.makedirs(os.path.join(base, ".githooks"))
            with open(os.path.join(standard, ".githooks", "hooks.py"), "w") as h:
                h.write("x")
            subprocess.run(["git", "init", "-q", project], check=True)
            ctx = types.SimpleNamespace(root=project, standard_root=standard, table=None)
            with open(os.path.join(project, ".githooks", "hooks.py"), "w") as h:
                h.write("x")
            os.makedirs(os.path.join(project, "__pycache__"))
            with open(os.path.join(project, "__pycache__", "a.pyc"), "w") as h:
                h.write("x")
            self.assertEqual(upgrade.dirty_outside_the_chain(ctx), [])
            with open(os.path.join(project, "mine.txt"), "w") as h:
                h.write("x")
            self.assertEqual(upgrade.dirty_outside_the_chain(ctx), ["mine.txt"])


class TargetTests(unittest.TestCase):
    def test_the_target_is_the_standard_of_the_checkout_and_a_placeholder_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, ".github"))
            for standard in ("V1.2.3", check_manifest.PLACEHOLDER):
                with open(os.path.join(folder, check_manifest.MANIFEST), "w", encoding="utf-8") as h:
                    json.dump({"standard": standard, "files": {}}, h)
                if standard == "V1.2.3":
                    self.assertEqual(upgrade.target_version(folder), "V1.2.3")
                else:
                    with self.assertRaises(kit_common.KitError):
                        upgrade.target_version(folder)

    def test_blockers_include_unsupported_and_unknown_states(self):
        ctx = types.SimpleNamespace(survey={"blockers": ["x"], "state": {"detected": "unsupported"}})
        self.assertEqual(len(upgrade.blocking(ctx)), 2)
        ctx = types.SimpleNamespace(survey={"state": {"detected": "version"}})
        self.assertEqual(upgrade.blocking(ctx), [])

    def test_legacy_version_tickets_block_until_the_conversion_is_asked_for(self):
        survey_ = {"board": {"legacy_version_tickets": {"total": 3}}, "state": {"detected": "version"}}
        found = upgrade.blocking(types.SimpleNamespace(survey=survey_, flags=set()))
        self.assertEqual(len(found), 1)
        self.assertIn("3 legacy Version ticket(s)", found[0])
        self.assertEqual(upgrade.blocking(types.SimpleNamespace(survey=survey_, flags={"convert_legacy"})), [])
        none = {"board": {"legacy_version_tickets": {"total": 0}}, "state": {"detected": "version"}}
        self.assertEqual(upgrade.blocking(types.SimpleNamespace(survey=none, flags=set())), [])

    def test_main_needs_a_path(self):
        self.assertEqual(upgrade.main([]), 1)


if __name__ == "__main__":
    unittest.main()
