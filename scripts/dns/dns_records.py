import dns.resolver
import json
import os

def get_dns_records(domain):
    """Fetch DNS records and TTL for a given domain."""
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR", "SRV"]
    all_records = {}

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records = [str(rdata) for rdata in answers]

            # Get TTL (same for all answers in rrset)
            ttl = answers.rrset.ttl if answers.rrset else None

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
    """Save DNS records into project json folder."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    json_dir = os.path.join(project_root, "json")
    os.makedirs(json_dir, exist_ok=True)

    file_path = os.path.join(json_dir, filename)
    records = get_dns_records(domain)

    with open(file_path, "w") as f:
        json.dump({domain: records}, f, indent=4)

    return file_path
