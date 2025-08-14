import os
import pandas as pd
import zlib

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # go up from /scripts/search_hashing
EXT_FILE = os.path.join(BASE_DIR, "datasets", "harmful_file_extensions", "harmful_file_extensions.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "harmful_file_extensions", "harmful_file_extensions.csv")

def process_extensions():
    if not os.path.exists(EXT_FILE):
        print(f"[x] File not found: {EXT_FILE}")
        return

    # Read CSV (assuming single-column file with no header)
    df = pd.read_csv(EXT_FILE, header=None)
    extensions = df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().unique()

    # Calculate CRC32 for each extension
    hashed_ext_list = [(ext, zlib.crc32(ext.encode('utf-8')) & 0xffffffff) for ext in extensions]

    # Sort by CRC32 value
    hashed_ext_list.sort(key=lambda x: x[1])

    # Save to CSV
    output_df = pd.DataFrame(hashed_ext_list, columns=["extensions", "hash"])
    output_df.to_csv(OUTPUT_FILE, index=False)

    print(f"[✓] Saved sorted CSV with CRC32 hashes to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_extensions()
