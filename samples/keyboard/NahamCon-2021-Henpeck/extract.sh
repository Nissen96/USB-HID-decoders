tshark -r capture.pcap -T fields -e usb.capdata -Y 'usb.src == "1.9.1"'
