# backend.py

from flask import Flask, render_template, request
import subprocess

MD5_CODE=0
NTLMV1_CODE=5500
NTLMV1NT_CODE=27000
NTLMV2_CODE=5600
NTLMV2NT_CODE=27100

hc_version = subprocess.run(['hashcat', '--version'], capture_output=True, text=True).stdout

app = Flask(__name__,template_folder='templates', static_folder='static')

@app.route('/submit', methods=['POST'])
def submit_form():
    hash_value = request.form['hash']
    hash_type = request.form['hash_id']

    # Run Hashcat command
    # result = subprocess.run(['hashcat', '-m', REQUIRED_HASH_CODE 'file_to_crack'], capture_output=True, text=True)

    # Process the hash_value as needed
    return render_template('/index.html', hash_value=request.form['hash'], hash_type=request.form['hash_id'],hc_version=hc_version)

# Route to serve the HTML page
@app.route('/')
def index():
    # Generate base index.html 
    return render_template('index.html', hc_version=hc_version)

if __name__ == '__main__':
    app.run(debug=True)
