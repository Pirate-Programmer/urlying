#!/usr/bin/env python3
import argparse
from api_manager import ApiManager


def main(domain):
    manager = ApiManager()

    # VirusTotal
    print("\n[+] VirusTotal")
    vt_result = manager.virustotal.fetch_result(domain)
    manager.virustotal.save_result_to_file(vt_result)
    print("✔ VirusTotal done")

    # AbuseIPDB
    print("\n[+] AbuseIPDB")
    abuse_result = manager.abuseipdb.fetch_result(domain)
    manager.abuseipdb.save_result_to_file(abuse_result)
    print("✔ AbuseIPDB done")

    # Google Safe Browsing
    print("\n[+] Google Safe Browsing (GSB)")
    gsb_result = manager.gsb.fetch_result(domain)
    manager.gsb.save_result_to_file(gsb_result)
    print("✔ GSB done")

    print("\n✅ Scan completed\n")


if __name__ == "__main__":
    main("veza-otp.com")
