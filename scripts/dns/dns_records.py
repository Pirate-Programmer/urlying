import dns.resolver
import dns.reversename
import dns.exception
import json
import os

def get_dns_records(domain):
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "CAA"]
    all_records = {}

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            all_records[rtype] = [str(rdata) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
            all_records[rtype] = []

    # Handle PTR separately if input is an IP
    try:
        rev = dns.reversename.from_address(domain)
        answers = dns.resolver.resolve(rev, "PTR")
        all_records["PTR"] = [str(rdata) for rdata in answers]
    except Exception:
        all_records["PTR"] = []

    output_file = os.path.join(os.path.dirname(__file__), "../../json/dns.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        json.dump({domain: all_records}, f, indent=4)

    print(f"DNS records for {domain} saved to {output_file}")

if __name__ == "__main__":
    get_dns_records("")
