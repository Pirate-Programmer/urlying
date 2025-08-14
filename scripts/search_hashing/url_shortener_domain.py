import os
import pandas as pd
import zlib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # from /scripts/search_hashing
INPUT_FILE = os.path.join(BASE_DIR, "datasets", "url_shorteners", "url_shortener_domain.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "url_shorteners", "url_shortener_domain.csv")

def process_url_shorteners():
    if not os.path.exists(INPUT_FILE):
        print(f"[x] File not found: {INPUT_FILE}")
        return

    # Read CSV (assumes first column contains the domains)
    df = pd.read_csv(INPUT_FILE)
    domains = df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().unique()

    # Calculate CRC32
    hashed_list = [(domain, zlib.crc32(domain.encode('utf-8')) & 0xffffffff) for domain in domains]

    # Sort by CRC32 value
    hashed_list.sort(key=lambda x: x[1])

    # Save to CSV
    output_df = pd.DataFrame(hashed_list, columns=["domain", "hash"])
    output_df.to_csv(OUTPUT_FILE, index=False)

    print(f"[✓] Saved sorted CSV with CRC32 hashes to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_url_shorteners()
