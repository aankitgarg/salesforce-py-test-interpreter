from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    logging.debug("Received code snippet:")
    logging.debug(code[:500] + '...')

    try:
        with contextlib.redirect_stdout(output_stream):
            stripped_code = code.strip()

            # ✅ Always use exec for multi-line or complex code
            exec(stripped_code, {}, local_vars)

            # Optionally: try to evaluate and print last expression
            lines = [line.strip() for line in stripped_code.splitlines() if line.strip()]
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

        output = output_stream.getvalue().strip()
        logging.debug("Execution output:")
        logging.debug(output[:500] + '...')
        return jsonify({"result": output})

    except Exception as e:
        logging.error("Execution failed:")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)