"""Bring a project to the version of the standard this checkout is at, step by step, from what the project really has.

It runs from a checkout of the standard with its full history, at the version to upgrade to, and is pointed at the
project. It surveys the project (`tools/survey.py`), lists the steps of the migration chain (`tools/migrations/`) that
the project needs, and, with `--apply`, applies them in order. After each step it surveys the project again and the step
must no longer be needed, or the chain stops. Nothing is remembered between runs but the log: to resume, run it again,
because the survey decides what is still to do.

A step that changes something the administrator decides or that cannot be restored runs only with its flag:
`--with-views` (the saved views), `--convert-legacy` (the legacy Version tickets; with `--include-open` also the planned
ones), `--delete-version-number` (the removal of the field Version#). `--overwrite-edited` replaces automation files
edited locally. `--only ID` runs one step. `--pause N` waits N seconds between steps (the API rate limits).

A dry run unless `--apply`. The restore files, backups and logs go to the state folder of the project, which git ignores.

    python tools/upgrade.py <project-path> [--repo owner/name] [--apply] [--only ID] [--with-views] [--convert-legacy]
        [--include-open] [--delete-version-number] [--overwrite-edited] [--pause N]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import kit_common  # noqa: E402
from kit_common import KitError, finalize  # noqa: E402

import audit_common  # noqa: E402
import build_fingerprints  # noqa: E402
import check_manifest  # noqa: E402
import migrations  # noqa: E402
from migrations import f01_files  # noqa: E402
import preflight  # noqa: E402
import survey  # noqa: E402
from github_api import GitHubError  # noqa: E402

FLAGS = {"--with-views": "views", "--convert-legacy": "convert_legacy", "--include-open": "include_open",
         "--delete-version-number": "delete_version_number", "--overwrite-edited": "overwrite_edited"}


def target_version(standard_root):
    """The version the checkout of the standard is at: the standard its manifest names. A placeholder is refused."""
    manifest = check_manifest.load(os.path.join(standard_root, check_manifest.MANIFEST))
    version = manifest.get("standard")

    if not version or version == check_manifest.PLACEHOLDER:
        raise KitError("this checkout of the standard is not at a finalized version (its manifest names {}): check out a version tag or "
                       "the commit of a Finalize".format(version))

    return version


def dirty_outside_the_chain(ctx):
    """The changed paths of the work tree that the chain did not write itself (the automation files of the standard and the
    manifest), so a chain that copied the files does not block its own next step."""
    code, out = audit_common.git(ctx.root, "status", "--porcelain", "-uall")
    own = set(check_manifest.automation_files(ctx.standard_root)) | {check_manifest.MANIFEST.replace(os.sep, "/")}
    own |= set(f01_files.known_hashes(ctx))  # the files of earlier versions, which the chain may have removed
    paths = []

    for line in (out.splitlines() if code == 0 and out else []):
        paths += [part.strip().strip('"') for part in line[3:].split(" -> ")]  # a rename names both paths

    own.add(survey.EMBEDDED)  # the pin of the standard's submodule is moved by the chain (S1) and is part of the adoption change
    return sorted(p for p in paths if p not in own and p not in survey.KIT_FILES and "__pycache__" not in p and not p.startswith(kit_common.STATE_FOLDER))


def blocking(ctx):
    """What stops an upgrade before any step: the survey's blockers and an unreadable state."""
    found = [b for b in ctx.survey.get("blockers", []) if "uncommitted" not in b]
    dirty = dirty_outside_the_chain(ctx) if hasattr(ctx, "root") and hasattr(ctx, "standard_root") else []

    if dirty:
        found.append("the working tree has uncommitted changes the chain did not make: {}".format(", ".join(dirty[:8])))

    legacy = (ctx.survey.get("board", {}).get("legacy_version_tickets") or {}).get("total", 0)

    if legacy and "convert_legacy" not in getattr(ctx, "flags", ()):
        found.append("{} legacy Version ticket(s): the files of this version no longer know the type, so they are converted first "
                     "(give --convert-legacy, and --include-open for the planned ones)".format(legacy))

    state = ctx.survey.get("state", {}).get("detected")

    if state == "unsupported":
        found.append("the automation files match no version of the standard and are not close to any: this is an adoption, not an upgrade")

    if state == "unknown":
        found.append("the files could not be identified (no fingerprints): run from a full-history checkout of the standard")

    return found


def chain(ctx, dry_run=True, only=None, pause=0, sleep=time.sleep, modules=None):
    """Go through the steps. Returns (Runner, report) where report lists, per step, what happened:
    {"id", "title", "status": done|skipped|gated|failed|not needed, "plan"}."""
    run = finalize.Runner(dry_run)
    report = []

    for module in (modules if modules is not None else migrations.steps()):
        if only and module.ID != only:
            continue

        entry = {"id": module.ID, "title": module.TITLE, "since": module.SINCE}
        report.append(entry)

        if not module.needed(ctx):
            entry["status"] = "not needed"
            continue

        entry["plan"] = module.plan(ctx)

        if module.GATE and module.GATE not in ctx.flags:
            entry["status"] = "gated"
            run.log.append("{} {}: needed, runs only with the flag {}: {}".format(module.ID, module.TITLE, module.GATE, "; ".join(entry["plan"])))
            continue

        run.log.append("{} {}: {}".format(module.ID, module.TITLE, "; ".join(entry["plan"])))

        if dry_run:
            module.apply(ctx, run)
            entry["status"] = "would apply"
            continue

        try:
            module.apply(ctx, run)
            ctx.refresh()
        except (KitError, GitHubError) as error:
            entry["status"] = "failed"
            entry["error"] = str(error)
            run.log.append("{}: FAILED, the chain stops: {}".format(module.ID, error))
            break

        if module.needed(ctx) and not getattr(ctx, "decisions", None):
            entry["status"] = "failed"
            entry["error"] = "the step ran but the project still lacks what it brings"
            run.log.append("{}: FAILED, the chain stops: the project still lacks what the step brings".format(module.ID))
            break

        entry["status"] = "done"

        if pause:
            sleep(pause)

    return run, report


def make_context(root, repo, flags):
    standard = kit_common.STANDARD
    target = target_version(standard)
    table = build_fingerprints.load_or_build(standard)
    repo_client, project_client = kit_common.connect(repo)

    def board():
        found = preflight.run(repo_client, project_client, store=False)
        return found.board or found.candidate, found.type_source  # the candidate is a board whose fields are not all there yet

    def survey_fn():
        return survey.survey(root, repo, audit_common.gh_api, survey.default_board_source(repo), table, fleet=False)

    ctx = migrations.Context(root, repo, repo_client, project_client, standard, target, flags, survey_fn, board)
    ctx.table = table
    return ctx


def render(report, blockers):
    lines = ["Upgrade plan"] + ["  blocked: " + b for b in blockers]

    for entry in report:
        lines.append("  {:<4} {:<12} {}".format(entry["id"], entry["status"], entry["title"]))

        for text in entry.get("plan", []):
            lines.append("         - " + text)

        if entry.get("error"):
            lines.append("         ! " + entry["error"])

    return "\n".join(lines)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])

    try:
        if not args or args[0].startswith("--"):
            raise KitError("usage: python tools/upgrade.py <project-path> [--repo owner/name] [--apply] [--only ID] [--with-views] "
                           "[--convert-legacy] [--include-open] [--delete-version-number] [--overwrite-edited] [--pause N]")

        root = os.path.abspath(args[0])
        repo = kit_common.option(args, "--repo") or audit_common.remote_repo(root)

        if not repo:
            raise KitError("the origin remote of {} is not a GitHub repository: say it with --repo owner/name".format(root))

        pause = kit_common.option(args, "--pause")
        ctx = make_context(root, repo, {flag for option, flag in FLAGS.items() if option in args})
        blockers = blocking(ctx)
        apply_it = "--apply" in args

        if apply_it and blockers:
            print(render([], blockers))
            raise KitError("resolve the blockers first (they came from the survey)")

        run, report = chain(ctx, not apply_it, kit_common.option(args, "--only"), int(pause) if pause else 0)
    except (KitError, GitHubError, ValueError, build_fingerprints.FingerprintError) as error:
        print("upgrade refused: {}".format(error))
        return 1

    print(render(report, blockers))
    kit_common.print_run(run)
    path = kit_common.save_log(root, "upgrade", run, {"report": report, "target": ctx.target})
    print("log: {}".format(path))
    return 1 if any(e["status"] == "failed" for e in report) else 0


if __name__ == "__main__":
    sys.exit(main())
