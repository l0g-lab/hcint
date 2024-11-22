#!/bin/env python3

from flask import Flask, render_template, request, Response, session, redirect, url_for
import subprocess
import time
import sys

app = Flask(__name__,template_folder='templates', static_folder='static')
app.secret_key = b'thisisatest'

# hashcat hash type codes
hash_types = {
        'MD5': 0,
        'NTLMV1' : 5500,
        'NTLMV1NT' : 27000,
        'NTLMV2' : 5600,
        'NTLMV2NT' : 27100
}

def is_hashcat_installed(package_name):
    # check if hashcat is installed
    try:
        result = subprocess.run(['which', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking package: {e}")
        return False

def generate(hash_type: str, hash_value: str):

    # run hashcat with user submitted values
    proc = subprocess.Popen(['hashcat', '-m', hash_type, hash_value], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    hc_pid = proc.pid

    # iterate through each line of output from hashcat command
    for line in iter(proc.stdout.readline,''):
        yield f"data: {line.strip()}\n\n"
        time.sleep(0.05)

    # kill process
    proc.stdout.close()
    proc.wait()

@app.route('/submit', methods=['POST'])
def submit_form():

    # set variable so new <div> is created in index.html template
    route_hit = True

    # get hash information from HTML input form
    hash_type = str(hash_types.get(request.form['hash_type']))
    hash_value = request.form['hash_value']

    # set session variables so they can be used in other parts of the app
    session['hash_type'] = hash_type
    session['hash_value'] = hash_value

    # Process the hash_value as needed
    return render_template('/index.html', hash_type=hash_type, hash_value=hash_value, hc_version=hc_version, route_hit=route_hit)

@app.route('/stream')
def stream():

    # get session variables from /submit route
    hash_type = session.get('hash_type')
    hash_value = session.get('hash_value')

    if not hash_value or not hash_type:
        return redirect(url_for('index'))

    # return response from generate() function
    try:
        return Response(generate(hash_type, hash_value), content_type='text/event-stream')
    except GenerateError as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    # Generate base index page
    return render_template('index.html', hc_version=hc_version)

if __name__ == '__main__':
    if not is_hashcat_installed('hashcat'):
        print("hashcat is not installed or not in your PATH. Please fix and re-run.")
        sys.exit(1)

    # set hashcat version
    hc_version = subprocess.run(['hashcat', '--version'], capture_output=True, text=True).stdout
    app.run(debug=True)
