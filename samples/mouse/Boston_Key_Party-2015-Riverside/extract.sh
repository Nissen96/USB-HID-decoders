tshark -r capture.pcapng -T fields -e usb.capdata -Y 'usb.src == "2.12.1"'
