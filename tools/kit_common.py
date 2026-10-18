"""What the tools of the adoption and upgrade kit share: the automation modules, the connection with GitHub, and the
state folder.

The tools run from a checkout of the standard and are pointed at a project with a path. They use the automation's own
modules (`.github/scripts`), so the board is read and written exactly as the automation does. They are read-only unless
`--apply` is given, and the state they keep (what they did, the restore files) goes into a folder of the project that
git ignores, never into the tracked files.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STANDARD = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(STANDARD, ".github", "scripts"))
sys.path.insert(0, HERE)

import finalize  # noqa: E402
import github_api  # noqa: E402

STATE_FOLDER = ".upgrade-state"


class KitError(Exception):
    """A refusal the tool explains: nothing was changed."""


def gh_token(env=None, runner=subprocess.run):
    """The token of the person: GITHUB_TOKEN or GH_TOKEN, else the one `gh` holds."""
    env = os.environ if env is None else env
    value = env.get("GITHUB_TOKEN") or env.get("GH_TOKEN")

    if value:
        return value

    try:
        result = runner(["gh", "auth", "token"], capture_output=True, text=True, encoding="utf-8")
    except OSError:
        raise KitError("`gh` is not installed: install it and run `gh auth login`, or set GITHUB_TOKEN")

    if result.returncode != 0 or not result.stdout.strip():
        raise KitError("not signed in: run `gh auth login` (scopes repo, workflow, project, read:org), or set GITHUB_TOKEN")

    return result.stdout.strip()


def connect(repo, env=None, runner=subprocess.run):
    """(repo client, project client) for `owner/name`. PROJECT_TOKEN, when set, is used for the board."""
    env = os.environ if env is None else env
    token = gh_token(env, runner)
    return github_api.Client(token, repo), github_api.Client(env.get("PROJECT_TOKEN") or token, repo)


def exclude_state_folder(root):
    """Make git ignore the state folder of the project at `root`, through `.git/info/exclude` (never tracked, never
    committed). Returns True when the entry is in place, False when `root` is not a git work tree."""
    git_dir = os.path.join(root, ".git")

    if not os.path.isdir(git_dir):
        return False

    path = os.path.join(git_dir, "info", "exclude")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    entry = STATE_FOLDER + "/"
    text = ""

    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            text = handle.read()

    if entry not in text.splitlines():
        with open(path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(("" if not text or text.endswith("\n") else "\n") + entry + "\n")

    return True


def state_path(root, *parts):
    """A path in the state folder of the project, which is created and ignored by git."""
    exclude_state_folder(root)
    folder = os.path.join(root, STATE_FOLDER)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, *parts)


def stamp(moment=None):
    return (moment or datetime.now(timezone.utc)).strftime("%Y%m%d%H%M%S")


def save_log(root, name, run, extra=None):
    """Write what a run did (or would do) to the state folder; returns the path."""
    path = state_path(root, "{}-{}.json".format(name, stamp()))

    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump({"tool": name, "dry_run": run.dry_run, "log": run.log, **(extra or {})}, handle, indent=1)
        handle.write("\n")

    return path


def print_run(run):
    prefix = "would: " if run.dry_run else "did: "

    for line in run.log:
        print(prefix + line)

    if run.dry_run:
        print("dry run: nothing was changed; add --apply to do it")


def option(args, name):
    """The value after `name` in `args`, or None; a missing value is a KitError."""
    if name not in args:
        return None

    index = args.index(name) + 1

    if index >= len(args) or args[index].startswith("--"):
        raise KitError("{} needs a value".format(name))

    return args[index]
