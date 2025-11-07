from flask import Flask, request, jsonify
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from datasets_fetch.run import run_all_parallel
from apis_geoip.run import run as run_apis
from dns_check.run import run as run_dns
from ssl_check.run import run as run_ssl
from whois_check.run import run as run_whois
from feature_extraction import process_urls
from run_ml import run as run_ml

app = Flask(__name__)

executor = ThreadPoolExecutor(max_workers=5)  # concurrent API calls

def domain(url) :
    try:
        if url.startswith("https://"):
            return url[8:]
        elif url.startswith("http://"):
            return url[7:]
        else:
            raise ValueError("Invalid URL: must start with http:// or https://")
    except Exception as e:
        print(f"Error: {e}")
        return "" 
    
#this process the url to compture threat score
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")
    config = data.get("config", {})
    level = int(config.get("securityLevel", 3))
    print("Received URL:", url, "Security level:", level)

    # Step 1: process URLs (no threading, as requested) 
    # this is feature extraction
    process_urls([url], max_workers=4)
    print("Feature Extraction Done !!!")

    # Step 2: Define tasks based on level
    tasks = []
    if level >= 1:
        tasks.append(run_ml)
    if level >= 2:
        tasks.append(run_dns)
    if level >= 3:
        tasks.append(run_ssl)
    if level >= 4:
        tasks.append(run_whois)
    if level >= 5:
        tasks.append(run_apis)

    # Step 3: Run selected functions in thread pool
    futures = []
    for fn in tasks:
        futures.append(executor.submit(fn))

    # Step 4: Collect numeric results
    total_score = 0
    for fut in futures:
        try:
            result = fut.result()
            if isinstance(result, (int, float)):
                total_score += result
            else:
                print(f"Non-numeric output from {fn.__name__}: {result}")
        except Exception as e:
            print("Error running task:", e)

    print(total_score)
    # Step 5: Prepare response
    return jsonify({
        "url": url,
        "domain": domain(url),
        "risk_score": total_score,
        "verdict": f"suspicious ({level})"
    })


#run the da run.py script on chrome launch
@app.route("/update_dataset", methods=["POST"])
def update_dataset():
    run_all_parallel()
    return "datasets_fetched"

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
