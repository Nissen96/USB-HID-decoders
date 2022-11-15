tshark -r capture.pcap -Y "btatt.value && frame.len == 20" -T fields -e "btatt.value"
