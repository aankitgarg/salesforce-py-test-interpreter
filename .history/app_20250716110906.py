import base64
import json
import traceback
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd

app = Flask(__name__)

def clean_for_json(obj):
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(i) for i in obj]
    else:
        return obj

@app.route("/")
def health_check():
    return "Python interpreter is running"

@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' in request body", "success": False}), 400

        encoded_code = data['code']
        decoded_code = base64.b64decode(encoded_code).decode('utf-8')

        local_vars = {}
        exec(decoded_code, {}, local_vars)

        if 'result' not in local_vars:
            return jsonify({"error": "'result' variable not defined in code", "success": False}), 400

        cleaned_result = clean_for_json(local_vars['result'])

        return jsonify({
            "success": True,
            "result": cleaned_result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Execution error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
