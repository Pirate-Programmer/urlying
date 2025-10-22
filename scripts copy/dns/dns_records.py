import dns.resolver
import json
import os

import dns.resolver
import dns.name
import dns.query
import dns.message
import dns.flags
import json
import os
import socket

def _get_authoritative_ns_names(domain):
    """Return list of authoritative NS hostnames (may be empty)."""
    try:
        ans = dns.resolver.resolve(domain, "NS", lifetime=2.0)
        return [str(rdata).rstrip('.') for rdata in ans]
    except Exception:
        return []

def _ns_names_to_ips(ns_names):
    """Resolve NS hostnames to IP addresses (A/AAAA)."""
    ips = []
    for ns in ns_names:
        try:
            a = dns.resolver.resolve(ns, "A", lifetime=2.0)
            ips.extend([str(r) for r in a])
        except Exception:
            pass
        try:
            aaaa = dns.resolver.resolve(ns, "AAAA", lifetime=2.0)
            ips.extend([str(r) for r in aaaa])
        except Exception:
            pass
    return ips

def _query_authoritative_ttl(domain, rtype, ns_ip):
    """
    Query an authoritative server IP directly (recursion off) and return rrset ttl if present.
    Returns None on failure / no answer.
    """
    try:
        q = dns.message.make_query(domain, rtype, use_edns=True)
        q.flags &= ~dns.flags.RD  # clear recursion desired
        # try UDP first
        try:
            resp = dns.query.udp(q, ns_ip, timeout=2.0)
        except (OSError, dns.exception.Timeout):
            # fallback to TCP
            resp = dns.query.tcp(q, ns_ip, timeout=2.0)
        if resp and resp.answer:
            for rrset in resp.answer:
                if rrset.rdtype == dns.rdatatype.from_text(rtype):
                    return rrset.ttl
    except Exception:
        pass
    return None

def get_dns_records(domain):
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR", "SRV"]
    all_records = {}

    # get authoritative NS names once (used for TTL lookups)
    ns_names = _get_authoritative_ns_names(domain)
    ns_ips = _ns_names_to_ips(ns_names) if ns_names else []

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records = [str(rdata) for rdata in answers]

            # Try to obtain the original (configured) TTL from an authoritative server.
            ttl = None
            for ns_ip in ns_ips:
                auth_ttl = _query_authoritative_ttl(domain, rtype, ns_ip)
                if auth_ttl is not None:
                    ttl = auth_ttl
                    break

            # Fallback: use resolver-provided rrset TTL (may be remaining TTL)
            if ttl is None:
                ttl = getattr(answers.rrset, 'ttl', None)

            all_records[rtype] = {
                "records": records,
                "ttl": ttl
            }
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
            all_records[rtype] = {
                "records": [],
                "ttl": None
            }

    return all_records

def save_dns_records(domain, filename="dns.json"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, filename)
    info = get_dns_records(domain)
    with open(file_path, "w") as f:
        json.dump(info, f, indent=4)

    return file_path

#  https://fse.studenttheses.ub.rug.nl/13509/1/master_thesis_pascal_bouwers.pdf

# https://learn.microsoft.com/en-us/archive/technet-wiki/7608.srv-records-registered-by-net-logon