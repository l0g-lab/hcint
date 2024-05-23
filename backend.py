# backend.py

from flask import Flask, render_template, request
import subprocess
import time

MD5_CODE=0
NTLMV1_CODE=5500
NTLMV1NT_CODE=27000
NTLMV2_CODE=5600
NTLMV2NT_CODE=27100

hc_version = subprocess.run(['hashcat', '--version'], capture_output=True, text=True).stdout

app = Flask(__name__,template_folder='templates', static_folder='static')

@app.route('/submit', methods=['POST'])
def submit_form():
    # Run Hashcat command
    #proc = subprocess.run(['hashcat', '-m', REQUIRED_HASH_CODE, HASH_TO_BE_CRACKED], shell=True, stdout=subprocess.PIPE, text=True)

    # Dummy scipt to emulate command output
    proc = subprocess.Popen(['cat /var/log/README'], shell=True, stdout=subprocess.PIPE, text=True)

    hc_output = ""
    for line in iter(proc.stdout.readline,''):
        time.sleep(0.1)
        #yield line.decode('utf8').rstrip() + '<br/>\n'
        hc_output += line + "<br/>\n"
    
    hash_value = request.form['hash_in']
    hash_type = request.form['hash_id']

    # Process the hash_value as needed
    return render_template('/index.html', hash_value=hash_value, hash_type=hash_type, hc_version=hc_version, hc_output=hc_output)

@app.route('/')
def index():
    # Generate base index page
    return render_template('index.html', hc_version=hc_version)

if __name__ == '__main__':
    app.run(debug=True)