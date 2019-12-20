# Raspberry Pi WiFi Configuration via Web interface

This is loosely based on https://github.com/schollz/raspberry-pi-turnkey, but in reality works quite differently.

An access point is set up on wireless interface uap0, which is always on. When this is accessed, the user can select which of the available WiFi networks the Raspberry Pi connects to. Once selected, the new network is joined without a reboot. The connection is confirmed in the web interface of the access point.

## Installation
Run the initialize.sh script. You will need sudo rights. This will install required packages, set up the configuration files, and install a systemd service `rpi-wifi-config` which provides the web UI.

## Access
The default hotspot SSID is `rpi-wifi-config` and the default password is `1234567890`.

Once connected, the Web UI is available on port 7000, and the default IP address is 192.168.4.1. I.e. http://192.168.4.1:7000/

## Configuration
The SSID, key, and IP address of the Access Point are set at the top of the initialize.sh script.

The port for the Web UI is set near the top of the web_ui.py script.

## Compatibility
This has been tested on Raspbian Buster running on a Raspberry Pi 4.