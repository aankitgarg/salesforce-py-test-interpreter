from flask import Flask, request, jsonify
import io
import contextlib
import traceback

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    code = request.json.get("code", "")
    
    # Use an isolated namespace
    local_vars = {}
    output_stream = io.StringIO()

    try:
        with contextlib.redirect_stdout(output_stream):
            try:
                # First try: evaluate as a single expression
                result = eval(code, {}, local_vars)
                if result is not None:
                    print(result)
            except SyntaxError:
                # Fallback: exec full code block
                exec(code, {}, local_vars)

                # Attempt to evaluate last line of code if it's an expression
                lines = code.strip().splitlines()
                last_line = lines[-1] if lines else ""
                try:
                    result = eval(last_line, {}, local_vars)
                    if result is not None:
                        print(result)
                except:
                    pass  # Ignore if last line can't be evaluated
            except Exception as e:
                print(f"Error during eval: {str(e)}")
        
        output = output_stream.getvalue().strip()
        return jsonify({"result": output})

    except Exception as e:
        return jsonify({
            "error": "Interpreter exception",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 400


if __name__ == '__main__':
    app.run(debug=True)