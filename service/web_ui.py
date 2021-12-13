import subprocess
import re
import os
import time

from flask import Flask, request, render_template, send_from_directory, redirect
app = Flask(__name__, static_url_path='')

PORT = 7000
SCAN_RETRIES = 10

currentdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdir)

ssid_list = []
def getssid():
    global ssid_list
    if len(ssid_list) > 0:
        return ssid_list
    ssid_list = []

    for i in range(SCAN_RETRIES):
        try:
            get_ssid_list = subprocess.check_output(('iw', 'dev', 'wlan0', 'scan', 'ap-force'))
            ssids = get_ssid_list.splitlines()
            break
        except subprocess.CalledProcessError as e:
            print(f"Error while trying to get WiFi list: {e}. Will retry (#{i})")
            time.sleep(1)

        if i == SCAN_RETRIES - 1:
            ssids = ['-- not available; please refresh --']
    
    for s in ssids:
        try:
            s = s.strip().decode('utf-8')
        except AttributeError:
            logger.error("Exception while trying to decode SSID scan output; leaving as is")

        if s.startswith("SSID"):
            a = s.split(": ")
            try:
                ssid_list.append(a[1])
            except:
                pass
    print(f"SSID list: {ssid_list}")
    ssid_list = sorted(list(set(ssid_list)))
    return ssid_list


def wificonnected():
    result = subprocess.check_output(['iwconfig', 'wlan0'])
    matches = re.findall(r'\"(.+?)\"', result.split(b'\n')[0].decode('utf-8'))
    ip_result = subprocess.check_output(['ifconfig', 'wlan0'])
    matchIP = re.findall('inet .{7,23}', ip_result.split(b'\n')[1].decode('utf-8'))
    ip = matchIP[0].replace('inet ', '')
    ip = ip[:ip.index(' ')]
    if len(matches) > 0:
        ip_string = str(matches[0]) + " with IP of " + str(ip)
        return ip_string
    else:
        return None


WPA_TEMPLATE = """country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="%s"
    %s
}"""


@app.route('/')
def main():
    current_network = wificonnected()
    if current_network:
        msg = f"Currently connected to '{current_network}' <br />Select new network if desired:"
    else:
        msg = "Welcome! Please select the WiFi network:"

    return render_template('index.html', ssids=getssid(), message=msg)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/connect', methods=['POST'])
def connect():
    ssid = request.form['ssid']
    password = request.form['password']

    pwd = 'psk="' + password + '"'
    if password == "":
        pwd = "key_mgmt=NONE" # If open AP

    print(f"Setting SSID {ssid}, password {password}")

    with open('/tmp/wpa.conf', 'w') as f:
        f.write(WPA_TEMPLATE % (ssid, pwd))
    subprocess.Popen(["./set_wpa.sh"])

    msg = f"Connecting to network '{ssid}'..."

    return render_template('connecting.html', ssids=getssid(), message=msg, redirect_interval=5, redirect_url='/connect')


@app.route('/connect', methods=['GET'])
def check_connection():

    current_network = wificonnected()
    if current_network:
        msg = f"Connected to '{current_network}'"
        sleep = 60
        redir_url = '/'
    else:
        msg = f"Connecting to network..."
        sleep = 5
        redir_url = '/connect'

    return render_template('connecting.html', ssids=getssid(), message=msg, redirect_interval=sleep, redirect_url=redir_url)


if __name__ == "__main__":
    print("Running access point web interface")
    app.run(host="0.0.0.0", port=PORT, threaded=True)
