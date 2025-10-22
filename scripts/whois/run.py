from whois_details import save_whois_info
import socket

if __name__ == "__main__":
    domain = "hianime.to"
    output_file = save_whois_info(domain)
    print(f"WHOIS info for {domain} saved to {output_file}")