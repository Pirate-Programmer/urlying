import requests
import socket
import json
import os

class AbuseIPDBScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.API_URL = "https://api.abuseipdb.com/api/v2/check"
        self.source = "AbuseIPDB"
        self.log_file = os.path.join(os.path.dirname(__file__), "abuseipdb_logs.json")

    def fetch_result(self, target_url):
        ip = self.resolve_to_ip(target_url)
        if not ip:
            result = {
                "success": False,
                "error": "Could not resolve domain or invalid IP",
                "source": self.source,
                "target": target_url
            }
            self.save_result_to_file(result)
            return result

        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }

        params = {
            "ipAddress": ip,
            "maxAgeInDays": 60,
            "verbose": True
        }

        try:
            response = requests.get(self.API_URL, headers=headers, params=params, timeout=5)
            response.raise_for_status()

            data = response.json().get("data", {})
            abuse_score = data.get("abuseConfidenceScore", 0)
            is_unsafe = abuse_score >= 50

            result = {
                "success": True,
                "unsafe": is_unsafe,
                "abuse_score": abuse_score,
                "ip": ip,
                "target": target_url,
                "source": self.source
            }

            self.save_result_to_file(result)
            return result

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "source": self.source,
                "target": target_url
            }
            self.save_result_to_file(result)
            return result

    def resolve_to_ip(self, input_value):
        try:
            return socket.gethostbyname(input_value)
        except socket.gaierror:
            return None

    def save_result_to_file(self, result):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "abuseIPDB.json")

            with open(file_path, "w") as f:
                json.dump(result, f, indent=4)

        except Exception as e:
            print(f"[ERROR] Could not write log: {e}")

