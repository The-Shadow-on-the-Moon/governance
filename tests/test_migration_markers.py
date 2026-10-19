import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kit_common  # noqa: E402,F401
import migrations  # noqa: E402

MARKER = re.compile(r"^\s*-\s*Project action:\s*([A-Za-z0-9]+(?:\s*,\s*[A-Za-z0-9]+)*)\s*:", re.M)


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
        return handle.read()


def marked_ids(text):
    """The step IDs named by the `Project action:` bullets of a changelog."""
    found = []

    for match in MARKER.finditer(text):
        found += [part.strip() for part in match.group(1).split(",")]

    return found


class MarkerTests(unittest.TestCase):
    def test_the_marker_is_read(self):
        text = "#### #1 — x\n- Project action: A5, L1: the views\n- other\n#### #2\n- Project action: A2: option\n"
        self.assertEqual(marked_ids(text), ["A5", "L1", "A2"])
        self.assertEqual(marked_ids("- project action: A5: x\n- Project action A5\n"), [])

    def test_every_marker_of_the_changelog_names_a_migration_step(self):
        ids = {m.ID for m in migrations.steps()}
        named = marked_ids(read("CHANGELOG.md"))
        self.assertTrue(named, "the changelog should carry at least the marker of the 0.15 series")
        for step in named:
            self.assertIn(step, ids, "a Project action names {} which is no step of tools/migrations".format(step))

    def test_every_step_is_described_in_the_upgrading_page_and_the_inventory(self):
        page = read("doc", "wiki", "Upgrading.md")
        for module in migrations.steps():
            self.assertIn("| {} |".format(module.ID), page, module.ID)

    def test_the_rule_is_in_the_guides_and_the_page_says_what_is_breaking(self):
        self.assertIn("Project action:", read("guides", "05-working-and-committing.md"))
        self.assertIn("Project action:", read("guides", "06-syncing-and-merging.md"))
        page = read("doc", "wiki", "Upgrading.md")
        self.assertIn("What counts as breaking", page)
        self.assertIn("Resolution *Done* filled", page)


if __name__ == "__main__":
    unittest.main()
