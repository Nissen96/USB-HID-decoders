tshark -r capture.pcapng -T fields -e usbhid.data -Y 'usb.src == "3.14.3"'
