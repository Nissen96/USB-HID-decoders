# USB HID Decoders

This repository contains decoders and visualizers for various USB Human Interface Devices (HIDs).

HID specification: https://www.usb.org/sites/default/files/hid1_11.pdf

Currently supports keyboard and mouse data.


## Installation

Clone repo
```bash
git clone https://github.com/Nissen96/USB-HID-decoders.git
cd USB-HID-decoders
```

Install dependencies in a virtual environment with `pipenv` (`pip install pipenv`)
```bash
pipenv install
```

Run script(s) within virtual environment
```bash
pipenv run python <script-name> <script-args>
```

Alternatively, install dependencies in the current environment and run scripts with
```bash
pip install -r requirements.txt
python <script-name> <script-args>
```


## Usage

### Keyboard

Converts keyboard scan codes to a human readable format.
```bash
python keyboard_decode.py <usbdata.txt> [options]
```

**Modes**

- `raw`: Output each keypress (with modifiers) explicitly on a separate line.
- `simulate`: Simulate the keypresses as if written in a text editor with a US-keyboard.
- `replay`: Replay keypresses on the actual machine in the current window (unsafe!).

`simulate` mode is default and will likely produce the expected output. It handles most scan codes and `Shift`. Key combos (e.g. `<Ctrl+c>`, `<Alt+TAB>`, `<Shift+LEFT>`) and some special keys (e.g. `<ESC>`) are not simulated, but written explicitly.

A simulation environment can be set with `--env` (`txt` or `cmd`). In text mode (default), a multiline text editor is assumed and e.g. all arrow key presses interpreted as cursor movement. `<ENTER>` will insert a line break at the cursor position. In command mode, a single-line interactive environment (terminal, browser, etc.) is assumed, where keys like `<TAB>`, `<ENTER>`, `<UP>`, and `<DOWN>` are considered action keys. `<ENTER>` starts a new line, and other actions are written out explicitly.

If the capture is from a non-US keyboard layout, the simulation may produce partially incorrect results.
In that case, use `raw` mode, set your keyboard layout correctly, move to the right environment, and simulate the keypresses manually in a text editor.

Optionally, use `replay` mode to simulate the keypresses automatically. *Never* use this mode on untrusted input, it will type whatever was typed during the capture, including any commands, shortcuts, etc. so make sure to first inspect the output from the raw and simulated modes. Press `q` at any time during replay to stop.

Note: `raw` mode and `replay` mode are the most accurate (assuming you set the right keyboard layout and are in the right environment) but in `replay` mode, `<Shift+ArrowKey>` does not select text on Windows 10. This is a known bug in the underlying keybord library. As a workaround, the program will stop and wait for you to perform those keypresses manually.

Key codes taken from https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

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

Moves and clicks can be animated by setting `--speed [1-10]`. Pause/resume animation with `<SPACE>` and clear the screen with `c`. Quit at any time by pressing `q`. These options are especially helpful for visualizing screen keyboard usage or when drawing/writing with the mouse in the same spot multiple times.

Colors indicate the mouse button(s) pressed when clicking/moving. Movement while no buttons are held is colored gray (in mode 2).


### Tablet

Visualizes pen drawing on tablet.
```bash
python tablet_decode.py <usbdata.txt> [options]
```

**Modes**

- 1: Show pen movement only on pen click
- 2: Show all pen movements

Animate drawing by setting `--speed [1-10]`. Pause/resume animation with `<SPACE>` and clear the screen with `c`. Quit at any time by pressing `q`.

Color indicates drawing while holding pen button. Pen movement with no buttons held is colored gray (in mode 2).

## PCAP Extraction

USB HID data can be extracted from a packet capture with `tshark`, the CLI of Wireshark. In Wireshark, the relevant data is stored in the field `usb.capdata` (Leftover Capture Data) or `usbhid.data` (HID Data). Extract with
```bash
tshark -r <pcap-file> -Y 'ubshid.data' -T fields -e usbhid.data > usbdata.txt
```
or
```bash
tshark -r <pcap-file> -Y 'usb.capdata' -T fields -e usb.capdata > usbdata.txt
```

Get data from a specific device by adding a filter for its address, e.g.
```bash
-Y 'usb.src == "1.3.1"'
```

Oneliner to extract HID data from all USB devices and store in separate files, named after device address.

```bash
tshark -r <pcap-file> -Y "usb.capdata || usbhid.data" -T fields -e usb.src -e usb.capdata -e usbhid.data |  # Extract usb.src, usb.capdata, and usbhid.data from all packets with HID data
sort -s -k1,1 |  # Sort on first field only (usb.src)
awk '{ printf "%s", (NR==1 ? $1 : pre!=$1 ? "\n" $1 : "") " " $2; pre=$1 }' |  # Group data by usb.src
awk '{ for (i=2; i<=NF; i++) print $i > "usbdata-" $1 ".txt" }'  # For each group, store data in usbdata-<usb.src>.txt
```
