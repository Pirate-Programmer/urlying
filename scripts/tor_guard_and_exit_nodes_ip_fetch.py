import requests
import hashlib
import os

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
def get_hash(data):
    return hashlib.md5(data).hexdigest()

def load_previous_hash(hash_file):
    if os.path.exists(hash_file):
        with open(hash_file, "r") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_file, hash_val):
    with open(hash_file, "w") as f:
        f.write(hash_val)

def ensure_dirs(path):
    os.makedirs(path, exist_ok=True)

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
            new_hash = get_hash(new_content)
            old_hash = load_previous_hash(hash_file)

            if new_hash == old_hash:
                print(f"[=] {filename}: No update needed.")
            else:
                with open(save_as, "wb") as f:
                    f.write(new_content)
                save_new_hash(hash_file, new_hash)
                print(f"[✓] {filename}: File updated.")

        except Exception as e:
            print(f"[!] Error fetching {filename}: {e}")

# ==== Run Script ====
if __name__ == "__main__":
    fetch_tor_lists()
