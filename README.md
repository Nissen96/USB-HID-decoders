# USB HID Decoders

This repository contains decoders and visualizers for various USB Human Interface Devices (HIDs).

HID specification: https://www.usb.org/sites/default/files/hid1_11.pdf

Currently supports keyboard, mouse, and tablet data but ignores pressure information for tablets.

A utility Python and bash script has been included to extract HID data from a PCAP file.


## Installation

Simply clone the repo and run any included script:

```bash
git clone https://github.com/Nissen96/USB-HID-decoders.git
cd USB-HID-decoders
```

Optionally install dependencies from requirements file:

```bash
pip install -r requirements.txt
```

- `matplotlib` is used by mouse and tablet scripts for drawing and not required for keyboard decoding.
- `scapy` is only used by `extract_hid_data.py` to load and parse PCAP files (optionally, use the bash script).
- `keyboard` is optional but needed for `replay` mode in the keyboard decoder and to use keyboard commands while running the mouse or tablet decoder.

Note, on Linux you can only use the `keyboard` library as root.

## Usage

### Keyboard

Converts keyboard scan codes to a human readable format

```bash
python keyboard_decode.py <usbdata.txt> [options]
```

Key codes taken from https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

**Modes**

- `raw`: Output each keypress (with modifiers) explicitly on a separate line.
- `simulate`: Simulate the keypresses as if written in a text editor with a US-keyboard.
- `replay`: Replay keypresses on the actual machine in the current window (unsafe!).

`simulate` mode is default and will likely produce the expected output. It handles most scan codes and `Shift`.
Key combos (e.g. `<Ctrl+c>`, `<Alt+TAB>`, `<Shift+LEFT>`) and some special keys (e.g. `<ESC>`) are not simulated, but written explicitly.

A simulation environment can be set with `--env` (`txt` or `cmd`).
In text mode (default), a multiline text editor is assumed and e.g. all arrow key presses interpreted as cursor movement.
`<ENTER>` will insert a line break at the cursor position.
In command mode, a single-line interactive environment (terminal, browser, etc.) is assumed, where keys like `<TAB>`, `<ENTER>`, `<UP>`, and `<DOWN>` are considered action keys.
`<ENTER>` starts a new line, and other actions are written out explicitly.

If the capture is from a non-US keyboard layout, the simulation may produce partially incorrect results.

Optionally, use `replay` mode to actually replay keypresses.
Be careful if using this mode on unknown/untrusted input, it will type whatever was typed during the capture, including any commands, shortcuts, etc.
Make sure to first inspect the output from the raw and simulated modes. Press `q` at any time during replay to stop.

In case anything important was written and then deleted during the capture, use `raw` or `replay` since `simulate` will simulate the deletions as well and provide only a final output.

Note: `raw` mode and `replay` mode are the most accurate (assuming you set the right keyboard layout and are in the right environment) but in `replay` mode, `<Shift+ArrowKey>` does not select text on Windows 10. This is a known bug in the underlying keybord library. As a workaround, the program will stop and wait for you to perform those keypresses manually.

**Other options**

The captured data might be prefixed with a few identical bytes, use `--offset` to specify the offset of the actual keyboard data in each line.

Normally, a scanline contains a modifier, then a reserved null byte followed by up to 6 keycodes.
Rarely, the reserved byte is not present, use `--no-reserved` to skip this.

### Mouse

Visualizes mouse movement

```bash
python mouse_decode.py <usbdata.txt> [options]
```

Button presses can be shown explicitly with `--clicks`.

**Modes**

- 0: Don't show any mouse movement (use with `--clicks` for clicks only)
- 1: Show mouse movement only while any mouse button is held
- 2: Show all mouse movements

Colors indicate the mouse button(s) pressed when clicking/moving.
Movement while no buttons are held is colored gray in mode 2.

**Other options**

Moves and clicks can be animated by setting `--speed [1-10]`.

The captured data might be prefixed with a few identical bytes, use `--offset` to specify the offset of the actual mouse data in each line.

Each data line has a field to indicate mousedown, x displacement, and y displacement.
These are little endian and may have different bit lengths (8, 12, or 16).
This can be set with `-b / --bit-lengths`, e.g. `-b 8 12 12`.

**Keyboard commands**

Pause/resume animation with `<SPACE>` and clear the screen with `c`. Quit at any time by pressing `q`.
These options are especially helpful for visualizing screen keyboard usage or when drawing/writing with the mouse in the same spot multiple times.

Note: Keyboard commands require the `keyboard library`.

### Tablet

Visualizes pen drawing on tablet.

```bash
python tablet_decode.py <usbdata.txt> [options]
```

**Modes**

- 1: Show pen movement only on pen click
- 2: Show all pen movements

Color indicates drawing while holding pen button. Pen movement with no buttons held is colored gray (in mode 2).

**Other options**

Animate drawing by setting `--speed [1-10]`.

The captured data might be prefixed with a few identical bytes, use `--offset` to specify the offset of the actual tablet data in each line.

**Keyboard commands**

Pause/resume animation with `<SPACE>` and clear the screen with `c`. Quit at any time by pressing `q`.

Note: Keyboard commands require the `keyboard library`.

## PCAP Extraction

The script `extract_hid_data.py` can be used to extract the USB HID data from a PCAP with the library `scapy`.

Alternatively, the bash script `extract_hid_data.sh` can be used, which extracts the data with `tshark`.

**Explanation**

USB HID data can be extracted from a packet capture with `tshark`, the CLI of Wireshark.
In Wireshark, the relevant data is stored in the field `usb.capdata` (Leftover Capture Data) or `usbhid.data` (HID Data).
Extract with

```bash
tshark -r <pcap-file> -Y 'usbhid.data' -T fields -e usbhid.data > usbdata.txt
```

or

```bash
tshark -r <pcap-file> -Y 'usb.capdata' -T fields -e usb.capdata > usbdata.txt
```

Get data from a specific device by adding a filter for its address, e.g.

```bash
-Y 'usb.src == "1.3.1"'
```

The bash script is a one-liner to extract HID data from all USB devices and store in separate files, named after device address:

```bash
tshark -r <pcap-file> -Y "usb.capdata || usbhid.data" -T fields -e usb.src -e usb.capdata -e usbhid.data |  # Extract usb.src, usb.capdata, and usbhid.data from all packets with HID data
sort -s -k1,1 |  # Sort on first field only (usb.src)
awk '{ printf "%s", (NR==1 ? $1 : pre!=$1 ? "\n" $1 : "") " " $2; pre=$1 }' |  # Group data by usb.src
awk '{ for (i=2; i<=NF; i++) print $i > "usbdata-" $1 ".txt" }'  # For each group, store data in usbdata-<usb.src>.txt
```

**Bluetooth Attribute Protocol data**

Extract HID data from Bluetooth Attribute Protocol (`btatt`):

```bash
tshark -r <pcap-file> -Y "btatt.value && frame.len == 20" -T fields -e "btatt.value" > usbdata.txt
```
