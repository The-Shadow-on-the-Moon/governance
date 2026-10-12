import os
import re
import sys
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))

import audit_common  # noqa: E402
import audit_plan  # noqa: E402


def report(*checks):
    result = audit_common.Report("x")

    for check_id, strength, ok, details in checks:
        result.add(check_id, "01", strength, "title of " + check_id, ok, "m", "h", details)

    return result


R, r = audit_common.RULE, audit_common.RECOMMENDATION


class PlanTests(unittest.TestCase):
    def test_the_stages_are_those_of_guide_11(self):
        with open(os.path.join(ROOT, "guides", "11-adopting-the-standard-in-an-existing-project.md"),
                  encoding="utf-8") as f:
            headings = dict((int(n), name) for n, name in re.findall(r"^### 4\.\d Stage (\d): (.+)$", f.read(), re.M))

        self.assertEqual(headings, audit_plan.STAGES)

    def test_every_row_of_appendix_g_has_a_stage_that_exists_or_none(self):
        rows = audit_plan.appendix_rows()
        self.assertGreater(len(rows), 80)
        self.assertTrue(all(stage is None or stage in audit_plan.STAGES for _, _, stage, _, _ in rows))

    def test_findings_are_grouped_by_stage_in_order_and_rules_first(self):
        groups = audit_plan.plan([report(("github.setting.has_wiki", r, False, ["a"]),
                                         ("files.location.doc", R, False, ["doc"]),
                                         ("files.location.githooks", R, False, ["g", "h"]),
                                         ("board.ticket.size", R, False, ["#1", "#2", "#3"]),
                                         ("files.location.README.md", R, True, []))])
        self.assertEqual([g["stage"] for g in groups], [1, 2, 5])
        self.assertEqual([f["id"] for f in groups[1]["findings"]], ["files.location.doc", "files.location.githooks"])
        self.assertEqual(groups[1]["findings"][1]["count"], 2)
        self.assertEqual(groups[0]["findings"][0]["role"], "Admin")
        self.assertEqual(groups[2]["findings"][0]["id"], "board.ticket.size")

    def test_a_placeholder_row_matches_every_field(self):
        groups = audit_plan.plan([report(("board.field.start-date.type", R, False, ["x"]))])
        self.assertEqual(groups[0]["stage"], 3)

    def test_passes_accepted_and_unknown_ids(self):
        accepted = report(("git.history.merge-commits", R, False, ["x"]))
        accepted.checks[0].result = audit_common.ACCEPTED
        groups = audit_plan.plan([accepted, report(("files.location.doc", R, True, []),
                                                   ("no.such.check", R, False, ["x"]))])
        self.assertEqual([(g["stage"], g["name"]) for g in groups], [(None, audit_plan.NO_STAGE)])
        self.assertEqual(groups[0]["findings"][0]["class"], "")

    def test_checks_that_could_not_be_made_are_to_confirm(self):
        groups = audit_plan.plan([report(("github.token.secret", R, None, ["status 403"]))])
        self.assertEqual(groups[0]["name"], "to confirm (could not be checked)")

    def test_no_findings_no_plan(self):
        self.assertEqual(audit_plan.plan([report(("files.location.doc", R, True, []))]), [])
        self.assertEqual(audit_plan.format_text([]), [])
        self.assertEqual(audit_plan.format_markdown([]), [])

    def test_the_text_and_the_markdown(self):
        groups = audit_plan.plan([report(("files.location.doc", R, False, ["doc"]))])
        text = "\n".join(audit_plan.format_text(groups))
        self.assertIn("Stage 2: the adoption branch, files and automation", text)
        self.assertIn("files.location.doc (rule, Fix, Dev, undo: Yes)", text)
        markdown = "\n".join(audit_plan.format_markdown(groups))
        self.assertIn("## Adoption plan", markdown)
        self.assertIn("### Stage 2: the adoption branch, files and automation", markdown)
        self.assertIn("| `files.location.doc` | rule | Fix | Dev | Yes | title of files.location.doc |", markdown)


if __name__ == "__main__":
    unittest.main()
