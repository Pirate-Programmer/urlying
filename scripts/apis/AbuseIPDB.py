import requests
import socket

class AbuseIPDBScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.API_URL = "https://api.abuseipdb.com/api/v2/check"
        self.source = "AbuseIPDB"

    """return -> dict
        if success == true, unsafe : bool (based on abuse score), source : str, extra : dict (abuse details)
        if success == false , error : str, source : str
    """
    def fetch_result(self, target_url):
        ip = self.resolve_to_ip(target_url)
        if not ip:
            return {
                "success": False,
                "error": "Could not resolve domain or invalid IP",
                "source": self.source
            }

        headers = {
            "Key": self.api_key,
            "Accept": "application/json"
        }

        params = {
            "ipAddress": ip,
            "maxAgeInDays": 365, #adjust value to get info from how long back 
            "verbose": True
        }

        try:
            response = requests.get(self.API_URL, headers=headers, params=params, timeout=5)
            response.raise_for_status()

            data = response.json().get("data", {})
            abuse_score = data.get("abuseConfidenceScore", 0)
            is_unsafe = abuse_score >= 50  #  You can adjust the threshold

            return {
                "success": True,
                "unsafe": is_unsafe,
                "source": self.source,
                "extra": data  # include full abuse info
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }


    def resolve_to_ip(self, input_value):
        try:
            return socket.gethostbyname(input_value)
        except socket.gaierror:
            return None
