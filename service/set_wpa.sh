#!/bin/bash

# load wan configuration
cp wpa.conf /etc/wpa_supplicant/wpa_supplicant.conf

wpa_cli -i wlan0 reconfigure