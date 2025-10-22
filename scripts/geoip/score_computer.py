import pandas as pd
import os

# Common base directory (relative to this script)
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


