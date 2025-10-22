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

def ttl_soa(ttl):
    if ttl is None:
        return 5
    if ttl <= 300:
        return 15
    elif ttl <= 3600:
        return 7
    elif ttl <= 86400:
        return -5
    else:
        return 5

def ttl_ptr(ttl):
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

def ttl_srv(ttl):
    if ttl is None:
        return 5
    if ttl <= 300:
        return 12
    elif ttl <= 3600:
        return 4
    elif ttl <= 86400:
        return -5
    else:
        return 5

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
        "no-ip.org", "noip.com", "duckdns.org", "dynu.com", "dynu.net",
        "freedns.afraid.org", "dnsdynamic.org", "ddns.net", "dyndns.org",
        "xip.io"
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

    # low-quality / dynamic hostnames
    DDNS_PROVIDERS = {
        "no-ip.org", "noip.com", "duckdns.org", "dynu.com", "dynu.net",
        "freedns.afraid.org", "dnsdynamic.org", "ddns.net", "dyndns.org", "xip.io"
    }
    
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

def txt_score():
    