import requests
import hashlib
import zlib
import os
import csv
import io

# ==== Configuration ====
RAW_URL = "https://raw.githubusercontent.com/drb-ra/C2IntelFeeds/master/vpn/CyberGhostVPNIPs.csv"
FILENAME = "cyberghost_vpn_ip_list.csv"
SAVE_AS = f"./datasets/vpn_ips/{FILENAME}"
HASH_FILE = f"./hashed_files/{FILENAME}.md5"

# ==== Utilities ====
def get_md5(data):
    """Return MD5 hash (hex) for whole file."""
    return hashlib.md5(data).hexdigest()

def get_crc32(data):
    """Return unsigned CRC32 hash as hex string."""
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
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)

# ==== Step 1: Fetch File ====
def fetch_file():
    try:
        ensure_dirs()

        response = requests.get(RAW_URL)
        if response.status_code != 200:
            print(f"[x] Failed to fetch. Status: {response.status_code}")
            return False, None

        new_content = response.content
        new_hash = get_md5(new_content)
        old_hash = load_previous_hash()

        if new_hash == old_hash:
            print("[=] File unchanged. No update needed.")
            return False, None

        save_new_hash(new_hash)
        print("[✓] File downloaded successfully.")
        return True, new_content

    except Exception as e:
        print(f"[!] Error: {e}")
        return False, None

# ==== Step 2: Process CSV ====
def process_csv(raw_csv_bytes):
    try:
        csv_data = io.StringIO(raw_csv_bytes.decode("utf-8", errors="ignore"))
        reader = csv.DictReader(csv_data)

        processed_rows = []
        for row in reader:
            ip_value = row.get("#ip") or row.get("ip")
            if ip_value:
                processed_rows.append({
                    "hash": get_crc32(ip_value.encode("utf-8")),
                    "ip": ip_value.strip()
                })

        # Sort by hash for binary search
        processed_rows.sort(key=lambda x: x["hash"])

        with open(SAVE_AS, "w", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["hash", "ip"])
            writer.writeheader()
            writer.writerows(processed_rows)

        print(f"[✓] Processed & saved: {SAVE_AS}")

    except Exception as e:
        print(f"[!] Error processing CSV: {e}")

# ==== Main Runner ====
if __name__ == "__main__":
    updated, content = fetch_file()
    if updated and content:
        process_csv(content)
