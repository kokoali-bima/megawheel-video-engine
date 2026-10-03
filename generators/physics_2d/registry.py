"""PRODUCTION_REGISTRY.json helpers (BLUEPRINT.md section 7).

One entry per video. Fingerprint = series | vehicles | track_id | outcomes.
A seed may be used once per (series, engine_version); a fingerprint only once overall.
"""
import fcntl
import json
import os

BASE = "/root/video-engine"
PATH = f"{BASE}/PRODUCTION_REGISTRY.json"
LOCK = PATH + ".lock"
ABOUT = ("Registry video MegaWheel Arena: keunikan + episode/season + status upload. Aturan: BLUEPRINT.md bagian 7. "
         "Diisi otomatis oleh engine dan episodes.py; jangan diedit manual, jangan hapus entri lama.")
IGNORED_STATUS = {"PROTOTYPE_NOT_FOR_UPLOAD", "REJECTED", "AUDIT_FAILED", "SUPERSEDED_REBRAND", "REPLACED"}


def fingerprint(e):
    return "|".join([e["series"], ",".join(e["vehicles"]), e["track_id"], ",".join(e["outcomes"])])


def load():
    if not os.path.exists(PATH):
        return {"_about": ABOUT, "videos": []}
    with open(PATH) as fh:
        return json.load(fh)


def _save(data):
    tmp = PATH + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, PATH)


def _active(exclude_id):
    return [e for e in load()["videos"] if e["video_id"] != exclude_id and e.get("status") not in IGNORED_STATUS]


def get(video_id):
    for e in load()["videos"]:
        if e["video_id"] == video_id:
            return e
    return None


def update(video_id, **fields):
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        data = load()
        for e in data["videos"]:
            if e["video_id"] == video_id:
                e.update(fields)
        _save(data)


def find_seed(series, engine_version, seed, exclude_id=None):
    for e in _active(exclude_id):
        if e["series"] == series and e.get("engine_version") == engine_version and e["seed"] == seed:
            return e["video_id"]
    return None


def find_fingerprint(fp, exclude_id=None):
    for e in _active(exclude_id):
        if fingerprint(e) == fp:
            return e["video_id"]
    return None


def series_streak(series, exclude_id=None):
    """How many of the most recent videos (newest last) belong to `series` in a row."""
    n = 0
    for e in reversed(_active(exclude_id)):
        if e["series"] != series:
            break
        n += 1
    return n


def upsert(entry):
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        data = load()
        vids = [e for e in data["videos"] if e["video_id"] != entry["video_id"]]
        vids.append(entry)
        data["videos"] = vids
        _save(data)


def set_status(video_id, status, **extra):
    with open(LOCK, "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        data = load()
        for e in data["videos"]:
            if e["video_id"] == video_id:
                e["status"] = status
                e.update(extra)
        _save(data)
