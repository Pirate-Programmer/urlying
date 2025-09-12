import whois
import json
import os
from datetime import datetime

def serialize(obj):
    """Convert non-serializable objects like datetime to string."""
    if isinstance(obj, (datetime, )):
        return obj.isoformat()
    if isinstance(obj, set):
        return list(obj)
    return str(obj)

def get_whois_info(domain):
    """Fetch WHOIS info for a given domain."""
    try:
        w = whois.whois(domain)
        return {
            "domain_name": w.domain_name,
            "registrar": w.registrar,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "updated_date": w.updated_date,
            "name_servers": w.name_servers,
            "emails": w.emails,
            "status": w.status
        }
    except Exception as e:
        return {"error": str(e)}

def save_whois_info(domain, filename="whois.json"):
    """Save WHOIS info into project json folder."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    json_dir = os.path.join(project_root, "json")
    os.makedirs(json_dir, exist_ok=True)

    file_path = os.path.join(json_dir, filename)
    info = get_whois_info(domain)

    with open(file_path, "w") as f:
        json.dump({domain: info}, f, indent=4, default=serialize)

    return file_path