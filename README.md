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

Visualizes mouse movement and/or button presses.
By default draws all movement to a canvas but moves and clicks can optionally be animated, which is useful for stepping through e.g. screen keyboard presses.

```
usage: mouse_decode.py [-h] [-a] [-d s] [-c] [-m 0-2] file

Decode USB Mouse HID data

positional arguments:
  file                mouse data file

options:
  -h, --help          show this help message and exit
  -a, --animate       animate mouse movement
  -d s, --delay s     animation delay in seconds after each click (default: 2)
  -c, --clicks        show mouse clicks explicitly
  -m 0-2, --mode 0-2  display mode for mouse movement, from less to more verbose [0-2] (default: 1)
                        0: don't show mouse movement (use with -c for clicks only)
                        1: show mouse movement when any mouse button is held
                        2: show all mouse movement
```

Colors indicate the mouse button(s) pressed when clicking/dragging. Gray is used for movement with no buttons held.

**Examples**

Display drawing made with mouse:

```
python mouse_decode.py <mousedata-file>
```

Visualize screen keyboard usage:

```
python mouse_decode.py <mousedata-file> --mode 0 --clicks --animate
```
(optionally mode 2 can be used to see movements in between clicks).





## Tablet

TODO
