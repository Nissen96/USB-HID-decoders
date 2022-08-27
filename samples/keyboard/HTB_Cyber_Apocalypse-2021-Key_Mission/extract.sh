tshark -r capture.pcap -T fields -e usbhid.data -Y 'usb.src == "3.2.1"'
