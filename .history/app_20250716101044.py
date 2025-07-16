from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import base64
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route('/run', methods=['POST'])
def run_code():
    try:
        # Expect base64-encoded Python code in request
        encoded_code = request.json.get("code", "")
        decoded_bytes = base64.b64decode(encoded_code)
        code = decoded_bytes.decode('utf-8')

        logging.debug("Received decoded code:\n" + code[:500] + '...')

        local_vars = {}
        output_stream = io.StringIO()

        with contextlib.redirect_stdout(output_stream):
            exec(code, {}, local_vars)

            # Try to capture the 'result' variable
            result_value = local_vars.get('result', '')

        output = output_stream.getvalue().strip()

        return jsonify({
            "result": str(result_value),
            "stdout": output,
            "success": True
        })

    except Exception as e:
        logging.error("Execution failed:")
        logging.error(traceback.format_exc())
        return jsonify({
            "error": "Execution error",
            "message": str(e),
            "success": False,
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)