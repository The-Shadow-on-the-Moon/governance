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


class WorkflowActionsTests(unittest.TestCase):
    """Every use of actions/checkout in the workflows names the same release, and it is not the Node 20 one (GitHub removed
    Node 20 from the runners on 2026-09-23, and a Node 20 action only runs there because the runner forces it onto Node 24)."""

    def uses(self):
        import glob
        import re

        found = []
        for path in glob.glob(os.path.join(ROOT, ".github", "workflows", "*.yml")):
            with open(path, encoding="utf-8") as handle:
                found += re.findall(r"uses:\s*actions/checkout@(\S+)", handle.read())
        return found

    def test_the_workflows_check_out_with_one_release(self):
        found = self.uses()
        self.assertGreaterEqual(len(found), 9)
        self.assertEqual(len(set(found)), 1, found)

    def test_that_release_runs_on_node_24(self):
        (release,) = set(self.uses())
        self.assertRegex(release, r"^v\d+$")
        self.assertGreaterEqual(int(release[1:]), 5)  # v5 is the first release built for Node 24


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


class GuideValueTests(unittest.TestCase):
    """Values that the guides repeat in several places must agree with each other and with the automation.

    The guides restate some rules in more than one place, and the section checks only prove that a section
    exists. These tests fail when a value changes in one place and not in the others.
    """

    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
            return handle.read()

    def guide(self, name):
        return self.read("guides", name)

    def automation(self, name):
        sys.path.insert(0, os.path.join(ROOT, ".github", "scripts"))
        try:
            return __import__(name)
        finally:
            sys.path.pop(0)

    def test_the_idle_thresholds_agree_with_the_automation(self):
        watch = self.automation("watch")
        days = {status: limit.days for status, limit in watch.THRESHOLDS.items()}
        self.assertEqual(days, {"Review": 7, "OnDeck": 30, "InProgress": 30, "Suspended": 182})
        self.assertEqual(watch.WAITING_AFTER.days, 14)
        text = self.guide("03-project-structure.md")
        for phrase in ("for a week", "for a month", "for six months", "two weeks"):
            self.assertIn(phrase, text, phrase)
        housekeeping = self.guide("07-issues-and-the-board-in-practice.md")
        for phrase in ("a week at *Review*", "about a month", "six months", "two weeks"):
            self.assertIn(phrase, housekeeping, phrase)

    def test_a_broken_rule_is_shown_without_a_wait(self):
        text = self.guide("03-project-structure.md")
        self.assertIn("needs no wait", text)
        for phrase in ("five minutes", "two hours"):
            self.assertNotIn(phrase, text, phrase)

    def test_the_fields_reference_does_not_repeat_the_attention_rules(self):
        reference = self.guide("appendix-c-ticket-fields-reference.md")
        for phrase in ("for a week", "for a month", "five minutes", "two hours"):
            self.assertNotIn(phrase, reference, phrase)
        self.assertIn("section 4.3", reference)

    def test_the_version_bump_per_type_is_the_same_in_both_places(self):
        import re

        branching = self.guide("02-branching-and-merging-strategy.md")
        table = branching.split("| Ticket Type | Bump |", 1)[1].split("\n\n", 1)[0]
        bump = {}
        for types, size in re.findall(r"^\s*\| (.*?) \| (sub|mod|none)[^|]*\|$", table, re.M):
            for name in re.split(r",\s*|\s+and\s+", types):
                bump[name.strip()] = size
        reference = self.guide("appendix-c-ticket-fields-reference.md")
        section = reference.split("## Type", 1)[1].split("## Area", 1)[0]
        listed = dict(re.findall(r"^\| \*\*([A-Za-z]+)\*\* \| .*? \| (sub|mod|none) \|$", section, re.M))
        self.assertEqual(len(listed), 8)
        self.assertEqual(listed, bump)

    def test_every_alert_kind_is_described_where_alerts_are_listed(self):
        import re

        alerts = self.automation("alerts")
        titles = [alerts.stale_alert("V1.0.0", [(1, "Version 0.9.0")])[0],
                  alerts.changelog_error_alert("x", "abc1234", "2026-10-05 16:40")[0]]
        self.assertEqual(len(titles), 2)  # the bypass Alert has two shapes, tested elsewhere
        unreadable = re.compile(r"cannot read|could not be read|unreadable|could not read")
        for name in ("03-project-structure.md", "07-issues-and-the-board-in-practice.md"):
            text = self.guide(name)
            self.assertTrue(unreadable.search(text), f"{name} does not mention the changelog-error Alert")
        self.assertIn("Changelog error on main", self.guide("03-project-structure.md"))

    def test_the_area_labels_are_the_same_in_every_guide_that_lists_them(self):
        import re

        reference = self.guide("appendix-c-ticket-fields-reference.md")
        area = reference.split("## Area", 1)[1].split("## The `dummy` label", 1)[0]
        labels = re.findall(r"^\| `([a-z]+)` \|", area, re.M)
        self.assertEqual(len(labels), 14)
        bootstrap = self.guide("10-new-project-bootstrap.md")
        for label in labels:
            self.assertIn(f"`{label}`", bootstrap, label)
        for name in ("01-concepts-and-vocabulary.md", "10-new-project-bootstrap.md"):
            text = self.guide(name)
            self.assertIn("14 Area labels", text, name)
            self.assertIn("`dummy`", text, name)

    def test_the_field_questions_are_the_same_in_the_guides_and_the_wiki(self):
        import re

        def questions(text):
            found = {}
            for field, question in re.findall(r"^\| (\*\*[^|]+?) \| ([^|]+?\?) \|", text, re.M):
                found[field] = question
            return found

        structure = self.guide("03-project-structure.md").split("### 4.2 The fields at a glance", 1)[1].split("### 4.3", 1)[0]
        model = self.guide("appendix-e-ticket-model.md").split("## 1. The idea", 1)[1].split("## 2.", 1)[0]
        wiki = self.read("doc", "wiki", "Ticket-Model.md")
        tables = [questions(structure), questions(model), questions(wiki)]
        shared = set(tables[0]) & set(tables[1]) & set(tables[2])
        self.assertGreaterEqual(len(shared), 8)
        for field in shared:
            self.assertEqual(tables[0][field], tables[1][field], field)
            self.assertEqual(tables[0][field], tables[2][field], field)

    def test_the_line_endings_rule_quotes_the_file_the_project_uses(self):
        line = self.read(".gitattributes").strip()
        self.assertEqual(line, "* text=auto eol=lf")
        for name in ("03-project-structure.md", "10-new-project-bootstrap.md"):
            self.assertIn(f"`{line}`", self.guide(name), name)

    def test_every_guide_defines_the_markers_it_uses(self):
        import glob

        names = sorted(glob.glob(os.path.join(ROOT, "guides", "[0-1][0-9]-*.md"))) + [os.path.join(ROOT, "guides", "README.md")]
        self.assertEqual(len(names), 11)
        for name in names:
            with open(name, encoding="utf-8") as handle:
                text = handle.read()
            for marker in ("Rule", "Recommendation", "Strong recommendation", "In GitHub"):
                self.assertIn(f"- **{marker}**:", text, f"{os.path.basename(name)}: {marker}")

    def test_the_examples_of_the_changelog_are_valid_changelogs(self):
        import re

        parser = self.automation("changelog")
        checked = 0
        for name in sorted(os.listdir(os.path.join(ROOT, "guides"))):
            if not name.endswith(".md") or name == "Developer-Guides-Complete.md":
                continue
            for block in re.findall(r"```[a-z]*\n(.*?)```", self.guide(name), re.S):
                if not re.search(r"^## (WIP-Version|V\d)", block, re.M):
                    continue
                if re.search(r"^#{2,4} .*\S {3,}\S", block, re.M):
                    continue  # the legend of the structure, which is annotated on purpose
                parser.parse("# Changelog\n\n" + block.strip("\n") + "\n")
                checked += 1
        self.assertGreaterEqual(checked, 5)

    def test_the_glossary_lists_the_same_values_as_the_board(self):
        import re

        glossary = self.guide("01-concepts-and-vocabulary.md")
        bootstrap = self.guide("10-new-project-bootstrap.md")
        table = bootstrap.split("| Field | Kind | Values |", 1)[1].split("Type is the issue type", 1)[0]
        rows = dict(re.findall(r"^\| (Status|Origin|Attention|Delivery) \| single select \| (.*?) \|$", table, re.M))
        row_of = {"Status": "Progress", "Origin": "Origin", "Attention": "Attention", "Delivery": "Delivery"}
        for field, values in rows.items():
            entry = re.search(r"^\| \*\*" + row_of[field] + r"\*\* \| (.*?) \|", glossary, re.M).group(1)
            for value in values.split(", "):
                value = re.sub(r" \(.*\)$", "", value)
                self.assertIn(f"*{value}*", entry, f"{field}: {value}")

    def test_the_guides_use_their_own_words(self):
        import re

        for name in sorted(os.listdir(os.path.join(ROOT, "guides"))):
            if not name.endswith(".md") or name == "Developer-Guides-Complete.md":
                continue
            text = self.guide(name)
            self.assertNotIn("that one release", text, name)  # a release is a version declared one; the marker is for a version
            self.assertNotIn("feature branch", text, name)  # the guides say work branch
            self.assertEqual(len(re.findall(r"merge request", text)), 1 if name.startswith("02-") else 0, name)

    def test_the_example_tickets_use_only_values_the_reference_defines(self):
        import re

        reference = self.guide("appendix-c-ticket-fields-reference.md")

        def values(start, end):
            return re.findall(r"^\| \*\*([^*]+)\*\* \|", reference.split(start, 1)[1].split(end, 1)[0], re.M)

        types = values("## Type", "## Area")
        areas = re.findall(r"^\| `([a-z]+)` \|", reference.split("## Area", 1)[1].split("## The `dummy`", 1)[0], re.M)
        priorities, sizes = values("## Priority", "## Size"), values("## Size", "## Risk")
        risks = values("## Risk", "## Version, Build")
        pattern = re.compile(r"\| \*\*Title\*\* \| (.*?) \|\n\| \*\*Type\*\* \| (.*?) \|\n(?:\| \*\*Area\*\* \| (.*?) \|\n)?"
                             r"\| \*\*Priority\*\* \| (.*?) \|\n\| \*\*Size\*\* \| (.*?) \|\n\| \*\*Risk\*\* \| (.*?) \|\n")
        checked = 0
        for name in ("03-project-structure.md", "appendix-d-ticket-examples.md"):
            for title, kind, area, priority, size, risk in pattern.findall(self.guide(name)):
                checked += 1
                self.assertIn(kind, types, title)
                for one in [a.strip() for a in area.split(",") if a.strip()]:
                    self.assertIn(one, areas, title)
                self.assertIn(priority, priorities, title)
                self.assertIn(size, sizes, title)
                self.assertIn(re.sub(r"[()]", "", risk), risks, title)
        self.assertGreaterEqual(checked, 12)

    def test_the_board_the_preflight_requires_is_the_table_of_the_bootstrap_guide(self):
        import re

        preflight = self.automation("preflight")
        bootstrap = self.guide("10-new-project-bootstrap.md")
        table = bootstrap.split("| Field | Kind | Values |", 1)[1].split("Type is the issue type", 1)[0]
        kinds = {"single select": "SINGLE_SELECT", "text": "TEXT", "number": "NUMBER", "date": "DATE"}
        from_guide, colours = {}, {}
        for names, kind, values in re.findall(r"^\| (.*?) \| (single select|text|number|date) \|(.*?)\|$", table, re.M):
            listed = []
            for value in [v.strip() for v in values.strip().split(", ") if v.strip()]:
                match = re.match(r"(.*?) \((\w+)\)$", value)
                if match:
                    value, colours[match.group(1)] = match.group(1), match.group(2).upper()
                listed.append(value)
            for name in [n.strip() for n in names.split(",")]:
                from_guide[name] = (kinds[kind], listed or None)
        self.assertEqual(from_guide, dict(preflight.REQUIRED_FIELDS))
        self.assertEqual(colours, preflight.OPTION_COLORS)
        self.assertEqual(list(from_guide), list(preflight.REQUIRED_FIELDS))

    def test_the_registry_and_the_automation_agree_on_the_ten_rules_of_the_guide(self):
        import re

        conditions = self.automation("conditions")
        section = self.guide("03-project-structure.md").split("### 4.4 Rules that span fields", 1)[1].split("> **In GitHub.**", 1)[0]
        self.assertGreaterEqual(len(re.findall(r"^\| ", section, re.M)), 12)
        self.assertEqual(len(conditions.FIX_RULES), 10)
        self.assertIn("Fix field", section)  # the rule table says the broken rule is listed in Fix

    def test_the_conditions_table_of_the_guide_is_the_registry(self):
        import re

        conditions = self.automation("conditions")
        section = self.guide("07-issues-and-the-board-in-practice.md").split("### 2.5 The conditions the board shows", 1)[1]
        section = section.split("- **Decide** conditions", 1)[0]
        rows = re.findall(r"^\| `([a-z-]+)` \| (.*?) \| (Decide|Follow up|Fix) \| (.*?) \|$", section, re.M)
        view = {"decide": "Decide", "follow-up": "Follow up", "fix": "Fix"}
        self.assertEqual(rows, [(c.id, c.name, view[c.nature], c.cleared_by) for c in conditions.CONDITIONS])

    def test_the_views_of_the_definition_are_the_ones_the_guides_name(self):
        import json

        names = [view["name"] for view in json.loads(self.read(".github", "views.json"))["views"]]
        word = {5: "five", 6: "six", 7: "seven", 8: "eight"}[len(names)]
        board = self.guide("07-issues-and-the-board-in-practice.md")
        self.assertIn(f"The board has {word} saved views", board)
        for name in names:
            self.assertIn(f"- **{name}:**", board, name)
        bootstrap = self.guide("10-new-project-bootstrap.md")
        self.assertIn(", ".join(names[:-1]) + " and " + names[-1] + " (see the guide on issues", bootstrap)
        self.assertIn("(" + ", ".join(names) + ")", bootstrap)

    def test_every_board_value_in_the_bootstrap_is_defined_in_the_fields_reference(self):
        import re

        bootstrap = self.guide("10-new-project-bootstrap.md")
        table = bootstrap.split("| Field | Kind | Values |", 1)[1].split("Type is the issue type", 1)[0]
        reference = self.guide("appendix-c-ticket-fields-reference.md")
        checked = 0
        for row in re.findall(r"^\| (Status|Origin|Waiting|Attention|Resolution|Delivery|Priority|Size|Risk) \| single select \| (.*?) \|$",
                              table, re.M):
            for value in row[1].split(", "):
                value = re.sub(r" \(.*\)$", "", value)
                self.assertIn(f"**{value}**", reference, f"{row[0]}: {value}")
                checked += 1
        self.assertGreater(checked, 40)
