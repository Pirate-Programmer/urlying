from sslcerts import save_ssl_info
import sys

if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "www.google.com"
    output_file = save_ssl_info(host, "ssl.json")
    print(f"✅ SSL info for {host} saved in {output_file}")
