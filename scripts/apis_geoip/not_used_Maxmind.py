import os
import requests
import dns.resolver

class MaxMindScanner:
    def __init__(self,api_key):
        self.api_key = api_key
        self.source = "MAXMIND"

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
                "extra": geo_results  
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
        url = f"https://geoip.maxmind.com/geoip/v2.1/city/{ip}"
        try:
            response = requests.get(url, auth=(self.api_key, ''), timeout=5)
            if response.status_code == 200:
                data = response.json()

                city = data.get("city", {}).get("names", {}).get("en", "N/A")
                region = (data.get("subdivisions") and data["subdivisions"][0].get("names", {}).get("en", "N/A")) or "N/A"
                country = data.get("country", {}).get("iso_code", "N/A")
                postal = data.get("postal", {}).get("code", "N/A")
                latitude = data.get("location", {}).get("latitude", "N/A")
                longitude = data.get("location", {}).get("longitude", "N/A")
                maps_url = f"https://maps.google.com/?q={latitude},{longitude}" if latitude != "N/A" else "N/A"

                return {
                    "ip": ip,
                    "hostname": "N/A",  
                    "city": city,
                    "region": region,
                    "country": country,
                    "postal": postal,
                    "latitude": latitude,
                    "longitude": longitude,
                    "google_maps": maps_url,
                    "org": "N/A", 
                    "timezone": data.get("location", {}).get("time_zone", "N/A")
                }
            else:
                return {"ip": ip, "error": f"{response.status_code}: {response.text}"}
        except Exception as e:
            return {"ip": ip, "error": str(e)}
