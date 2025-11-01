import re

def ttl_a(ttl):
    if ttl is None:
        return 5
    if ttl <= 60:
        return 20
    elif ttl < 300:
        return 7
    elif ttl >= 300:
        return -5
    else:
        return 5
    
def ttl_aaaa(ttl):
    if ttl is None:
        return 5
    if ttl <= 60:
        return 20
    elif ttl < 300:
        return 7
    elif ttl >= 300:
        return -5
    else:
        return 5
    
def ttl_cname(ttl):
    if ttl is None:
        return 5
    if ttl <= 60:
        return 15
    elif ttl <= 3600:
        return 7
    elif ttl <= 86400:
        return -5
    else:
        return 5

def ttl_mx(ttl):
    if ttl is None:
        return 5
    if ttl <= 300:
        return 20
    elif ttl <= 3600:
        return 7
    elif ttl <= 86400:
        return -5
    else:
        return 5

def ttl_ns(ttl):
    if ttl is None:
        return 5
    if ttl <= 300:
        return 10
    elif ttl <= 3600:
        return 3
    elif ttl <= 86400:
        return -5
    else:
        return 5

def ttl_txt(ttl):
    if ttl is None:
        return 5
    if ttl == 3600:
        return -5
    return 10

def mx_score(records, a_records=None):
    score = 0
    has_mx = len(records) > 0

    if not has_mx:
        score += 10
        return score

    records = [r.lower() for r in records]
    a_records = [a.lower() for a in (a_records or [])]

    # Known dynamic/DDNS provider substrings
    DDNS_PROVIDERS = [
        "dynu.com", "dyn.com", "no-ip.com", "noip.com", "changeip.com", "afraid.org",
        "duckdns.org", "dnsdynamic.org", "duiadns.net", "myonlineportal.com", "dns4e.com",
        "gslb.me", "system-ns.com", "dnsexit.com", "nubem.com", "dtdns.com", "nsupdate.info",
        "dnsomatic.com", "x24hr.com", "tzo.com", "3322.net", "serverthuis.com", "dtdns.net",
        "spdyn.de", "pubyun.com", "gogoip.com", "do.de", "ddnss.de"
    ]

    for mx in records:        
        # Suspicious if MX host is a known DDNS provider
        if any(ddns in mx for ddns in DDNS_PROVIDERS):
            score += 25  # heavier penalty for DDNS MX
        
        # Suspicious if MX is same as A record (web and mail same host)
        if any(mx.startswith(a) or a in mx for a in a_records):
            score += 7
        
        # Suspicious if generic or low-quality hostname pattern
        if any(x in mx for x in ["mail.local", "localhost", "example", "test", "temp"]):
            score += 15
        
        # Otherwise, minor safe offset for clean MX
        if "google" in mx or "outlook" in mx or "yahoo" in mx or "zoho" in mx:
            score -= 10

    return score

def ns_score(records, a_records=None):
    score = 0
    if not records:
        return 15 

    records = [r.lower() for r in records]
    a_records = [a.lower() for a in (a_records or [])]

    DDNS_PROVIDERS = [
        "dynu.com", "dyn.com", "no-ip.com", "noip.com", "changeip.com", "afraid.org",
        "duckdns.org", "dnsdynamic.org", "duiadns.net", "myonlineportal.com", "dns4e.com",
        "gslb.me", "system-ns.com", "dnsexit.com", "nubem.com", "dtdns.com", "nsupdate.info",
        "dnsomatic.com", "x24hr.com", "tzo.com", "3322.net", "serverthuis.com", "dtdns.net",
        "spdyn.de", "pubyun.com", "gogoip.com", "do.de", "ddnss.de"
    ]
    
    TRUSTED_PROVIDERS = {"cloudflare", "google", "awsdns", "akamai", "azure"}

    for ns in records:
        # dynamic/DDNS
        if any(ddns in ns for ddns in DDNS_PROVIDERS):
            score += 20

        # trusted provider reduces score
        if any(tp in ns for tp in TRUSTED_PROVIDERS):
            score -= 5

        # same as A record
        if any(ns.startswith(a) or a in ns for a in a_records):
            score += 5

    return score

def txt_score(records):
    # No TXT records = suspicious / missing email auth
    if not records:
        return 10  
    
    score = 0

    # Too many TXT records (DNS abuse / crypto mining / malware C2)
    if len(records) > 50:
        score += 10  

    safe_prefixes = [
        "v=spf1", "v=dkim1", "v=dmarc1", "google-site-verification",
        "apple-domain-verification", "ms=", "facebook-domain-verification",
        "yandex-verification", "onetrust-domain-verification",
        "cisco-ci-domain-verification", "docusign", "globalsign-smime-dv",
        "_amazonses", "v=bimi1", "sendgrid", "mailchimp", "mailgun"
    ]

    for txt in records:
        t = txt.lower().strip()

        # Safe TXT patterns
        if any(t.startswith(prefix) for prefix in safe_prefixes):
            score -= 8 

        # Base64 encoded payload (possible C2)
        if re.fullmatch(r"[A-Za-z0-9+/]{20,}={0,3}", t):
            score += 10  

        # Hex blob (botnet / key / payload)
        if re.fullmatch(r"[0-9a-f]{30,}", t):
            score += 10  

        # VERY long TXT entry (DNS tunneling behavior)
        if len(t) > 200:
            score += 30

    return score

