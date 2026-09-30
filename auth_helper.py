#!/usr/bin/env python3
"""
YouTube OAuth Helper with PKCE State Persistence
Usage:
  1. Generate URL:
     python3 auth_helper.py --generate
  2. Exchange Code:
     python3 auth_helper.py --code "4/0A..."
     OR
     python3 auth_helper.py --url "http://localhost:8080/?code=4/0A...&state=..."
"""

import os
import sys
import json
import argparse
import urllib.parse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from core.youtube_uploader import SCOPES, DEFAULT_CLIENT_SECRETS, DEFAULT_TOKEN_FILE

STATE_FILE = "/root/video-engine/credentials/oauth_flow_state.json"
REDIRECT_URI = "http://localhost:8080/"

def generate():
    if not os.path.exists(DEFAULT_CLIENT_SECRETS):
        print(f"[ERROR] client_secrets.json not found at: {DEFAULT_CLIENT_SECRETS}")
        sys.exit(1)

    flow = InstalledAppFlow.from_client_secrets_file(
        DEFAULT_CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )

    # Save state and code_verifier for exchange step
    state_data = {
        "state": state,
        "code_verifier": getattr(flow, "code_verifier", None),
        "redirect_uri": REDIRECT_URI
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state_data, f)

    print("=" * 70)
    print("  LINK OTORISASI YOUTUBE CHANNEL")
    print("=" * 70)
    print(auth_url)
    print("=" * 70)
    print("\nPetunjuk:")
    print("1. Buka link di atas di browser Anda.")
    print("2. Login & pilih akun Channel YouTube Anda.")
    print("3. Setelah klik Allow/Izinkan, browser akan diarahkan ke halaman 'http://localhost:8080/?code=...' (walau halaman tertulis 'Cannot connect', itu NORMAL).")
    print("4. Cukup salin seluruh URL dari address bar browser (atau bagian code=...) dan kirimkan ke chat ini!")

def exchange(code_or_url: str):
    if not os.path.exists(STATE_FILE):
        print(f"[ERROR] State file not found. Please run --generate first.")
        sys.exit(1)

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state_data = json.load(f)

    # Extract code if full URL was provided
    code = code_or_url.strip()
    if "code=" in code:
        parsed = urllib.parse.urlparse(code)
        query = urllib.parse.parse_qs(parsed.query)
        if "code" in query:
            code = query["code"][0]

    flow = InstalledAppFlow.from_client_secrets_file(
        DEFAULT_CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=state_data.get("redirect_uri", REDIRECT_URI),
        state=state_data.get("state")
    )
    if state_data.get("code_verifier"):
        flow.code_verifier = state_data["code_verifier"]

    print(f"Menukarkan kode otorisasi Google...")
    flow.fetch_token(code=code)
    creds = flow.credentials

    os.makedirs(os.path.dirname(DEFAULT_TOKEN_FILE), exist_ok=True)
    with open(DEFAULT_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    # Verify channel info
    try:
        yt = build("youtube", "v3", credentials=creds)
        res = yt.channels().list(part="snippet,statistics", mine=True).execute()
        if res.get("items"):
            ch = res["items"][0]
            title = ch["snippet"]["title"]
            subs = ch["statistics"].get("subscriberCount", "Hidden")
            print("\n" + "=" * 70)
            print(f"  [BERHASIL] Channel YouTube Terhubung: {title}")
            print(f"  Jumlah Subscriber : {subs}")
            print(f"  Token tersimpan di: {DEFAULT_TOKEN_FILE}")
            print("=" * 70)
            return
    except Exception as e:
        print(f"Warning checking channel details: {e}")

    print(f"\n[SUKSES] Kredensial YouTube berhasil disimpan di: {DEFAULT_TOKEN_FILE}")

def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth Helper")
    parser.add_argument("--generate", action="store_true", help="Generate authorization URL")
    parser.add_argument("--code", type=str, help="Authorization code from Google")
    parser.add_argument("--url", type=str, help="Full redirect URL from browser")

    args = parser.parse_args()

    if args.generate:
        generate()
    elif args.code:
        exchange(args.code)
    elif args.url:
        exchange(args.url)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
