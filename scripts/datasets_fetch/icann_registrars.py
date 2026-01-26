import os
import pandas as pd
import hashlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  
EXT_FILE = os.path.join(BASE_DIR, "datasets", "icann_registrars", "icann_registrars.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "datasets", "icann_registrars", "icann_registrars.csv")
HASH_FILE = os.path.join(BASE_DIR, "hashed_files", "icann_registrars.md5")

def get_md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()

def load_previous_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def save_new_hash(hash_val):
    os.makedirs(os.path.dirname(HASH_FILE), exist_ok=True)
    with open(HASH_FILE, "w", encoding="utf-8") as f:
        f.write(hash_val)

def ensure_dirs(path):
    os.makedirs(path, exist_ok=True)

def process_registrars():
    if not os.path.exists(EXT_FILE):
        print(f"[x] File not found: {EXT_FILE}")
        return

    df = pd.read_csv(EXT_FILE, dtype=str, keep_default_na=False)

    for drop_col in ["Public Contact", "Link"]:
        if drop_col in df.columns:
            df.drop(columns=[drop_col], inplace=True)


    reg_col = next((c for c in df.columns if c.strip().lower() == "registrars"), None)
    if reg_col is None:
        raise KeyError("Could not find a 'registrars' column in the CSV headers.")
    
    df["registrar_clean"] = df[reg_col].astype(str).str.strip()
    df["registrar_lower"] = df["registrar_clean"].str.lower()

    keep_cols = ["registrar_clean", "registrar_lower"]
    if "IANA Number" in df.columns:
        keep_cols.append("IANA Number")
    if "Country/Territory" in df.columns:
        keep_cols.append("Country/Territory")

    dedup_df = df[keep_cols].dropna(subset=["registrar_clean"])
    dedup_df = dedup_df.drop_duplicates(subset=["registrar_lower"], keep="first").reset_index(drop=True)

    dedup_df = dedup_df.sort_values("registrar_lower").reset_index(drop=True)

    dedup_df = dedup_df.rename(columns={"registrar_clean": "registrars"})

    out_cols = ["registrars", "registrar_lower"]
    if "IANA Number" in dedup_df.columns:
        out_cols.append("IANA Number")
    if "Country/Territory" in dedup_df.columns:
        out_cols.append("Country/Territory")

    csv_bytes = dedup_df.to_csv(index=False, columns=out_cols, encoding="utf-8").encode("utf-8")
    new_hash = get_md5(csv_bytes)
    old_hash = load_previous_hash()

    if new_hash == old_hash:
        print("[=] CSV unchanged. No update needed.")
        return

    ensure_dirs(os.path.dirname(OUTPUT_FILE))
    with open(OUTPUT_FILE, "wb") as f:
        f.write(csv_bytes)
    save_new_hash(new_hash)
    print(f"[✓] Saved cleaned and deduplicated CSV with MD5 hash to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_registrars()
