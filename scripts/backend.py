from flask import Flask, request, jsonify
import asyncio
from concurrent.futures import ThreadPoolExecutor
# from apis.api_manager import ApiManager
from urllib.parse import urlparse

import subprocess


app = Flask(__name__)
# api_manager = ApiManager()

# Mapping security levels to APIs (updated, ipinfo removed)
LEVEL_API_MAPPING = {
    1: ["gsb"],                                # light / fast check
    2: ["gsb"],                                # level 2 still only GSB
    3: ["gsb", "abuseipdb"],                   # include AbuseIPDB
    4: ["gsb", "abuseipdb", "virustotal"],    # include VirusTotal
    5: ["gsb", "abuseipdb", "virustotal", "maxmind"],  # include MaxMind
    6: ["gsb", "abuseipdb", "virustotal", "maxmind"],  # max scrutiny
}

executor = ThreadPoolExecutor(max_workers=5)  # concurrent API calls

# async def call_api_async(api_name, target_url, hostname):
#     loop = asyncio.get_event_loop()
#     try:
#         if api_name == "abuseipdb":
#             return await loop.run_in_executor(executor, api_manager.abuseipdb.fetch_result, hostname)
#         elif api_name == "gsb":
#             return await loop.run_in_executor(executor, api_manager.gsb.fetch_result, target_url)
#         elif api_name == "virustotal":
#             return await loop.run_in_executor(executor, api_manager.virustotal.fetch_result, target_url)
#         elif api_name == "maxmind":
#             return await loop.run_in_executor(executor, api_manager.maxmind.fetch_result, hostname)
#     except Exception as e:
#         return {"success": False, "unsafe": False, "source": api_name, "error": str(e)}

# async def run_apis(url, hostname, level):
#     apis_to_call = LEVEL_API_MAPPING.get(level, ["gsb", "abuseipdb"])
#     results_list = await asyncio.gather(*(call_api_async(api, url, hostname) for api in apis_to_call))
#     return {api: res for api, res in zip(apis_to_call, results_list)}

#this process the url to compture threat score
@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")
    config = data.get("config", {})
    level = int(config.get("securityLevel", 3))
    print("Received URL:", url, "Security level:", level)
    
            

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    print(f"hostname: {hostname}")
    # # Run all API calls asynchronously
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # api_results = loop.run_until_complete(run_apis(url, hostname, level))

    # # Compute simple risk score for now
    # risk_score = 0
    # for res in api_results.values():
    #     print(res)
    #     if res.get("success") and res.get("unsafe"):
    #         risk_score += 25  # each unsafe API contributes to risk score
    # risk_score = min(risk_score, 100)
    risk_score = 60
    # Placeholder for ML model integration per security level
    # ML_MODEL_RESULT = ml_model.predict(url)  # to be implemented later
    
    print(risk_score)

    result = {
        "url": url,
        "risk_score": risk_score,
        "verdict": f"suspicious ({level})",
       # "api_results": api_results
    }
    return jsonify(result)


#run the da run.py script on chrome launch
@app.route("/update_dataset", methods=["POST"])
def update_dataset():
    print("\n\nYOO chrome just lauched less go!!\n\n")
    return "IT WORKS"
    # import subprocess, sys, os

    # script_path = os.path.join(os.path.dirname(__file__), "run.py")
    # try:
    #     subprocess.Popen([sys.executable, script_path])
    #     return {"status": "ok", "message": "Dataset update started"}, 200
    # except Exception as e:
    #     return {"status": "error", "message": str(e)}, 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
