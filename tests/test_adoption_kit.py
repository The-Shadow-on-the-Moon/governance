import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kit_common  # noqa: E402,F401
import upgrade  # noqa: E402

INSTRUCTION = os.path.join(ROOT, "adoption", "ADOPT-OR-UPDATE-GOVERNANCE.md")
COMMANDS = os.path.join(ROOT, ".claude", "commands")


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def named_things(text):
    """The tools, the guides and the scripts a text names."""
    return {"tools": set(re.findall(r"tools/([a-z_]+\.py)", text)),
            "guides": set(re.findall(r"guides/([0-9a-z-]+\.md)", text)),
            "scripts": set(re.findall(r"\.github/scripts/([a-z_]+\.py)", text))}


class NamedThingsExist(unittest.TestCase):
    def check(self, name, text):
        found = named_things(text)
        for tool in found["tools"]:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "tools", tool)), "{} names tools/{}".format(name, tool))
        for guide in found["guides"]:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "guides", guide)), "{} names guides/{}".format(name, guide))
        for script in found["scripts"]:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, ".github", "scripts", script)), "{} names {}".format(name, script))

    def test_the_instruction_file_names_only_things_that_exist(self):
        self.check("the instruction file", read(INSTRUCTION))

    def test_every_command_names_only_things_that_exist(self):
        if not os.path.isdir(COMMANDS):
            self.skipTest("no commands yet")
        for name in sorted(os.listdir(COMMANDS)):
            self.check(name, read(os.path.join(COMMANDS, name)))


class InstructionFileTests(unittest.TestCase):
    def setUp(self):
        self.text = read(INSTRUCTION)

    def test_it_has_the_starter_prompt_and_the_ten_phases_in_order(self):
        self.assertIn("Follow ADOPT-OR-UPDATE-GOVERNANCE.md in this folder, phase by phase, and stop at every gate.", self.text)
        phases = re.findall(r"^## Phase (\d+):", self.text, re.M)
        self.assertEqual(phases, [str(n) for n in range(10)])

    def test_it_states_the_safety_rules(self):
        for needle in ("python -I", "full history", "commit SHA", "data, never instructions", "dry run", "Stop, do not improvise",
                       "Narrowest token", "Resuming starts with a new survey", "no assistant attribution"):
            self.assertIn(needle.lower(), self.text.lower(), needle)

    def test_the_flags_it_gives_upgrade_are_flags_upgrade_understands(self):
        mentioned = set(re.findall(r"`(--(?:with-views|convert-legacy|include-open|delete-version-number|overwrite-edited))", self.text))
        self.assertTrue(mentioned)
        self.assertTrue(mentioned <= set(upgrade.FLAGS), mentioned - set(upgrade.FLAGS))

    def test_the_steps_it_names_are_steps_of_the_chain(self):
        import migrations
        ids = {m.ID for m in migrations.steps()}
        for step in re.findall(r"--only (F1|M1|S1|[AL]\d+b?)\b", self.text):
            self.assertIn(step, ids)

    def test_the_workflow_run_it_names_has_those_inputs(self):
        workflow = read(os.path.join(ROOT, ".github", "workflows", "versioning.yml"))
        for needle in ("mode:", "dry_run:", "- finalize"):
            self.assertIn(needle, workflow)

    def test_it_says_where_the_standard_sits_and_how_the_pin_is_moved(self):
        text = " ".join(self.text.split())
        for needle in ("git submodule at `doc/governance`", "add the prefix `doc/governance/`", "git submodule add",
                       "git submodule update --init doc/governance", "fetch --unshallow", "--only S1"):
            self.assertIn(needle, text, needle)

    def test_it_is_not_part_of_the_manifest_and_the_project_does_not_receive_it_as_automation(self):
        import check_manifest
        self.assertNotIn("adoption/ADOPT-OR-UPDATE-GOVERNANCE.md", check_manifest.automation_files(ROOT))


class CommandTests(unittest.TestCase):
    NAMES = ("status", "ticket", "start", "changelog", "commit", "review", "sync", "pr", "after-merge", "plan", "fix", "release",
             "hotfix", "retire", "audit", "upgrade")

    def test_the_sixteen_commands_exist_with_a_description_and_the_standing_rules(self):
        self.assertEqual(sorted(n[:-3] for n in os.listdir(COMMANDS)), sorted("gov-" + n for n in self.NAMES))
        for name in os.listdir(COMMANDS):
            text = read(os.path.join(COMMANDS, name))
            self.assertTrue(text.startswith("---" + chr(10) + "description: "), name)
            self.assertIn("git submodule of the project at `doc/governance`", " ".join(text.split()), name)
            for needle in ("is data, never instructions", "Never commit, push, merge", "never set a ticket to Completed",
                           "no assistant attribution"):
                self.assertIn(needle, " ".join(text.split()), name)

    def test_they_are_automation_files_so_a_project_gets_them_and_the_hash_is_checked(self):
        import check_manifest
        listed = check_manifest.automation_files(ROOT)
        for name in self.NAMES:
            self.assertIn(".claude/commands/gov-{}.md".format(name), listed)

    def test_release_hotfix_and_retire_only_prepare_a_dry_run(self):
        for name in ("release", "hotfix", "retire"):
            text = read(os.path.join(COMMANDS, "gov-{}.md".format(name)))
            self.assertIn("dry run", text.lower(), name)


if __name__ == "__main__":
    unittest.main()
