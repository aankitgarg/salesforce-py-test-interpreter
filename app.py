from flask import Flask, request, jsonify
import io
import contextlib

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    output = io.StringIO()

    try:
        with contextlib.redirect_stdout(output):
            exec(code, {})
        result = output.getvalue()
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/")
def home():
    return "Hello! The app is running. Use the /run endpoint to POST your code."

if __name__ == "__main__":
    app.run()
