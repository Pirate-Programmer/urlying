from dns_records import save_dns_records
import sys

if __name__ == "__main__":
    domain = sys.argv[1] if len(sys.argv) > 1 else "netmirror.app"
    output_file = save_dns_records(domain, "dns.json")
    print(f"✅ DNS records for {domain} saved in {output_file}")
