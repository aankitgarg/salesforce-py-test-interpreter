from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code_b64 = data.get("code_b64", "")
        code = base64.b64decode(code_b64).decode('utf-8')

        local_vars = {}
        output_stream = io.StringIO()

        logging.debug("Decoded code received.")
        logging.debug(f"Code snippet:\n{code[:500]}...")

        with contextlib.redirect_stdout(output_stream):
            try:
                exec(code, {}, local_vars)
                lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
                last_line = lines[-1] if lines else ""

                if last_line and not last_line.startswith("print") and "=" not in last_line:
                    try:
                        result = eval(last_line, {}, local_vars)
                        if result is not None:
                            print(result)
                    except Exception as eval_error:
                        logging.debug(f"Could not evaluate last line: {eval_error}")
            except Exception as exec_error:
                logging.error(f"Execution error: {exec_error}")
                raise

        output = output_stream.getvalue().strip()
        logging.debug(f"Execution output:\n{output[:500]}")  # Log up to 500 characters

        return jsonify({"result": output})

    except Exception as e:
        logging.error(f"Unhandled exception:\n{traceback.format_exc()}")
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500