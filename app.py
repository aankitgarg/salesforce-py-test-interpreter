from flask import Flask, request, jsonify
import sys
import io
import traceback
import builtins
import json
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["POST"])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}

    # Setup safe execution environment
    safe_globals = {
        "__builtins__": builtins.__dict__,
        "json": json,
        "pd": pd
    }

    # Capture printed output
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        # Split into lines
        lines = code.strip().split("\n")
        if lines:
            *exec_lines, last_line = lines
            exec_code = "\n".join(exec_lines)

            # First run all but last line (if any)
            if exec_code.strip():
                exec(exec_code, safe_globals, local_vars)

            # Try to evaluate the last line
            try:
                result = eval(last_line, safe_globals, local_vars)
                if result is not None:
                    print(result)
            except Exception:
                exec(last_line, safe_globals, local_vars)
        else:
            exec(code, safe_globals, local_vars)

        # Return captured output
        output = sys.stdout.getvalue()
        return jsonify({"output": output})

    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": tb
        }), 500

    finally:
        sys.stdout = original_stdout

if __name__ == "__main__":
    app.run(debug=True)
