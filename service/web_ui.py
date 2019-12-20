import subprocess
import re
import os

from flask import Flask, request, render_template, redirect
app = Flask(__name__, static_url_path='')

currentdir = os.path.dirname(os.path.abspath(__file__))
os.chdir(currentdir)

ssid_list = []
def getssid():
    global ssid_list
    if len(ssid_list) > 0:
        return ssid_list
    ssid_list = []
    get_ssid_list = subprocess.check_output(('iw', 'dev', 'wlan0', 'scan', 'ap-force'))
    ssids = get_ssid_list.splitlines()
    for s in ssids:
        s = s.strip().decode('utf-8')
        if s.startswith("SSID"):
            a = s.split(": ")
            try:
                ssid_list.append(a[1])
            except:
                pass
    print(ssid_list)
    ssid_list = sorted(list(set(ssid_list)))
    return ssid_list


def wificonnected():
    result = subprocess.check_output(['iwconfig', 'wlan0'])
    matches = re.findall(r'\"(.+?)\"', result.split(b'\n')[0].decode('utf-8'))
    if len(matches) > 0:
        return matches[0]
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

# Captive portal when connected with iOS or Android
@app.route('/generate_204')
def redirect204():
    return redirect("http://192.168.4.1", code=302)

@app.route('/hotspot-detect.html')
def applecaptive():
    return redirect("http://192.168.4.1", code=302)

# Not working for Windows, needs work!
@app.route('/ncsi.txt')
def windowscaptive():
    return redirect("http://192.168.4.1", code=302)

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

    with open('wpa.conf', 'w') as f:
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
    app.run(host="0.0.0.0", port=8888, threaded=True)
