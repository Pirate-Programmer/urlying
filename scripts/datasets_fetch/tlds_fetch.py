import requests
import hashlib
import os
import csv

RAW_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
FILENAME_TXT = "tlds.txt"
FILENAME_CSV = "tlds.csv"
SAVE_TXT = f"./datasets/tlds/{FILENAME_TXT}"
SAVE_CSV = f"./datasets/tlds/{FILENAME_CSV}"
HASH_FILE = f"./hashed_files/{FILENAME_TXT}.md5"

def get_md5(data):
    """Return MD5 hash (hex) for full file update checking."""
    return hashlib.md5(data).hexdigest()

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
    os.makedirs(os.path.dirname(SAVE_TXT), exist_ok=True)
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)

def fetch_tld_list():
    try:
        ensure_dirs()

        response = requests.get(RAW_URL)
        if response.status_code != 200:
            print(f"[x] Failed to fetch TLD list. Status: {response.status_code}")
            return False

        new_content = response.content
        new_hash = get_md5(new_content)
        old_hash = load_previous_hash()

        if new_hash == old_hash:
            print("[=] TLD list unchanged. No update needed.")
            return False

        # Save updated file and hash
        with open(SAVE_TXT, "wb") as f:
            f.write(new_content)
        save_new_hash(new_hash)
        print("[✓] TLD list updated successfully.")
        return True

    except Exception as e:
        print(f"[!] Error fetching TLD list: {e}")
        return False

def convert_txt_to_csv(txt_file, csv_file):
    try:
        with open(txt_file, "r") as infile:
            lines = infile.readlines()

        tlds = [line.strip().lower() for line in lines if not line.startswith("#")]

        with open(csv_file, "w", newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["tld"])
            for tld in sorted(tlds):
                writer.writerow([tld])

        print(f"[✓] Converted to CSV: {csv_file}")
    except Exception as e:
        print(f"[!] Error during CSV conversion: {e}")

def run():
    was_updated = fetch_tld_list()
    if was_updated:
        convert_txt_to_csv(SAVE_TXT, SAVE_CSV)
    else:
        print("[=] Skipping CSV conversion — no changes in TLD list.")

if __name__ == "__main__":
    run()
