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

    try:
        with contextlib.redirect_stdout(output_stream):
            stripped_code = code.strip()

            # Use exec always for multiline code
            exec(stripped_code, {}, local_vars)

            # Attempt to evaluate final expression
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
                    logging.debug(f"Eval skipped: {eval_error}")

        output = output_stream.getvalue().strip()
        return jsonify({"result": output})

    except Exception as e:
        return jsonify({
            "error": "Execution error",
            "message": str(e),
            "success": False,
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)