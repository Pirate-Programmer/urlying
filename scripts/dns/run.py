from dns_records import save_dns_records
import sys

def run(domain):
    output_file = save_dns_records(domain, "dns.json")
    print(f"DNS info for {domain} saved in {output_file}")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "hanime.tv"
    run(host)
