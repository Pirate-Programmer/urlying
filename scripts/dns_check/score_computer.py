import re
import socket
import os
import json, pandas as pd

def tld_score(domain) :
    parts = domain.split('.')
    if len(parts) < 2:
        return 0
    tld = parts[-1]
    base_path = os.path.dirname(__file__) 
    csv_path = os.path.join(base_path, "..", "..", "datasets", "tlds", "suspicious_tlds.csv")
    csv_path = os.path.abspath(csv_path)  

    sus_tlds = pd.read_csv(csv_path)
    sus_tlds = set(sus_tlds)

    if tld in sus_tlds:
        return 10
    
    return 0

def ttl_a(ttl):
    if ttl is None: # https://developers.cloudflare.com/dns/manage-dns-records/reference/ttl/
        return 0
    if ttl <= 60:
        return 10
    elif ttl < 300:
        return 5
    elif ttl >= 300:
        return -10
    else:
        return 0

def ttl_aaaa(ttl): # https://developers.cloudflare.com/dns/manage-dns-records/reference/ttl/
    if ttl is None:
        return 0
    if ttl <= 60:
        return 10
    elif ttl < 300:
        return 5
    elif ttl >= 300:
        return -10
    else:
        return 0


def ttl_cname(ttl):
    if ttl is None:
        return 0
    if ttl <= 60:
        return 10
    elif ttl <= 3600:
        return 5
    elif ttl <= 86400:
        return -10
    else:
        return 0

def ttl_mx(ttl):
    if ttl is None:
        return 0
    if ttl <= 300:
        return 10
    elif ttl <= 3600:
        return 5
    elif ttl <= 86400:
        return -10
    else:
        return 0

def ttl_ns(ttl):
    if ttl is None:
        return 0
    if ttl <= 300:
        return 10
    elif ttl <= 3600:
        return 5
    elif ttl <= 86400:
        return -10
    else:
        return 0

def ttl_txt(ttl):
    if ttl is None:
        return 0
    if ttl >= 3600:
        return -10
    return 5

def aaaa_score(records):
    if not records:
        return 0
    if len(records) > 2:
        return 5  # suspicious: multiple IPv6 addresses
    return 0

def cname_score(cname_records, resolve_timeout_seconds=3):
    BAD_CNAME_HOSTS = [
        "cloudapp.net", "herokuapp.com", "github.io", "pages.dev",
        "azurewebsites.net", "s3.amazonaws.com", "amazonaws.com",
        "wordpress.com", "weebly.com", "netlify.app", "firebaseapp.com",
        "dynu.com", "dyn.com", "no-ip.com", "noip.com", "changeip.com", "afraid.org",
        "duckdns.org", "dnsdynamic.org", "duiadns.net", "myonlineportal.com", "dns4e.com",
        "gslb.me", "system-ns.com", "dnsexit.com", "nubem.com", "dtdns.com", "nsupdate.info",
        "dnsomatic.com", "x24hr.com", "tzo.com", "3322.net", "serverthuis.com", "dtdns.net",
        "spdyn.de", "pubyun.com", "gogoip.com", "do.de", "ddnss.de"
    ]

    cname_records = cname_records or []
    score = 0

    if not cname_records:
        return score

    for cname in cname_records:
        if not cname:
            continue

        c = cname.strip()
        cl = c.lower()

        # Root CNAME (bad practice)
        if c in ("@", "", "@."):
            score += 10
            continue

        # Flag bad host patterns (DDNS / takeover surfaces)
        for bad in BAD_CNAME_HOSTS:
            if bad in cl:
                penalty = 5 if bad in ("github.io", "herokuapp.com", "azurewebsites.net", "pages.dev") else 10
                score += penalty
                # don't break; a record might match multiple tokens

        # Resolve test for dangling CNAME (always resolve)
        try:
            old = socket.getdefaulttimeout()
            socket.setdefaulttimeout(resolve_timeout_seconds)
            try:
                info = socket.getaddrinfo(c, None)
                score -= 7  # reward: it resolves
            finally:
                socket.setdefaulttimeout(old)

        except socket.gaierror as e:
            # dangling/unresolvable = takeover possible
            pen = 15
            score += pen

        except Exception:
            # small penalty for unexpected errors
            score += 2

    return score

def mx_score(records, a_records=None):
    score = 0
    has_mx = len(records) > 0

    if not has_mx:
        return score

    records = [r.lower() for r in records]
    a_records = [a.lower() for a in (a_records or [])]

    DDNS_PROVIDERS = [
        "dynu.com", "dyn.com", "no-ip.com", "noip.com", "changeip.com", "afraid.org",
        "duckdns.org", "dnsdynamic.org", "duiadns.net", "myonlineportal.com", "dns4e.com",
        "gslb.me", "system-ns.com", "dnsexit.com", "nubem.com", "dtdns.com", "nsupdate.info",
        "dnsomatic.com", "x24hr.com", "tzo.com", "3322.net", "serverthuis.com", "dtdns.net",
        "spdyn.de", "pubyun.com", "gogoip.com", "do.de", "ddnss.de"
    ]

    for mx in records:
        if any(ddns in mx for ddns in DDNS_PROVIDERS):
            score += 15

        if any(mx.startswith(a) or a in mx for a in a_records):
            score += 5

        if any(x in mx for x in ["mail.local", "localhost", "example", "test", "temp"]):
            score += 10

        if "google" in mx or "outlook" in mx or "yahoo" in mx or "zoho" in mx:
            score -= 10

    return score

def ns_score(records, a_records=None):
    score = 0
    if not records:
        return 10

    records = [r.lower() for r in records]
    a_records = [a.lower() for a in (a_records or [])]

    DDNS_PROVIDERS = [
        "dynu.com", "dyn.com", "no-ip.com", "noip.com", "changeip.com", "afraid.org",
        "duckdns.org", "dnsdynamic.org", "duiadns.net", "myonlineportal.com", "dns4e.com",
        "gslb.me", "system-ns.com", "dnsexit.com", "nubem.com", "dtdns.com", "nsupdate.info",
        "dnsomatic.com", "x24hr.com", "tzo.com", "3322.net", "serverthuis.com", "dtdns.net",
        "spdyn.de", "pubyun.com", "gogoip.com", "do.de", "ddnss.de"
    ]

    TRUSTED_PROVIDERS = {"cloudflare", "google", "awsdns", "akamai", "azure", "yandex"}

    for ns in records:
        if any(ddns in ns for ddns in DDNS_PROVIDERS):
            score += 15

        if any(tp in ns for tp in TRUSTED_PROVIDERS):
            score -= 10

        if any(ns.startswith(a) or a in ns for a in a_records):
            score += 5

    return score

def txt_score(records):
    if not records:
        return 5

    score = 0

    if len(records) > 50:
        score += 5

    safe_prefixes = [
        "v=spf1", "v=dkim1", "v=dmarc1", "google-site-verification",
        "apple-domain-verification", "ms=", "facebook-domain-verification",
        "yandex-verification", "onetrust-domain-verification",
        "cisco-ci-domain-verification", "docusign", "globalsign-smime-dv",
        "_amazonses", "v=bimi1", "sendgrid", "mailchimp", "mailgun",
        "protonmail-verification"
    ]

    for txt in records:
        t = txt.lower().strip().strip('"')

        if any(t.startswith(prefix) for prefix in safe_prefixes):
            score -= 8

        if re.fullmatch(r"[A-Za-z0-9+/]{20,}={0,3}", t):
            score += 5

        if re.fullmatch(r"[0-9a-f]{30,}", t):
            score += 5

        if len(t) > 200:
            score += 15

    return score

def score_computer():
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "dns.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path}. Put dns.json next to this script.")
    except Exception as e:
        return {"error": "failed to load dns.json", "exception": str(e)}

    domain = data.get("domain")
    a_records, a_records_ttl       = (data.get("A") or {}).get("records") or [], (data.get("A") or {}).get("ttl")
    aaaa_records, aaaa_records_ttl = (data.get("AAAA") or {}).get("records") or [], (data.get("AAAA") or {}).get("ttl")
    cname_records, cname_records_ttl = (data.get("CNAME") or {}).get("records") or [], (data.get("CNAME") or {}).get("ttl")
    mx_records, mx_records_ttl     = (data.get("MX") or {}).get("records") or [], (data.get("MX") or {}).get("ttl")
    ns_records, ns_records_ttl     = (data.get("NS") or {}).get("records") or [], (data.get("NS") or {}).get("ttl")
    txt_records, txt_records_ttl   = (data.get("TXT") or {}).get("records") or [], (data.get("TXT") or {}).get("ttl")

    score = 0

    score += tld_score(domain)
    if a_records:
        score += ttl_a(a_records_ttl)

    if aaaa_records:
        score += aaaa_score(aaaa_records)
        score += ttl_aaaa(aaaa_records_ttl)

    if cname_records:
        score += cname_score(cname_records)
        score += ttl_cname(cname_records_ttl)

    if mx_records:
        score += ttl_mx(mx_records_ttl)
        score += mx_score(mx_records, a_records)

    if ns_records:
        score += ttl_ns(ns_records_ttl)
        score += ns_score(ns_records, a_records)
    else:
        score += 10

    if txt_records:
        score += ttl_txt(txt_records_ttl)
        score += txt_score(txt_records)
    else:
        score += 10

    return score

if __name__ == "__main__":
    print(score_computer())
