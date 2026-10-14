"""Prepare and check a small remote repository without deleting local files.

Standard library only. Preparation copies current working bytes, keeps an
omission inventory, and initializes a new Git repository. It never commits,
pushes, deletes, copies old history, or runs scientific generators.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "plan/submission-policy.json"
LOCAL_MANIFEST = "plan/remote-local-files.json"
COPY_MANIFEST = "plan/remote-copy-manifest.json"


def git(root: Path, *args: str, data: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args], input=data,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def policy(root: Path) -> dict:
    return json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))


def reason(name: str, size: int, rules: dict) -> str | None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return "unsafe_path"
    if path.parts[0] in rules["excluded_roots"] and name not in rules["allowed_exact"]:
        return "local_directory"
    if any(part in rules["excluded_directory_names"] for part in path.parts[:-1]):
        return "archive_or_cache"
    if path.suffix.lower() in rules["forbidden_extensions"]:
        return "binary_asset_or_historical_source"
    if not (
        path.suffix.lower() in rules["allowed_extensions"]
        or path.name in rules["allowed_names"]
        or name in rules["allowed_exact"]
    ):
        return "outside_text_scope"
    if size >= rules["max_file_bytes"]:
        return "file_size_limit"
    return None


def names(root: Path, include_untracked: bool = False) -> list[str]:
    args = ["ls-files", "-z", "--cached"]
    if include_untracked:
        args += ["--others", "--exclude-standard"]
    return sorted(set(n.decode("utf-8") for n in git(root, *args).split(b"\0") if n))


def size_tree(path: Path) -> int:
    total = 0
    for item in path.rglob("*"):
        if item.is_symlink():
            raise ValueError(f"Symlink is not allowed: {item}")
        if item.is_file():
            total += item.stat().st_size
    return total


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare(root: Path, destination: Path) -> dict:
    rules = policy(root)
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Destination exists; no file will be overwritten")
    if destination == root or root in destination.parents:
        raise ValueError("Use a new destination outside the complete research workspace")
    tracked = set(names(root))
    selected, omitted = [], []
    head = git(root, "rev-parse", "HEAD").decode().strip()
    for name in names(root, include_untracked=True):
        if name in {LOCAL_MANIFEST, COPY_MANIFEST}:
            continue
        path = root / name
        if path.is_symlink():
            raise ValueError(f"Symlink: {name}")
        if path.is_dir() and reason(name, 0, rules):
            if name in tracked:
                omitted.append({"path": name, "bytes": None, "sha256": None,
                                "reason": "local_directory_or_gitlink",
                                "disposition": "retained_at_source_path"})
            continue
        if not path.is_file():
            raise ValueError(f"Missing tracked/source file: {name}")
        size = path.stat().st_size
        why = reason(name, size, rules)
        row = {"path": name, "bytes": size, "sha256": sha(path)}
        if why:
            if name in tracked:
                omitted.append({**row, "reason": why, "disposition": "retained_at_source_path"})
        else:
            # UTF-8 text only; a renamed binary asset cannot slip through by suffix.
            content = path.read_bytes()
            content.decode("utf-8-sig")
            if b"\0" in content:
                raise ValueError(f"Binary content with text extension: {name}")
            selected.append(row)
    if sum(row["bytes"] for row in selected) >= rules["max_repository_bytes"]:
        raise ValueError("Selected working files already exceed repository budget")

    destination.mkdir(parents=True)
    for row in selected:
        source = root / row["path"]
        target = destination / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation and source hash validation guard against concurrent edits.
        content = source.read_bytes()
        if hashlib.sha256(content).hexdigest() != row["sha256"]:
            raise ValueError(f"Source changed during preparation: {row['path']}")
        with target.open("xb") as stream:
            stream.write(content)
    save(destination / LOCAL_MANIFEST, {
        "source_head": head, "source_root": str(root),
        "scope": "Previously tracked omitted files only; ignored local assets are not fully inventoried",
        "files": omitted,
    })
    save(destination / COPY_MANIFEST, {
        "source_head": head, "source_root": str(root),
        "scope": "Current working bytes, including uncommitted writing and evidence-route changes",
        "history_copied": False,
        "files": selected,
        "generated_in_destination": [LOCAL_MANIFEST, COPY_MANIFEST],
    })
    git(destination, "init", "--initial-branch=master")
    git(destination, "config", "core.autocrlf", "false")
    git(destination, "config", "core.hooksPath", ".githooks")
    # Keep copied bytes in this upload workspace without changing the source
    # repository's shared attributes (which would create unrelated EOL diffs).
    with (destination / ".git/info/attributes").open("x", encoding="utf-8") as stream:
        stream.write("* -text\n")
    git(destination, "add", "--all")
    git(destination, "update-index", "--chmod=+x", ".githooks/pre-commit", ".githooks/pre-push")
    report = check(destination, history=False)
    expected = {row["path"] for row in selected} | {LOCAL_MANIFEST, COPY_MANIFEST}
    if set(names(destination)) != expected:
        raise ValueError("Copied and staged files differ; inspect ignore rules")
    for row in selected:
        committed_bytes = git(destination, "show", ":" + row["path"])
        if hashlib.sha256(committed_bytes).hexdigest() != row["sha256"]:
            raise ValueError(f"Staging altered bytes: {row['path']}")
    return {
        **report, "copied_files": len(selected), "omitted_tracked_files": len(omitted),
        "omission_reasons": dict(Counter(row["reason"] for row in omitted)),
        "source_head": head, "copy_hashes": "Verified", "automatic_commit": False,
        "automatic_push": False,
    }


def check(root: Path, history: bool) -> dict:
    rules = policy(root)
    errors = []
    entries = []
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        metadata, encoded_name = record.split(b"\t", 1)
        mode, oid, stage = metadata.decode().split()
        name = encoded_name.decode("utf-8")
        if mode not in {"100644", "100755"} or stage != "0":
            errors.append(f"Unsupported index mode/stage: {name}")
        entries.append((name, oid))
    objects = {}
    requests = sorted({oid for _, oid in entries})
    if history:
        git(root, "rev-parse", "--verify", "HEAD")
        # A reintroduced old branch/tag also makes its forbidden blobs reachable.
        refs = git(root, "rev-list", "--objects", "--all").decode("utf-8").splitlines()
        requests = sorted(set(requests) | {line.split(" ", 1)[0] for line in refs})
        # rev-list names each object only once. Check all historical path names
        # too, including an archive alias that shares a blob with an allowed file.
        changed_names = git(root, "log", "--all", "--format=", "--name-only", "-z")
        for encoded_name in changed_names.split(b"\0"):
            name = encoded_name.decode("utf-8").strip("\n")
            if name and reason(name, 0, rules):
                errors.append(f"Historical path outside scope: {name}")
    else:
        refs = []
    if requests:
        response = git(root, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)",
                       data=("\n".join(requests) + "\n").encode())
        for line in response.decode().splitlines():
            oid, kind, size = line.split()
            objects[oid] = (kind, int(size))
    total_staged = 0
    for name, oid in entries:
        kind, size = objects[oid]
        total_staged += size
        why = reason(name, size, rules)
        if kind != "blob" or why:
            errors.append(f"Index: {name}: {why or kind}")
    if history:
        for line in refs:
            oid, _, name = line.partition(" ")
            kind, size = objects[oid]
            if kind == "blob":
                why = reason(name, size, rules)
                if why:
                    errors.append(f"History: {name}: {why}")
    git_directory = Path(git(root, "rev-parse", "--absolute-git-dir").decode().strip())
    if (git_directory / "objects/info/alternates").exists():
        errors.append("External object storage is not allowed")
    git_bytes = size_tree(git_directory)
    # Ignore local restored assets, but count every uploaded file and Git object.
    repository_bytes = total_staged + git_bytes
    if repository_bytes >= rules["max_repository_bytes"]:
        errors.append(f"Repository budget exceeded: {repository_bytes}")
    if errors:
        raise ValueError("\n".join(errors[:25]) + f"\nTotal violations: {len(errors)}")
    return {
        "status": "Verified", "root": str(root),
        "checked_scope": "index_and_reachable_history" if history else "index",
        "tracked_files": len(entries), "tracked_bytes": total_staged,
        "git_directory_bytes": git_bytes, "repository_bytes": repository_bytes,
        "limit_bytes": rules["max_repository_bytes"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare_parser = commands.add_parser("prepare")
    prepare_parser.add_argument("--destination", type=Path, required=True)
    check_parser = commands.add_parser("check")
    choice = check_parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--staged", action="store_true")
    choice.add_argument("--history", action="store_true")
    args = parser.parse_args()
    try:
        report = prepare(ROOT, args.destination) if args.command == "prepare" else check(ROOT, args.history)
    except (ValueError, RuntimeError, OSError, UnicodeError) as error:
        parser.exit(1, f"Not verified: {error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
