import os
from dotenv import load_dotenv

from AbuseIPDB import AbuseIPDBScanner
from IPInfoScanner import IPInfoScanner
from SSLScanner import SSLCertScanner
from VirusTotal import VirusTotalScanner
from WHOis import WhoisScanner
from GSB import GSB

load_dotenv()  # Load environment variables from .env

class ApiManager:
    def __init__(self):
        
        #instantiate all the api services
        self.virustotal = VirusTotalScanner(api_key=os.getenv("VIRUSTOTAL_API_KEY"))
        self.abuseipdb = AbuseIPDBScanner(api_key=os.getenv("ABUSEIPDB_API_KEY"))
        self.ipinfo = IPInfoScanner(api_key=os.getenv("IPINFO_API_KEY"))
        self.whois = WhoisScanner(api_key=os.getenv("WHOIS_API_KEY"))
        self.ssl = SSLCertScanner()  # No API key needed
        self.gsb = GSB(api_key=os.getenv("GSB_API_KEY"))
