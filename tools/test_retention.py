#!/usr/bin/env python3
"""Behavioural tests for tools/retention.py (safety rules, boundaries, promote, invalid policies).
Run: python3 tools/test_retention.py [--now EPOCH]  (or: python3 tools/test_retention.py --clip-out PATH)

Exit 0 when all checks pass, 1 otherwise. Symlink checks are skipped when symlinks are not supported.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import time
import contextlib
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import retention  # noqa: E402

DAY = 86400
NOW = 1761000000  # fixed epoch; every mtime is derived from it


# ------------------------------------------------------------------------------------------------- helpers
def _mkfile(path: str, size: int, age_days: float = 0.0, now: float = NOW) -> None:
    """Write `size` bytes and set mtime to now - age_days days (exact seconds)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"x" * size)
    _touch(path, age_days, now)


def _touch(path: str, age_days: float, now: float = NOW) -> None:
    mtime = now - age_days * DAY
    os.utime(path, (mtime, mtime))


def _walk_snapshot(root: str) -> Dict[str, Tuple[str, int, float]]:
    """Snapshot all paths under root: {path: (kind, size, mtime)}. Uses lstat to not follow links."""
    snap: Dict[str, Tuple[str, int, float]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        for name in [""] + dirnames + filenames:
            p = dirpath if name == "" else os.path.join(dirpath, name)
            try:
                st = os.lstat(p)
            except OSError:
                snap[p] = ("missing", -1, -1.0)
                continue
            if os.path.islink(p):
                kind = "link"
            elif os.path.isdir(p):
                kind = "dir"
            else:
                kind = "file"
            snap[p] = (kind, st.st_size, round(st.st_mtime, 6))
    return snap


def _run(argv: List[str]) -> Tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = retention.main(argv)
    return rc, buf.getvalue()


def _summary(out: str) -> Dict[str, Any]:
    lines = [ln for ln in out.splitlines() if ln.strip()]
    for ln in reversed(lines):
        s = ln.strip()
        try:
            obj = json.loads(s)
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj
    raise AssertionError("no JSON summary line in output: " + out)


def _scan_lines(out: str) -> List[str]:
    """All report unit lines (not header, not JSON summary)."""
    rows: List[str] = []
    for ln in out.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("{"):
            continue
        rows.append(s)
    return rows


def _units(out: str) -> Dict[str, str]:
    """path -> state, parsed from report lines `STATE  AGE_DAYS d  SIZE MB  PATH`."""
    states: Dict[str, str] = {}
    for ln in _scan_lines(out):
        first = ln.split(None, 1)[0] if ln.split() else ""
        if first not in ("EXPIRED", "SOON", "FRESH", "PROTECTED", "DEFERRED", "DELETED", "FAILED"):
            continue
        # PATH is the last whitespace-separated field (paths in tests never contain spaces).
        path = ln.split()[-1]
        states[path] = first
    return states


# ------------------------------------------------------------------------------------------------- fixtures
def build_tree(t: str, now: float = NOW) -> Tuple[str, str]:
    """Create the fixture tree and policy. Returns (policy_path, lab_root)."""
    lab = os.path.join(t, "lab")
    os.makedirs(lab, exist_ok=True)

    # old_exp: 45 days, two files (1024 + 2048 = 3072 bytes)
    _mkfile(os.path.join(lab, "old_exp", "a.bin"), 1024, 45, now)
    _mkfile(os.path.join(lab, "old_exp", "b.bin"), 2048, 45, now)
    _touch(os.path.join(lab, "old_exp"), 45, now)

    # edge_exp: exactly 30 days -> NOT expired
    _mkfile(os.path.join(lab, "edge_exp", "c.bin"), 100, 30, now)
    _touch(os.path.join(lab, "edge_exp"), 30, now)

    # edge_over: 30 days + 1 second -> EXPIRED
    over_secs = 30 * DAY + 1
    _mkfile(os.path.join(lab, "edge_over", "d.bin"), 100, 0, now)  # placeholder write
    _set_abs_mtime(os.path.join(lab, "edge_over", "d.bin"), now - over_secs)
    _set_abs_mtime(os.path.join(lab, "edge_over"), now - over_secs)

    # soon_exp: 25 days -> SOON (>23, <=30)
    _mkfile(os.path.join(lab, "soon_exp", "e.bin"), 100, 25, now)
    _touch(os.path.join(lab, "soon_exp"), 25, now)

    # fresh_exp: 2 days -> FRESH
    _mkfile(os.path.join(lab, "fresh_exp", "f.bin"), 100, 2, now)
    _touch(os.path.join(lab, "fresh_exp"), 2, now)

    # sfx: 60 days but kept -> not a unit
    _mkfile(os.path.join(lab, "sfx", "g.bin"), 100, 60, now)
    _touch(os.path.join(lab, "sfx"), 60, now)

    # held: 60 days but has a top-level .keep -> PROTECTED
    _mkfile(os.path.join(lab, "held", "h.bin"), 100, 60, now)
    _mkfile(os.path.join(lab, "held", ".keep"), 0, 60, now)
    _touch(os.path.join(lab, "held"), 60, now)

    # old_file.mp4: plain file, 40 days -> EXPIRED
    _mkfile(os.path.join(lab, "old_file.mp4"), 512, 40, now)

    # mixed: old file 50 d + new file 1 d -> unit is FRESH (newest mtime)
    _mkfile(os.path.join(lab, "mixed", "old.bin"), 100, 50, now)
    _mkfile(os.path.join(lab, "mixed", "new.bin"), 100, 1, now)
    _touch(os.path.join(lab, "mixed"), 1, now)

    # glob targets: x_lab 20 d (FRESH), y_lab 90 d (EXPIRED)
    _mkfile(os.path.join(t, "x_lab", "x.bin"), 100, 20, now)
    _touch(os.path.join(t, "x_lab"), 20, now)
    _mkfile(os.path.join(t, "y_lab", "y.bin"), 100, 90, now)
    _touch(os.path.join(t, "y_lab"), 90, now)

    policy_path = os.path.join(t, "policy.json")
    write_policy(policy_path, t, lab)
    return policy_path, lab


def _set_abs_mtime(path: str, abs_mtime: float) -> None:
    os.utime(path, (abs_mtime, abs_mtime))


def write_policy(policy_path: str, t: str, lab: str, *, max_age_days: int = 30,
                 warn_days: int = 7, max_units_per_run: int = 50) -> None:
    policy = {
        "max_age_days": max_age_days,
        "warn_days": warn_days,
        "max_units_per_run": max_units_per_run,
        "promote_dir": os.path.join(t, "kept"),
        "roots": [{"path": lab, "keep": ["sfx"]}],
        "globs": [os.path.join(t, "*_lab")],
    }
    with open(policy_path, "w", encoding="utf-8") as fh:
        json.dump(policy, fh)


# ------------------------------------------------------------------------------------------------- checks
RESULTS: List[Tuple[str, bool]] = []


def check(name: str, cond: bool) -> bool:
    RESULTS.append((name, bool(cond)))
    print(("PASS - " if cond else "FAIL - ") + name)
    return bool(cond)


def skip(name: str) -> None:
    print("SKIP - " + name)


def _mb(size: int) -> str:
    return f"{size / 1048576:.1f}"


def test_scan(t: str, policy: str) -> None:
    lab = os.path.join(t, "lab")
    before = _walk_snapshot(t)
    rc, out = _run(["--policy", policy, "--now", str(NOW), "scan"])
    after = _walk_snapshot(t)
    check("scan exits 0", rc == 0)
    check("scan leaves filesystem unchanged", before == after)
    units = _units(out)
    check("scan marks old_exp EXPIRED", units.get(os.path.join(lab, "old_exp")) == "EXPIRED")
    check("scan marks edge_over EXPIRED", units.get(os.path.join(lab, "edge_over")) == "EXPIRED")
    check("scan marks old_file.mp4 EXPIRED", units.get(os.path.join(lab, "old_file.mp4")) == "EXPIRED")
    check("scan marks y_lab EXPIRED", units.get(os.path.join(t, "y_lab")) == "EXPIRED")
    check("scan does NOT mark edge_exp expired",
          units.get(os.path.join(lab, "edge_exp"), "") != "EXPIRED")
    check("scan marks soon_exp SOON", units.get(os.path.join(lab, "soon_exp")) == "SOON")
    check("scan marks fresh_exp FRESH", units.get(os.path.join(lab, "fresh_exp")) == "FRESH")
    check("scan marks mixed FRESH", units.get(os.path.join(lab, "mixed")) == "FRESH")
    check("scan marks x_lab FRESH", units.get(os.path.join(t, "x_lab")) == "FRESH")
    check("scan marks held PROTECTED", units.get(os.path.join(lab, "held")) == "PROTECTED")
    check("scan does not list kept sfx as a unit", os.path.join(lab, "sfx") not in units)
    check("scan does not list root lab as a unit", lab not in units)
    summ = _summary(out)
    check("scan summary expired == 4", summ.get("expired") == 4)
    check("scan summary soon == 2 (soon_exp 25 d + edge_exp exactly 30 d)", summ.get("soon") == 2)
    check("scan summary protected == 1", summ.get("protected") == 1)
    check("scan summary deleted == 0", summ.get("deleted") == 0)


def test_report_lines(t: str, policy: str) -> None:
    lab = os.path.join(t, "lab")
    rc, out = _run(["--policy", policy, "--now", str(NOW), "scan"])
    check("report scan exits 0", rc == 0)
    row = None
    for ln in _scan_lines(out):
        if ln.split()[-1] == os.path.join(lab, "old_exp"):
            row = ln
            break
    check("report has a line for old_exp", row is not None)
    if row:
        check("report old_exp shows 45 days", "45.0" in row.split())
        check("report old_exp shows 0.0 MB size (3072 bytes)", "0.0" in row.split() and _mb(3072) == "0.0")


def test_apply(t: str, policy: str) -> None:
    lab = os.path.join(t, "lab")
    rc, out = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("apply exits 0", rc == 0)
    summ = _summary(out)
    check("apply summary deleted == 4", summ.get("deleted") == 4)
    freed = float(summ.get("freed_mb") or 0.0)
    # 3072 + 100 + 512 + 100 = 3784 bytes (old_exp, edge_over, old_file.mp4, y_lab)
    expected_mb = 3784 / 1048576.0
    check("apply freed_mb close to sum", abs(freed - expected_mb) < 0.05)
    check("apply removed old_exp", not os.path.exists(os.path.join(lab, "old_exp")))
    check("apply removed edge_over", not os.path.exists(os.path.join(lab, "edge_over")))
    check("apply removed old_file.mp4", not os.path.exists(os.path.join(lab, "old_file.mp4")))
    check("apply removed y_lab", not os.path.exists(os.path.join(t, "y_lab")))
    check("apply kept edge_exp", os.path.exists(os.path.join(lab, "edge_exp")))
    check("apply kept soon_exp", os.path.exists(os.path.join(lab, "soon_exp")))
    check("apply kept fresh_exp", os.path.exists(os.path.join(lab, "fresh_exp")))
    check("apply kept mixed (both files)",
          os.path.exists(os.path.join(lab, "mixed", "old.bin")) and
          os.path.exists(os.path.join(lab, "mixed", "new.bin")))
    check("apply kept sfx", os.path.exists(os.path.join(lab, "sfx")))
    check("apply kept held", os.path.exists(os.path.join(lab, "held")))
    check("apply kept x_lab", os.path.exists(os.path.join(t, "x_lab")))
    check("apply kept root lab", os.path.isdir(lab))
    check("apply kept top temp dir", os.path.isdir(t))


def test_apply_twice(t: str, policy: str) -> None:
    rc, out = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("second apply exits 0", rc == 0)
    check("second apply deletes nothing", _summary(out).get("deleted") == 0)


def test_keep_removal(t: str, policy: str) -> None:
    lab = os.path.join(t, "lab")
    # held: 60 days, drop .keep -> expired on next apply
    keep = os.path.join(lab, "held", ".keep")
    check("held initially has PROTECTED state",
          _units(_run(["--policy", policy, "--now", str(NOW), "scan"])[1]).get(os.path.join(lab, "held")) == "PROTECTED")
    os.remove(keep)
    _touch(os.path.join(lab, "held"), 60)
    st, _ = _run(["--policy", policy, "--now", str(NOW), "scan"])
    units = _units(_run(["--policy", policy, "--now", str(NOW), "scan"])[1])
    check("held without .keep is EXPIRED", units.get(os.path.join(lab, "held")) == "EXPIRED")
    rc, out = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("apply after .keep removal exits 0", rc == 0)
    check("held deleted after .keep removal", not os.path.exists(os.path.join(lab, "held")))

    # adding a .keep to a fresh expired unit protects it: make fresh_exp old + .keep
    fe = os.path.join(lab, "fresh_exp")
    _touch(os.path.join(fe, "f.bin"), 60)
    _touch(fe, 60)
    _mkfile(os.path.join(fe, ".keep"), 0, 60)
    _touch(fe, 60)
    units = _units(_run(["--policy", policy, "--now", str(NOW), "scan"])[1])
    check("unit with added .keep shows PROTECTED", units.get(fe) == "PROTECTED")
    rc, _ = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("unit with .keep survives apply", os.path.exists(fe))


def test_cap(t: str) -> None:
    t2 = os.path.join(t, "cap")
    os.makedirs(t2, exist_ok=True)
    lab = os.path.join(t2, "lab")
    os.makedirs(lab, exist_ok=True)
    # four expired units with different ages: y_lab 90, old_exp 45, a50 50, b60 60
    for name, age in (("old_exp", 45), ("a50", 50), ("b60", 60)):
        _mkfile(os.path.join(lab, name, "f.bin"), 100, age)
        _touch(os.path.join(lab, name), age)
    _mkfile(os.path.join(t2, "y_lab", "y.bin"), 100, 90)
    _touch(os.path.join(t2, "y_lab"), 90)
    policy = os.path.join(t2, "policy.json")
    write_policy(policy, t2, lab, max_units_per_run=2)
    rc, out = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("capped apply exits 0", rc == 0)
    summ = _summary(out)
    check("capped apply deletes exactly 2", summ.get("deleted") == 2)
    check("capped apply reports 2 deferred", summ.get("deferred") == 2)
    check("oldest (y_lab 90d) deleted first", not os.path.exists(os.path.join(t2, "y_lab")))
    check("second oldest (b60 60d) deleted", not os.path.exists(os.path.join(lab, "b60")))
    check("a50 (50d) survives the cap", os.path.exists(os.path.join(lab, "a50")))
    check("old_exp (45d) survives the cap", os.path.exists(os.path.join(lab, "old_exp")))


def test_promote(t: str, policy: str) -> None:
    lab = os.path.join(t, "lab")
    src = os.path.join(lab, "old_exp")
    _mkfile(os.path.join(src, "a.bin"), 1024, 45)
    _mkfile(os.path.join(src, "b.bin"), 2048, 45)
    _touch(os.path.join(src), 45)
    dest = os.path.join(t, "kept", "old_exp")
    rc, out = _run(["--policy", policy, "--now", str(NOW), "promote", src])
    check("promote exits 0", rc == 0)
    check("promote prints PROMOTED", "PROMOTED" in out)
    check("promote moved old_exp to kept", os.path.isdir(dest) and not os.path.exists(src))
    check("promote kept contents intact (both files)",
          os.path.getsize(os.path.join(dest, "a.bin")) == 1024 and
          os.path.getsize(os.path.join(dest, "b.bin")) == 2048)
    # second promote: destination exists -> exit 2
    _mkfile(os.path.join(lab, "old_exp", "a.bin"), 1024, 45)
    _touch(os.path.join(lab, "old_exp"), 45)
    rc2, _ = _run(["--policy", policy, "--now", str(NOW), "promote", os.path.join(lab, "old_exp")])
    check("promote refuses existing destination (exit 2)", rc2 == 2)
    check("refused promote left the source in place", os.path.exists(os.path.join(lab, "old_exp")))
    # not a unit: kept sfx
    rc3, _ = _run(["--policy", policy, "--now", str(NOW), "promote", os.path.join(lab, "sfx")])
    check("promote of a kept path exits 2", rc3 == 2)
    # not a unit: outside roots
    elsewhere = os.path.join(t, "elsewhere")
    os.makedirs(elsewhere, exist_ok=True)
    rc4, _ = _run(["--policy", policy, "--now", str(NOW), "promote", elsewhere])
    check("promote of a non-unit path exits 2", rc4 == 2)
    # --to DIR honoured
    other = os.path.join(t, "other")
    src2 = os.path.join(lab, "soon_exp")
    rc5, out5 = _run(["--policy", policy, "--now", str(NOW), "promote", src2, "--to", other])
    check("promote --to exits 0", rc5 == 0)
    check("promote --to placed unit in other dir", os.path.isdir(os.path.join(other, "soon_exp")))


def test_invalid_policies(t: str) -> None:
    inv = os.path.join(t, "invalid")
    os.makedirs(inv, exist_ok=True)
    lab = os.path.join(inv, "lab")
    _mkfile(os.path.join(lab, "old_exp", "a.bin"), 100, 45)
    _touch(os.path.join(lab, "old_exp"), 45)
    before = _walk_snapshot(inv)

    def run_bad(name: str, content: str) -> None:
        p = os.path.join(t, name)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(content)
        rc, _ = _run(["--policy", p, "--now", str(NOW), "apply"])
        check("invalid policy '%s' exits 2" % name, rc == 2)
        check("invalid policy '%s' changes nothing" % name, _walk_snapshot(inv) == before)

    base = {"max_age_days": 30, "warn_days": 7, "max_units_per_run": 50,
            "promote_dir": os.path.join(inv, "kept"),
            "roots": [{"path": lab, "keep": []}], "globs": []}

    run_bad("bad.json", "{not json")

    d = dict(base); d["max_age_days"] = 0
    run_bad("zero.json", json.dumps(d))

    d = dict(base); d["warn_days"] = 99
    run_bad("warn.json", json.dumps(d))

    d = dict(base); d["roots"] = [{"path": "relative/lab", "keep": []}]
    run_bad("relative.json", json.dumps(d))

    d = dict(base); d["roots"] = [{"path": "/", "keep": []}]
    run_bad("root.json", json.dumps(d))


def test_symlink(t: str, policy: str, sym_ok: bool) -> None:
    if not sym_ok:
        skip("symlinks")
        return
    lab = os.path.join(t, "lab")
    target = os.path.join(t, "outside_target")
    os.makedirs(target, exist_ok=True)
    with open(os.path.join(target, "payload.bin"), "wb") as fh:
        fh.write(b"y" * 256)
    _touch(os.path.join(target, "payload.bin"), 90)
    _touch(target, 90)
    link = os.path.join(lab, "link_out")
    try:
        os.symlink(target, link)
    except (OSError, NotImplementedError):
        skip("symlinks")
        return
    # age the link itself (lstat) far past the limit
    _set_abs_mtime(link, NOW - 120 * DAY) if False else None
    os.utime(link, (NOW - 120 * DAY, NOW - 120 * DAY), follow_symlinks=False)
    rc, out = _run(["--policy", policy, "--now", str(NOW), "apply"])
    check("symlink apply exits 0", rc == 0)
    check("symlink itself untouched", os.path.islink(link))
    check("symlink target directory untouched", os.path.isdir(target))
    check("symlink target file untouched", os.path.exists(os.path.join(target, "payload.bin")))
    units = _units(_run(["--policy", policy, "--now", str(NOW), "scan"])[1])
    check("symlink unit reported PROTECTED", units.get(link) == "PROTECTED")


def test_default_policy_pin() -> None:
    missing = os.path.join(tempfile.gettempdir(), "mw-retention-nonexistent-" + str(os.getpid()) + ".json")
    if os.path.exists(missing):
        os.remove(missing)
    original = retention.DEFAULT_POLICY
    retention.DEFAULT_POLICY = missing
    try:
        before = os.path.exists(missing)
        rc, _ = _run(["scan"])
        check("E029 pinned DEFAULT_POLICY missing -> exit 2", rc == 2)
        check("E029 pinned DEFAULT_POLICY not created", os.path.exists(missing) == before)
    finally:
        retention.DEFAULT_POLICY = original


def main(argv: List[str]) -> int:
    global NOW
    args = list(argv)
    if "--now" in args:
        i = args.index("--now")
        try:
            NOW = int(args[i + 1])
        except (IndexError, ValueError):
            pass
    t = tempfile.mkdtemp(prefix="mw-retention-test-")
    sym_ok = True
    try:
        try:
            probe = os.path.join(t, "sym-probe")
            os.mkdir(os.path.join(t, "sym-target"))
            os.symlink(os.path.join(t, "sym-target"), probe)
            os.remove(probe)
        except (OSError, NotImplementedError):
            sym_ok = False

        # run 1..4 share one fixture (apply destructively mutates it)
        policy, _lab = build_tree(t)
        test_scan(t, policy)
        test_report_lines(t, policy)
        test_apply(t, policy)
        test_apply_twice(t, policy)
        test_keep_removal(t, policy)

        # cap and promote use fresh subtrees to keep counting clear
        test_cap(t)
        test_promote(t, policy)
        test_invalid_policies(t)
        test_symlink(t, policy, sym_ok)
        test_default_policy_pin()
    finally:
        shutil.rmtree(t, ignore_errors=True)

    passed = sum(1 for _, ok in RESULTS if ok)
    total = len(RESULTS)
    print("%d/%d passed" % (passed, total))
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
