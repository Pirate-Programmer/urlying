import os, re
import json
from datetime import datetime, timezone
import pandas as pd

def parse_iso(datestr):
    
    if not datestr:
        return None
    if isinstance(datestr, datetime):
        dt = datestr
    else:
        try:
            dt = datetime.fromisoformat(datestr)
        except Exception:
            fmts = [
                "%Y-%m-%dT%H:%M:%S.%f%z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d"
            ]
            dt = None
            for f in fmts:
                try:
                    dt = datetime.strptime(datestr, f)
                    break
                except Exception:
                    dt = None
            if dt is None:
                return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

def domain_age_score(creation_date):
    now = datetime.now(timezone.utc)
    dt = parse_iso(creation_date)
    if not dt:
        return 5
    years = (now - dt).days / 365.0
    if years <= 1:
        return 5
    if years <= 3:
        return 0
    return -10

def expiry_score(expiration_date):
    now = datetime.now(timezone.utc)
    dt = parse_iso(expiration_date)
    if not dt:
        return 0
    days = (dt - now).days
    if days < 1:
        return 15
    if days <= 30:
        return 5

    return -10

def registrar_score(registrar):
    if not registrar:
        return 0

    base_path = os.path.dirname(__file__) 
    csv_path = os.path.join(base_path, "..", "..", "datasets", "icann_registrars", "icann_registrars.csv")
    csv_path = os.path.abspath(csv_path)  

    registrars = pd.read_csv(csv_path)
    reg = set(registrars["registrars"])
    if registrar in reg:
        return -10
    return 5

def status_score(status):
    if not status:
        return 0

    # Ensure status is a list
    if isinstance(status, str):
        status = [status]

    score = 0
    
    safe = ["ok", "clientTransferProhibited", "clientDeleteProhibited", "clientUpdateProhibited",
            "serverTransferProhibited", "serverDeleteProhibited", "serverUpdateProhibited"]
    malicious = ["redemptionPeriod", "serverHold", "clientHold", "pendingRestore", "pendingDelete"]
    suspicious = ["inactive", "pendingCreate", "pendingRenew", "pendingUpdate",
                  "pendingTransfer", "clientRenewProhibited", "serverRenewProhibited"]

    for x in status:
        if not x or len(x.strip()) == 0:
            continue
        cleaned_status = x.strip().split()[0]
        if cleaned_status in safe:
            score -= 5
        elif cleaned_status in malicious:
            score += 5
        elif cleaned_status in suspicious:
            score += 2
        else:
            score += 10

    return score

def email_score(emails, registrar, hostname=None):
    if not emails:
        return 5

    # Normalize and split registrar into meaningful parts
    registrar_parts = set()
    if registrar:
        reg = registrar.lower()
        # Replace punctuation except dot and dash with space (commas, parentheses, slashes, etc.)
        reg = re.sub(r"[^a-z0-9\.\-\s]", " ", reg)
        # Replace multiple spaces with single space, then split
        for part in re.split(r"\s+", reg.strip()):
            if part:
                registrar_parts.add(part)

    # Normalize hostname similarly (store as string)
    hostname_norm = None
    if hostname:
        hn = hostname.lower().strip()
        hn = re.sub(r"[^a-z0-9\.\-]", "", hn)
        if hn:
            hostname_norm = hn

    score = 0

    # regex to extract domain part after '@' (handles <Name> formats too)
    email_domain_re = re.compile(r"@([A-Za-z0-9\.\-]+)")

    for email in emails:
        try:
            if not email or not isinstance(email, str):
                score += 5
                continue

            m = email_domain_re.search(email)
            if not m:
                # no domain found -> treat as suspicious/invalid
                score += 5
                continue

            domain_part = m.group(1).lower().strip()

            # Clean domain (strip trailing punctuation)
            domain_part = domain_part.strip(" .,-_")

            matched = False

            # Check registrar parts as substrings in the domain
            for part in registrar_parts:
                # skip trivial parts
                if len(part) < 2:
                    continue
                if part in domain_part:
                    matched = True
                    break

            # Check hostname if not matched yet
            if not matched and hostname_norm:
                if hostname_norm in domain_part:
                    matched = True

            if matched:
                score -= 10
            else:
                score += 5

        except Exception:
            score += 5

    return score

def updated_date_score(updated_date):
    now = datetime.now(timezone.utc)
    dt = parse_iso(updated_date)
    if not dt:
        return 0   # No penalty because some WHOIS hides this

    days = (now - dt).days

    # Recently updated (< 90 days) often legit
    if days <= 90:
        return -10 
    
    # Updated a long time back (> 2 years) suspicious
    if days > 730:
        return 5
    
    return 0  # Slight neutral suspicion otherwise

def dnssec_score(dnssec):
    if dnssec == "signed":
        return -10
    return 0

def asn_score(asn):
    if asn is None:
        return 0
    
    base_path = os.path.dirname(__file__) 
    csv_path = os.path.join(base_path, "..", "..", "datasets", "bad_asns", "bad_asns.csv")
    csv_path = os.path.abspath(csv_path)  

    asns = pd.read_csv(csv_path)
    asns = set(asns)

    if asn in asns:
        return 10
    
    return 0

def whois_score_computer():
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "whois.json")

    # Load json
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)  
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path}. Put whois.json next to this script.")
    except Exception as e:
        return {"error": "failed to load whois.json", "exception": str(e)}

    score = 0
    domain = data.get("domain_name")
    creation_date = data.get("creation_date")
    expiration_date = data.get("expiration_date")
    updated_date = data.get("updated_date")
    dnssec = data.get("dnssec")
    status = data.get("status") or []
    emails = data.get("emails") or []
    registrar = data.get("registrar")
    asn = data.get("asn")
 
    if creation_date:
        score += domain_age_score(creation_date)
    if expiration_date:
        score += expiry_score(expiration_date)
    if updated_date:
        score += updated_date_score(updated_date)
    if registrar:
        score += registrar_score(registrar)
        if emails:
            score += email_score(emails, registrar, domain)
        else:
            score += 10
    if dnssec:
        score += dnssec_score(dnssec)
    if status:
        score += status_score(status)
    if asn:
        score += asn_score(asn)

    return score

if __name__ == "__main__":
    result = whois_score_computer()
    print(json.dumps(result, indent=4))

