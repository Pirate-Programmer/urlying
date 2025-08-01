import requests
import hashlib
import os

RAW_URL = "https://raw.githubusercontent.com/mthcht/awesome-lists/main/Lists/VPN/MullVad/mullvad_relay_servers_ips_list.csv"

FILENAME = "mullvad_vpn_ip_list.csv"
SAVE_AS = f"./datasets/vpn_ips/{FILENAME}"
HASH_FILE = f"./hashed_files/{FILENAME}.md5"

def get_hash(data):
    return hashlib.md5(data).hexdigest()

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_val):
    with open(HASH_FILE, "w") as f:
        f.write(hash_val)

def fetch_file():
    try:
        response = requests.get(RAW_URL)
        if response.status_code != 200:
            print(f"[x] Failed to fetch. Status: {response.status_code}")
            return

        new_content = response.content
        new_hash = get_hash(new_content)
        old_hash = load_previous_hash()

        if new_hash == old_hash:
            print("[=] File unchanged. No update needed.")
        else:
            with open(SAVE_AS, "wb") as f:
                f.write(new_content)
            save_new_hash(new_hash)
            print("[✓] File updated successfully.")

    except Exception as e:
        print(f"[!] Error: {e}")

fetch_file()
