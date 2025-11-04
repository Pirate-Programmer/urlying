from .whois_details import save_whois_info
from .score_computer import whois_score_computer
import os, json

def run():
    base_path = os.path.dirname(__file__)
    json_path = os.path.join(base_path, "..", "features.json")

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find {json_path}. Put features.json next to this script.")
    except Exception as e:
        return {"error": "failed to load features.json", "exception": str(e)}

    features = data.get("features") or []
    if not features:
        raise ValueError("features.json does not contain a 'features' array or it's empty.")

    first = features[0]
    domain = first.get("domain")
    if not domain:
        raise ValueError("First feature does not contain a 'domain' key.")

    output_file = save_whois_info(domain, "whois.json")
    print(f"DNS info for {domain} saved in {output_file}")

    score = whois_score_computer()
    return score

if __name__ == "__main__":
    print(run())
