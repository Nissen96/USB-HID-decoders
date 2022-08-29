#!/usr/bin/env python3
import argparse
import struct

from draw import draw_movement


def to_signed_int(n, bitlength):
    if n >= 2 ** (bitlength - 1):
        n -= 2 ** bitlength
    return n


def decode_tablet_data(raw_data):
    tablet_data = [''.join(d.strip().split(':')) for d in raw_data.split('\n') if d]

    clicks, xs, ys, pressures = [], [], [], []
    for line in tablet_data:
        click, x, y, pressure = struct.unpack('<Bhhh', bytes.fromhex(line[2:16]))
        clicks.append(click & 0b1)
        pressures.append(pressure)
        xs.append(x)
        ys.append(-y)

    return clicks, xs, ys, pressures


def parse_args():
    parser = argparse.ArgumentParser(
        description='Visualize USB Tablet Data',
        epilog='Keyboard commands:\n  <SPACE>: pause/resume animation\n  c: clear screen during animation\n  q: quit', 
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('file', type=argparse.FileType('r'), help='tablet data file')
    parser.add_argument('-m', '--mode', type=int, choices=range(3), default=1, metavar='1-2', help='''display mode for pen movement, from less to more verbose (default: %(default)s)
  1: show pen movements only while clicked
  2: show all pen movements''')
    parser.add_argument('-s', '--speed', type=int, choices=range(0, 11), default=0, metavar='0, 1-10', help='animation speed, 0 for no animation (default: %(default)s)')
    return parser.parse_args()


def main():
    args = parse_args()
    clicks, xs, ys, _ = decode_tablet_data(args.file.read())
    draw_movement(clicks, xs, ys, draw_mode=args.mode, draw_clicks=False, speed=args.speed)


if __name__ == '__main__':
    main()
