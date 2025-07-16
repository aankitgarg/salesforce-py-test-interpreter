import base64
import json
import traceback
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd

app = Flask(__name__)

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

        # Set up isolated execution environment
        local_vars = {}
        exec(decoded_code, {}, local_vars)

        # Expect 'result' variable to be defined
        if 'result' not in local_vars:
            return jsonify({"error": "'result' variable not defined in code", "success": False}), 400

        return jsonify({
            "success": True,
            "result": local_vars["result"]
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
