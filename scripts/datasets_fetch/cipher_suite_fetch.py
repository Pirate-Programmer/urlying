import os
import requests
import io
import pandas as pd
import hashlib

# Config
IANA_CSV_URL = "https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
OUT_CSV = f"./datasets/cipher_suites/cipher_suites_iana.csv"
HASH_FILE = f"./hashed_files/cipher_suites_iana.md5"

# ==== Utilities ====
def get_md5(data: bytes) -> str:
    """Return MD5 hash for given bytes."""
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

# ==== Download CSV ====
def download_csv(url: str, timeout: int = 30) -> pd.DataFrame:
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    buf = io.StringIO(resp.text)
    df = pd.read_csv(buf)
    return df

# ==== Process DataFrame ====
def process_df(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip() for c in df.columns]

    if "Description" not in df.columns:
        raise KeyError("Expected 'Description' column in IANA CSV")

    df = df.rename(columns={"Description": "Cipher_Suite"})

    for col in ("Reference", "Comment"):
        if col in df.columns:
            df = df.drop(columns=[col])

    df["Cipher_Suite"] = df["Cipher_Suite"].astype(str).str.strip()
    return df

# ==== Save CSV ====
def save_outputs(df: pd.DataFrame, csv_path: str):
    df.to_csv(csv_path, index=False)
    print(f"[✓] Saved CSV -> {csv_path}")

# ==== Main Runner ====
def run():
    print("[*] Downloading IANA TLS parameters CSV...")
    df = download_csv(IANA_CSV_URL)

    # Compute MD5 of the downloaded CSV content
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    new_hash = get_md5(csv_bytes)
    old_hash = load_previous_hash()

    if new_hash == old_hash:
        print("[=] CSV unchanged. No update needed.")
        return

    df_clean = process_df(df)
    save_outputs(df_clean, OUT_CSV)
    save_new_hash(new_hash)
    print("[✓] Done.")

if __name__ == "__main__":
    run()
