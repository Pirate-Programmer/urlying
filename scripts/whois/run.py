from whois_details import save_whois_info
import sys

def run(domain):
    output_file = save_whois_info(domain, "whois.json")
    print(f"SSL info for {domain} saved in {output_file}")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "www.ultrafima.com"
    run(host)
