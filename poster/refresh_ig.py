#!/usr/bin/env python3
"""Renew every Instagram channel's token (they last 60 days) and save it back
as a repo secret. Needs the gh CLI signed in with a token that can write secrets."""
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SECRETS = json.loads(os.environ.get("SECRETS_JSON") or "{}")
ACCOUNTS = json.loads((ROOT / "accounts.json").read_text())["accounts"]
REPO = os.environ["GITHUB_REPOSITORY"]

failed = 0
for acc in ACCOUNTS:
    if acc["platform"] != "instagram":
        continue
    name = f"IG_{acc['key'].upper()}_TOKEN"
    token = SECRETS.get(name)
    if not token:
        print(f"{acc['name']}: no token saved yet, skipped")
        continue
    r = requests.get("https://graph.instagram.com/refresh_access_token", timeout=30,
                     params={"grant_type": "ig_refresh_token", "access_token": token})
    new = r.json().get("access_token") if r.status_code == 200 else None
    if not new:
        print(f"::error::{acc['name']}: Instagram did not renew the token ({r.status_code})")
        failed += 1
        continue
    print(f"::add-mask::{new}")
    subprocess.run(["gh", "secret", "set", name, "--repo", REPO, "--body", new], check=True)
    print(f"{acc['name']}: token renewed")
sys.exit(1 if failed else 0)
