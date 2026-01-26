import requests
import hashlib
import os
import csv
from io import StringIO

RAW_URL = "https://raw.githubusercontent.com/mthcht/awesome-lists/main/Lists/VPN/SurfSharkVPN/surfshark_vpn_servers_domains_and_ips_list.csv"

FILENAME = "surfshark_vpn_ip_list.csv"
SAVE_AS = f"./datasets/vpn_ips/{FILENAME}"
HASH_FILE = f"./hashed_files/{FILENAME}.md5"

def get_md5(data):
    return hashlib.md5(data).hexdigest()

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_val):
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(hash_val)

def ensure_dirs():
    os.makedirs(os.path.dirname(SAVE_AS), exist_ok=True)
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)

def process_csv(content):
    decoded = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(decoded))

    processed_ips = []
    for row in reader:
        ip = (row.get("dest_ip") or row.get("ip") or "").strip()
        if ip:
            processed_ips.append(ip)

    # dedupe and sort
    unique_sorted_ips = sorted(set(processed_ips))

    with open(SAVE_AS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ip"])
        writer.writeheader()
        for ip in unique_sorted_ips:
            writer.writerow({"ip": ip})

    print(f"[✓] Processed & saved: {SAVE_AS} (count: {len(unique_sorted_ips)})")

def fetch_file():
    try:
        ensure_dirs()
        response = requests.get(RAW_URL)
        if response.status_code != 200:
            print(f"[x] Failed to fetch. Status: {response.status_code}")
            return

        new_content = response.content
        new_hash = get_md5(new_content)
        old_hash = load_previous_hash()

        if new_hash == old_hash:
            print("[=] File unchanged. No update needed.")
        else:
            process_csv(new_content)
            save_new_hash(new_hash)
            print("[✓] File updated successfully.")

    except Exception as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    fetch_file()
