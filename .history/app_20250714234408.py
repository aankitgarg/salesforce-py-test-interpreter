from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging

app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    logging.debug("Received code.")
    logging.debug(f"Code snippet:\n{code[:500]}...")  # Log beginning of code

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                stripped_code = code.strip()

                # Case 1: Single-line expression (like "6 + 6")
                if '\n' not in stripped_code and '=' not in stripped_code and not stripped_code.startswith('print'):
                    result = eval(stripped_code, {}, local_vars)
                    if result is not None:
                        print(result)

                # Case 2: Multi-line code
                else:
                    exec(stripped_code, {}, local_vars)
                    lines = [line.strip() for line in stripped_code.splitlines() if line.strip()]
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
        logging.debug(f"Execution output:\n{output[:500]}")  # Log output start
        return jsonify({"result": output})

    except Exception as e:
        error_details = {
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        logging.error(f"Unhandled exception:\n{traceback.format_exc()}")
        return jsonify(error_details), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
