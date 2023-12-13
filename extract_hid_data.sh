#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 <pcap-file>"
    exit 1
fi

tshark -r $1 -Y "usb.capdata || usbhid.data" -T fields -e usb.src -e usb.capdata -e usbhid.data |  # Extract usb.src, usb.capdata, and usbhid.data from all packets with HID data
sort -s -k1,1 |  # Sort on first field only (usb.src)
awk '{ printf "%s", (NR==1 ? $1 : pre!=$1 ? "\n" $1 : "") " " $2; pre=$1 }' |  # Group data by usb.src
awk '{ for (i=2; i<=NF; i++) print $i > "usbdata-" $1 ".txt" }'  # For each group, store data in usbdata-<usb.src>.txt
