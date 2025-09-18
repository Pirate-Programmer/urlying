from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/check_url", methods=["POST"])
def check_url():
    data = request.get_json()
    url = data.get("url")

    # Placeholder: call your Python scripts (whois, ssl, VirusTotal, ML model, etc.)
    print("Received URL:", url)

    # Dummy response (replace later with real scoring logic)
    result = {
        "url": url,
        "risk_score": 42,
        "verdict": "suspicious"
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
