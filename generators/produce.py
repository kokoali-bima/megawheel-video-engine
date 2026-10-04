"""PRODUCE — the one standard command for making a MegaWheel Short (user 2026-10-04: "buatkan sistem perintah baku
agar pembuatan video sesuai standar kita, terutama variasinya"). It runs the whole SOP (BLUEPRINT + AGENT_VIDEO_PRODUCER)
with hard gates; any failed gate stops and nothing is sent for review.

  cd /root/video-engine && venv/bin/python generators/produce.py challenge [--series potholes] [--count 1]
  cd /root/video-engine && venv/bin/python generators/produce.py race   [--count 1]
  cd /root/video-engine && venv/bin/python generators/produce.py smash  [--count 1]
  add --dry-run to see the plan (series, seed, gates) without rendering.

Steps
 1. preflight: git_sync pull and VM HEAD == origin/main; no other render running; not inside the upload-cron window
    (04:50-05:40 UTC); pending stock < 9 (AGENT_VIDEO_PRODUCER rule)
 2. series + seed: CHALLENGE series by SERIES_WEIGHT vs. registry (or --series); seed = largest used + 1
 3. render with the production engine (variety director inside: layout / obstacles / contents / race layout);
    exit 1 (analysis STOP) -> next seed, max 8 tries; exit 5 (audit failed) -> stop and report
 4. standard gates on the result: status pending, Shorts technical length, preview PNGs, structure not repeated in
    the last 10 of its family, engine checks all true (RACE realistic order), no kids wording in title/description.
    Duration is NOT capped (user 2026-10-04): it is reported for the weekly retention evaluation.
 5. PRODUCTION_LOG.md row, Drive review upload, git_sync push
 6. report: VIDEO_ID, Drive path, duration, cast, theme, narrator, variety plan, gates
Never approves, schedules or uploads (those stay with the user).
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for sub in ("physics_2d", "publishing", "variety"):
    sys.path.insert(0, os.path.join(BASE, "generators", sub))
import registry  # noqa: E402

ENGINES = {"challenge": "generators/physics_2d/sim_engine.py", "race": "generators/lanes25d/race25d.py",
           "smash": "generators/lanes25d/smash25d.py"}
SERIES_OF = {"race": "race25d", "smash": "smash25d"}
SHORTS_MAX_S = 175.0                                  # YouTube Shorts technical limit (3 min) with a margin
MAX_TRIES = 8
FORBIDDEN = re.compile(r"\b(kids?|children|toddlers?|bab(y|ies)|nursery|for kids)\b", re.I)
AGENT = os.environ.get("PRODUCE_AGENT", "Claude Code Opus")


def say(msg):
    print(f"[produce] {msg}", flush=True)


def stop(msg):
    say(f"STOP: {msg}")
    raise SystemExit(2)


def sh(cmd, **kw):
    return subprocess.run(cmd, cwd=BASE, capture_output=True, text=True, **kw)


# ------------------------------------------------------------------ 1. preflight
def preflight(dry):
    r = sh(["bash", "git_sync.sh", "pull"])
    if r.returncode != 0 or "STOP" in r.stdout + r.stderr:
        stop("git_sync pull gagal / berhenti:\n" + (r.stdout + r.stderr)[-600:])
    head = sh(["git", "rev-parse", "HEAD"]).stdout.strip()
    sh(["git", "fetch", "-q", "origin"])
    origin = sh(["git", "rev-parse", "origin/main"]).stdout.strip()
    if head != origin:
        stop(f"VM HEAD {head[:7]} != origin/main {origin[:7]} (ERROR_LOG: render dengan kode lama)")
    busy = sh(["pgrep", "-af", "sim_engine.py|race25d.py|smash25d.py"]).stdout.strip()
    busy = "\n".join(ln for ln in busy.splitlines() if "pgrep" not in ln)
    if busy:
        stop("render lain masih berjalan (ERROR_LOG: jangan render bersamaan):\n" + busy)
    now = dt.datetime.utcnow()
    if dt.time(4, 50) <= now.time() <= dt.time(5, 40):
        stop("jendela cron upload 05:00 UTC; coba lagi setelah 05:40 UTC")
    pending = [e for e in registry.load()["videos"] if e.get("status") == "RENDERED_PENDING_APPROVAL"]
    if len(pending) >= 9 and not dry:
        stop(f"stok pending belum di-review sudah {len(pending)} (≥ 9): tunggu review user")
    say(f"preflight OK · HEAD {head[:7]} · pending {len(pending)}")


# ------------------------------------------------------------------ 2. series + seed
def pick_series(fmt, forced):
    if fmt != "challenge":
        return SERIES_OF[fmt]
    if forced:
        return forced
    import sim_engine as se                                      # SERIES_DEFS / SERIES_WEIGHT live in the engine
    active = registry._active(None)
    counts = {s: sum(1 for e in active if e.get("series") == s) for s in se.SERIES_DEFS}
    return min(se.SERIES_DEFS, key=lambda s: counts[s] / se.SERIES_WEIGHT.get(s, 1))


def next_seed(series):
    seeds = [int(e["seed"]) for e in registry.load()["videos"] if e.get("series") == series and e.get("seed")]
    return (max(seeds) + 1) if seeds else 1


# ------------------------------------------------------------------ 3. render
def render(fmt, series, seed, log):
    cmd = [os.path.join(BASE, "venv/bin/python"), ENGINES[fmt], "--seed", str(seed)]
    if fmt == "challenge":
        cmd += ["--series", series]
    with open(log, "w") as fh:
        r = subprocess.run(cmd, cwd=BASE, stdout=fh, stderr=subprocess.STDOUT, timeout=5400)
    text = open(log).read()
    m = re.findall(r"\[result\] (\{.*\})", text)
    res = json.loads(m[-1]) if m else {}
    return r.returncode, res, text


# ------------------------------------------------------------------ 4. gates
def gates(vid):
    e = registry.get(vid) or {}
    folder = os.path.join(BASE, e.get("folder", ""))
    man_p = os.path.join(folder, f"{vid}.json")
    man = json.load(open(man_p)) if os.path.exists(man_p) else {}
    items = []

    def g(name, ok, val=""):
        items.append((name, bool(ok), str(val)))

    g("status RENDERED_PENDING_APPROVAL", e.get("status") == "RENDERED_PENDING_APPROVAL", e.get("status"))
    dur = float(man.get("duration") or e.get("duration") or 0)
    g(f"durasi ≤ batas teknis Shorts ({SHORTS_MAX_S:.0f} s; durasi tidak dibatasi kaku)", 0 < dur <= SHORTS_MAX_S,
      f"{dur:.1f} s")
    prev = man.get("preview_dir") or os.path.join(folder, "preview")
    pngs = sorted(os.listdir(prev)) if os.path.isdir(prev) else []
    g("preview PNG standar (≥ 2, termasuk outro)", len(pngs) >= 2 and "outro.png" in pngs, f"{len(pngs)} file")
    checks = man.get("checks") or {}
    bad = [k for k, ok in checks.items() if not ok]
    g("cek engine semua lolos (RACE: urutan realistis)", not bad, bad or "ok")
    analysis = man.get("analysis") or []
    fails = [a.get("id") for a in analysis if isinstance(a, dict) and a.get("hard", True) and not a.get("ok", True)]
    g("analisa tanpa FAIL", not fails, fails or "ok")
    st = e.get("structure")
    if st:
        fam = [x for x in reversed(registry._active(vid)) if x.get("structure") and
               (x.get("series") == e.get("series") or {x.get("series"), e.get("series")} <= {"potholes", "lava_potholes"})]
        recent = [x.get("structure") for x in fam[:10]]
        g("struktur variasi tidak sama dengan 10 video terakhir", st not in recent, st)
    else:
        g("struktur variasi tercatat", e.get("series") in ("smash25d", "bumps", "splash", "lava"),
          "belum ada (format tanpa plan)")
    text = " ".join([man.get("title", ""), man.get("description", "")] + list(man.get("tags", [])))
    hit = FORBIDDEN.findall(text)
    g("tanpa kata kids/children/baby (BLUEPRINT §12)", not hit, hit or "ok")
    return items, e, man


def log_row(vid, e, man, ok, note):
    import sim_engine as se
    names = " → ".join(se.VEHICLES[v]["nick"] for v in e.get("vehicles", []) if v in se.VEHICLES)
    wib = (dt.datetime.utcnow() + dt.timedelta(hours=7)).strftime("%Y-%m-%d %H:%M")
    row = (f"| {wib} | {AGENT} | {vid} | {e.get('series', '')} | {e.get('seed', '')} | {names} | "
           f"{float(man.get('duration') or 0):.1f} s | {'PASS' if ok else 'FAIL'} | {note} |\n")
    with open(os.path.join(BASE, "PRODUCTION_LOG.md"), "a") as fh:
        fh.write(row)


# ------------------------------------------------------------------ main
def produce_one(fmt, forced_series, dry):
    series = pick_series(fmt, forced_series)
    seed = next_seed(series)
    say(f"format {fmt} · seri {series} · seed mulai {seed}")
    if dry:
        return None
    os.makedirs(os.path.join(BASE, "work", "produce"), exist_ok=True)
    failed = []                                                  # renders that failed the engine checks (reported)
    for k in range(MAX_TRIES):
        s = seed + k
        log = os.path.join(BASE, "work", "produce", f"{series}_s{s}.log")
        say(f"render {series} seed {s} … (log {os.path.relpath(log, BASE)})")
        code, res, text = render(fmt, series, s, log)
        if code == 1:
            why = (re.findall(r"STOP: .*", text) or ["STOP"])[-1][:160]
            say(f"seed {s}: analisa/registry STOP ({why}) → seed berikutnya")
            continue
        if code == 5:                                            # engine checks failed: never sent; try the next seed
            failed.append(res.get("video_id", f"seed {s}"))
            say(f"seed {s}: cek engine GAGAL ({res.get('video_id', '?')}_audit.md, status AUDIT_FAILED) → seed berikutnya")
            continue
        if code != 0:
            stop(f"seed {s}: engine error (exit {code}); lihat {log}")
        vid = res.get("video_id")
        items, e, man = gates(vid)
        ok = all(o for _, o, _ in items)
        for name, o, val in items:
            say(f"  {'✅' if o else '❌'} {name}: {val}")
        plan = e.get("structure") or (man.get("params") or {}).get("plan") or ""
        if not ok:
            registry.update(vid, status="AUDIT_FAILED")
            log_row(vid, e, man, False, "gerbang produce.py gagal: " + ", ".join(n for n, o, _ in items if not o))
            stop(f"{vid}: gerbang standar gagal → AUDIT_FAILED, tidak dikirim ke review")
        log_row(vid, e, man, True, f"produce.py · {man.get('theme_id', '')} · {plan}")
        try:
            import drive_sync
            drive_sync.sync_one(vid)
        except Exception as ex:                                  # noqa: BLE001
            say(f"Drive sync gagal: {ex} (catat di ERROR_LOG)")
        r = sh(["bash", "git_sync.sh", "push", f"produce: {vid} (pending review) [{AGENT}]"])
        say((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "git_sync push")
        say(f"SELESAI {vid} · Drive review/{vid}.mp4 · {float(man.get('duration') or 0):.1f} s · "
            f"tokoh {e.get('vehicles')} · tema {man.get('theme_id')} · narator {man.get('voice')} · variasi {plan}")
        if failed:
            say(f"(dilewati karena gagal cek engine: {failed})")
        say("Menunggu approval Anda. Belum dijadwalkan dan belum diupload.")
        return vid
    stop(f"{MAX_TRIES} seed berturut-turut STOP di analisa: laporkan ke user (jangan pakai --force)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("format", choices=list(ENGINES))
    ap.add_argument("--series", default="", help="CHALLENGE series (default: by SERIES_WEIGHT vs. registry)")
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    preflight(a.dry_run)
    done = [produce_one(a.format, a.series, a.dry_run) for _ in range(a.count)]
    say(f"{len([d for d in done if d])} video dibuat: {done}")


if __name__ == "__main__":
    main()
