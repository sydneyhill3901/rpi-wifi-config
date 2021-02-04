#!/bin/bash

# load wan configuration
cp /tmp/wpa.conf /etc/wpa_supplicant/wpa_supplicant.conf

wpa_cli -i wlan0 reconfigure