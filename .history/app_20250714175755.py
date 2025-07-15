from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    logging.info("Received code:\n%s", code)

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                # Attempt to evaluate one-liner expressions
                result = eval(code, {}, local_vars)
                if result is not None:
                    print(result)
            except SyntaxError:
                # Treat as full script block
                exec(code, {}, local_vars)

                # Try to evaluate last line if possible
                lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
                last_line = lines[-1] if lines else ""

                if last_line and not last_line.startswith("print") and "=" not in last_line:
                    try:
                        result = eval(last_line, {}, local_vars)
                        if result is not None:
                            print(result)
                    except Exception as inner_eval_error:
                        logging.debug("Ignored eval on last line: %s", inner_eval_error)

            except Exception as inner_exec_error:
                logging.error("Error during eval/exec: %s", inner_exec_error)
                print(f"Error during eval/exec: {str(inner_exec_error)}")

        output = output_stream.getvalue().strip()
        logging.info("Execution result:\n%s", output)
        return jsonify({"result": output})

    except Exception as outer_error:
        logging.exception("Unhandled exception in /run")
        return jsonify({
            "error": "Interpreter exception",
            "message": str(outer_error),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
