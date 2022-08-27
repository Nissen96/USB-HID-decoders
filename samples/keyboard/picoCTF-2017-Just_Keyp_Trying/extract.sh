tshark -r capture.pcap -T fields -e usb.capdata -Y 'usb.src == "2.1.1"'
