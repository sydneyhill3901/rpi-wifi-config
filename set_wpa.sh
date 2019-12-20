#!/bin/bash

# load wan configuration
cp wpa.conf /etc/wpa_supplicant/wpa_supplicant.conf

systemctl restart dhcpcd

sleep 5

dhclient wlan0