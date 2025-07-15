from flask import Flask, request, jsonify
import io
import contextlib
import traceback
import logging
import base64
import signal
import sys
from functools import wraps

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

def with_timeout(seconds=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
        return wrapper
    return decorator

def is_simple_expression(code):
    """
    Determine if code is a simple expression that can be evaluated with eval()
    This is very conservative - only simple arithmetic and function calls
    """
    lines = [line.strip() for line in code.splitlines() if line.strip()]
    
    # Must be exactly one line
    if len(lines) != 1:
        return False
    
    line = lines[0]
    
    # Exclude anything that looks like a statement or complex operation
    exclude_keywords = [
        'import', 'from', 'def', 'class', 'for', 'while', 'if', 'try', 'with',
        'print', 'json', 'pandas', 'pd.', 'DataFrame', 'loads', 'dumps',
        'current_expenses', 'related_expenses', '=', ':', '#'
    ]
    
    # Check for excluded keywords
    for keyword in exclude_keywords:
        if keyword in line:
            return False
    
    # Must be short and simple
    if len(line) > 50:
        return False
    
    # Check for complex patterns
    if any(char in line for char in ['[', '{', '"', "'"]):
        # Allow simple list/dict access but not complex structures
        if line.count('[') > 1 or line.count('{') > 1 or line.count('"') > 2:
            return False
    
    return True

@app.route('/run', methods=['POST'])
@with_timeout(120)  # Increased timeout for complex analysis
def run_code():
    try:
        # Handle both base64 and plain text
        code_b64 = request.json.get("code_b64", "")
        code = request.json.get("code", "")
        
        if code_b64:
            try:
                code = base64.b64decode(code_b64).decode('utf-8')
            except Exception as decode_error:
                logging.error(f"Base64 decode error: {decode_error}")
                return jsonify({
                    "error": "Base64 decode error",
                    "message": str(decode_error)
                }), 400
        
        if not code:
            return jsonify({"error": "No code provided"}), 400
        
        # Clean up the code
        stripped_code = code.strip()
        
        # Log code information
        logging.debug(f"Received code length: {len(stripped_code)} characters")
        logging.debug(f"Number of lines: {len(stripped_code.splitlines())}")
        logging.debug(f"Code preview: {stripped_code[:500]}...")
        
        # Set up execution environment
        local_vars = {}
        global_vars = {'__builtins__': __builtins__}
        output_stream = io.StringIO()
        
        with contextlib.redirect_stdout(output_stream):
            # ALWAYS use exec() for generated code unless it's obviously simple
            if is_simple_expression(stripped_code):
                logging.debug("Executing as simple expression with eval()")
                try:
                    result = eval(stripped_code, global_vars, local_vars)
                    if result is not None:
                        print(result)
                except Exception as eval_error:
                    logging.debug(f"eval() failed, falling back to exec(): {eval_error}")
                    exec(stripped_code, global_vars, local_vars)
            else:
                logging.debug("Executing as code block with exec()")
                exec(stripped_code, global_vars, local_vars)
        
        output = output_stream.getvalue().strip()
        
        # Log execution results
        logging.debug(f"Execution completed successfully")
        logging.debug(f"Output length: {len(output)} characters")
        logging.debug(f"Output preview: {output[:300]}...")
        
        return jsonify({
            "result": output,
            "success": True,
            "code_length": len(stripped_code),
            "output_length": len(output)
        })
        
    except TimeoutError:
        logging.error("Code execution timed out")
        return jsonify({
            "error": "Execution timeout",
            "message": "Code execution exceeded time limit",
            "success": False
        }), 408
        
    except SyntaxError as e:
        logging.error(f"Syntax error in code: {e}")
        return jsonify({
            "error": "Syntax error",
            "message": f"Syntax error in provided code: {str(e)}",
            "line_number": getattr(e, 'lineno', None),
            "success": False
        }), 400
        
    except Exception as e:
        logging.error(f"Execution error: {traceback.format_exc()}")
        return jsonify({
            "error": "Execution error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "success": False
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "python-interpreter",
        "version": "2.0"
    })

@app.route('/test', methods=['POST'])
def test_endpoint():
    """Test endpoint to verify the service is working"""
    try:
        test_code = request.json.get("code", "print('Hello from Python service!')")
        
        output_stream = io.StringIO()
        with contextlib.redirect_stdout(output_stream):
            exec(test_code, {}, {})
        
        output = output_stream.getvalue().strip()
        
        return jsonify({
            "result": output,
            "success": True,
            "message": "Test successful"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Test failed",
            "message": str(e),
            "success": False
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)