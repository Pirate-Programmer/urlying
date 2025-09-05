import dns.resolver
import json
import os

def get_dns_records(domain):
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR", "SRV"]
    all_records = {}

    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            all_records[rtype] = [str(rdata) for rdata in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            all_records[rtype] = []

    output_file = os.path.join(os.path.dirname(__file__), "../../json/dns.json")

    with open(output_file, "w") as f:
        json.dump({domain: all_records}, f, indent=4)

    print(f"DNS records for {domain} saved to {output_file}")

get_dns_records("google.com")
