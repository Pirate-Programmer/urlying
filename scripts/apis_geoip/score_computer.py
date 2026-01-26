import pandas as pd
import os, json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "..", "datasets", "vpn_ips"))

def load_ip_set(filename):
    csv_path = os.path.join(DATA_DIR, filename)
    csv_path = os.path.normpath(csv_path)
    
    if not os.path.isfile(csv_path):
        print(f"[Error] CSV file not found: {csv_path}")
        return set()
    
    df = pd.read_csv(csv_path, dtype={"ip": str})
    return set(df["ip"])

def cyberghost(ip):
    return ip in load_ip_set("cyberghost_vpn_ip_list.csv")

def mullvad(ip):
    return ip in load_ip_set("mullvad_vpn_ip_list.csv")

def nord(ip):
    return ip in load_ip_set("nord_vpn_ip_list.csv")

def proton(ip):
    return ip in load_ip_set("proton_vpn_ip_list.csv")

def surfshark(ip):
    return ip in load_ip_set("surfshark_vpn_ip_list.csv")

def tor_exit(ip):
    return ip in load_ip_set("tor_exit_nodes_ip_list.csv")

def tor_entry(ip):
    return ip in load_ip_set("tor_guard_nodes_ip_list.csv")

def abuseIPDB(unsafe, abuse_score):
    score = 0
    if unsafe:
        score += 5
    else:
        score -= 5
    if isinstance(abuse_score, (int, float)):
        score += abuse_score * 0.5
    else:
        # score += 0 
        pass

    return score

def gsb(unsafe):
    score = 0
    if unsafe:
        score += 5
    else:
        score -= 5

    return score

def virustotal(unsafe, reputation):
    score = 0
    if unsafe:
        score += 5
    else:
        score -= 5

    rep = reputation if isinstance(reputation, (int, float)) else 0

    score -= rep * 0.1
    return score

def score_computer():
    json_path1 = os.path.normpath(os.path.join(BASE_DIR, "..", "apis_geoip", "abuseIPDB.json"))
    json_path2 = os.path.normpath(os.path.join(BASE_DIR, "..", "apis_geoip", "gsb.json"))
    json_path3 = os.path.normpath(os.path.join(BASE_DIR, "..", "apis_geoip", "virustotal.json"))

    try:
        with open(json_path1, "r", encoding="utf-8") as f:
            data1 = json.load(f)
        with open(json_path2, "r", encoding="utf-8") as f:
            data2 = json.load(f)
        with open(json_path3, "r", encoding="utf-8") as f:
            data3 = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path1}. Put dns.json next to this script.")
    except Exception as e:
        return {"error": "failed to load dns.json", "exception": str(e)}
    
    score = 0
    ip = data1.get("ip")
    unsafe_abuseipdb = data1.get("unsafe")
    abuse_score = data1.get("abuse_score")
    unsafe_gsb = data2.get("unsafe")
    unsafe_virustotal = data3.get("unsafe")
    reputation = data3.get("reputation")

    if cyberghost(ip) : 
        score += 10
    elif mullvad(ip) :
        score += 10
    elif nord(ip) :
        score += 10
    elif proton(ip) : 
        score += 10
    elif surfshark(ip) :
        score += 10
    elif tor_entry(ip) : 
        score -= 10
    elif tor_exit(ip) :
        score += 10

    score += abuseIPDB(unsafe_abuseipdb, abuse_score)
    score += gsb(unsafe_gsb)
    score += virustotal(unsafe_virustotal, reputation)

    return score

