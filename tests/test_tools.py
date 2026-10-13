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

        for letter in "ABCDEFG":
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


class AppendixFTests(unittest.TestCase):
    """Appendix F (board views, columns and sorting) must say what .github/views.json says."""

    @classmethod
    def setUpClass(cls):
        import json

        with open(os.path.join(ROOT, "guides", "appendix-f-board-views-layout.md"), encoding="utf-8") as handle:
            cls.text = handle.read()
        with open(os.path.join(ROOT, ".github", "views.json"), encoding="utf-8") as handle:
            cls.views = {view["name"]: view for view in json.load(handle)["views"]}

    def table(self, heading):
        """The rows of the first table after a heading, as lists of cells with the bold marks removed."""
        section = self.text.split(heading, 1)[1]
        rows = []
        for line in section.splitlines():
            if line.startswith("|"):
                rows.append([cell.strip().replace("**", "") for cell in line.strip().strip("|").split("|")])
            elif rows:
                break
        return rows[2:]  # leave out the header and the separator

    def sort_text(self, view):
        parts = ["{}, {}ending".format(field, direction) for field, direction in view["sort_by"]]
        return ", then ".join(parts)

    def test_the_table_views_have_the_columns_in_the_order_of_the_file(self):
        rows = self.table("## 1. Table views")
        names = [cell for cell in self.text.split("## 1. Table views", 1)[1].splitlines()
                 if cell.startswith("| Field")][0].strip("|").split("|")
        names = [name.strip() for name in names][1:]
        self.assertEqual(set(names), {n for n, v in self.views.items() if v["layout"] == "table"})
        for column, name in enumerate(names, start=1):
            positions = {}
            for row in rows:
                if row[column].isdigit():
                    positions[int(row[column])] = row[0]
            shown = [positions[n] for n in sorted(positions)]
            self.assertEqual(shown, self.views[name]["visible_fields"], name)

    def test_the_table_views_have_the_sort_and_grouping_of_the_file(self):
        rows = {row[0]: row for row in self.table("## 1. Table views") if not row[1].isdigit() and row[1] != "·"}
        names = [n.strip() for n in [c for c in self.text.splitlines() if c.startswith("| Field")][0].strip("|").split("|")][1:]
        for column, name in enumerate(names, start=1):
            view = self.views[name]
            self.assertEqual(rows["Sort"][column], self.sort_text(view), name)
            group = view.get("group_by")
            if group:
                self.assertTrue(rows["Group"][column].startswith(group), name)
            else:
                self.assertEqual(rows["Group"][column], "none", name)

    def test_the_board_views_have_the_columns_rows_card_fields_and_sort_of_the_file(self):
        rows = self.table("## 2. Board views")
        self.assertEqual({row[0] for row in rows}, {n for n, v in self.views.items() if v["layout"] == "board"})
        for name, layout, columns, swimlanes, card, sort in rows:
            view = self.views[name]
            self.assertEqual(layout, "board", name)
            self.assertEqual(columns, view["vertical_group_by"], name)
            self.assertEqual(swimlanes, view.get("group_by") or "none", name)
            # Title is always drawn and Type is not reported by the API, so neither is listed.
            shown = {field for field in view["visible_fields"] if field not in ("Title", "Type")}
            self.assertEqual(set(card.split(", ")), shown, name)
            self.assertEqual(sort, self.sort_text(view), name)

    def test_every_view_of_the_file_is_in_the_appendix(self):
        for name in self.views:
            self.assertIn(name, self.text)


class StatementsAboutTheRepositoryTests(unittest.TestCase):
    """The counts and descriptions of the README, the wiki Home and the guide index must match the files."""

    def read(self, *parts):
        with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
            return handle.read()

    def guides_and_appendices(self):
        names = os.listdir(os.path.join(ROOT, "guides"))
        guides = sorted(n[:2] for n in names if n[:2].isdigit() and n.endswith(".md"))
        appendices = sorted(n.split("-")[1].upper() for n in names if n.startswith("appendix-"))
        return guides, appendices

    def test_the_root_readme_names_the_guides_and_appendices_there_are(self):
        import re

        guides, appendices = self.guides_and_appendices()
        text = self.read("README.md")
        self.assertIn(f"The guides (01 to {guides[-1]})", text)
        self.assertIn(f"the appendices (A to {appendices[-1]})", text)
        self.assertEqual(guides, [f"{n:02d}" for n in range(1, len(guides) + 1)])
        self.assertEqual(appendices, [chr(ord("A") + n) for n in range(len(appendices))])

    def test_the_wiki_home_names_the_guides_and_appendices_there_are(self):
        guides, appendices = self.guides_and_appendices()
        text = self.read("doc", "wiki", "Home.md")
        self.assertIn(f"guides 01 to {guides[-1]} and appendices A to {appendices[-1]}", text)
        words = {10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen"}
        self.assertIn(f"The {words[len(guides)]} guides:", text)

    def test_the_guide_index_has_a_row_for_every_guide_and_appendix(self):
        import re

        guides, appendices = self.guides_and_appendices()
        text = self.read("guides", "README.md")
        self.assertEqual(re.findall(r"^\| \*\*(\d\d) ", text, re.M), guides)
        self.assertEqual(re.findall(r"^\| \*\*([A-G]) ", text, re.M), appendices)

    def test_the_root_readme_names_every_tool(self):
        text = self.read("README.md")
        for name in sorted(os.listdir(os.path.join(ROOT, "tools"))):
            if name.endswith(".py"):
                self.assertIn(f"`{name}`", text, name)

    def test_the_automation_page_describes_every_hook(self):
        text = self.read("doc", "wiki", "Automation.md")
        for name in sorted(os.listdir(os.path.join(ROOT, ".githooks"))):
            if name not in ("hooks.py", "__pycache__"):
                self.assertIn(f"`{name}`", text, name)



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

    def test_the_guides_say_how_a_trial_is_tagged_and_what_happens_when_the_box_is_forgotten(self):
        trials = self.guide("05-working-and-committing.md")
        for phrase in ("Warning: the trial box", "What happens when you tick it", "What happens when you forget it", "test/released/V9.9.9"):
            self.assertIn(phrase, trials, phrase)
        self.assertIn("test/", self.guide("02-branching-and-merging-strategy.md"))
        self.assertIn("**trial**", self.guide("08-releases-hotfixes-and-retiring-branches.md"))
        with open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8") as handle:
            self.assertIn("`trial`", handle.read())

    def test_a_broken_rule_is_shown_without_a_wait_and_commented_after_one(self):
        text = self.guide("03-project-structure.md")
        self.assertIn("needs no wait", text)
        self.assertNotIn("five minutes", text)
        self.assertIn("stays broken for two hours", text)
        conditions = self.automation("conditions")
        self.assertEqual(conditions.FIX_COMMENT_AFTER.total_seconds(), 2 * 3600)

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

    def test_appendix_g_has_a_row_for_every_check_the_audits_can_report(self):
        import re

        import audit_files
        import audit_github

        emitted = set()

        for name in ("audit.py", "audit_baseline.py", "audit_files.py", "audit_git.py", "audit_github.py",
                     "audit_board.py"):
            source = self.read("tools", name)
            emitted |= {i for i in re.findall(r'"((?:files|git|github|board|baseline)\.[A-Za-z0-9_.\-]+)"', source)
                        if not i.endswith(".")}

        source = self.read("tools", "audit_board.py")
        emitted |= {"board.ticket." + i for i in re.findall(r'^    add\("([a-z-]+)"', source, re.M)}
        emitted |= {"github.setting." + key for key, *_ in audit_github.SETTINGS}
        emitted |= {"files.location." + n.strip(".").replace("/", ".") for n, *_ in audit_files.LOCATIONS}
        emitted |= {"board.field.<field>" + suffix for suffix in ("", ".type", ".values", ".colors")}
        # the ids built from a name in the source are listed through the three families above
        emitted -= {"board.field", "board.field.name"}
        documented = set(re.findall(r"^\| `([^`]+)` \|", self.guide("appendix-g-audit-findings-and-fixes.md"), re.M))
        self.assertEqual(sorted(emitted - documented), [], "audit checks with no row in appendix G")
        self.assertEqual(sorted(documented - emitted), [], "rows of appendix G that no audit reports")

    def test_every_guide_defines_the_markers_it_uses(self):
        import glob

        names = sorted(glob.glob(os.path.join(ROOT, "guides", "[0-1][0-9]-*.md"))) + [os.path.join(ROOT, "guides", "README.md")]
        self.assertEqual(len(names), 12)
        for name in names:
            with open(name, encoding="utf-8") as handle:
                text = handle.read()
            for marker in ("Rule", "Recommendation", "Strong recommendation", "In GitHub"):
                self.assertIn(f"- **{marker}**:", text, f"{os.path.basename(name)}: {marker}")

    def test_the_examples_of_the_changelog_are_valid_changelogs(self):
        import re

        parser = self.automation("changelog")
        checked = 0
        texts = [self.guide(name) for name in sorted(os.listdir(os.path.join(ROOT, "guides")))
                 if name.endswith(".md") and name != "Developer-Guides-Complete.md"]
        with open(os.path.join(ROOT, "doc", "wiki", "Walkthrough-CSV-Export.md"), encoding="utf-8") as handle:
            texts.append(handle.read())  # the walkthrough page of the wiki has changelog examples too
        for text in texts:
            for block in re.findall(r"```[a-z]*\n(.*?)```", text, re.S):
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
        from_guide = {}
        for names, kind, values in re.findall(r"^\| (.*?) \| (single select|text|number|date) \|(.*?)\|$", table, re.M):
            listed = [v.strip() for v in values.strip().split(", ") if v.strip()]
            for name in [n.strip() for n in names.split(",")]:
                from_guide[name] = (kinds[kind], listed or None)
        ticket_type = self.automation("ticket_type")
        kind = from_guide.pop(ticket_type.FIELD)  # only when the Type lives in the field
        self.assertEqual(kind[0], "SINGLE_SELECT")
        self.assertEqual([re.sub(r" \(.*\)$", "", v) for v in kind[1]], ticket_type.VALUES)
        self.assertEqual(from_guide, dict(preflight.REQUIRED_FIELDS))
        self.assertEqual(list(from_guide), list(preflight.REQUIRED_FIELDS))

    def test_the_colors_and_descriptions_of_the_preflight_are_those_of_appendix_c(self):
        import re

        preflight = self.automation("preflight")
        text = self.guide("appendix-c-ticket-fields-reference.md")
        sections = ("Progress (Status)", "Origin and REF", "Waiting", "Attention", "Resolution", "Delivery", "Priority", "Size", "Risk")
        colors, descriptions = {}, {}
        for section in re.split(r"^## ", text, flags=re.M)[1:]:
            title, _, body = section.partition(chr(10))
            if title not in sections:
                continue
            for row in re.findall(r"^\| \*\*(.*?)\*\* \| (.*?) \| (.*?) \|", body, re.M):
                name, color, meaning = row
                colors[name] = color
                descriptions[name] = re.sub(r"[*`]", "", meaning) if title != "Size" else f"Estimated effort: {meaning}."
        self.assertEqual(colors, dict(preflight.OPTION_COLORS))
        self.assertEqual(descriptions, dict(preflight.OPTION_DESCRIPTIONS))
        ticket_type = self.automation("ticket_type")
        type_colors, type_descriptions = {}, {}
        for section in re.split(r"^## ", text, flags=re.M)[1:]:
            title, _, body = section.partition(chr(10))
            if title == "Type":
                for name, color, meaning in re.findall(r"^\| \*\*(.*?)\*\* \| (.*?) \| (.*?) \|", body, re.M):
                    type_colors[name] = color
                    type_descriptions[name] = re.sub(r"[*`]", "", meaning)
        self.assertEqual(type_colors, ticket_type.COLORS)
        self.assertEqual(type_descriptions, ticket_type.DESCRIPTIONS)
        self.assertLessEqual(set(colors.values()), {"GRAY", "BLUE", "GREEN", "YELLOW", "ORANGE", "RED", "PINK", "PURPLE"})
        areas = re.findall(r"^\| `(\w+)` \| ([0-9A-F]{6}) \|", text, re.M)
        self.assertEqual(len(areas), 15)  # the 14 Area labels and dummy

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

    def test_the_texts_the_automation_writes_are_shown_in_the_guides_as_they_are_written(self):
        import re

        alerts, finalize, checks = self.automation("alerts"), self.automation("finalize"), self.automation("checks")

        def flat(text):
            return re.sub(r"\s+", " ", re.sub(r"(?m)^>\s?", "", text)).strip()

        structure = flat(self.guide("03-project-structure.md"))
        version = alerts.Version(2, 4, 1)
        found = [checks.Finding("abc1234def", checks.NOT_IDENTICAL, "Merge pull request #186 from report-fixes", "Sam")]
        title, body = alerts.bypass_alert(found, False, version, "abc1234def0", "2026-10-05 16:40")
        self.assertIn(title, structure)
        self.assertIn(flat(body), structure)
        description = finalize.version_description(version, "2026-10-05 16:41", finalize.bump_reason({204: "Bug"}, "", False), 186,
                                                   "20261005143045", [(204, "Report totals ignore the last day of the month", "Bug")])
        self.assertIn(flat(description), structure)
        _, explanation = alerts.bypass_headline(found, False)
        entry = alerts.add_autoref("## WIP-Version\n", "20261005164000", 187, explanation, False).splitlines()
        bullet = flat(entry[3])
        for name in (("guides", "02-branching-and-merging-strategy.md"), ("guides", "03-project-structure.md"),
                     ("doc", "wiki", "Walkthrough-CSV-Export.md")):
            self.assertIn(bullet, flat(self.read(*name)), name[-1])


if __name__ == "__main__":
    unittest.main()
