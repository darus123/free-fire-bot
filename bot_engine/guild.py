import json
import os
import time
import sys
import asyncio

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

ACCOUNTS_FILE = "accounts.json"

def load_accounts(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and "accounts" in data:
            data = data["accounts"]
        if not isinstance(data, list):
            raise ValueError("accounts.json must contain a JSON array")
        return data
    except FileNotFoundError:
        print(f"[ERROR] {filepath} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {filepath}: {e}")
        return []

async def join_guild_native(guild_id, uid, password, region="BD"):
    try:
        ad = await app.process_account_uid_pass(uid, password, region)
        if ad and ad.get("token"):
            jwt = ad["token"]
            surl = ad.get("server_url") or "https://clientbp.ppmainecoonghj.com"
            ok = await app.join_clan(jwt, guild_id, surl)
            if ok:
                return True, "SUCCESS"
            return False, "RequestJoinClan returned false"
        return False, "Login failed"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 55)
    print("   SachinDev X FFFZ — Native Free Fire Guild Join Bot")
    print("=" * 55)

    guild_id = input("Enter Guild ID : ").strip()
    if not guild_id:
        print("[ERROR] Guild ID cannot be empty. Exiting.")
        return

    accounts = load_accounts(ACCOUNTS_FILE)
    if not accounts:
        print("[ERROR] No accounts loaded. Exiting.")
        return

    print("-" * 55)
    print(f"[INFO] Target Guild ID : {guild_id}")
    print(f"[INFO] Total Accounts   : {len(accounts)}")
    print("-" * 55)

    async def run_all():
        success_count = 0
        fail_count = 0
        for idx, acc in enumerate(accounts, start=1):
            uid = str(acc.get("uid", "")).strip()
            password = str(acc.get("password", "")).strip()
            region = str(acc.get("region", "BD")).strip() or "BD"

            if not uid or not password:
                print(f"[{idx}/{len(accounts)}] SKIPPED — missing uid or password")
                fail_count += 1
                continue

            masked_pw = password[:2] + "*" * (len(password) - 2) if len(password) > 2 else "***"
            print(f"[{idx}/{len(accounts)}] UID: {uid} | PW: {masked_pw} ... ", end="", flush=True)

            ok, msg = await join_guild_native(guild_id, uid, password, region)
            if ok:
                success_count += 1
                print("✅ JOINED")
            else:
                fail_count += 1
                print(f"❌ FAILED — {msg}")

            await asyncio.sleep(0.5)

        print("-" * 55)
        print(f"[DONE] Success: {success_count} | Failed: {fail_count} | Total: {len(accounts)}")
        print("=" * 55)

    asyncio.run(run_all())

if __name__ == "__main__":
    main()