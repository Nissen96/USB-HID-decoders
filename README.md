# USB HID Decoders

Decoders and visualizers for USB Human Interface Devices (HIDs) — keyboard, mouse, and tablet — including tools to extract raw HID data from PCAP files.

📄 HID Spec: [USB HID 1.11](https://www.usb.org/sites/default/files/hid1_11.pdf)

## ✨ Features

- **[PCAP extraction](#-pcap-extraction)** — extract raw HID data using `scapy` or `tshark`.
- **[Keyboard decoder](#️-keyboard-decoder)** — translate scan codes into keystrokes
- **[Mouse decoder](#️-mouse-decoder)** — draw mouse movement and clicks
- **[Tablet decoder](#️-tablet-decoder)** — draw tablet pen strokes

## 🚀 Installation

Clone the repo:

```bash
git clone https://github.com/Nissen96/USB-HID-decoders.git
cd USB-HID-decoders
```

Install Python dependencies (optional):

```bash
pip install -r requirements.txt
```

- `matplotlib`: Required for mouse/tablet visualizations
- `scapy`: Needed for `extract_hid_data.py` (not required if using bash version).
- `keyboard`: Enables replay mode and keyboard shortcuts during mouse/tablet animations (must be run as root on Linux, unsupported in WSL).

## Usage

### 📥 PCAP Extraction

Extract the HID data from a PCAP with one of the two helper scripts:

#### Bash

```bash
./extract_hid_data.sh <input.pcap>
```

Requires `tshark`, the command line version of Wireshark. Simplest and most reliable.

One-liner to extract HID data from Bluetooth Attribute Protocol (`btatt`):

```bash
tshark -r <pcap-file> -Y "btatt.value && frame.len == 20" -T fields -e "btatt.value" > usbdata.txt
```

#### Python

```bash
python extract_hid_data.py <input.pcap> -o output.txt
```

Requires the Python library `scapy`. Tries to recover device name and info if possible, but less reliable for now.

---

### ⌨️ Keyboard Decoder

Convert HID scan codes to readable keystrokes.

📎[Scan code reference](https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2).

```bash
python keyboard_decode.py [--offset N] [--mode {raw,simulate,replay}]
                          [--env {txt,cmd}] [--delay MS] [--no-reserved]
                          [-o OUTPUT] file
```

**Modes (`--mode`)**:

- `raw`: Print each keypress (with modifiers) on a separate line
- `simulate` _(default)_: Simulate typed text on a US-keyboard
- `replay`: Replays keystrokes in active window (⚠️ unsafe for untrusted input)
  - `--delay <DELAY>` to set delay in miliseconds between keystrokes (default: `50`)

**Environment (`--env`)** _(`simulate` mode only)_:

- `txt` _(default)_: Multiline editor behavior
  - Arrow keys are interpreted as cursor movement and simulated
  - `<ENTER>` will insert a line break at the cursor position
- `cmd`: Interactive shell/browser behavior
  - Keys like `<TAB>`, `<ENTER>`, `<UP>`, and `<DOWN>` are considered action keys
  - `<ENTER>` starts a new line, but other actions are written out explicitly

**Data Format**:

Normal keyboard HID data has a modifier byte (e.g. `SHIFT`, `CTRL`, etc.), a reserved null byte, and then up to six keycode bytes (in case of multiple keys pressed):

```
| Modifier | Reserved | Keycode 1 | ... | Keycode 6 |
```

Format options:

- `--offset`: Index of modifier byte in case of added prefix bytes (default: `0`)
- `--no-reserved`: Use if the reserved byte is missing (e.g. USBPcap outputs)

---

### 🖱️ Mouse Decoder

Visualize mouse movements and clicks.

```bash
python mouse_decode.py [--offset N] [--mode 0-2] [--clicks] [--speed SPEED]
                       [--bit-lengths {8,12,16}...] [--absolute] file
```

**Modes (`--mode`)**:

- `0`: Do not draw movement
  - Combine with `--clicks` to show button clicks only
- `1` _(default)_: Draw movement when buttons are held
- `2`: Draw all movements

Colors indicate the mouse button(s) pressed when clicking/moving (left/middle/right).
Movement while no buttons are held is colored gray in mode 2.

**Animation**:

- `--speed`: Set animation speed 0-10 (default: `0`)
  - `0` disables animation and shows finished drawing

Keyboard controls during animation (very helpful for onscreen keyboard usage or drawing/writing in the same spot multiple times):

- `SPACE`: Pause/resumse
- `c`: Clear screen and continue
- `q`: Quit

Requires Python library `keyboard`

**Data Format**:

Mouse data can come in many formats but has consecutive fields for `click`, `x`, and `y`.
The fields are each either 8, 12, or 16 bits, and should in total be divisible by 16.

Format options:

- `--offset`: Index of `click` field in each data line (default: `0`)
- `--bit-lengths`: Bit lengths of fields `[click, x, y]` (default: `8 12 12`)
- `--absolute`: Interpret coordinates as absolute instead of the default relative cumulative

---

### 🖊️​ Tablet Decoder

Visualize tablet/pen input (pressure ignored).

```bash
python tablet_decode.py [--offset N] [--mode 0-2]
                        [--speed SPEED] file
```

**Modes (`--mode`)**:

- `1` _(default)_: Draw only when pen is clicked
- `2`: Draw all movements

Colors indicate the mouse button(s) pressed when clicking/moving (left and/or right).
Movement while no buttons are held is colored gray in mode 2.

**Animation**:

- `--speed`: Set animation speed 0-10 (default: `0`)
  - `0` disables animation and shows finished drawing

Keyboard controls during animation:

- `SPACE`: Pause/resumse
- `c`: Clear screen and continue
- `q`: Quit

Requires Python library `keyboard`

---

### 📌 Tips

- The decoders often work out of the box, but you might need to analyze some data lines manually to figure out the format options
  - All scripts support an `--offset` to the real data when data lines are prefixed with extra bytes
  - Mouse decoder supports different bit lengths for the three data fields
- For animation, enable keyboard interaction by installing Python library `keyboard`
- For keyboard decoding, `simulate` mode typically produces the expected final output
  - Handles most scan codes, arrow keys, `Shift`, etc.
  - Key combos (e.g. `<Ctrl+c>`, `<Alt+TAB>`, `<Shift+LEFT>`) and some special keys (e.g. `<ESC>`) are written explicitly.
- Be careful with `replay` mode, this will repeat all keypresses typed during the capture
  - This includes any commands, shortcuts, etc. - can be useful for e.g. a Vim capture
  - Inspect output from raw/simulated mode before running replay
  - Set the computer's keyboard layout to the same as the expected layout used during capture
  - Press `q` at any time to stop immediately
- A keyboard capture might contain important text that is later deleted/overwritten
  - `simulate` will only provide the final output
  - Use `raw` to see every keypress explicitly or `replay` with a delay to see the behaviour in real time
- In `replay` mode, `<Shift+ArrowKey>` does not select text on Windows 10 due to a bug in the `keyboard` library
  - As a workaround, the program will stop and wait for you to perform those keypresses manually.
- Check out the samples folder to see usage from various CTFs

---

### 🔎​ Extraction Details

USB HID data can be extracted from a packet capture with `tshark`, the CLI of Wireshark.
In Wireshark, the relevant data is stored in the field `usb.capdata` (Leftover Capture Data) or `usbhid.data` (HID Data).

These can be extracted separately with

```bash
tshark -r <pcap-file> -Y 'usbhid.data' -T fields -e usbhid.data > usbdata.txt
```

and

```bash
tshark -r <pcap-file> -Y 'usb.capdata' -T fields -e usb.capdata > usbdata.txt
```

Get data from a specific device by adding a filter for its address, e.g.

```bash
-Y 'usb.src == "1.3.1"'
```

The bash script provided in the repo is a one-liner to extract HID data from all USB devices and store in separate files, named after device address:

```bash
tshark -r <pcap-file> -Y "usb.capdata || usbhid.data" -T fields -e usb.src -e usb.capdata -e usbhid.data |  # Extract usb.src, usb.capdata, and usbhid.data from all packets with HID data
sort -s -k1,1 |  # Sort on first field only (usb.src)
awk '{ printf "%s", (NR==1 ? $1 : pre!=$1 ? "\n" $1 : "") " " $2; pre=$1 }' |  # Group data by usb.src
awk '{ for (i=2; i<=NF; i++) print $i > "usbdata-" $1 ".txt" }'  # For each group, store data in usbdata-<usb.src>.txt
```
