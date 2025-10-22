import os
from dotenv import load_dotenv

from .AbuseIPDB import AbuseIPDBScanner
from .VirusTotal import VirusTotalScanner
from .GSB import GSB
from .Maxmind import MaxMindScanner

load_dotenv()  # Load environment variables from .env

class ApiManager:
    def __init__(self):
        
        #instantiate all the api services
        self.virustotal = VirusTotalScanner(api_key=os.getenv("VIRUSTOTAL_API_KEY"))
        self.abuseipdb = AbuseIPDBScanner(api_key=os.getenv("ABUSEIPDB_API_KEY"))
        self.gsb = GSB(api_key=os.getenv("GSB_API_KEY"))
        self.maxmind = MaxMindScanner(api_key=os.getenv("Maxmind_GEOIP_KEY"))
