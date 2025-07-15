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
        # Split code into lines
        lines = code.strip().split("\n")
        if lines:
            *exec_lines, last_line = lines

            # Execute all lines except last
            exec("\n".join(exec_lines), {}, local_vars)

            # Try to eval the last line as an expression
            try:
                result = eval(last_line, {}, local_vars)
                if result is not None:
                    print(result)
            except:
                # If eval fails, treat as exec (e.g., if last line is print(...) or assignment)
                exec(last_line, {}, local_vars)
        else:
            exec(code, {}, local_vars)

        # Get all printed output
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
