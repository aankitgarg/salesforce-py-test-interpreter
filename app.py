from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging

app = Flask(__name__)

# Set up debug logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                logging.debug("Attempting eval of code...")
                result = eval(code, {}, local_vars)
                if result is not None:
                    print(result)
            except SyntaxError:
                logging.debug("SyntaxError during eval, trying exec...")
                exec(code, {}, local_vars)

                # Attempt to auto-print the result of the last line if it's a variable
                lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
                last_line = lines[-1] if lines else ""

                # Auto-print the value of the last variable if it exists and is not a print or assignment
                if last_line and not last_line.startswith("print") and "=" not in last_line:
                    if last_line in local_vars:
                        try:
                            print(local_vars[last_line])
                        except Exception as eval_error:
                            logging.debug(f"Could not print variable '{last_line}': {eval_error}")
            except Exception as e:
                logging.exception("Exception during eval block:")
                print(f"Error during eval: {str(e)}")

        output = output_stream.getvalue().strip()
        logging.debug(f"Execution output: {output}")
        return jsonify({"result": output})

    except Exception as e:
        logging.exception("Exception during run_code:")
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
