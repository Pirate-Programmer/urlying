import sys
from sslcerts import save_ssl_info   # adjust if needed

def run(domain):
    output_file = save_ssl_info(domain, "ssl.json")
    print(f"SSL info for {domain} saved in {output_file}")

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "google.com"
    run(host)
