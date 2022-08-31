#!/usr/bin/env python3
import argparse
import time
import sys


SCAN_CODES = {
    0x04: ('a', 'A'),
    0x05: ('b', 'B'),
    0x06: ('c', 'C'),
    0x07: ('d', 'D'),
    0x08: ('e', 'E'),
    0x09: ('f', 'F'),
    0x0A: ('g', 'G'),
    0x0B: ('h', 'H'),
    0x0C: ('i', 'I'),
    0x0D: ('j', 'J'),
    0x0E: ('k', 'K'),
    0x0F: ('l', 'L'),
    0x10: ('m', 'M'),
    0x11: ('n', 'N'),
    0x12: ('o', 'O'),
    0x13: ('p', 'P'),
    0x14: ('q', 'Q'),
    0x15: ('r', 'R'),
    0x16: ('s', 'S'),
    0x17: ('t', 'T'),
    0x18: ('u', 'U'),
    0x19: ('v', 'V'),
    0x1A: ('w', 'W'),
    0x1B: ('x', 'X'),
    0x1C: ('y', 'Y'),
    0x1D: ('z', 'Z'),
    0x1E: ('1', '!'),
    0x1F: ('2', '@'),
    0x20: ('3', '#'),
    0x21: ('4', '$'),
    0x22: ('5', '%'),
    0x23: ('6', '^'),
    0x24: ('7', '&'),
    0x25: ('8', '*'),
    0x26: ('9', '('),
    0x27: ('0', ')'),
    0x28: ('ENTER',),
    0x29: ('ESC',),
    0x2A: ('BACKSPACE',),
    0x2B: ('TAB',),
    0x2C: ('SPACE',),
    0x2D: ('-', '_'),
    0x2E: ('=', '+'),
    0x2F: ('[', '{'),
    0x30: (']', '}'),
    0x31: ('\\', '|'),
    0x32: ('#','~'),
    0x33: (';', ':'),
    0x34: ('\'', '"'),
    0x35: ('`', '~'),
    0x36: (',', '<'),
    0x37: ('.', '>'),
    0x38: ('/', '?'),
    0x39: ('CAPS LOCK',),
    0x4A: ('HOME',),
    0x4B: ('PAGE UP',),
    0x4C: ('DELETE',),
    0x4D: ('END',),
    0x4E: ('PAGE DOWN',),
    0x4F: ('RIGHT',),
    0x50: ('LEFT',),
    0x51: ('DOWN',),
    0x52: ('UP',),
} | {0x3A + i: f'F{i + 1}' for i in range(12)}

MODIFIER_CODES = {
    0x01: 'Ctrl',
    0x02: 'Shift',
    0x04: 'Alt',
    0x08: 'WIN',
    0x10: 'Ctrl',
    0x20: 'Shift',
    0x40: 'AltGr',
    0x80: 'WIN'
}


def replay_keypresses(keypresses, delay=20):
    import keyboard
    import os
    import signal

    # Force quit on q and sigint (e.g. Ctrl+C)
    keyboard.on_press_key('q', lambda _: os._exit(0))
    signal.signal(signal.SIGINT, lambda signum, frame: os._exit(0))

    print('Please open the program you want the keystrokes to be replayed in (e.g. notepad, terminal, browser, email...)')
    print('Press <SPACE> in that window to start and \'q\' at any point to stop')
    keyboard.wait('space', suppress=True)
    time.sleep(0.1)

    for modifiers, keypress in keypresses:
        shift = modifiers == {'Shift'}
        key = k if (k := keypress[0]).isalnum() else keypress[-shift]  # Shouldn't be necessary to manually select shifted/not, but keyboard library has bugs

        # Replace AltGr with Ctrl+Alt
        if 'AltGr' in modifiers:
            modifiers = modifiers - {'AltGr'} | {'Ctrl', 'Alt'}

        # Workaround for <Shift+Arrow Keys> not working correctly in Win10 - let users do this manually
        if shift and key in {'RIGHT', 'LEFT', 'DOWN', 'UP'}:
            print(f'Please press <Shift+{key}> manually...')
            hotkey = keyboard.get_hotkey_name([*modifiers, key])
            keyboard.wait(f'shift+{key.lower()} arrow')
            time.sleep(1)
        else:
            hotkey = keyboard.get_hotkey_name([*modifiers, key])
            keyboard.send(hotkey)
            time.sleep(delay / 1000)


def simulate_keypresses(keypresses, text_mode=True):
    output = [[]]
    capslock = False
    pos = 0
    line = 0

    for modifiers, key in keypresses:
        # Write out shortcut keypresses explicitly
        if len(modifiers - {'Shift', 'AltGr'}) > 0:
            ordered_modifiers = list(sorted(modifiers, key=lambda m: ['Ctrl', 'Shift', 'Alt', 'AltGr', 'WIN'].index(m)))
            output[line].insert(pos, f'<{"+".join(ordered_modifiers + [key[0]])}>')
            pos += 1
            continue
        elif modifiers == {'Shift'} and key[0] in ('RIGHT', 'LEFT', 'DOWN', 'UP'):
            output[line].insert(pos, f'<Shift+{key[0]}>')
            pos += 1
            continue

        # Shift pressed? AltGr is used on many European keyboard layouts for some of the same symbols SHIFT is on US layout (e.g. @, $)
        shift = len(modifiers & {'Shift', 'AltGr'}) > 0

        match key[0]:
            case 'SPACE':
                output[line].insert(pos, ' ')
                pos += 1
            case 'ENTER':
                output.insert(line + 1, [])

                # In text mode, move remainder of line down to start of new line
                if text_mode:
                    output[line + 1].extend(output[line][pos:])
                    del output[line][pos:]

                line += 1
                pos = 0
            case 'BACKSPACE':
                if pos > 0:
                    pos -= 1
                    output[line].pop(pos)
                elif line > 0:
                    output[line - 1].extend(output[line])
                    output.pop(line)
                    line -= 1
                    pos = len(output[line])
            case 'TAB':
                output[line].insert(pos, '\t' if text_mode else '<TAB>')
                pos += 1
            case 'CAPS LOCK':
                capslock = not capslock
            case 'HOME':
                pos = 0
            case 'DELETE':
                if pos < len(output[line]):
                    output[line].pop(pos)
                elif line < len(output) - 1:
                    output[line].extend(output[line + 1])
                    output.pop(line)
            case 'END':
                pos = len(output[line])
            case 'RIGHT':
                if pos < len(output[line]):
                    pos += 1
                elif line < len(output) - 1:
                    line += 1
                    pos = 0
            case 'LEFT':
                if pos > 0:
                    pos -= 1
                elif line > 0:
                    line -= 1
                    pos = len(output[line])
            case 'DOWN':
                if text_mode:
                    line = min(line + 1, len(output) - 1)
                    pos = min(pos, len(output[line]))
                else:
                    output[line].insert(pos, '<DOWN>')
                    pos += 1
            case 'UP':
                if text_mode:
                    line = max(line - 1, 0)
                    pos = min(pos, len(output[line]))
                else:
                    output[line].insert(pos, '<UP>')
                    pos += 1
            case _:
                if key[0].isalpha():
                    shift ^= capslock
                output[line].insert(pos, key[-shift] if len(key) == 2 else f'<{key[0]}>')
                pos += 1

    return '\n'.join([''.join(line) for line in output])


def format_raw_keypresses(keypresses):
    keys = []
    for modifiers, key in keypresses:
        ordered_modifiers = list(sorted(modifiers, key=lambda m: ['Ctrl', 'Shift', 'Alt', 'AltGr', 'WIN'].index(m)))
        key_combo = '+'.join(ordered_modifiers + [key[0]])
        if len(modifiers) > 0 or len(key) == 1:
            key_combo = f'<{key_combo}>'

        keys.append(key_combo)

    return '\n'.join(keys)


def decode_keypresses(raw_data):
    keyboard_data = [''.join(d.strip().split(':')) for d in raw_data.split('\n') if d]

    keypresses = []
    pressed_keys = set()

    for line in keyboard_data:
        modifier = int(line[:2], 16)
        scan_codes = set(bytes.fromhex(line[4:])) - {0}
        new_keys = scan_codes - pressed_keys
        pressed_keys = scan_codes

        for scan_code in sorted(new_keys, reverse=True):
            if scan_code not in SCAN_CODES:
                print(f'Unrecognized scan code: {hex(scan_code)}, please lookup USB HID keyboard scan codes!')
                continue

            modifiers = {m for code, m in MODIFIER_CODES.items() if modifier & code == code}

            keypresses.append((modifiers, SCAN_CODES[scan_code]))

    return keypresses


def parse_args():
    parser = argparse.ArgumentParser(
        description='Decode USB Keyboard HID data',
        epilog='''
=============
  MORE INFO
=============
Simulation mode will in most cases provide a similar result to the original input, but is limited and assumes US layout.

Key combos, text selection, and some special keys are not simulated, but instead written out explicitly (e.g. <Ctrl+c>, <Alt+TAB>, <Shift+LEFT>, <ESC>).
If needed, use raw mode to list all keystrokes separately.

Replay mode automates this replaying on your machine (may require root perms), using the current keyboard layout.
  WARNING: NEVER use this for untrusted input! What was captured will be played back on your machine, malicious or not.
           Press q to force quit anytime mid-replay.

Limitations:
  In replay mode, <Shift+ArrowKey> does not select text as expected. This is due to a known issue in the underlying library.
  As a workaround, the program will stop and ask you to manually press these keys before taking over automatically.
'''.strip(),
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', type=argparse.FileType('r'), help='keyboard data file')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help='output file', default=sys.stdout)
    parser.add_argument('-m', '--mode', choices=('raw', 'simulate', 'replay'), default='simulate', help='''keystroke output mode (default: %(default)s)
    raw: output each keystroke on a separate line
    simulate: output a simulation of the keystrokes (safe)
    replay: play back each keystroke directly on your machine (unsafe)''')
    parser.add_argument('-d', '--delay', type=int, default=50, help='delay in milliseconds between keystrokes for replay mode (default: %(default)s)')
    parser.add_argument('-e', '--env', choices=('txt', 'cmd'), default='txt', help='''assumed environment for simulation mode (default: %(default)s)
    txt: multi-line text editor environment. Arrow keys move the cursor and <ENTER> inserts a line break.
    cmd: assume single-line interactive environment, i.e. terminal, browser, etc.
         <UP>, <DOWN>, and <TAB> are output explicitly and <ENTER> starts a new line.''')
    return parser.parse_args()


def main():
    args = parse_args()
    keypresses = decode_keypresses(args.file.read())

    if args.mode == 'raw':
        output = format_raw_keypresses(keypresses)
        args.output.write(output) if args.output else print(output)
    elif args.mode == 'simulate':
        output = simulate_keypresses(keypresses, text_mode=args.env == 'txt')
        args.output.write(output) if args.output else print(output)
    elif args.mode == 'replay':
        return replay_keypresses(keypresses, args.delay)


if __name__ == '__main__':
    main()
