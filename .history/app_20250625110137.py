from flask import Flask, request, jsonify
import io
import contextlib

app = Flask(__name__)

@app.route("/run", methods=["GET", "POST"])
def run_code():
    if request.method == "POST":
        code = request.json.get("code", "")
        output = io.StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, {})
            result = output.getvalue()
            return jsonify({"result": result})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
    else:
        # GET request to /run
        return (
            "Please send a POST request with JSON body containing 'code' to execute.",
            200,
        )

@app.route("/")
def home():
    return "Hello! The app is running. Use the /run endpoint to POST your code."
