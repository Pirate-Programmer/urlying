import requests
import hashlib
import os
import csv
from io import StringIO

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

def get_md5(data):
    return hashlib.md5(data).hexdigest()

def load_previous_hash(hash_file):
    if os.path.exists(hash_file):
        with open(hash_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_file, hash_val):
    os.makedirs(os.path.dirname(hash_file), exist_ok=True)
    with open(hash_file, "w", encoding="utf-8") as f:
        f.write(hash_val)

def ensure_dirs(path):
    os.makedirs(path, exist_ok=True)

def process_csv(content, save_as):
    decoded = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(decoded))

    ips = []
    for row in reader:
        ip = (row.get("dest_ip") or row.get("ip") or "").strip()
        if ip:
            ips.append(ip)

    unique_sorted_ips = sorted(set(ips))

    os.makedirs(os.path.dirname(save_as), exist_ok=True)
    with open(save_as, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ip"])
        writer.writeheader()
        for ip in unique_sorted_ips:
            writer.writerow({"ip": ip})

    print(f"[✓] Processed & saved: {save_as} (count: {len(unique_sorted_ips)})")

def fetch_tor_lists():
    for source in TOR_SOURCES:
        filename = source["name"]
        raw_url = source["url"]

        save_as = f"./datasets/vpn_ips/{filename}"
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

if __name__ == "__main__":
    fetch_tor_lists()
