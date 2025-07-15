from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    logging.debug("Received code:")
    logging.debug(code[:500] + '...')  # Limit log output for large code blocks

    try:
        with contextlib.redirect_stdout(output_stream):
            stripped_code = code.strip()

            # Determine if it's a simple expression or complex code
            is_single_expression = (
                '\n' not in stripped_code and
                not stripped_code.startswith(('import', 'def', 'for', 'if', 'while', 'class', 'with')) and
                '=' not in stripped_code
            )

            try:
                if is_single_expression:
                    # ✅ Safe to eval simple expressions like "6 + 6"
                    result = eval(stripped_code, {}, local_vars)
                    if result is not None:
                        print(result)
                else:
                    # ✅ For everything else (multi-line, import, def, etc.)
                    exec(stripped_code, {}, local_vars)

                    # Try to eval the last line if it's an expression
                    lines = [line.strip() for line in stripped_code.splitlines() if line.strip()]
                    last_line = lines[-1] if lines else ""

                    is_last_line_expression = (
                        last_line and
                        not last_line.startswith("print") and
                        not last_line.startswith(('import', 'def', 'for', 'if', 'while', 'class', 'with')) and
                        '=' not in last_line
                    )

                    if is_last_line_expression:
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
        logging.debug("Execution output:")
        logging.debug(output[:500] + '...')
        return jsonify({"result": output})

    except Exception as e:
        logging.error("Unhandled exception:")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)