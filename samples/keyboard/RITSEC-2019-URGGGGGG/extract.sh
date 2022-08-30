tshark -r capture.pcapng -T fields -e usb.capdata -Y 'usb.src == "1.2.3"'
