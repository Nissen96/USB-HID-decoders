tshark -r capture.pcapng -Y 'btl2cap.payload && usb.src == "1.3.2"' -T fields -e btl2cap.payload
