import os
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import combine  # noqa: E402
import xref_check  # noqa: E402


class CombineTests(unittest.TestCase):
    def test_shift_headings_demotes_outside_code_only(self):
        lines = combine.shift_headings("# A\n```\n# not a heading\n```\n## B")
        self.assertEqual(lines, ["## A", "```", "# not a heading", "```", "### B"])

    def test_split_title(self):
        title, rest = combine.split_title("# Title\n\nBody\n")
        self.assertEqual((title, rest), ("Title", "Body"))

    def test_slug_numbers_duplicates(self):
        slug = combine.slugger()
        self.assertEqual(slug("8. Checklist"), "8-checklist")
        self.assertEqual(slug("8. Checklist"), "8-checklist-1")

    def test_build_has_every_guide_and_appendix(self):
        document = combine.build()
        self.assertIn("## Table of contents", document)

        for num, _ in combine.GUIDES:
            self.assertIn("## Guide {}:".format(num), document)

        for letter in "ABCDE":
            self.assertIn("## Appendix {}:".format(letter), document)

    def test_combined_file_is_up_to_date(self):
        path = os.path.join(combine.GUIDES_DIR, combine.OUT_NAME)

        with open(path, encoding="utf-8") as f:
            self.assertEqual(f.read().replace("\r\n", "\n"), combine.build())

    def test_build_fails_clearly_without_a_title(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ["README.md"] + [n for _, n in combine.GUIDES] + combine.APPENDICES:
                with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                    f.write("no title here\n")

            with self.assertRaises(ValueError):
                combine.build(folder)


class CrossReferenceTests(unittest.TestCase):
    def test_sections_are_found(self):
        sections = xref_check.find_sections({"01": "## 1. A\n### 1.1 B\n```\n## 9. not\n```\n"})
        self.assertEqual(sections["01"], {"1", "1.1"})

    def test_a_reference_to_a_missing_section_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            for key, name in xref_check.FILES.items():
                with open(os.path.join(folder, name), "w", encoding="utf-8") as f:
                    f.write("## 1. Only section\n")

            with open(os.path.join(folder, xref_check.FILES["04"]), "a", encoding="utf-8") as f:
                f.write("See the guide on project structure, section 9.\n")

            _, checked, problems = xref_check.check(folder)

        self.assertEqual(checked, 1)
        self.assertEqual(len(problems), 1)

    def test_the_guides_have_no_broken_references(self):
        _, checked, problems = xref_check.check()
        self.assertGreater(checked, 100)
        self.assertEqual(problems, [])


class BoardViewsPageTests(unittest.TestCase):
    """The wiki page on the board views must say what .github/views.json says."""

    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
            return handle.read()

    def test_the_wiki_page_lists_every_view_and_its_filter(self):
        import json

        page = self.read("doc", "wiki", "Board-Views.md")
        for view in json.loads(self.read(".github", "views.json"))["views"]:
            self.assertIn(f"| {view['name']} |", page, view["name"])
            if view.get("filter"):
                self.assertIn(f"`{view['filter']}`", page, view["name"])

    def test_nothing_says_the_views_cannot_be_scripted(self):
        for parts in (("doc", "wiki", "Board-Views.md"), ("guides", "07-issues-and-the-board-in-practice.md"),
                      ("guides", "10-new-project-bootstrap.md")):
            self.assertNotIn("cannot create views", self.read(*parts), parts)
            self.assertNotIn("creates them in the web interface", self.read(*parts), parts)


if __name__ == "__main__":
    unittest.main()
