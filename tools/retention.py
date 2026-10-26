#!/usr/bin/env python3
"""30-day retention for experiment artefacts (owner rule 2026-10-26; see CONTRACT_RETENTION.md).
The source of the rule lives in the repo: `claude/retention/CONTRACT_RETENTION.md`.
  python3 tools/retention.py                          # == scan with tools/retention_policy.json
  python3 tools/retention.py --policy F scan          # dry run: report only, nothing deleted
  python3 tools/retention.py --policy F apply         # delete EXPIRED units (capped per run)
  python3 tools/retention.py promote SRC [--to DIR]   # move one unit to the promote dir
  python3 tools/retention.py --now 1761000000 scan    # override the clock (tests / demos)
Exit codes: 0 ok, 2 bad usage / invalid policy / refused promote, 3 a deletion failed.
Every run ends with ONE JSON summary line: {"expired":..,"soon":..,"protected":..,"deleted":..,
"failed":..,"deferred":..,"freed_mb":..}. stdlib only; never follows symlinks; deletes only `apply`."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from typing import Dict, Iterator, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_POLICY = os.path.join(HERE, "retention_policy.json")
DAY = 86400.0
KEEP_FILE = ".keep"

# kept in one place so the checks and the report agree
STATE_EXPIRED = "EXPIRED"
STATE_SOON = "SOON"
STATE_FRESH = "FRESH"
STATE_PROTECTED = "PROTECTED"

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_FAILED = 3


class PolicyError(Exception):
    """Invalid policy file (exit 2, nothing is touched)."""


class Refused(Exception):
    """A promote request that the policy forbids (exit 2, nothing is moved)."""


_AgeSize = Tuple[float, float]  # (age_days, size_bytes)


# --------------------------------------------------------------------------------------- policy loading
def _is_abs_nonroot(path: object) -> bool:
    return isinstance(path, str) and os.path.isabs(path) and path not in ("", "/")


def load_policy(path: str) -> Dict[str, object]:
    """Read and validate the policy; raise PolicyError on anything the contract forbids."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        raise PolicyError("policy file not found: %s" % path)
    except OSError as exc:
        raise PolicyError("cannot read policy %s: %s" % (path, exc))
    except ValueError as exc:
        raise PolicyError("policy %s is not valid JSON: %s" % (path, exc))
    if not isinstance(raw, dict):
        raise PolicyError("policy must be a JSON object")

    max_age = raw.get("max_age_days")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age < 1:
        raise PolicyError("max_age_days must be an int >= 1")
    warn = raw.get("warn_days")
    if not isinstance(warn, int) or isinstance(warn, bool) or not (0 <= warn <= max_age):
        raise PolicyError("warn_days must be an int in 0..max_age_days")
    cap = raw.get("max_units_per_run")
    if not isinstance(cap, int) or isinstance(cap, bool) or cap < 0:
        raise PolicyError("max_units_per_run must be an int >= 0")

    promote_dir = raw.get("promote_dir")
    if not isinstance(promote_dir, str) or not promote_dir:
        raise PolicyError("promote_dir must be a non-empty string")

    roots_raw = raw.get("roots", [])
    if not isinstance(roots_raw, list):
        raise PolicyError("roots must be a list")
    roots: List[Dict[str, object]] = []
    for entry in roots_raw:
        if not isinstance(entry, dict):
            raise PolicyError("every root must be an object")
        rpath = entry.get("path")
        if not _is_abs_nonroot(rpath):
            raise PolicyError("root path must be absolute and not '/': %r" % (rpath,))
        keep = entry.get("keep", [])
        if not isinstance(keep, list) or any(not isinstance(k, str) for k in keep):
            raise PolicyError("root keep must be a list of names")
        roots.append({"path": os.path.normpath(rpath), "keep": frozenset(keep)})

    globs_raw = raw.get("globs", [])
    if not isinstance(globs_raw, list) or any(not isinstance(g, str) for g in globs_raw):
        raise PolicyError("globs must be a list of strings")
    globs: List[str] = []
    for g in globs_raw:
        if not os.path.isabs(g):
            raise PolicyError("glob must be absolute: %r" % (g,))
        if g.rstrip("/") == "":
            raise PolicyError("glob must not be '/'")
        globs.append(g)

    return {
        "max_age_days": max_age,
        "warn_days": warn,
        "max_units_per_run": cap,
        "promote_dir": os.path.normpath(promote_dir),
        "roots": roots,
        "globs": globs,
    }


# --------------------------------------------------------------------------------------------- units
def _newest_mtime(path: str) -> float:
    """Newest mtime of `path`, walking a directory with scandir; never follows symlinks."""
    try:
        st = os.lstat(path)
    except OSError:
        return 0.0
    newest = st.st_mtime
    if not os.path.isdir(path) or os.path.islink(path):
        return newest
    stack: List[str] = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_symlink():
                            est = entry.stat(follow_symlinks=False)
                            if est.st_mtime > newest:
                                newest = est.st_mtime
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                            continue
                        est = entry.stat(follow_symlinks=False)
                        if est.st_mtime > newest:
                            newest = est.st_mtime
                    except OSError:
                        continue
        except OSError:
            continue
    return newest


def _unit_size(path: str) -> int:
    """Sum of file sizes inside `path` (no symlink following); a file is its own size."""
    try:
        st = os.lstat(path)
    except OSError:
        return 0
    if not os.path.isdir(path) or os.path.islink(path):
        return int(st.st_size)
    total = 0
    stack: List[str] = [path]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path)
                            continue
                        total += int(entry.stat(follow_symlinks=False).st_size)
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def unit_age_and_size(path: str, now: float) -> _AgeSize:
    age_days = max(0.0, (now - _newest_mtime(path)) / DAY)
    return age_days, float(_unit_size(path))


def _has_top_keep(path: str) -> bool:
    if not os.path.isdir(path) or os.path.islink(path):
        return False
    return os.path.isfile(os.path.join(path, KEEP_FILE))


def _real_inside(child: str, parent: str) -> bool:
    """True when realpath(child) is strictly inside realpath(parent)."""
    rc = os.path.realpath(child)
    rp = os.path.realpath(parent)
    if rc == rp:
        return False
    prefix = rp if rp.endswith(os.sep) else rp + os.sep
    return rc.startswith(prefix)


def _candidate_roots(policy: Dict[str, object]) -> List[str]:
    """Direct children of every configured root, minus the kept names (deduped, sorted)."""
    seen: List[str] = []
    seen_set = set()
    for root in policy["roots"]:  # type: ignore[index]
        rpath = str(root["path"])
        keep = root["keep"]  # type: ignore[index]
        try:
            with os.scandir(rpath) as it:
                names = sorted(entry.name for entry in it)
        except OSError:
            continue
        for name in names:
            if name in keep:
                continue
            child = os.path.join(rpath, name)
            if child not in seen_set:
                seen_set.add(child)
                seen.append(child)
    return seen


def _candidate_globs(policy: Dict[str, object]) -> List[str]:
    import glob as globmod
    out: List[str] = []
    seen_set = set()
    for pattern in policy["globs"]:  # type: ignore[index]
        for match in sorted(globmod.glob(pattern)):
            norm = os.path.normpath(match)
            if norm not in seen_set:
                seen_set.add(norm)
                out.append(norm)
    return out


def _parent_of_unit(path: str, policy: Dict[str, object]) -> Optional[str]:
    """Return the root (or glob literal parent) that owns `path`, or None when not a unit."""
    norm = os.path.normpath(path)
    parent = os.path.dirname(norm)
    name = os.path.basename(norm)
    for root in policy["roots"]:  # type: ignore[index]
        rpath = osslash(root["path"])
        if os.path.normpath(parent) == rpath and name not in root["keep"]:  # type: ignore[index]
            return rpath
    import glob as globmod
    for pattern in policy["globs"]:  # type: ignore[index]
        for match in globmod.glob(pattern):
            if os.path.normpath(match) == norm:
                return os.path.normpath(os.path.dirname(pattern))
    return None


def osslash(path: object) -> str:
    return os.path.normpath(str(path))


def is_protected(path: str, owner: Optional[str]) -> bool:
    if os.path.islink(path):
        return True
    if _has_top_keep(path):
        return True
    if owner is not None and not _real_inside(path, owner):
        return True
    return False


def iter_units(policy: Dict[str, object]) -> Iterator[Tuple[str, Optional[str]]]:
    """Yield (unit_path, owner_path) for every candidate unit, deterministically sorted."""
    seen = set()
    candidates = _candidate_roots(policy) + _candidate_globs(policy)
    for path in sorted(candidates):
        norm = os.path.normpath(path)
        if norm in seen:
            continue
        seen.add(norm)
        if not os.path.lexists(norm):
            continue
        yield norm, _parent_of_unit(norm, policy)


def classify(age_days: float, max_age_days: int, warn_days: int) -> str:
    if age_days > max_age_days:
        return STATE_EXPIRED
    if age_days > max_age_days - warn_days:
        return STATE_SOON
    return STATE_FRESH


# ------------------------------------------------------------------------------------------- operations
def _fmt_mb(size_bytes: float) -> str:
    return "%.1f" % (size_bytes / 1048576.0)


def _fmt_gb(size_bytes: float) -> str:
    return "%.1f" % (size_bytes / 1073741824.0)


def _scan(policy: Dict[str, object], now: float) -> List[Dict[str, object]]:
    max_age = int(policy["max_age_days"])  # type: ignore[arg-type]
    warn = int(policy["warn_days"])  # type: ignore[arg-type]
    rows: List[Dict[str, object]] = []
    for path, owner in iter_units(policy):
        age, size = unit_age_and_size(path, now)
        if is_protected(path, owner):
            state = STATE_PROTECTED
        else:
            state = classify(age, max_age, warn)
        rows.append({"path": path, "owner": owner, "age": age, "size": size, "state": state})
    rows.sort(key=lambda r: (-float(r["age"]), str(r["path"])))
    return rows


def _print_report(policy: Dict[str, object], rows: List[Dict[str, object]]) -> None:
    roots = ", ".join(str(r["path"]) for r in policy["roots"])  # type: ignore[index]
    print("retention: max_age=%sd warn=%sd cap=%s promote_dir=%s" % (
        policy["max_age_days"], policy["warn_days"], policy["max_units_per_run"], policy["promote_dir"]))
    print("roots: %s" % (roots or "-"))
    print("globs: %s" % (", ".join(str(g) for g in policy["globs"]) or "-"))  # type: ignore[index]
    for row in rows:
        print("%-9s %8.1f d  %8s MB  %s" % (
            row["state"], row["age"], _fmt_mb(float(row["size"])), row["path"]))
    expired = [r for r in rows if r["state"] == STATE_EXPIRED]
    soon = [r for r in rows if r["state"] == STATE_SOON]
    protected = [r for r in rows if r["state"] == STATE_PROTECTED]
    freed = sum(float(r["size"]) for r in expired)
    print("expired: %d units, %s GB; soon: %d units; protected: %d" % (
        len(expired), _fmt_gb(freed), len(soon), len(protected)))


def delete_unit(path: str, owner: Optional[str]) -> None:
    """Delete one unit: re-check protection first, then rmtree/remove."""
    if is_protected(path, owner):
        raise Refused("protected")
    if owner is not None and not _real_inside(path, owner):
        raise Refused("outside allowed parent")
    if os.path.islink(path):
        raise Refused("symlink")
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)


def promote_unit(src: str, dest_dir: str, policy: Dict[str, object]) -> str:
    owner = _parent_of_unit(src, policy)
    if owner is None:
        raise Refused("not a unit of the policy")
    if os.path.islink(src):
        raise Refused("symlink")
    if not os.path.lexists(src):
        raise Refused("source does not exist")
    dest = os.path.join(dest_dir, os.path.basename(os.path.normpath(src)))
    if os.path.lexists(dest):
        raise Refused("destination exists: %s" % dest)
    os.makedirs(dest_dir, exist_ok=True)
    shutil.move(src, dest)
    return dest


# ------------------------------------------------------------------------------------------------- main
def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="retention.py", add_help=True,
                                     description="30-day retention for experiment artefacts")
    parser.add_argument("--policy", default=None, help="policy JSON (default: tools/retention_policy.json)")
    parser.add_argument("--now", type=float, default=None, help="epoch seconds to use as clock")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("scan")
    sub.add_parser("apply")
    promo = sub.add_parser("promote")
    promo.add_argument("src")
    promo.add_argument("--to", default=None)
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    try:
        args = _parse_args(argv)
    except SystemExit as exc:  # argparse exits 2 on usage errors; keep that contract
        return int(exc.code) if isinstance(exc.code, int) else EXIT_USAGE

    policy_path = args.policy if args.policy is not None else DEFAULT_POLICY
    now = args.now if args.now is not None else time.time()

    try:
        policy = load_policy(policy_path)
    except PolicyError as exc:
        print("retention: %s" % exc)
        _print_json({"expired": 0, "soon": 0, "protected": 0, "deleted": 0,
                     "failed": 0, "deferred": 0, "freed_mb": 0.0})
        return EXIT_USAGE

    command = args.command or "scan"
    if command == "promote":
        dest_dir = args.to if args.to else str(policy["promote_dir"])
        try:
            dest = promote_unit(os.path.normpath(args.src), os.path.normpath(dest_dir), policy)
        except Refused as exc:
            print("REFUSED %s: %s" % (args.src, exc))
            _print_json({"expired": 0, "soon": 0, "protected": 0, "deleted": 0,
                         "failed": 0, "deferred": 0, "freed_mb": 0.0})
            return EXIT_USAGE
        except OSError as exc:
            print("FAILED %s: %s" % (args.src, exc))
            _print_json({"expired": 0, "soon": 0, "protected": 0, "deleted": 0,
                         "failed": 1, "deferred": 0, "freed_mb": 0.0})
            return EXIT_FAILED
        print("PROMOTED %s -> %s" % (args.src, dest))
        _print_json({"expired": 0, "soon": 0, "protected": 0, "deleted": 0,
                     "failed": 0, "deferred": 0, "freed_mb": 0.0})
        return EXIT_OK

    rows = _scan(policy, now)
    _print_report(policy, rows)

    expired = [r for r in rows if r["state"] == STATE_EXPIRED]  # already oldest first
    soon = [r for r in rows if r["state"] == STATE_SOON]
    protected = [r for r in rows if r["state"] == STATE_PROTECTED]

    deleted = failed = deferred = 0
    freed = 0.0

    if command == "apply":
        cap = int(policy["max_units_per_run"])  # type: ignore[arg-type]
        for idx, row in enumerate(expired):
            path = str(row["path"])
            owner = row["owner"]
            if idx >= cap:
                print("DEFERRED %s" % path)
                deferred += 1
                continue
            size = float(row["size"])
            try:
                delete_unit(path, owner)  # type: ignore[arg-type]
            except Refused as exc:
                print("FAILED %s %s" % (path, exc))
                failed += 1
                continue
            except OSError as exc:
                print("FAILED %s %s" % (path, exc))
                failed += 1
                continue
            print("DELETED %s %s MB" % (path, _fmt_mb(size)))
            deleted += 1
            freed += size

    _print_json({"expired": len(expired), "soon": len(soon), "protected": len(protected),
                 "deleted": deleted, "failed": failed, "deferred": deferred,
                 "freed_mb": round(freed / 1048576.0, 4)})
    return EXIT_FAILED if failed else EXIT_OK


def _print_json(obj: Dict[str, object]) -> None:
    print(json.dumps(obj, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
