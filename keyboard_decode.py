#!/usr/bin/env python3
import argparse


KEY_CODES = {
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
    0x28: ('<ENTER>',),
    0x29: ('<ESC>',),
    0x2A: ('<BACKSPACE>',),
    0x2B: ('<TAB>',),
    0x2C: (' ',),
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
    0x39: ('<CAPS LOCK>',),
    0x4A: ('<HOME>',),
    0x4C: ('<DELETE>',),
    0x4D: ('<END>',),
    0x4F: ('<RIGHT>',),
    0x50: ('<LEFT>',),
    0x51: ('<DOWN>',),
    0x52: ('<UP>',),
}


def simulate_keypresses(keypresses):
    output = [[]]
    capslock = False
    pos = 0
    line = 0
    for key, shift in keypresses:
        match key[0]:
            case '<ENTER>':
                line += 1
                pos = 0
                output.insert(line, [])
            case '<BACKSPACE>':
                if pos > 0:
                    pos -= 1
                    output[line].pop(pos)
                elif line > 0:
                    output[line - 1].extend(output[line])
                    output.pop(line)
                    line -= 1
                    pos = len(output[line])
            case '<TAB>':
                output[line].insert(pos, '\t')
                pos += 1
            case '<CAPS LOCK>':
                capslock = not capslock
            case '<HOME>':
                pos = 0
            case '<DELETE>':
                if pos < len(output[line]):
                    output[line].pop()
                elif line < len(output) - 1:
                    output[line].extend(output[line + 1])
                    output.pop(line)
            case '<END>':
                pos = len(output[line])
            case '<RIGHT>':
                if pos < len(output[line]):
                    pos += 1
                elif line < len(output) - 1:
                    line += 1
                    pos = 0
            case '<LEFT>':
                if pos > 0:
                    pos -= 1
                elif line > 0:
                    line -= 1
                    pos = len(output[line])
            case '<DOWN>':
                line = min(line + 1, len(output) - 1)
                pos = min(pos, len(output[line]))
            case '<UP>':
                line = max(line - 1, 0)
                pos = min(pos, len(output[line]))
            case _:
                if key[0].isalpha():
                    shift ^= capslock
                output[line].insert(pos, key[-shift])
                pos += 1

    return '\n'.join([''.join(line) for line in output])


def decode_keypresses(raw_data, simulate=False):
    keypresses = []
    skip_next = False
    for line in raw_data:
        if skip_next:
            skip_next = False
            continue
        
        shift = int(line[0:2], 16) in (0x02, 0x20)
        keycode = int(line[4:6], 16)

        if keycode == 0 or int(line[6:8], 16) != 0:
            continue
        
        if keycode not in KEY_CODES:
            print(f'Unrecognized keycode: {hex(keycode)}, please lookup USB HID keyboard scan codes!')
            continue
        
        if shift:
            skip_next = True
        
        keypresses.append((KEY_CODES[keycode], shift))
 
    if simulate:
        return simulate_keypresses(keypresses)
    
    return ''.join([key[-shift] for key, shift in keypresses])


def parse_args():
    parser = argparse.ArgumentParser(description='Decode USB Keyboard HID data')
    parser.add_argument('file', type=argparse.FileType('r'), help='keyboard data file')
    parser.add_argument('--simulate', action='store_true', help='simulate keypresses')
    return parser.parse_args()


def main():
    args = parse_args()
    keyboard_data = [''.join(d.strip().split(':')) for d in args.file.read().split('\n') if d]
    print(decode_keypresses(keyboard_data, args.simulate))


if __name__ == '__main__':
    main()
