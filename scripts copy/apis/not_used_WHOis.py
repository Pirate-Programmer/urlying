import requests

class WhoisScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.source = "WhoisXML"

    def fetch_result(self, target_url):
        WHOIS_URL = "https://www.whoisxmlapi.com/whoisserver/WhoisService"
        params = {
            "apiKey": self.api_key,
            "domainName": target_url,
            "outputFormat": "JSON"
        }

        try:
            response = requests.get(WHOIS_URL, params=params)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"{response.status_code}: {response.text}",
                    "source": self.source
                }

            data = response.json().get("WhoisRecord", {})
            result = {
                "success": True,
                "unsafe": False,  # WHOIS doesn't give threat info directly
                "source": self.source,
                "extra": {
                    "domain": data.get("domainName"),
                    "created": data.get("createdDate"),
                    "expires": data.get("expiresDate"),
                    "updated": data.get("updatedDate"),
                    "registrar": data.get("registrarName"),
                    "nameservers": data.get("nameServers", {}).get("hostNames", []),
                    "contact_email": data.get("contactEmail")
                }
            }
            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }
