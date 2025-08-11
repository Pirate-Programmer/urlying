import requests
import hashlib
import os
import csv
import zlib
from io import StringIO

# ==== Tor Node Feeds ====
TOR_SOURCES = [
    {
        "name": "tor_exit_nodes_ip_list.csv",
        "url": "https://raw.githubusercontent.com/mthcht/awesome-lists/main/Lists/TOR/only_tor_exit_nodes_IP_list.csv"
    },
    {
        "name": "tor_guard_nodes_ip_list.csv",
        "url": "https://raw.githubusercontent.com/mthcht/awesome-lists/main/Lists/TOR/only_tor_guard_nodes_IP_list.csv"
    }
]

# ==== Utilities ====
def get_md5(data):
    return hashlib.md5(data).hexdigest()

def get_crc32(data):
    return format(zlib.crc32(data) & 0xffffffff, "08x")

def load_previous_hash(hash_file):
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_file, hash_val):
    os.makedirs(os.path.dirname(hash_file), exist_ok=True)
    with open(hash_file, "w") as f:
        f.write(hash_val)

def ensure_dirs(path):
    os.makedirs(path, exist_ok=True)

# ==== CSV Processing ====
def process_csv(content, save_as):
    decoded = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(decoded))

    processed_rows = []
    for row in reader:
        ip = row.get("dest_ip", "").strip()
        if ip:
            processed_rows.append({
                "ip": ip,
                "hash": get_crc32(ip.encode("utf-8"))
            })

    # Remove duplicates
    seen = {}
    for entry in processed_rows:
        seen[entry["ip"]] = entry
    unique_rows = list(seen.values())

    # Sort by hash for binary search
    unique_rows.sort(key=lambda x: x["hash"])

    with open(save_as, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ip", "hash"])
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"[✓] Processed & saved: {save_as}")

# ==== Fetch Logic ====
def fetch_tor_lists():
    for source in TOR_SOURCES:
        filename = source["name"]
        raw_url = source["url"]

        save_as = f"./datasets/tor_nodes_ips/{filename}"
        hash_file = f"./hashed_files/{filename}.md5"

        ensure_dirs(os.path.dirname(save_as))
        ensure_dirs(os.path.dirname(hash_file))

        try:
            response = requests.get(raw_url)
            if response.status_code != 200:
                print(f"[x] Failed to fetch {filename}. Status: {response.status_code}")
                continue

            new_content = response.content
            new_hash = get_md5(new_content)
            old_hash = load_previous_hash(hash_file)

            if new_hash == old_hash:
                print(f"[=] {filename}: No update needed.")
            else:
                process_csv(new_content, save_as)
                save_new_hash(hash_file, new_hash)
                print(f"[✓] {filename}: File updated.")

        except Exception as e:
            print(f"[!] Error fetching {filename}: {e}")

# ==== Run Script ====
if __name__ == "__main__":
    fetch_tor_lists()
