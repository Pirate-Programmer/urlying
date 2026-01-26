import requests
import json
import os

class GSB:

    def __init__(self, api_key):
        self.API_KEY = api_key
        self.source = "GSB"
        self.GSB_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.API_KEY}"
    
    def fetch_result(self, target_url):
        payload = {
            "client": {
                "clientId": "urlying",
                "clientVersion": "1.0"
            },
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION"
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": target_url}
                ]
            }
        }

        try:
            response = requests.post(self.GSB_URL, json=payload, timeout=5)
            response.raise_for_status()
            is_unsafe = "matches" in response.json()

            result = {
                "success": True,
                "unsafe": is_unsafe,
                "target": target_url,
                "source": self.source
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


    def save_result_to_file(self, result):
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, "gsb.json")

            with open(file_path, "w") as f:
                json.dump(result, f, indent=4)

        except Exception as e:
            print(f"[ERROR] Could not write log: {e}")
