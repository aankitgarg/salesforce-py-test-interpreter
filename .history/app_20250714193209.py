from flask import Flask, request, jsonify
import sys
import io
import traceback

app = Flask(__name__)

@app.route("/", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}

    # Redirect stdout to capture print output
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Safely execute multi-line Python code
        exec(code, {}, local_vars)
        # Capture printed output
        output = sys.stdout.getvalue()
        return jsonify({"output": output})
    except Exception as e:
        # Capture exception details
        tb = traceback.format_exc()
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": tb
        }), 500
    finally:
        # Reset stdout to original
        sys.stdout = original_stdout

if __name__ == "__main__":
    app.run(debug=True)
