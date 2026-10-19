"""The fingerprints of every version of the standard, derived from its git history.

For each finalized version, the hash of each automation file as it was at the commit that finalized it, so a survey
can say which version each file of a project comes from and which files were edited. The hashes are computed from
the files in git, with line endings normalized as the manifest check does (`check_manifest.file_hash`); the
`standard` that old manifests name is not used, because some named a version that never existed (V0.7.1) or were
corrected later. A version is found by its commit `Finalize V0.1.2`; one finalized by hand, without that commit, by
the commit that added its heading to `CHANGELOG.md`; a hotfix version (finished on its own branch, and counted once it has its `released/` tag) by its commit
on any ref.

The table is derived at run time from the history, because a version can be fingerprinted only after its own merge:
a committed table would always lag one version. `--cache` keeps the result between runs, keyed by the commit of
`HEAD`. The history must be complete: a shallow clone is refused.

    python tools/build_fingerprints.py                              summary of every version
    python tools/build_fingerprints.py --json table.json            also write the whole table
    python tools/build_fingerprints.py --cache table.json           reuse the table while HEAD has not moved
    python tools/build_fingerprints.py --identify <project-path>    which version(s) the project's automation files are
    python tools/build_fingerprints.py --repo <path>                the standard's clone (default: this repository)

Read-only. Exit code 2 for a bad argument or an incomplete history.
"""
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STANDARD = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(STANDARD, ".github", "scripts"))

import changelog  # noqa: E402
import check_manifest  # noqa: E402

FINALIZE = re.compile(r"^Finalize (V\d+\.\d+\.\d+(?:-HF\d+)?)$")
MANIFEST = check_manifest.MANIFEST.replace(os.sep, "/")
CHANGELOG = "CHANGELOG.md"


class FingerprintError(Exception):
    pass


def git(repo, *args):
    """(exit code, standard output as text without the final newline)."""
    result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout.rstrip("\n")


class Blobs:
    """The files of commits, read through one `git cat-file --batch` process."""

    def __init__(self, repo):
        self.process = subprocess.Popen(["git", "cat-file", "--batch"], cwd=repo, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def read(self, spec):
        """The bytes of `<commit>:<path>`, or None when there is no such file."""
        self.process.stdin.write((spec + "\n").encode("utf-8"))
        self.process.stdin.flush()
        header = self.process.stdout.readline()

        if header.rstrip().endswith(b" missing") or not header:
            return None

        size = int(header.split()[2])
        data = self.process.stdout.read(size)
        self.process.stdout.read(1)
        return data

    def close(self):
        self.process.stdin.close()
        self.process.wait()
        self.process.stdout.close()


def digest(data):
    """SHA-256 with line endings normalized, as `check_manifest.file_hash` does for a file."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def is_shallow(repo):
    code, out = git(repo, "rev-parse", "--is-shallow-repository")
    return code == 0 and out == "true"


def finalize_commits(repo):
    """{version: oldest commit with the subject `Finalize <version>`} on any ref."""
    code, out = git(repo, "log", "--all", "--format=%H%x09%s")
    found = {}

    for line in reversed(out.split("\n") if code == 0 and out else []):
        sha, _, subject = line.partition("\t")
        match = FINALIZE.match(subject)

        if match:
            found.setdefault(match.group(1), sha)

    return found


def heading_commit(repo, version):
    """The oldest commit that added the heading of `version` to the changelog, for a version finalized by hand."""
    code, out = git(repo, "log", "--all", "--reverse", "--format=%H", "-S## {} — ".format(version), "--", CHANGELOG)
    return out.split("\n")[0] if code == 0 and out else None


def changelog_versions(repo, ref):
    """The finalized versions of the changelog at `ref`, newest first."""
    code, out = git(repo, "show", "{}:{}".format(ref, CHANGELOG))

    if code != 0:
        return []

    return [str(s.version) for s in changelog.parse(out + "\n") if s.kind == "final"]


def version_key(version):
    base, _, hotfix = version[1:].partition("-HF")
    return tuple(int(x) for x in base.split(".")) + (int(hotfix or 0),)


def automation_paths(repo, sha, blobs):
    """(the paths to fingerprint at `sha`, the manifest dictionary or None). A commit with a manifest is trusted for
    which files the standard declared; one without is judged by the patterns of the manifest check."""
    raw = blobs.read("{}:{}".format(sha, MANIFEST))

    if raw is not None:
        manifest = json.loads(raw.decode("utf-8"))
        return sorted(manifest.get("files", {})), manifest

    code, out = git(repo, "ls-tree", "-r", "--name-only", sha)
    import fnmatch
    names = out.split("\n") if code == 0 and out else []
    return sorted(n for n in names if any(fnmatch.fnmatch(n, p) for p in check_manifest.PATTERNS)), None


def fingerprint(repo, version, sha, method, blobs):
    paths, manifest = automation_paths(repo, sha, blobs)
    files, missing, stale = {}, [], []

    for path in paths:
        data = blobs.read("{}:{}".format(sha, path))

        if data is None:
            missing.append(path)
            continue

        files[path] = digest(data)

        if manifest is not None and manifest["files"].get(path) not in (None, files[path]):
            stale.append(path)

    code, date = git(repo, "show", "-s", "--format=%cI", sha)
    return {"commit": sha, "method": method, "date": date if code == 0 else None,
            "manifest_standard": manifest.get("standard") if manifest else None,
            "files": files, "missing": missing, "stale_manifest": stale}


def build(repo=STANDARD, ref="HEAD"):
    """The table {"head": commit, "versions": {version: entry}}; raises FingerprintError on an incomplete history."""
    if is_shallow(repo):
        raise FingerprintError("the history of {} is shallow: clone it with its full history "
                               "(`git fetch --unshallow`) so that every version can be fingerprinted".format(repo))

    code, head = git(repo, "rev-parse", ref)

    if code != 0:
        raise FingerprintError("{} is not a git repository with a commit {}".format(repo, ref))

    commits = finalize_commits(repo)
    versions = changelog_versions(repo, ref)
    # A hotfix version is finished on its own branch, so it is not in the changelog of main: it counts when it was
    # released (the tag `released/<version>`), not when it is a trial or an unfinished branch.
    versions += [v for v in commits if v not in versions and git(repo, "rev-parse", "-q", "--verify", "refs/tags/released/" + v)[0] == 0]
    table = {}
    blobs = Blobs(repo)

    try:
        for version in sorted(set(versions), key=version_key):
            sha, method = commits.get(version), "finalize-commit"

            if not sha:
                sha, method = heading_commit(repo, version), "changelog-heading"

            if not sha:
                table[version] = {"commit": None, "method": "none", "date": None, "manifest_standard": None,
                                  "files": {}, "missing": [], "stale_manifest": []}
                continue

            table[version] = fingerprint(repo, version, sha, method, blobs)
    finally:
        blobs.close()

    return {"head": head, "versions": table}


def load_or_build(repo=STANDARD, cache=None):
    """The table, reusing `cache` (a file) while its `head` is the commit of HEAD."""
    if cache and os.path.isfile(cache):
        with open(cache, encoding="utf-8") as handle:
            stored = json.load(handle)

        code, head = git(repo, "rev-parse", "HEAD")

        if code == 0 and stored.get("head") == head:
            return stored

    table = build(repo)

    if cache:
        with open(cache, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(table, handle, indent=1, sort_keys=True)
            handle.write("\n")

    return table


def identify(root, table):
    """Which version(s) of the standard the automation files of the project at `root` come from.

    Returns {"state", "versions", "files", "closest"}:
    - state `none`: the project has no automation file;
    - `match`: its files are exactly those of every version in `versions` (versions that changed no automation file
      are indistinguishable, so there can be several);
    - `mixed`: every file is from some version, but not all from the same one;
    - `modified`: a file matches no version of the standard (edited locally, or from a version unknown to the table).
    `files` gives, per file, the versions it matches; `closest` the versions that match most files."""
    paths = check_manifest.automation_files(root)

    if not paths:
        return {"state": "none", "versions": [], "files": {}, "closest": []}

    hashes = {p: check_manifest.file_hash(os.path.join(root, p)) for p in paths}
    versions = table["versions"]
    matches = {p: sorted((v for v, e in versions.items() if e["files"].get(p) == hashes[p]), key=version_key) for p in paths}
    inscope = lambda path: any(fnmatch.fnmatch(path, pattern) for pattern in check_manifest.PATTERNS)  # noqa: E731
    # The files of an old version are compared as far as today's patterns see them: a pattern that did not exist then, or a
    # file that is no longer an automation file, must not make a project that holds exactly that version look mixed.
    same = [v for v, e in versions.items() if {p for p in e["files"] if inscope(p)} == set(paths)
            and all(e["files"][p] == hashes[p] for p in paths)]
    score = {v: sum(1 for p in paths if v in matches[p]) for v in versions}
    best = max(score.values()) if score else 0
    closest = sorted((v for v, s in score.items() if s == best and best), key=version_key)

    if same:
        state = "match"
    elif all(matches[p] for p in paths):
        state = "mixed"
    else:
        state = "modified"

    return {"state": state, "versions": sorted(same, key=version_key), "files": matches, "closest": closest}


def summary(table):
    lines = ["{:<14} {:<8} {:<18} {:>5}  {}".format("version", "commit", "found by", "files", "notes")]

    for version, entry in sorted(table["versions"].items(), key=lambda kv: version_key(kv[0])):
        notes = []

        if entry["missing"]:
            notes.append("{} listed file(s) missing".format(len(entry["missing"])))

        if entry["stale_manifest"]:
            notes.append("{} stale manifest hash(es)".format(len(entry["stale_manifest"])))

        if entry["manifest_standard"] and entry["manifest_standard"] != version:
            notes.append("manifest names {}".format(entry["manifest_standard"]))

        lines.append("{:<14} {:<8} {:<18} {:>5}  {}".format(version, (entry["commit"] or "-")[:7], entry["method"],
                                                           len(entry["files"]), "; ".join(notes)))

    return "\n".join(lines)


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    args = list(argv if argv is not None else sys.argv[1:])
    options = {}

    for flag in ("--repo", "--json", "--cache", "--identify"):
        if flag in args:
            index = args.index(flag)

            if index + 1 >= len(args) or args[index + 1].startswith("--"):
                print("{} needs a value".format(flag))
                return 2

            options[flag] = args[index + 1]

    repo = os.path.abspath(options.get("--repo", STANDARD))

    try:
        table = load_or_build(repo, options.get("--cache"))
    except FingerprintError as error:
        print(error)
        return 2

    if "--json" in options:
        with open(options["--json"], "w", encoding="utf-8", newline="\n") as handle:
            json.dump(table, handle, indent=1, sort_keys=True)
            handle.write("\n")

    if "--identify" in options:
        result = identify(os.path.abspath(options["--identify"]), table)
        print("state: {}".format(result["state"]))
        print("versions: {}".format(", ".join(result["versions"]) or "-"))
        print("closest: {}".format(", ".join(result["closest"]) or "-"))
        return 0

    print(summary(table))
    return 0


if __name__ == "__main__":
    sys.exit(main())
