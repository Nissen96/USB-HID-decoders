tshark -r capture.btsnoop -Y "btatt.handle == 0x2c" -T fields -e "btatt.value"
