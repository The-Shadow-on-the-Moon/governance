import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import kit_common  # noqa: E402
import survey  # noqa: E402
import preflight  # noqa: E402
import versions  # noqa: E402


def ticket(**kw):
    base = {"number": 1, "state": "OPEN", "type": "Feature", "status": "InProgress", "delivery": "", "resolution": None,
            "version": "", "fix": "", "waiting": None, "origin": None, "attention": None, "ref": "", "end": None}
    base.update(kw)
    return base


def board_data(tickets, fields=None, views_=(), type_source="issue-type"):
    fields = fields if fields is not None else {n: {"type": k, "options": {v: v for v in (vals or [])}}
                                                for n, (k, vals) in preflight.REQUIRED_FIELDS.items()}
    return {"board": {"number": 3, "title": "B", "fields": fields}, "type_source": type_source, "tickets": tickets,
            "views": list(views_)}


class BoardFactTests(unittest.TestCase):
    def test_version_forms_are_classified(self):
        self.assertEqual([survey.classify_version(t) for t in ("", "V000.015.001", "V0.15.1", "Version 1", "V000.015.001-HF1")],
                         ["blank", "board", "short", "other", "board"])

    def test_the_board_facts_count_types_legacy_and_previews(self):
        tickets = [ticket(number=1, type="Version", state="OPEN"), ticket(number=2, status="Completed", resolution=None),
                   ticket(number=3, status="InProgress", resolution="Done"), ticket(number=4, version="V000.015.000", status="InProgress")]
        facts = survey.facts_board(lambda: board_data(tickets), versions.Version.parse("V0.15.1"))
        self.assertEqual(facts["tickets"]["by_type"], {"Version": 1, "Feature": 3})
        self.assertEqual(facts["legacy_version_tickets"], {"total": 1, "open": 1, "open_without_delivery": 1})
        self.assertEqual(facts["preview"]["resolution_done_to_fill"], 1)
        self.assertEqual(facts["preview"]["resolution_done_to_clear"], 1)
        self.assertEqual(facts["preview"]["stale_plans"], 1)
        self.assertEqual(facts["version_forms"]["board"], 1)

    def test_offline_and_unreadable_boards_are_unknown_not_guessed(self):
        self.assertIn("not read", survey.facts_board(None, None)["unknown"][0])
        self.assertFalse(survey.facts_board(lambda: {"error": "no token"}, None)["found"])
        self.assertFalse(survey.facts_board(lambda: {"board": None}, None)["found"])


class GapTests(unittest.TestCase):
    def test_a_project_without_a_board_lacks_the_board(self):
        found = survey.gaps({}, {"found": False}, None, "User")
        self.assertEqual([g["id"] for g in found], ["A1"])

    def test_missing_field_and_legacy_tickets_are_gaps_tied_to_a_version(self):
        fields = {n: {"type": k, "options": {}} for n, (k, _) in preflight.REQUIRED_FIELDS.items() if n != "Fix"}
        facts = survey.facts_board(lambda: board_data([ticket(type="Version")], fields), None)
        found = {g["id"]: g for g in survey.gaps({}, facts, False, "Organization")}
        self.assertEqual(found["A6"]["since"], "V0.10.0")
        self.assertIn("L1", found)
        self.assertIn("A4", found)

    def test_a_placeholder_in_a_project_is_a_gap(self):
        self.assertIn("M1", [g["id"] for g in survey.gaps({"placeholder_in_a_project": True}, {"found": False}, True, "User")])


class DetectionTests(unittest.TestCase):
    def test_states(self):
        self.assertEqual(survey.detect_state({"identity": {"state": "match", "versions": ["V0.14.0"]}})["detected"], "version")
        self.assertEqual(survey.detect_state({"identity": {"state": "none"}})["detected"], "none")
        self.assertEqual(survey.detect_state({"identity": {"state": "mixed", "closest": ["V0.1.0"]}})["detected"], "mixed")
        self.assertEqual(survey.detect_state({"identity": {"state": "modified", "closest": []}})["detected"], "unsupported")
        self.assertEqual(survey.detect_state({"identity": {"state": "unknown"}})["detected"], "unknown")

    def test_blockers(self):
        found = survey.blockers({"hotfix_branches": ["hotfix-1"], "clean_tree": False, "shallow": True, "open_pull_requests": 2}, {})
        self.assertEqual(len(found), 4)
        self.assertEqual(survey.blockers({"hotfix_branches": [], "clean_tree": True, "shallow": False, "open_pull_requests": 0}, {}), [])


class OfflineRunTests(unittest.TestCase):
    def test_an_empty_git_project_is_state_none_and_the_state_folder_is_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True)
            result = survey.survey(folder, None, None, None, {})
            self.assertEqual(result["state"]["detected"], "none")
            self.assertTrue(result["manual"])
            self.assertIn("# Survey of", survey.render(result))
            kit_common.state_path(folder)
            with open(os.path.join(folder, ".git", "info", "exclude"), encoding="utf-8") as h:
                self.assertIn(kit_common.STATE_FOLDER + "/", h.read())
            json.dumps(result, default=str)

    def test_the_kits_own_files_do_not_make_the_tree_dirty_but_other_files_do(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True)
            os.makedirs(os.path.join(folder, "doc"))
            for name in ("ADOPT-OR-UPDATE-GOVERNANCE.md", os.path.join("doc", "adoption-plan.md")):
                with open(os.path.join(folder, name), "w") as h:
                    h.write("x")
            self.assertTrue(survey.survey(folder, None, None, None, {})["repository"]["clean_tree"])
            with open(os.path.join(folder, "mine.txt"), "w") as h:
                h.write("x")
            self.assertFalse(survey.survey(folder, None, None, None, {})["repository"]["clean_tree"])

    def test_the_survey_writes_nothing_into_the_project(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run(["git", "init", "-q", folder], check=True)
            survey.survey(folder, None, None, None, {})
            self.assertEqual([n for n in os.listdir(folder) if n != ".git"], [])


if __name__ == "__main__":
    unittest.main()
