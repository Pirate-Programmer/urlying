import requests
import hashlib
import os
import csv
import io

RAW_URL = "https://raw.githubusercontent.com/mthcht/awesome-lists/refs/heads/main/Lists/ASNs/spamhaus_asn_list.csv"
FILENAME = "bad_asns.csv"
SAVE_AS = f"./datasets/bad_asns/{FILENAME}"
HASH_FILE = f"./hashed_files/{FILENAME}.md5"

def get_md5(data):
    """Return MD5 hash (hex) for the whole file."""
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
    os.makedirs(os.path.dirname(SAVE_AS), exist_ok=True)
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)

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

def process_csv(raw_csv_bytes):
    try:
        csv_data = io.StringIO(raw_csv_bytes.decode("utf-8", errors="ignore"))
        reader = csv.DictReader(csv_data)

        processed_rows = []
        for row in reader:
            as_number = row.get("as_number")
            if as_number:
                processed_rows.append({"as_number": as_number.strip()})

        unique_rows = sorted({r["as_number"] for r in processed_rows})
        processed_rows = [{"as_number": x} for x in unique_rows]

        with open(SAVE_AS, "w", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=["as_number"])
            writer.writeheader()
            writer.writerows(processed_rows)

        print(f"[✓] Processed & saved: {SAVE_AS}")

    except Exception as e:
        print(f"[!] Error processing CSV: {e}")

def run():
    changed, content = fetch_file()
    if changed and content:
        process_csv(content)
    else:
        print("[i] Skipping processing since file is unchanged.")

if __name__ == "__main__":
    run()
