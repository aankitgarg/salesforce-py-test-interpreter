from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import re

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                # Try evaluating if it's a single-line expression
                result = eval(code, {}, local_vars)
                if result is not None:
                    print(result)
            except SyntaxError:
                # Multi-line code: run it
                exec(code, {}, local_vars)

                # Detect last line
                lines = code.strip().splitlines()
                last_line = lines[-1].strip() if lines else ""

                # 1. If last line is an expression (not print or assignment), try to eval
                if last_line and not last_line.startswith("print") and "=" not in last_line:
                    try:
                        result = eval(last_line, {}, local_vars)
                        if result is not None:
                            print(result)
                    except:
                        pass

                # 2. If last line is an assignment, print that variable
                assign_match = re.match(r"^(\w+)\s*=", last_line)
                if assign_match:
                    var_name = assign_match.group(1)
                    if var_name in local_vars:
                        print(local_vars[var_name])

            except Exception as e:
                print(f"Error during eval: {str(e)}")

        output = output_stream.getvalue().strip()
        return jsonify({"result": output})

    except Exception as e:
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 400

@app.route('/')
def home():
    return "Python Interpreter is running."
