tshark -r capture.pcap -T fields -e usb.capdata -Y 'usb.src == "4.5.1"'
