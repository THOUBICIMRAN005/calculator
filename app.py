from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data['expression']
    
    try:
        # Replace common math functions and constants
        expression = expression.replace('^', '**')
        expression = expression.replace('π', 'math.pi')
        expression = expression.replace('e', 'math.e')
        
        # Handle trigonometric functions (convert degrees to radians)
        trig_functions = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan']
        for func in trig_functions:
            if f"{func}(" in expression:
                if func in ['asin', 'acos', 'atan']:
                    # Inverse trig functions return radians, we'll convert to degrees
                    expression = re.sub(fr"{func}\(([^)]+)\)", 
                                      f"math.degrees(math.{func}(\\1))", expression)
                else:
                    # Regular trig functions take radians, convert input from degrees
                    expression = re.sub(fr"{func}\(([^)]+)\)", 
                                      f"math.{func}(math.radians(\\1))", expression)
        
        # Handle logarithmic functions
        if 'log(' in expression:
            expression = re.sub(r"log\(([^,]+),\s*([^)]+)\)", r"math.log(\\1, \\2)", expression)
            expression = expression.replace('log(', 'math.log10(')
        
        if 'ln(' in expression:
            expression = expression.replace('ln(', 'math.log(')
        
        # Handle square roots and other functions
        expression = expression.replace('√(', 'math.sqrt(')
        expression = expression.replace('abs(', 'math.fabs(')
        expression = expression.replace('fact(', 'math.factorial(')
        
        # Evaluate the expression safely
        result = eval(expression, {'__builtins__': None}, {'math': math})
        
        return jsonify({'result': result, 'error': None})
    
    except Exception as e:
        return jsonify({'result': None, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)