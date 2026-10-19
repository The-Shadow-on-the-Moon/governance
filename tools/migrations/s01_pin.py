"""S1: the pin of the standard in a project that carries it as a submodule at `doc/governance` (every version).

The submodule is moved to the commit of the standard this checkout is at, and the new pointer is staged, so it travels
in the adoption change with the files copied from it. When the tool runs from the submodule itself nothing is moved,
only staged. A project that does not carry the standard as a submodule (the standard's own repository, a project that
keeps the checkout elsewhere) has no such step."""
import os

import audit_common
import kit_common
import survey

ID, SINCE, TITLE, GATE = "S1", "V0.3.0", "the pin of the standard (submodule doc/governance)", None


def target_commit(ctx):
    code, out = audit_common.git(ctx.standard_root, "rev-parse", "HEAD")
    return out if code == 0 else None


def embedded(ctx):
    return ctx.survey.get("embedded", {})


def needed(ctx):
    found = embedded(ctx)
    return bool(found.get("present") and found.get("initialized") and target_commit(ctx) and found.get("pinned") != target_commit(ctx))


def plan(ctx):
    found = embedded(ctx)
    lines = []

    if found.get("checked_out") != target_commit(ctx):
        lines.append("move the submodule {} from {} to {}".format(survey.EMBEDDED, (found.get("checked_out") or "")[:8], target_commit(ctx)[:8]))

    lines.append("stage the pointer {} ({} to {}) for the adoption change".format(survey.EMBEDDED, (found.get("pinned") or "")[:8], target_commit(ctx)[:8]))
    return lines


def git(folder, *args):
    code, out = audit_common.git(folder, *args)

    if code != 0:
        raise kit_common.KitError("git {} failed in {}: {}".format(" ".join(args), folder, out or "no output"))


def move(ctx, folder, commit):
    git(folder, "fetch", os.path.abspath(ctx.standard_root), commit)  # from the checkout the tool runs from: no network, the exact commit
    git(folder, "checkout", "--detach", commit)


def apply(ctx, run):
    found = embedded(ctx)
    folder = os.path.join(ctx.root, *survey.EMBEDDED.split("/"))
    commit = target_commit(ctx)

    if found.get("checked_out") != commit:
        run.do("move the submodule {} to {}".format(survey.EMBEDDED, commit[:8]), move, ctx, folder, commit)

    run.do("stage the pointer {}".format(survey.EMBEDDED), git, ctx.root, "add", "--", survey.EMBEDDED)
