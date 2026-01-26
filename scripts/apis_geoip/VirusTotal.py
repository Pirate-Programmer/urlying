import requests
import base64
import json
import os

class VirusTotalScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.VT_URL = "https://www.virustotal.com/api/v3/urls/"
        self.source = "VirusTotal"

    def fetch_result(self, target_url):
        headers = {
            "x-apikey": self.api_key
        }

        encoded_url = self.encode_url(target_url)
        full_url = self.VT_URL + encoded_url

        try:
            response = requests.get(full_url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json().get("data", {}).get("attributes", {})

            stats = data.get("last_analysis_stats", {})
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)

            is_unsafe = malicious > 0 or suspicious > 0

            result = {
                "success": True,
                "unsafe": is_unsafe,
                "target": target_url,
                "source": self.source,
                "extra": {
                    "stats": stats,
                    "reputation": data.get("reputation"),
                    "scan_date": data.get("last_analysis_date")
                }
            }

            self.save_result_to_file(result)
            return result

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "target": target_url,
                "source": self.source
            }
            self.save_result_to_file(result)
            return result

    def encode_url(self, url):
        encoded = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        return encoded

    def save_result_to_file(self, result):
        """Store ONLY the latest scan result"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "virustotal.json")

            with open(file_path, "w") as f:
                json.dump(result, f, indent=4)

        except Exception as e:
            print(f"[ERROR] Could not write log: {e}")
