from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def calculator():
    if request.method == 'POST':
        num1 = float(request.form['num1'])
        num2 = float(request.form['num2'])
        operation = request.form['operation']
        if operation == 'add':
            result = num1 + num2
            operator = '+'
        elif operation == 'sub':
            result = num1 - num2
            operator = '-'
        elif operation == 'mult':
            result = num1 * num2
            operator = '*'
        elif operation == 'div':
            result = num1 / num2
            operator = '/'
        return render_template('calculator.html', result=result)
    else:
        return render_template('calculator.html')
    
@app.route('/', methods=['GET'])
def template():
    return render_template('calculator.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=50053)
