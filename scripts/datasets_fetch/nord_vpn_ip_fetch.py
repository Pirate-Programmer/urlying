import requests
import hashlib
import os
import csv
import zlib
from io import StringIO

# GitHub raw file URL for NordVPN IPs
RAW_URL = "https://raw.githubusercontent.com/drb-ra/C2IntelFeeds/master/vpn/NordVPNIPs.csv"

FILENAME = "nord_vpn_ip_list.csv"
SAVE_AS = f"./datasets/vpn_ips/{FILENAME}"
HASH_FILE = f"./hashed_files/{FILENAME}.md5"

def get_md5(data):
    return hashlib.md5(data).hexdigest()

def get_crc32(data):
    return format(zlib.crc32(data) & 0xffffffff, "08x")

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_val):
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, "w") as f:
        f.write(hash_val)

def ensure_dirs():
    os.makedirs(os.path.dirname(SAVE_AS), exist_ok=True)

def process_csv(content):
    decoded = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(decoded))
    
    processed_rows = []
    for row in reader:
        ip = row.get("#ip") or row.get("ip")
        if not ip:
            continue
        ip = ip.strip()
        processed_rows.append({
            "ip": ip,
            "hash": get_crc32(ip.encode("utf-8"))
        })
    
    processed_rows.sort(key=lambda x: x["hash"])
    
    with open(SAVE_AS, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "hash"])
        writer.writeheader()
        writer.writerows(processed_rows)
    
    print(f"[✓] Processed & saved: {SAVE_AS}")

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
