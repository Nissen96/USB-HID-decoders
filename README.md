# USB HID Decoders

This repository contains decoders for various USB Human Interface Devices (HIDs).

## Keyboard

Converts keyboard scan codes to a human readable format.
Special keys are by default written out explicitly but can optionally be simulated.

```
usage: keyboard_decode.py [-h] [--simulate] file

Decode USB Keyboard HID data

positional arguments:
  file        keyboard data file

options:
  -h, --help  show this help message and exit
  --simulate  simulate keypresses
```

To extract keyboard data from a Wireshark dump, use
```
tshark -r <pcap-file> -T fields -e usbhid.data > keyboarddata.txt
```
or
```
tshark -r <pcap-file> -T fields -e usb.capdata > keyboarddata.txt
```
depending on the USB device. Optionally filter for a specific device with e.g.
```
-Y 'usb.src == "1.3.1"'
```

Key codes taken from https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

## Mouse

TODO

## Tablet

TODO
