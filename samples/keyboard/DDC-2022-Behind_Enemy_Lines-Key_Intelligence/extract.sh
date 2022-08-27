tshark -r capture.pcap -T fields -e usbhid.data -Y 'usb.src == "1.2.1"'
