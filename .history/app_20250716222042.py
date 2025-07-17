from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging
import base64
import numpy as np

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

# Utility to safely convert numpy types to native Python types
def convert_to_builtin_type(obj):
    if isinstance(obj, dict):
        return {k: convert_to_builtin_type(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_builtin_type(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return obj

@app.route('/run', methods=['POST'])
def run_code():
    try:
        encoded = request.json.get("code", "")
        code = base64.b64decode(encoded).decode("utf-8")
        local_vars = {}
        output_stream = io.StringIO()

        logging.debug("Received base64-encoded code.")
        logging.debug(f"Decoded code snippet:\n{code[:500]}...")

        with contextlib.redirect_stdout(output_stream):
            exec(code, {}, local_vars)

            # Auto-eval last line if it's a valid expression
            lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
            last_line = lines[-1] if lines else ""
            if (
                last_line and
                not last_line.startswith(('import', 'def', 'for', 'if', 'while', 'class', 'with', 'print')) and
                '=' not in last_line
            ):
                try:
                    result = eval(last_line, {}, local_vars)
                    if result is not None:
                        print(result)
                except Exception as eval_error:
                    logging.debug(f"Skipped eval on last line: {eval_error}")

        # Collect output or final result
        output = output_stream.getvalue().strip()
        logging.debug(f"Execution output:\n{output[:500]}...")

        result = local_vars.get("result", output)
        cleaned_result = convert_to_builtin_type(result)

        return jsonify({"result": cleaned_result})

    except Exception as e:
        logging.error("Execution failed:")
        logging.error(traceback.format_exc())
        error_message = {
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        return jsonify(error_message), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)