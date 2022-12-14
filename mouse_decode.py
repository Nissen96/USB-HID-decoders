#!/usr/bin/env python3
import argparse
import struct
from draw import draw_movement


def to_signed_int(n, bitlength):
    if n >= 2 ** (bitlength - 1):
        n -= 2 ** bitlength
    return n


def decode_line(line, format, offset=0):
    if format == 'short':
        return struct.unpack('<Bbb', bytes.fromhex(line[offset:offset + 6]))

    if format == 'medium':
        return struct.unpack('<Bhh', bytes.fromhex(line[:10]))

    if format == 'long':
        return (
            struct.unpack('<B', bytes.fromhex(line[2:4]))[0],
            to_signed_int(int(line[offset + 3] + line[offset:offset + 2], 16), bitlength=12),
            to_signed_int(int(line[offset + 4:offset + 6] + line[offset + 2], 16), bitlength=12)
        )

    raise ValueError(f'\'{format}\' is not a supported format')


def get_format(data):
    # Entries can have a few different formats (made up names, just to differentiate between known cases)
    data_len = len(data[0])
    format = 'unknown'
    if data_len in (8, 12):
        format = 'short'
    elif data_len == 14:
        format = 'medium'
    elif data_len == 16:
        format = 'long'

    offset = 0

    # For format 'short', offset can be 0 or 4
    if format == 'short' and data_len == 12:
        offset = 4

    # For format 'long', data will start at offset 2, but x-displacement data can start at offset 4 or 6
    # Heuristically guess by checking number of non-zero bytes at the possible boundaries (offset 4-5 and 10-11)
    if format == 'long':
        evidence_4, evidence_6 = 0, 0
        for line in data:
            if line[4:6] != '00':
                evidence_4 += 1
            if line[10:12] != '00':
                evidence_6 += 1
        offset = (4, 6)[evidence_4 < evidence_6]

    return format, offset


def decode_mouse_data(raw_data):
    mouse_data = [''.join(d.strip().split(':')) for d in raw_data.split('\n') if d]
    format, offset = get_format(mouse_data)

    clicks, xs, ys = [], [], []
    x, y = 0, 0
    for line in mouse_data:
        click, x_displacement, y_displacement = decode_line(line, format=format, offset=offset)
        clicks.append(click)

        x += x_displacement
        xs.append(x)

        y -= y_displacement
        ys.append(y)

    return clicks, xs, ys


def parse_args():
    parser = argparse.ArgumentParser(
        description='Visualize USB Mouse data',
        epilog='Keyboard commands:\n  <SPACE>: pause/resume animation\n  c: clear screen during animation\n  q: quit', 
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', type=argparse.FileType('r'), help='mouse data file')
    parser.add_argument('-m', '--mode', type=int, choices=range(3), default=1, metavar='0-2', help='''display mode for mouse movement, from less to more verbose (default: %(default)s)
  0: hide mouse movements (use with -c for clicks only)
  1: show mouse movements while any mouse button is held
  2: show all mouse movements''')
    parser.add_argument('-c', '--clicks', action='store_true', help='show mouse clicks explicitly')
    parser.add_argument('-s', '--speed', type=int, choices=range(0, 11), default=0, metavar='0, 1-10', help='animation speed, 0 for no animation (default: %(default)s)')
    return parser.parse_args()


def main():
    args = parse_args()
    clicks, xs, ys = decode_mouse_data(args.file.read())
    draw_movement(clicks, xs, ys, draw_mode=args.mode, draw_clicks=args.clicks, speed=args.speed)


if __name__ == '__main__':
    main()
