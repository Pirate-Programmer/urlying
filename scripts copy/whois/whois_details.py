import whois
import json
import os
from datetime import datetime
import socket
from ipwhois import IPWhois

def serialize(obj):
    if isinstance(obj, (datetime, )):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)

def get_asn(domain):
    try:
        # Resolve domain to IP
        ip = socket.gethostbyname(domain)
        
        # Lookup ASN info
        obj = IPWhois(ip)
        results = obj.lookup_rdap(asn_methods=["whois", "http"])
        
        return {
            "asn": results.get("asn"),
            "asn_country_code": results.get("asn_country_code"),
        }
    except Exception as e:
        return {"ip": None, "asn": None, "error": str(e)}


def get_whois_info(domain):
    try:
        w = whois.whois(domain)

        # Normalize domain name
        domain_name = w.domain_name[0] if isinstance(w.domain_name, list) else w.domain_name

        # Base WHOIS data
        whois_data = {
            "domain_name": domain_name,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "updated_date": w.updated_date,
            "dnssec": w.dnssec,
            "status": w.status,
            "emails": w.emails,
            "registrar": w.registrar
        }

        # Add ASN info
        asn_info = get_asn(domain_name)
        whois_data.update(asn_info)

        return whois_data

    except Exception as e:
        return {"error": str(e)}

def save_whois_info(domain, filename="whois.json"):
    info = get_whois_info(domain)

    with open(filename, "w") as f:
        json.dump({domain: info}, f, indent=4, default=serialize)

    return filename

# https://pam2024.cs.northwestern.edu/pdfs/paper-89.pdf
# https://bpb-us-e2.wpmucdn.com/faculty.sites.uci.edu/dist/5/764/files/2021/02/ndss21.pdf