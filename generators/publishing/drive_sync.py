#!/usr/bin/env python3
"""MegaWheel Arena <-> Google Drive (Drive API v3): ONE place for people to see the videos (user 2026-10-01).

Drive layout (folders under My Drive):
  me/ai-develop/ipandu-video/review/              rendered, waiting for the user's review   <VIDEO_ID>.mp4 + _sheet.png
  me/ai-develop/ipandu-video/review/approved/     approved, waiting to air                  E016_<VIDEO_ID>.mp4
  me/ai-develop/ipandu-video/archive/S01/ ...     aired on YouTube (channel history)        E016_<VIDEO_ID>.mp4
  me/ai-develop/ipandu-video/archive/rejected/    rejected / superseded (history)           <VIDEO_ID>.mp4
The VM keeps an MP4 only as a working copy until the video is on YouTube (publish needs the file); after it is
archived on Drive (size verified) the local MP4 is deleted. Manifests/audits stay in git.

Run on VM 99.3 (cd /root/video-engine):
  venv/bin/python generators/publishing/drive_sync.py sync            # idempotent: put every video where it belongs
  venv/bin/python generators/publishing/drive_sync.py sync --only SIM_SMASH25D_V4_S014
  venv/bin/python generators/publishing/drive_sync.py status          # what is where
  venv/bin/python generators/publishing/drive_sync.py auth --port 8085   # one-time login (token -> credentials/)
episodes.py approve/reject and publish_queue.py upload call sync_one() automatically (non-fatal if Drive is down).
Credentials (never committed): credentials/drive_client_secret.json, credentials/drive_token.json
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(BASE, "generators", "physics_2d"))
import registry  # noqa: E402

SECRET = os.path.join(BASE, "credentials", "drive_client_secret.json")
TOKEN = os.path.join(BASE, "credentials", "drive_token.json")
SCOPES = ["https://www.googleapis.com/auth/drive"]          # existing user folders (approved by user)
ROOT_PATH = ["me", "ai-develop", "ipandu-video"]
FOLDER_MIME = "application/vnd.google-apps.folder"
SKIP_STATUS = {"AUDIT_FAILED", "CHECKS_FAILED", "PROTOTYPE_NOT_FOR_UPLOAD"}
_svc, _folders = None, {}


# ------------------------------------------------------------------ Drive basics
def service():
    global _svc
    if _svc is None:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        if not os.path.exists(TOKEN):
            raise RuntimeError("drive_token.json belum ada: jalankan 'drive_sync.py auth' (sekali, lihat SOP)")
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
        if not creds.valid:
            creds.refresh(Request())
            with open(TOKEN, "w") as fh:
                fh.write(creds.to_json())
        _svc = build("drive", "v3", credentials=creds, cache_discovery=False)
    return _svc


def _child(parent, name, create=True):
    q = (f"name = '{name}' and '{parent}' in parents and mimeType = '{FOLDER_MIME}' and trashed = false")
    r = service().files().list(q=q, fields="files(id)", pageSize=5).execute().get("files", [])
    if r:
        return r[0]["id"]
    if not create:
        return None
    return service().files().create(body=dict(name=name, mimeType=FOLDER_MIME, parents=[parent]),
                                    fields="id").execute()["id"]


def folder(*parts):
    """Folder id of ipandu-video/<parts...> (created when missing)."""
    key = "/".join(parts)
    if key not in _folders:
        fid = "root"
        for i, name in enumerate(ROOT_PATH + list(parts)):
            fid = _child(fid, name, create=i >= len(ROOT_PATH))
            if fid is None:
                raise RuntimeError(f"folder Drive tidak ditemukan: {'/'.join(ROOT_PATH[:i + 1])}")
        _folders[key] = fid
    return _folders[key]


def upload(local, parent, name):
    from googleapiclient.http import MediaFileUpload
    mime = "video/mp4" if local.endswith(".mp4") else "image/png"
    media = MediaFileUpload(local, mimetype=mime, resumable=True, chunksize=8 * 1024 * 1024)
    f = service().files().create(body=dict(name=name, parents=[parent]), media_body=media,
                                 fields="id,size").execute()
    if int(f.get("size", -1)) != os.path.getsize(local):
        raise RuntimeError(f"ukuran di Drive tidak sama untuk {name}")
    return f["id"]


def move(fid, parent, name=None):
    meta = service().files().get(fileId=fid, fields="parents,name,trashed").execute()
    if meta.get("trashed"):
        return None                                               # user deleted it on Drive: forget it
    body = {"name": name} if name and name != meta["name"] else {}
    old = ",".join(p for p in meta.get("parents", []) if p != parent)
    if body or old:
        service().files().update(fileId=fid, body=body, addParents=parent if old else None,
                                 removeParents=old or None, fields="id").execute()
    return fid


def exists_with_size(fid, size):
    try:
        f = service().files().get(fileId=fid, fields="size,trashed").execute()
        return not f.get("trashed") and int(f.get("size", -1)) == size
    except Exception:
        return False


# ------------------------------------------------------------------ where each video belongs
def target(e):
    """(drive folder parts, file name) for a registry entry, or None."""
    st, vid = e.get("status", ""), e["video_id"]
    if st in SKIP_STATUS:
        return None
    ep = e.get("episode")
    if e.get("youtube_url"):
        return ("archive", f"S{(e.get('season') or 1):02d}"), f"E{ep:03d}_{vid}.mp4"
    if st == "APPROVED":
        return ("review", "approved"), f"E{ep:03d}_{vid}.mp4"
    if st == "RENDERED_PENDING_APPROVAL":
        return ("review",), f"{vid}.mp4"
    if st.startswith("REJECTED") or st == "SUPERSEDED_REBRAND":
        return ("archive", "rejected"), f"{vid}.mp4"
    return None


def contact_sheet(e, out):
    prev = os.path.join(BASE, e["folder"], "preview")
    pngs = sorted(os.path.join(prev, f) for f in os.listdir(prev) if f.endswith(".png")) if os.path.isdir(prev) else []
    if not pngs:
        return None
    ins = sum((["-i", p] for p in pngs), [])
    fc = "".join(f"[{i}]scale=300:-1[v{i}];" for i in range(len(pngs))) + \
         "".join(f"[v{i}]" for i in range(len(pngs))) + f"hstack=inputs={len(pngs)}"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", fc, out], check=True)
    return out


def sync_one(video_id, quiet=False):
    e = registry.get(video_id)
    if not e:
        return
    t = target(e)
    if t is None:
        return
    parts, name = t
    parent = folder(*parts)
    local = os.path.join(BASE, e["folder"], f"{video_id}.mp4")
    fid = e.get("drive_id")
    if fid:
        fid = move(fid, parent, name)
    if not fid:
        if not os.path.exists(local):
            if not quiet:
                print(f"[drive] {video_id}: tidak ada MP4 lokal maupun di Drive -> dilewati")
            return
        fid = upload(local, parent, name)
        if parts == ("review",):                                 # review: add a contact sheet next to the video
            sheet = contact_sheet(e, f"/tmp/{video_id}_sheet.png")
            if sheet:
                registry.update(video_id, drive_sheet_id=upload(sheet, parent, f"{video_id}_sheet.png"))
        print(f"[drive] {video_id}: upload -> {'/'.join(parts)}/{name}")
    elif not quiet:
        print(f"[drive] {video_id}: {'/'.join(parts)}/{name}")
    if e.get("drive_sheet_id") and parts != ("review",):           # the sheet is only for reviewing
        try:
            service().files().delete(fileId=e["drive_sheet_id"]).execute()
        except Exception:
            pass
        registry.update(video_id, drive_sheet_id=None)
    registry.update(video_id, drive_id=fid, drive_path="/".join(ROOT_PATH + list(parts) + [name]))
    # archived (aired or rejected) + verified on Drive -> the VM working copy is no longer needed
    if parts[0] == "archive" and os.path.exists(local) and exists_with_size(fid, os.path.getsize(local)):
        os.remove(local)
        print(f"[drive] {video_id}: salinan lokal dihapus (aman di Drive)")


def sync(only=None):
    ids = [only] if only else [e["video_id"] for e in registry.load()["videos"]]
    for vid in ids:
        try:
            sync_one(vid, quiet=not only)
        except Exception as ex:
            print(f"[drive] {vid}: GAGAL {ex}")


def try_sync_one(video_id):
    """Hook for episodes.py / publish_queue.py: never breaks the caller."""
    try:
        if os.path.exists(TOKEN):
            sync_one(video_id)
    except Exception as ex:
        print(f"[drive] sync {video_id} gagal (akan dicoba lagi oleh 'drive_sync.py sync'): {ex}")


def status():
    for e in registry.load()["videos"]:
        t = target(e)
        if t:
            print(f"{e['video_id']:26s} {e.get('status', '')[:24]:24s} -> {e.get('drive_path') or '(belum di Drive)'}")


def auth(port):
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_secrets_file(SECRET, SCOPES)
    creds = flow.run_local_server(host="localhost", port=port, open_browser=False, access_type="offline",
                                  prompt="consent", authorization_prompt_message="[drive] buka URL ini di browser PC:\n{url}\n")
    with open(TOKEN, "w") as fh:
        fh.write(creds.to_json())
    os.chmod(TOKEN, 0o600)
    print("[drive] token tersimpan:", TOKEN)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["sync", "status", "auth"])
    ap.add_argument("--only", default="")
    ap.add_argument("--port", type=int, default=8085)
    a = ap.parse_args()
    if a.cmd == "auth":
        auth(a.port)
    elif a.cmd == "status":
        status()
    else:
        sync(a.only or None)
