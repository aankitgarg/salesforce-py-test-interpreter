from flask import Flask, request, jsonify
import io
import contextlib
import traceback

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    local_vars = {}
    output_stream = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                # Try to evaluate single-line expressions
                result = eval(code, {}, local_vars)
                if result is not None:
                    print(result)
            except SyntaxError:
                # Run as full block
                exec(code, {}, local_vars)

                # Try evaluating last line if it's an expression
                lines = [line.strip() for line in code.strip().splitlines() if line.strip()]
                last_line = lines[-1] if lines else ""

                # Don't try to eval if it's an assignment or a print statement
                if last_line and not last_line.startswith("print") and "=" not in last_line:
                    try:
                        result = eval(last_line, {}, local_vars)
                        if result is not None:
                            print(result)
                    except Exception:
                        pass
            except Exception as e:
                print(f"Error during eval: {str(e)}")

        output = output_stream.getvalue().strip()
        return jsonify({"result": output})

    except Exception as e:
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }),
