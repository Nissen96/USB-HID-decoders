# USB HID Decoders

This repository contains decoders and visualizers for various USB Human Interface Devices (HIDs).

HID specification: https://www.usb.org/sites/default/files/hid1_11.pdf

Currently supports keyboard and mouse data.


## Installation

Clone repo
```
git clone https://github.com/Nissen96/USB-HID-decoders.git
cd USB-HID-decoders
```

Install dependencies in a virtual environment with `pipenv` (`pip install pipenv`)
```
pipenv install
```

Run script(s) within virtual environment
```
pipenv run python <script-name> <script-args>
```

Alternatively, install dependencies in the current environment and run scripts with
```
pip install -r requirements.txt
python <script-name> <script-args>
```


## Usage

### Keyboard

Converts keyboard scan codes to a human readable format.

Special keys are by default written out explicitly but can optionally be simulated with `--simulate`.

Key codes taken from https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

### Mouse

Visualizes mouse movement. Button presses can be shown explicitly with `--clicks`.

**Modes**

- 0: Don't show any mouse movement (use with `--clicks` for clicks only)
- 1: Show mouse movement only while any mouse button is held
- 2: Show all mouse movements

Moves and clicks can optionally be animated with `--animate` (by default all movements are showed statically at once).

Colors indicate the mouse button(s) pressed when clicking/moving. Movement while no buttons are held is colored gray (in mode 2).

**Examples**

Display drawing/text made with mouse:

```
python mouse_decode.py <mousedata-file>
```

Visualize screen keyboard usage:

```
python mouse_decode.py <mousedata-file> --mode 0 --clicks --animate
```
(optionally mode 2 can be used to see movements in between clicks).


## PCAP Extraction

Extract USB HID data from a packet capture with
```
tshark -r <pcap-file> -T fields -e usbhid.data > usbdata.txt
```
or
```
tshark -r <pcap-file> -T fields -e usb.capdata > usbdata.txt
```
depending on the USB device (if in doubt, try both).

Get data from a specific device by adding a filter for its address/interface, e.g.
```
-Y 'usb.src == "1.3.1"'
```
Important if capture contains data from multiple USB devices.
