tshark -r capture.btsnoop -Y "btatt.handle == 0x2c" -T fields -e "btatt.value" | grep -v "^$" | sed -e "s/\(.*\)/00\0/"
