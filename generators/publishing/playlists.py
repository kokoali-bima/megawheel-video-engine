#!/usr/bin/env python3
"""MegaWheel Arena playlists: 4 playlists by video type, new uploads join the right one automatically.

  CHALLENGE (11:00 ET Shorts)  -> "MegaWheel Challenges"
  RACE      (15:00 ET)         -> "MegaWheel Races"
  SMASH     (19:00 ET)         -> "MegaWheel Smash Arena"
  STORY     (long + trailer)   -> "MegaWheel Stories"

Why a SEPARATE token: the upload token only has upload + readonly scopes and cannot touch playlists. Playlist changes use
their own token (scope `youtube`, file credentials/youtube_playlist_token.json), so the upload token is never changed and
a missing/expired playlist token can only skip the playlist step, never block an upload.

  python generators/publishing/playlists.py auth-url                  # owner opens the URL, allows, sends back the localhost address
  python generators/publishing/playlists.py auth-finish "<redirect url>"
  python generators/publishing/playlists.py ensure                   # create the 4 playlists once (public), ids cached in credentials/playlists.json
  python generators/publishing/playlists.py backfill [--dry-run]     # put every uploaded episode in its playlist (oldest first)
  python generators/publishing/playlists.py add EPISODE              # one episode
publish_queue.py calls add_for_episode() after every upload (errors are printed, never raised).
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CRED = "/root/video-engine/credentials"
CLIENT = f"{CRED}/client_secrets.json"
TOKEN = f"{CRED}/youtube_playlist_token.json"
STATE = f"{CRED}/playlist_oauth_state.json"
CACHE = f"{CRED}/playlists.json"
SCOPES = ["https://www.googleapis.com/auth/youtube"]
PLAYLISTS = {
    "short": ("MegaWheel Challenges", "Every daily CHALLENGE: cars take on a brand-new obstacle course. Who survives? NEW 3D graphics."),
    "race": ("MegaWheel Races", "Every daily RACE: the fastest car does not always win. Watch the finish line!"),
    "smash": ("MegaWheel Smash Arena", "Every SMASH ARENA battle: heavy metal, big crashes, one winner."),
    "story": ("MegaWheel Stories", "The MegaWheel Arena story episodes and trailers, in order."),
}


def _os_env():
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")       # redirect is http://localhost (never leaves the machine)
    os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")


def _flow(port):
    _os_env()
    from google_auth_oauthlib.flow import Flow
    f = Flow.from_client_secrets_file(CLIENT, scopes=SCOPES)
    f.redirect_uri = f"http://localhost:{port}/"
    return f


def cmd_auth_url(port=8087):
    f = _flow(port)
    url, state = f.authorization_url(access_type="offline", prompt="consent", include_granted_scopes="false")
    json.dump(dict(state=state, port=port, code_verifier=getattr(f, "code_verifier", None)), open(STATE, "w"))
    os.chmod(STATE, 0o600)
    print("[playlists] open this URL with the MegaWheel Arena account, choose the MegaWheel Arena channel, allow:\n")
    print(url)


def cmd_auth_finish(redirect):
    st = json.load(open(STATE))
    f = _flow(st["port"])
    if st.get("code_verifier"):
        f.code_verifier = st["code_verifier"]
    f.fetch_token(authorization_response=redirect)
    c = f.credentials
    if not c.refresh_token:
        sys.exit("[playlists] no refresh token (revoke the app at myaccount.google.com/permissions and repeat)")
    with open(TOKEN, "w") as fh:
        fh.write(c.to_json())
    os.chmod(TOKEN, 0o600)
    from googleapiclient.discovery import build
    r = build("youtube", "v3", credentials=c, cache_discovery=False).channels().list(part="snippet", mine=True).execute()
    print(f"[playlists] token saved; channel '{r['items'][0]['snippet']['title']}'")


def service():
    _os_env()
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    if not os.path.exists(TOKEN):
        raise RuntimeError("playlist token missing (run auth-url / auth-finish once)")
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    c.refresh(Request())
    return build("youtube", "v3", credentials=c, cache_discovery=False)


def _cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}


def ensure(yt=None):
    """Create the 4 playlists once (matched by title if they already exist). Returns {role: playlist_id}."""
    yt = yt or service()
    ids = _cache()
    have = {}
    token = None
    while True:
        r = yt.playlists().list(part="snippet", mine=True, maxResults=50, pageToken=token).execute()
        have.update({p["snippet"]["title"]: p["id"] for p in r["items"]})
        token = r.get("nextPageToken")
        if not token:
            break
    for role, (title, desc) in PLAYLISTS.items():
        if role in ids and ids[role] in have.values():
            continue
        if title in have:
            ids[role] = have[title]
            continue
        r = yt.playlists().insert(part="snippet,status", body=dict(
            snippet=dict(title=title, description=desc, defaultLanguage="en-US"),
            status=dict(privacyStatus="public"))).execute()
        ids[role] = r["id"]
        print(f"[playlists] created '{title}' {r['id']}")
    json.dump(ids, open(CACHE, "w"), indent=1)
    return ids


def _members(yt, pid):
    out, token = set(), None
    while True:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pid, maxResults=50, pageToken=token).execute()
        out |= {x["contentDetails"]["videoId"] for x in r["items"]}
        token = r.get("nextPageToken")
        if not token:
            return out


def add(yt, ids, role, video_id, members=None):
    """Add one video (skips it when already inside)."""
    pid = ids[role]
    if video_id in (members if members is not None else _members(yt, pid)):
        return False
    yt.playlistItems().insert(part="snippet", body=dict(snippet=dict(
        playlistId=pid, resourceId=dict(kind="youtube#video", videoId=video_id)))).execute()
    return True


def video_id_of(url):
    m = re.search(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})", url or "")
    return m.group(1) if m else None


def role_of(series):
    import episodes
    return episodes._role(series)


def add_for_episode(ep, url):
    """Hook for publish_queue: never raises (a playlist problem must not stop the upload run)."""
    try:
        e = next(x for x in __import__("episodes").episodes() if x["episode"] == ep)
        vid = video_id_of(url)
        yt = service()
        ids = ensure(yt)
        role = role_of(e.get("series", ""))
        print(f"[playlists] Ep. {ep} -> {PLAYLISTS[role][0]}: " + ("added" if add(yt, ids, role, vid) else "already there"))
    except Exception as ex:
        print(f"[playlists] SKIPPED Ep. {ep}: {str(ex)[:120]} (upload itself is fine; run `playlists.py backfill` later)")


def backfill(dry=False):
    import episodes
    yt = service()
    ids = ensure(yt) if not dry else _cache()
    todo = sorted((e for e in episodes.episodes() if e.get("youtube_url")), key=lambda e: e["episode"])
    members = {r: (_members(yt, ids[r]) if r in ids else set()) for r in PLAYLISTS}
    n = 0
    for e in todo:
        vid, role = video_id_of(e["youtube_url"]), role_of(e.get("series", ""))
        if not vid or vid in members[role]:
            continue
        print(f"[playlists] Ep. {e['episode']:>4} {e.get('series', ''):<16} -> {PLAYLISTS[role][0]}")
        if not dry:
            add(yt, ids, role, vid, members[role])
            members[role].add(vid)
        n += 1
    print(f"[playlists] {'would add' if dry else 'added'} {n} video(s)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("auth-url")
    s = sub.add_parser("auth-finish"); s.add_argument("redirect")
    sub.add_parser("ensure")
    s = sub.add_parser("backfill"); s.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("add"); s.add_argument("episode", type=int)
    a = ap.parse_args()
    if a.cmd == "auth-url":
        cmd_auth_url()
    elif a.cmd == "auth-finish":
        cmd_auth_finish(a.redirect)
    elif a.cmd == "ensure":
        print(ensure())
    elif a.cmd == "backfill":
        backfill(a.dry_run)
    elif a.cmd == "add":
        import episodes
        e = next(x for x in episodes.episodes() if x["episode"] == a.episode)
        add_for_episode(a.episode, e.get("youtube_url"))


if __name__ == "__main__":
    main()
