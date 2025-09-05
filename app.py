from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# Base directory where scripts are located
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "scripts", "datasets_fetch")

@app.route('/trigger', methods=['POST'])
def trigger_action():
    data = request.json
    script_name = data.get("script")  # script name expected from extension, e.g., "tlds_fetch.py"

    if not script_name:
        return jsonify({"status": "error", "message": "No script name provided"}), 400

    script_path = os.path.join(SCRIPTS_DIR, script_name)

    if not os.path.isfile(script_path):
        return jsonify({"status": "error", "message": f"Script {script_name} not found"}), 404

    try:
        # Run the script
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=True
        )
        return jsonify({
            "status": "success",
            "script": script_name,
            "output": result.stdout
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "script": script_name,
            "error": e.stderr
        })

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
