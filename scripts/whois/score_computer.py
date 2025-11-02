import os
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
        return 15
    years = (now - dt).days / 365.0
    if years <= 1:
        return 20
    if years <= 3:
        return 5
    return -5

def expiry_score(expiration_date):
    now = datetime.now(timezone.utc)
    dt = parse_iso(expiration_date)
    if not dt:
        return 10
    days = (dt - now).days
    if days < 1:
        return 30
    if days <= 30:
        return 20

    return -5

def registrar_score(registrar):
    if not registrar:
        return 0

    base_path = os.path.dirname(__file__) 
    csv_path = os.path.join(base_path, "..", "..", "datasets", "icann_registrars", "icann_registrars.csv")
    csv_path = os.path.abspath(csv_path)  

    registrars = pd.read_csv(csv_path)
    reg = set(registrars["registrars"])
    if registrar in reg:
        return -5
    return 20

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
            score += 10
        elif cleaned_status in suspicious:
            score += 5

    return score

def email_score(emails, registrar):
    if not emails:
        return 5
    
    registrar_word = ""
    if registrar:
        registrar_word = registrar.split()[0].lower().strip()  # first word, lowercase

    score = 0

    for email in emails:
        try:
            # Extract domain after '@'
            parts = email.split("@")
            if len(parts) == 2:
                domain_part = parts[1].lower()

                # Check substring match (not exact)
                if registrar_word and registrar_word in domain_part:
                    score -= 5
                else:
                    score += 5
            else:
                score += 5  # invalid email format
        except Exception:
            score += 5
    
    return score

def dnssec_score(dnssec):
    if dnssec == "signed":
        return -5
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

    domain = data.get("domain_name")
    baseline = 50
    breakdown = {}

    d_age = domain_age_score(data.get("creation_date"))
    breakdown["age"] = d_age

    d_exp = expiry_score(data.get("expiration_date"))
    breakdown["expiry"] = d_exp

    d_reg = registrar_score(data.get("registrar"))
    breakdown["registrar"] = d_reg

    d_stat = status_score(data.get("status"))
    breakdown["status"] = d_stat

    d_dns = dnssec_score(data.get("dnssec"))
    breakdown["dnssec"] = d_dns

    d_email = email_score(data.get("emails"), data.get("registrar"))
    breakdown["emails"] = d_email

    d_asn = asn_score(data.get("asn"))
    breakdown["asn"] = d_asn

    raw_sum = d_age + d_exp + d_reg + d_stat + d_dns + d_email + d_asn
    score = baseline + raw_sum

    if score >= 75:
        label = "malicious"
    elif score >= 50:
        label = "suspicious"
    elif score >= 25:
        label = "neutral"
    else:
        label = "safe"

    output = {
        domain: {
            "score": int(score),
            "label": label,
            "breakdown": breakdown,
            **data
        }
    }

    return output

if __name__ == "__main__":
    result = whois_score_computer()
    print(json.dumps(result, indent=4))

