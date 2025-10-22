import os
import pandas as pd
import zlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) 
INPUT_FILE = os.path.join(BASE_DIR, "datasets", "tlds", "special_use_domain.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "tlds", "special_use_domain.csv")

def process_special_use_domain():
    if not os.path.exists(INPUT_FILE):
        print(f"[x] File not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    domains = df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().unique()

    hashed_list = [(domain, zlib.crc32(domain.encode('utf-8')) & 0xffffffff) for domain in domains]

    hashed_list.sort(key=lambda x: x[1])

    output_df = pd.DataFrame(hashed_list, columns=["domain", "hash"])
    output_df.to_csv(OUTPUT_FILE, index=False)

    print(f"[✓] Saved sorted CSV with CRC32 hashes to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_special_use_domain()
