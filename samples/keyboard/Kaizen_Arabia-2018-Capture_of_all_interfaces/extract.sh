tshark -r capture.pcapng -T fields -e usbhid.data -Y 'usb.src == "2.6.1"'
