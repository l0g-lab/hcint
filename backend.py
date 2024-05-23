# backend.py

from flask import Flask, render_template, request
import subprocess

app = Flask(__name__,template_folder='templates', static_folder='static')

@app.route('/submit', methods=['POST'])
def submit_form():
    hash_value = request.form['hash']
    hash_type = request.form['hash_id']
    # Process the hash_value as needed

    return "Received hash: " + hash_value + "<br>" + "Hash Type Set: " + hash_type

# Route to serve the HTML page
@app.route('/')
def index():
    # Run Hashcat command
    #result = subprocess.run(['hashcat', 'options', 'file_to_crack'], capture_output=True, text=True)
    result = subprocess.run(['hashcat', '--version'], capture_output=True, text=True)

    # Extract relevant output
    hashcat_output = result.stdout
    return render_template('index.html', hashcat_output=hashcat_output)

if __name__ == '__main__':
    app.run(debug=True)
