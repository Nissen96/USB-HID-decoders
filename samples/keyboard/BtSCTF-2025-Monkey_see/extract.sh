tshark -r capture.pcapng -T fields -e usbhid.data -Y 'usb.src == "1.9.1"'
