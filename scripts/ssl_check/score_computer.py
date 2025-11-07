import os, pandas as pd, zlib, json
from datetime import datetime, timezone

def cipher_suite(cipher_suite) : 
    cipher_suite = cipher_suite.replace("-", "_")
    base_path = os.path.dirname(__file__) 
    csv_path = os.path.join(base_path, "..", "..", "datasets", "cipher_suites", "cipher_suites_iana.csv")
    csv_path = os.path.abspath(csv_path)  
    df = pd.read_csv(csv_path)

    row = df[df["Cipher_Suite"] == cipher_suite]

    if row.empty:
        return "U"
    
    return row["Recommended"].values[0].strip()

def cipher_suite_score(cipher):
    isRecommended = cipher_suite(cipher)

    if isRecommended == 'Y':
        return -10
    elif isRecommended == 'N':
        return 5
    elif isRecommended == 'D':
        return 15
    elif isRecommended == 'U':
        return 5
    
    return 0

def is_wildcard_in_san(san):
    if not san:
        return False
    for s in san:
        if isinstance(s, str) and s.startswith("*."):
            return True
    return False

def issuer_trust_score(issuer_name):
    if not issuer_name:
        return 0

    n = issuer_name.lower()

    # self-signed detection
    if "self-signed" in n or "selfsigned" in n or ("self" in n and "signed" in n):
        return 15

    return 0

def tls_version_score(ver):
    if not ver:
        return 0
    v = ver.lower()
    if "tlsv1.3" in v or "tls1.3" in v:
        return -10
    if "tlsv1.2" in v or "tls1.2" in v:
        return 0
    if "tlsv1.1" in v or "tlsv1.0" in v or "tls1.1" in v or "tls1.0" in v:
        return 5
    if "sslv3" in v or "ssl" in v:
        return 10
    return 2

def signature_alg_score(alg):
    if not alg:
        return 0
    a = alg.lower()
    if "sha1" in a or "md5" in a or "sha-1" in a:
        return 15
    return 0

def key_size_score(key_size, cipher):
    if key_size is None:
        return 0
    
    try:
        k = int(key_size)
    except Exception:
        return 0
    
    # Treat AES key sizes specially if they appear (128/256), otherwise RSA-like bits
    if k in (128, 256) and cipher.find("AES") != -1:
        return -10
    
    if k < 2048:
        return 10
    if k >= 2048:
        return -10
    
    return 0

def cn_san_match_score(cn, san_list, hostname):
    if not hostname: # change this later to get directly from url
        return 0
    host = hostname.lower()
    cn_ok = False
    san_ok = False
    if cn and isinstance(cn, str):
        cns = cn.lower()
        if cns == host:
            cn_ok = True
        if cns.startswith("*.") and host.endswith(cns[2:]):
            cn_ok = True
    if san_list and isinstance(san_list, list):
        for s in san_list:
            if not isinstance(s, str):
                continue
            s_l = s.lower()
            if s_l == host:
                san_ok = True
            if s_l.startswith("*.") and host.endswith(s_l[2:]):
                san_ok = True

    if cn_ok or san_ok:
        return -10
    
    if is_wildcard_in_san(san_list) and not (cn_ok or san_ok):
        return 5
    # mismatch heavy penalty
    return 15

def parse_iso(datestr):
    if not datestr:
        return None

    if isinstance(datestr, datetime):
        dt = datestr
    else:
        try:
            # Python 3.7+ fromisoformat (handles offset-aware strings)
            dt = datetime.fromisoformat(datestr)
        except Exception:
            # fallback formats
            fmts = [
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d"
            ]
            parsed = None
            for f in fmts:
                try:
                    parsed = datetime.strptime(datestr, f)
                    dt = parsed
                    break
                except Exception:
                    parsed = None
            if parsed is None:
                return None

    # Make timezone-aware (assume UTC if none)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

def parse_validity_days(not_before, not_after):
    if not_before is None or not_after is None:
        return None
    try:
        return (not_after - not_before).days
    except Exception:
        return None

def validity_score(not_before_s, not_after_s):
    nb = parse_iso(not_before_s)
    na = parse_iso(not_after_s)
    now = datetime.now(timezone.utc)
    delta = 0

    validity_days = parse_validity_days(nb, na)

    # Expired certificate
    if na and na < now:
        delta += 15

    # Very short-lived certificate
    if validity_days is not None:
        if validity_days < 2:
            delta += 10
        elif validity_days <= 30:
            delta += 2

    # Near expiry or long validity
    if na:
        try:
            days_to_expiry = (na - now).days
            if days_to_expiry < 1:
                delta += 20
            elif days_to_expiry < 7:
                delta += 5
            elif days_to_expiry > 365 * 2:
                delta += 5
        except Exception:
            pass

    # Future notBefore
    if nb and nb > now:
        delta += 5

    return delta

def serial_score(serial):
    if not serial:
        return 0
    s = str(serial)
    if len(s) < 8:
        return 5
    if all(ch in "01" for ch in s.lower()):
        return 5
    return 0

def san_count_score(san_list):
    if not san_list:
        return 5  # no SAN entries, slightly risky

    count = len(san_list)

    # Excessive number of SANs may indicate over-permissive certificate
    if count > 10:
        return 5

    return 0

def version_score(version) : # https://learn.microsoft.com/en-us/azure/iot-hub/reference-x509-certificates
    if not version: return 0

    if version == 2 or version == 1 or version == "v2" or version == "v1":
        return 10
    
    return -10

def issuer_score(issuer_name: str, is_root: bool = False) -> int:
    if not issuer_name:
        return 0

    n = issuer_name.strip().lower()

    # ---- Curated trusted set (common widely-trusted CAs) ----
    trusted_keywords = (
        "digicert", "globalsign", "entrust", "sectigo", "comodor", "comodo",
        "godaddy", "google trust", "microsoft corporation", "amazon trust services",
        "identrust", "quovadis", "d-trust", "dtrust", "buypass", "netlock",
        "trustis", "trustcor", "certipost", "certigna", "gov", "government",
        "post", "kisa", "isrg root x1"  # note: ISRG Root X1 is the root that signs Let's Encrypt intermediates
    )

    # ---- Suspicious / caution list (lower severity) ----
    suspicious_keywords = (
        "let's encrypt", "lets encrypt", "let's encrypt", "letsencrypt",
        "let's encrypt authority", "let's encrypt r", "let's encrypt r12",
        "cnnic", "china internet network information center", "cnn ic",
        "certum", "startcom", "start commercial", "startcom ltd", "startcom",
        "wo sign", "wosign", "wo sign ca", "wo sign ca limited",
        "certum", "e-town", "some lesser-known regional ca"
    )

    # ---- Known problematic / high-risk list (history of incidents) ----
    malicious_keywords = (
        "wo sign", "wosign", "startcom", "start commercial (startcom) ltd",
        "chunghwa telecom"  # include only if you want stricter checks (example)
    )

    score = 0

    # trusted check (exact/contains)
    for kw in trusted_keywords:
        if kw in n:
            # special-case: user wanted Let's Encrypt treated as suspicious,
            # so we do NOT include any variants of Let's Encrypt here.
            score += -10
            break

    # suspicious check (only if not already marked trusted)
    if score == 0:
        for kw in suspicious_keywords:
            if kw in n:
                score += 5
                break

    # malicious check (stronger penalty)
    for kw in malicious_keywords:
        if kw in n:
            # raise to malicious if matched
            # if suspicious matched earlier, replace with stronger penalty
            score = max(score, 15)
            break

    # If nothing matched, keep score 0 (unknown)
    # Apply extra penalty if this issuer is a root and it's suspicious/malicious
    if is_root and score > 0:
        # amplify root-level problems
        if score >= 20:
            score += 10   # malicious root -> very bad
        else:
            score += 5    # suspicious root -> worse than intermediate

    return score


def extract_cert_info(cert):
    subject = cert.get("subject") or {}
    issuer = cert.get("issuer") or {}
    return {
        "subject_cn": subject.get("commonName") or subject.get("CN"),
        "issuer_cn": issuer.get("commonName") or issuer.get("CN"),
        "notBefore": cert.get("notBefore"),
        "notAfter": cert.get("notAfter"),
        "serial": cert.get("serialNumber") or cert.get("serial"),
    }

def score_computer():
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "ssl.json")

    # Load json
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path}. Put ssl.json next to this script.")
    except Exception as e:
        return {"error": "failed to load ssl.json", "exception": str(e)}

    # Extract fields
    hostname = data.get("hostname")
    tls_version = data.get("tls_version")
    cipher = data.get("cipher")
    key_size = data.get("key_size")
    subject = data.get("subject") or {}
    cn = subject.get("commonName") or subject.get("CN") or None
    issuer = data.get("issuer") or {}
    issuer_cn = issuer.get("commonName") or issuer.get("organizationName") or issuer.get("organization") or None
    serial = data.get("serialNumber")
    version = data.get("version")
    notBefore = data.get("notBefore")
    notAfter = data.get("notAfter")
    san = data.get("subjectAltName") or []
    sig_alg = data.get("signature_algorithm")
    chain = data.get("chain") or []
    chain = chain[1:] if len(chain) > 1 else []
    intermediate_certs = []
    root_cert = None
    if chain:
        # Last one = root cert
        root_cert = chain[-1]
        # Everything before last = intermediates
        if len(chain) > 1:
            intermediate_certs = chain[:-1]
 
    score = 0
    
    if hostname:
        host = hostname.lower()
        has_digit = any(ch.isdigit() for ch in host)
        # crude heuristic: digits in hostname often indicate typosquat / homoglyph attempts
        # (this is intentionally simple to avoid adding new helper funcs)
        if has_digit and any(ch.isalpha() for ch in host):
            # treat digit-substitution as high suspicion
            score += 30
        elif any(x in host for x in ["free-", "login", "secure", "update", "verify", "account", "stream", "crack", "otp", "bank"]):
            score += 10
    else:
        score += 5

    if cipher:
        score += cipher_suite_score(cipher)
    if tls_version:
        score += tls_version_score(tls_version)
    if sig_alg:
        score += signature_alg_score(sig_alg)
    if key_size:
        score += key_size_score(key_size,cipher)
    if notBefore and notAfter:
        score += validity_score(notBefore, notAfter)
    if cn:
        if san:
            score += cn_san_match_score(cn, san, hostname)
            score += san_count_score(san)
    if serial:
        score += serial_score(serial)
    if version:
        score += version_score(version) 
    if issuer_cn:
        score += issuer_score(issuer_cn, is_root=False)


    if intermediate_certs:
        for cert in intermediate_certs:
            info = extract_cert_info(cert)

            inter_score = 0
            if info.get("signature_algorithm"):
                inter_score += signature_alg_score(info["signature_algorithm"])
            if info.get("key_size"):
                inter_score += key_size_score(info["key_size"], info.get("cipher"))
            if info.get("notBefore") and info.get("notAfter"):
                inter_score += validity_score(info["notBefore"], info["notAfter"])
            if info.get("version"):
                inter_score += version_score(info["version"])
            if(info.get("serial")):
                score += serial_score("serial")
    
            score += inter_score

    # ---- Add score for root cert ----
    if root_cert:
        info = extract_cert_info(root_cert)

        root_score = 0
        if info.get("signature_algorithm"):
            root_score += signature_alg_score(info["signature_algorithm"])
        if info.get("key_size"):
            root_score += key_size_score(info["key_size"], info.get("cipher"))
        if info.get("notBefore") and info.get("notAfter"):
            root_score += validity_score(info["notBefore"], info["notAfter"])
        if(info.get("serial")):
            score += serial_score("serial")

    return score


if __name__ == "__main__":
    print(score_computer())
