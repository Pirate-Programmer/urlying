import requests
import dns.resolver

class IPInfoScanner:
    def __init__(self, api_key):
        self.api_key = api_key
        self.source = "IPINFO"


    """return -> dict
        if success == true, unsafe : bool (always False here), source : str, extra : list[dict] (geo info per IP)
        if success == false, error : str, source : str
    """
    def fetch_result(self, target_url):
        try:
            ip_list = self.resolve_domain_dns(target_url)

            if not ip_list:
                return {
                    "success": False,
                    "error": "No IPs found via DNS",
                    "source": self.source
                }

            geo_results = []
            for ip in ip_list:
                geo = self.get_geo_from_ip(ip)
                geo_results.append(geo)

            return {
                "success": True,
                "unsafe": False,
                "source": self.source,
                "extra": geo_results  # contains all IP geo info
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source": self.source
            }



    def resolve_domain_dns(self, domain):
        try:
            result = dns.resolver.resolve(domain, 'A')
            return [rdata.address for rdata in result]
        except Exception:
            return []


    def get_geo_from_ip(self, ip):
        url = f"https://ipinfo.io/{ip}?token={self.api_key}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                loc = data.get("loc", "")
                lat, lon = loc.split(",") if "," in loc else ("N/A", "N/A")
                maps_url = f"https://maps.google.com/?q={lat},{lon}" if lat != "N/A" else "N/A"

                return {
                    "ip": data.get("ip", "N/A"),
                    "hostname": data.get("hostname", "N/A"),
                    "city": data.get("city", "N/A"),
                    "region": data.get("region", "N/A"),
                    "country": data.get("country", "N/A"),
                    "postal": data.get("postal", "N/A"),
                    "latitude": lat,
                    "longitude": lon,
                    "google_maps": maps_url,
                    "org": data.get("org", "N/A"),
                    "timezone": data.get("timezone", "N/A")
                }
            else:
                return {"ip": ip, "error": f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {"ip": ip, "error": str(e)}
