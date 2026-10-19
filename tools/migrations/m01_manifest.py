"""The manifest (V0.3.0, #226): its `standard` names the version of the files the project holds. In a project that is
not the standard's repository it is never the placeholder. Written after the files are copied."""
import os

import check_manifest

ID, SINCE, TITLE, GATE = "M1", "V0.15.0", "the manifest of the project", None


def current(ctx):
    path = os.path.join(ctx.root, check_manifest.MANIFEST)
    return check_manifest.load(path) if os.path.isfile(path) else None


def wanted(ctx):
    return check_manifest.build(ctx.root, ctx.target)


def needed(ctx):
    if os.path.abspath(ctx.root) == os.path.abspath(ctx.standard_root):
        return False

    return current(ctx) != wanted(ctx)


def plan(ctx):
    return ["write {} with the standard {} and the hashes of the {} automation files".format(
        check_manifest.MANIFEST, ctx.target, len(check_manifest.automation_files(ctx.standard_root)))]


def write(root, manifest):
    os.makedirs(os.path.dirname(os.path.join(root, check_manifest.MANIFEST)), exist_ok=True)
    check_manifest.write(root, manifest)


def apply(ctx, run):
    run.do("write the manifest (standard {})".format(ctx.target), write, ctx.root, wanted(ctx))
