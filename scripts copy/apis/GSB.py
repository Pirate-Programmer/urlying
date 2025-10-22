import requests

class GSB:

    def __init__(self,api_key):
        self.API_KEY = api_key
        self.source="GSB"
        self.GSB_URL = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.API_KEY}"
        


    """return -> dict
        if success == true, unsafe : bool, source : str
        if success == false , error : str, source : str
    """
    def fetch_result(self, target_url):
        payload = {
            "client": {
                "clientId": "urllying",
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

            return {
                "success": True,
                "unsafe": is_unsafe,
                "source": self.source
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }

