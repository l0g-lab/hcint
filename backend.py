#!/bin/env python3

from flask import Flask, render_template, request, Response, session, redirect, url_for
import subprocess
import time
import sys
import requests
import os.path
from urllib.parse import urlparse

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

# hashcat attack modes
attack_modes = {
        'straight': 0
}

# wordlist URLs
wordlist_urls = {
    'rockyou-25.txt' : 'https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Leaked-Databases/rockyou-25.txt',
    'rockyou-50.txt' : 'https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Leaked-Databases/rockyou-50.txt',
    'rockyou-75.txt' : 'https://raw.githubusercontent.com/danielmiessler/SecLists/refs/heads/master/Passwords/Leaked-Databases/rockyou-75.txt'
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

def dl_wordlists(wordlist):

    # open requests to wordlist URL
    wl = requests.get(wordlist)

    # set filename
    wl_filename = os.path.basename(urlparse(wordlist).path)

    # write wordlist to file if not exist
    f = open(wl_filename, 'w')
    f.write(wl.text)

    # add wordlist to wordlist_urls dict
    wordlist_urls.update({wl_filename: wordlist})

    return wl.status_code

def generate(attack_mode: str, hash_type: str, hash_value: str, wordlist_used: str):

    # run hashcat with user submitted values
    proc = subprocess.Popen(['hashcat', '-a', attack_mode, '-m', hash_type, hash_value, wordlist_used, '--status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    hc_pid = proc.pid

    # iterate through each line of output from hashcat command
    for line in iter(proc.stdout.readline,''):
        yield f"data: {line.strip()}\n\n"
        time.sleep(0.05)

    # kill process
    proc.stdout.close()
    proc.wait()

@app.route('/downloadwl', methods=['POST'])
def downloadwl():

    # set variable for downloading wordlist
    wl_route_hit = True

    # get wordlist_used for conditional
    what_word = request.form['wordlist_used']

    # check if wordlist needed is from list or user supplied
    if what_word != 'url-input':
        wl = wordlist_urls.get(what_word)
    else:
        wl = request.form.get('wordlist_url')

    # download wordlist
    dl_status = dl_wordlists(wl)

    return render_template('/index.html',
                            hc_version=hc_version,
                            wl_route_hit=wl_route_hit,
                            dl_status=dl_status,
                            wordlist_urls=wordlist_urls
                            )

@app.route('/submit', methods=['POST'])
def submit_form():

    # set variable so new <div> is created in index.html template
    route_hit = True

    # get hashcat attack mode
    attack_mode = str(attack_modes.get(request.form['attack_mode']))

    # get hash information from HTML input form
    hash_type = str(hash_types.get(request.form['hash_type']))
    hash_value = request.form['hash_value']

    # get wordlist selection from HTML input form
    wordlist_url = str(wordlist_urls.get(request.form['wordlist_used']))
    wordlist_used = next((key for key, value in wordlist_urls.items() if value == wordlist_url), None)

    # set session variables so they can be used in other parts of the app
    session['attack_mode'] = attack_mode
    session['hash_type'] = hash_type
    session['hash_value'] = hash_value
    session['wordlist_used'] = wordlist_used

    # Process the hash_value as needed
    return render_template('/index.html',
                            attack_mode=attack_mode,
                            hash_type=hash_type,
                            hash_value=hash_value,
                            hc_version=hc_version,
                            route_hit=route_hit,
                            wordlist_urls=wordlist_urls
                            )

@app.route('/stream')
def stream():

    # get session variables from /submit route
    hash_type = session.get('hash_type')
    hash_value = session.get('hash_value')
    attack_mode = session.get('attack_mode')
    wordlist_used = session.get('wordlist_used')

    if not hash_value or not hash_type:
        return redirect(url_for('index'))

    # return response from generate() function
    try:
        return Response(generate(attack_mode, hash_type, hash_value, wordlist_used), content_type='text/event-stream')
    except GenerateError as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    # Generate base index page
    return render_template('index.html', hc_version=hc_version, wordlist_urls=wordlist_urls)

if __name__ == '__main__':
    if not is_hashcat_installed('hashcat'):
        print("hashcat is not installed or not in your PATH. Please fix and re-run.")
        sys.exit(1)

    # set hashcat version
    hc_version = subprocess.run(['hashcat', '--version'], capture_output=True, text=True).stdout

    app.run(host="0.0.0.0",debug=True)
