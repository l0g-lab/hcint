# backend.py

from flask import Flask, render_template, request, Response, session, redirect, url_for
import subprocess
import time

MD5_CODE=0
NTLMV1_CODE=5500
NTLMV1NT_CODE=27000
NTLMV2_CODE=5600
NTLMV2NT_CODE=27100

hc_version = subprocess.run(['hashcat', '--version'], capture_output=True, text=True).stdout

app = Flask(__name__,template_folder='templates', static_folder='static')
app.secret_key = b'thisisatest'

def generate(hash_type: str, hash_value: str):

    # Dummy scipt to emulate command output
    proc = subprocess.Popen(['ls', '-lah'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # proc = subprocess.run(['hashcat', '-m', REQUIRED_HASH_CODE, HASH_TO_BE_CRACKED], shell=True, stdout=subprocess.PIPE, text=True)

    for line in iter(proc.stdout.readline,''):
        yield f"data: {line.strip()}\n\n"
        time.sleep(0.5)
    proc.stdout.close()
    proc.wait()

@app.route('/submit', methods=['POST'])
def submit_form():

    route_hit = True

    hash_type = request.form['hash_type']
    hash_value = request.form['hash_value']

    session['hash_type'] = hash_type
    session['hash_value'] = hash_value

    # Process the hash_value as needed
    return render_template('/index.html', hash_type=hash_type, hash_value=hash_value, hc_version=hc_version, route_hit=route_hit)

@app.route('/stream')
def stream():
    hash_type = session.get('hash_type')
    print(hash_type)
    hash_value = session.get('hash_value')
    print(hash_value)

    if not hash_value or not hash_type:
        return redirect(url_for('index'))

    return Response(generate(hash_type, hash_value), content_type='text/event-stream')

@app.route('/')
def index():
    # Generate base index page
    return render_template('index.html', hc_version=hc_version)

if __name__ == '__main__':
    app.run(debug=True)
