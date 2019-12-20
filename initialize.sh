#!/bin/bash

set -e

export SSID="rpi-wifi-config"
export PSK="1234567890"
export HOSTAP_IP=192.168.4.1
export HOSTAP_NETMASK=255.255.255.0
export HOSTAP_DHCP_START=192.168.4.2
export HOSTAP_DHCP_END=192.168.4.20

echo ===
echo === Installing packages
echo ===

sudo apt-get install -y dnsmasq hostapd python3-flask
sudo systemctl stop dnsmasq && sudo systemctl stop hostapd

echo
echo ===
echo === Setting configuration files
echo ===

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig

echo "interface=lo,uap0
no-dhcp-interface=lo,wlan0
dhcp-range=$HOSTAP_DHCP_START,$HOSTAP_DHCP_END,24h" | sudo tee /etc/dnsmasq.conf


echo 'ACTION=="add", SUBSYSTEM=="ieee80211", KERNEL=="phy0", \
    RUN+="/sbin/iw phy %k interface add uap0 type __ap"' | sudo tee /etc/udev/rules.d/90-wireless.rules


echo 'if [ -z "$wpa_supplicant_conf" ]; then
	for x in \
		/etc/wpa_supplicant/wpa_supplicant-"$interface".conf \
		/etc/wpa_supplicant/wpa_supplicant.conf \
		/etc/wpa_supplicant-"$interface".conf \
		/etc/wpa_supplicant.conf \
	; do
		if [ -s "$x" ]; then
			wpa_supplicant_conf="$x"
			break
		fi
	done
fi
: ${wpa_supplicant_conf:=/etc/wpa_supplicant.conf}

if [ "$ifwireless" = "1" ] && \
    type wpa_supplicant >/dev/null 2>&1 && \
    type wpa_cli >/dev/null 2>&1
then
    case "$reason" in
        PREINIT)        wpa_supplicant_start;;
        RECONFIGURE)    wpa_supplicant_reconfigure;;
        DEPARTED)       wpa_supplicant_stop;;
        IPV4LL)         wpa_supplicant -B -iwlan0 -f/var/log/wpa_supplicant.log -c/etc/wpa_supplicant/wpa_supplicant.conf;;
    esac
fi
' | sudo tee /lib/dhcpcd/dhcpcd-hooks/10-wpa_supplicant


echo 'country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
network={
    ssid="sample"
    psk="sample123"
}
' | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf


sudo systemctl daemon-reload
sudo systemctl restart dhcpcd


echo "allow-hotplug uap0
auto uap0
iface uap0 inet static
    address $HOSTAP_IP
    netmask $HOSTAP_NETMASK" | sudo tee /etc/network/interfaces.d/ap


echo "interface=uap0
ssid=$SSID
hw_mode=g
channel=6
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=$PSK
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP" | sudo tee /etc/hostapd/hostapd.conf

echo 'DAEMON_CONF="/etc/hostapd/hostapd.conf"' | sudo tee --append /etc/default/hostapd

echo 
echo ===
echo === Starting access point
echo ===

sudo systemctl unmask hostapd
sudo systemctl enable hostapd

sudo systemctl daemon-reload

sudo systemctl start hostapd && sudo systemctl start dnsmasq

echo
echo ===
echo === Setting up Web UI service
echo ===

sudo cp -r ./service /opt/rpi-wifi-config-service
sudo cp rpi-wifi-config.service /etc/systemd/system/
sudo chmod 644 /etc/systemd/system/rpi-wifi-config.service
sudo systemctl enable rpi-wifi-config.service

echo
echo === DONE
echo
echo Please reboot.