#!/usr/bin/env python3
"""
Interactive YouTube Authorization Helper
Run this script to authenticate your YouTube Channel:
  python3 auth_youtube.py
"""

import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from core.youtube_uploader import SCOPES, DEFAULT_CLIENT_SECRETS, DEFAULT_TOKEN_FILE

def main():
    print("=" * 60)
    print("  iPandu Video Engine - YouTube Channel Authorization")
    print("=" * 60)
    
    secrets_file = DEFAULT_CLIENT_SECRETS
    if not os.path.exists(secrets_file):
        print(f"\n[ERROR] client_secrets.json not found at: {secrets_file}")
        print("\nCara mendapatkan client_secrets.json:")
        print("1. Buka Google Cloud Console: https://console.cloud.google.com/")
        print("2. Aktifkan 'YouTube Data API v3'.")
        print("3. Di menu 'Credentials', buat 'OAuth Client ID' tipe 'Desktop App'.")
        print("4. Download JSON dan simpan ke /root/video-engine/credentials/client_secrets.json")
        sys.exit(1)

    print(f"\nMenggunakan Client Secrets: {secrets_file}")
    print("Membuat link otentikasi Google...")

    flow = InstalledAppFlow.from_client_secrets_file(
        secrets_file,
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

    print("\n" + "=" * 60)
    print("Silakan buka link berikut di browser untuk login ke Akun YouTube:")
    print("=" * 60)
    print(auth_url)
    print("=" * 60 + "\n")

    auth_code = input("Masukkan Kode Verifikasi (Authorization Code) dari browser: ").strip()
    if not auth_code:
        print("Kode verifikasi kosong. Otentikasi dibatalkan.")
        sys.exit(1)

    flow.fetch_token(code=auth_code)
    creds = flow.credentials

    os.makedirs(os.path.dirname(DEFAULT_TOKEN_FILE), exist_ok=True)
    with open(DEFAULT_TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(creds.to_json())

    print(f"\n[SUKSES] Kredensial YouTube berhasil disimpan di: {DEFAULT_TOKEN_FILE}")
    print("YouTube Uploader sekarang sudah siap digunakan!")

if __name__ == "__main__":
    main()
