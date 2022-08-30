#!/usr/bin/env python3
import argparse
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
    0x2C: (' ', ' '),
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
} | {0x3A + i: f'<F{i + 1}>' for i in range(12)}

MODIFIER_CODES = {
    0x01: ('L_CTRL', 'Ctrl'),
    0x02: ('L_SHIFT', 'Shift'),
    0x04: ('L_ALT', 'Alt'),
    0x08: ('L_GUI', 'GUI'),
    0x10: ('R_CTRL', 'Ctrl'),
    0x20: ('R_SHIFT', 'Shift'),
    0x40: ('R_ALT', 'AltGr'),
    0x80: ('R_GUI', 'GUI')
}


def simulate_keypresses(keypresses):
    output = [[]]
    capslock = False
    pos = 0
    line = 0

    for modifiers, key in keypresses:
        # Write out shortcut keypresses explicitly for now - simulate things like selection, copy, cut, paste etc. later
        key_combo = {m[1] for m in modifiers}
        if len(key_combo - {'Shift', 'AltGr'}) > 0:
            ordered_combo = list(sorted(key_combo, key=lambda m: ['Ctrl', 'Shift', 'Alt', 'AltGr', 'GUI'].index(m)))
            output[line].insert(pos, f'<{"+".join(ordered_combo + [key[0]])}>')
            pos += 1
            continue
        elif key_combo == {'Shift'} and key[0] in ('RIGHT', 'LEFT', 'DOWN', 'UP'):
            output[line].insert(pos, f'<Shift+{key[0]}>')
            pos += 1
            continue


        # Shift pressed? AltGr is used on many European keyboard layouts for some of the same symbols SHIFT is on US layout (e.g. @, $)
        shift = len(key_combo & {'Shift', 'AltGr'}) > 0

        match key[0]:
            case 'ENTER':
                line += 1
                pos = 0
                output.insert(line, [])
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
                output[line].insert(pos, '\t')
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
                line = min(line + 1, len(output) - 1)
                pos = min(pos, len(output[line]))
            case 'UP':
                line = max(line - 1, 0)
                pos = min(pos, len(output[line]))
            case _:
                if key[0].isalpha():
                    shift ^= capslock
                output[line].insert(pos, key[-shift] if len(key) == 2 else f'<{key[0]}>')
                pos += 1

    return '\n'.join([''.join(line) for line in output])


def format_keypresses(keypresses):
    keys = []
    current_modifiers = set()
    for modifiers, key in keypresses:
        # Add pressed modifier keys
        for modifier in modifiers - current_modifiers:
            keys.append(f'<{modifier[0]}> PRESSED')

        # Add released modifier keys
        for modifier in current_modifiers - modifiers:
            keys.append(f'<{modifier[0]}> RELEASED')

        current_modifiers = modifiers

        # Add <> around special keys
        keys.append(key[0] if len(key) == 2 else f'<{key[0]}>')

    return '\n'.join(keys)


def decode_keypresses(raw_data, simulate=False):
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

    return simulate_keypresses(keypresses) if simulate else format_keypresses(keypresses)


def parse_args():
    parser = argparse.ArgumentParser(description='Decode USB Keyboard HID data')
    parser.add_argument('file', type=argparse.FileType('r'), help='keyboard data file')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), help='output file', default=sys.stdout)
    parser.add_argument('-s', '--simulate', action='store_true', help='simulate keypresses')
    return parser.parse_args()


def main():
    args = parse_args()
    keypresses = decode_keypresses(args.file.read(), simulate=args.simulate)
    if args.output:
        args.output.write(keypresses)
    else:
        print(keypresses)


if __name__ == '__main__':
    main()
