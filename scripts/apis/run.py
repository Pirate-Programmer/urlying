#!/usr/bin/env python3
import os, json
from api_manager import ApiManager


def run():
    manager = ApiManager()

    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "..", "features.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path}. Put features.json next to this script.")
    except Exception as e:
        return {"error": "failed to load features.json", "exception": str(e)}

    features = data.get("features") or []
    if not features:
        raise ValueError("features.json does not contain a 'features' array or it's empty.")

    first = features[0]
    domain = first.get("domain")
    if not domain:
        raise ValueError("First feature does not contain a 'domain' key.")
    
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
    run()
