"""The automation files (every version): the files the manifest of the standard lists are copied into the project.

Each file that differs is first saved in the state folder. A file edited locally (it matches no version of the standard)
stops the step unless the flag `overwrite_edited` is given, because the edit would be lost from the working tree (it
stays in git). A file that an earlier version of the standard had and the standard no longer has is removed when it is
exactly that earlier file (saved first), because it would otherwise break the project's own tests; one that was
edited is listed and kept."""
import os
import shutil

import check_manifest
import kit_common

ID, SINCE, TITLE, GATE = "F1", "V0.3.0", "the automation files of the standard", None


def sources(ctx):
    return check_manifest.automation_files(ctx.standard_root)


def differing(ctx):
    found = []

    for path in sources(ctx):
        mine = os.path.join(ctx.root, path)

        if not os.path.exists(mine) or check_manifest.file_hash(mine) != check_manifest.file_hash(os.path.join(ctx.standard_root, path)):
            found.append(path)

    return found


def edited(ctx):
    files = ctx.survey.get("files", {}).get("identity", {}).get("files", {})
    return sorted(path for path in differing(ctx) if path in files and not files[path])


def known_hashes(ctx):
    """{path: hashes it had in any version of the standard}, from the fingerprints."""
    found = {}

    for entry in (getattr(ctx, "table", None) or {}).get("versions", {}).values():
        for path, digest in entry["files"].items():
            found.setdefault(path, set()).add(digest)

    return found


def removable(ctx):
    """Files of the project that are exactly a file an earlier version of the standard had and this one has not."""
    current = set(sources(ctx))
    return sorted(path for path, digests in known_hashes(ctx).items() if path not in current
                  and os.path.isfile(os.path.join(ctx.root, path)) and check_manifest.file_hash(os.path.join(ctx.root, path)) in digests)


def obsolete(ctx):
    """Automation-looking files the standard no longer has that are not exactly an earlier version's: kept."""
    return sorted(set(check_manifest.automation_files(ctx.root)) - set(sources(ctx)) - set(removable(ctx)))


def needed(ctx):
    return bool(differing(ctx) or removable(ctx))


def plan(ctx):
    lines = ["copy {} automation file(s) of the standard {}".format(len(differing(ctx)), ctx.target)]
    lines += ["edited locally, needs the flag overwrite_edited: " + p for p in edited(ctx) if "overwrite_edited" not in ctx.flags]
    lines += ["remove (an earlier version's file the standard no longer has): " + p for p in removable(ctx)]
    lines += ["not in the standard any longer, edited or unknown (kept; delete by hand if you agree): " + p for p in obsolete(ctx)]
    return lines


def apply(ctx, run):
    blocked = [p for p in edited(ctx) if "overwrite_edited" not in ctx.flags]

    if blocked:
        raise kit_common.KitError("these files were edited locally: {}; give the flag overwrite_edited to replace them (they stay in git)"
                                  .format(", ".join(blocked)))

    for path in differing(ctx):
        mine = os.path.join(ctx.root, path)
        backup = os.path.join(ctx.root, kit_common.STATE_FOLDER, "backup", path) if run.dry_run else kit_common.state_path(ctx.root, "backup", path)
        run.do("copy {}".format(path), copy, os.path.join(ctx.standard_root, path), mine, backup)

    for path in removable(ctx):
        backup = os.path.join(ctx.root, kit_common.STATE_FOLDER, "backup", path) if run.dry_run else kit_common.state_path(ctx.root, "backup", path)
        run.do("remove {} (an earlier version's file the standard no longer has)".format(path), remove, os.path.join(ctx.root, path), backup)

    for path in obsolete(ctx):
        run.log.append("not in the standard any longer, kept: {}".format(path))


def remove(target, backup):
    os.makedirs(os.path.dirname(backup), exist_ok=True)
    shutil.copy2(target, backup)
    os.remove(target)


def copy(source, target, backup):
    if os.path.exists(target):
        os.makedirs(os.path.dirname(backup), exist_ok=True)
        shutil.copy2(target, backup)

    os.makedirs(os.path.dirname(target), exist_ok=True)
    shutil.copy2(source, target)  # keeps the executable bit of the hooks
