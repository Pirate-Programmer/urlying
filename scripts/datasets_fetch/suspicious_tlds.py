import os
import pandas as pd
import zlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "datasets", "tlds", "suspicious_tlds.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "tlds", "suspicious_tlds.csv")

def process_special_use_domain():
    if not os.path.exists(INPUT_FILE):
        print(f"[x] File not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    if "tld" not in df.columns:
        print("[x] 'tld' column not found in CSV.")
        return

    df["hash"] = df["tld"].astype(str).str.strip().str.lower().apply(
        lambda x: zlib.crc32(x.encode("utf-8")) & 0xffffffff
    )

    df = df.sort_values(by="hash", ascending=True)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"[✓] Saved CSV with hashed tlds to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_special_use_domain()
