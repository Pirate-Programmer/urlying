import requests
import base64

class VirusTotalScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.VT_URL = "https://www.virustotal.com/api/v3/urls/"
        self.source = "VirusTotal"

    """return -> dict
        if success == true, unsafe : bool, source : str, extra : dict (scan stats)
        if success == false , error : str, source : str
    """
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

            return {
                "success": True,
                "unsafe": is_unsafe,
                "source": self.source,
                "extra": {
                    "stats": stats,
                    "reputation": data.get("reputation"),
                    "scan_date": data.get("last_analysis_date")
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }

    def encode_url(self, url):
        encoded = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        return encoded
