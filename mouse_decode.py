#!/usr/bin/env python3
import argparse
import keyboard
import matplotlib.pyplot as plt
import os
import signal
import struct


# Pause on <SPACE>
PAUSED = False
def pause(_):
    global PAUSED
    PAUSED = True
keyboard.on_press_key('space', pause)


# Force quit on q
def quit(_):
    os._exit(0)
keyboard.on_press_key('q', quit)

# Force quit on Ctrl+C
signal.signal(signal.SIGINT, lambda signum, frame: os._exit(0))


def to_signed_int(n, bitlength):
    if n >= 2 ** (bitlength - 1):
        n -= 2 ** bitlength
    return n


def decode_line(line, format, offset=0):
    if format == 'short':
        return struct.unpack('<Bbb', bytes.fromhex(line[offset:offset + 6]))

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


def decode(raw_data):
    clicks, xs, ys = [], [], []
    x, y = 0, 0

    format, offset = get_format(raw_data)

    for line in raw_data:
        click, x_displacement, y_displacement = decode_line(line, format=format, offset=offset)
        clicks.append(click)

        x += x_displacement
        xs.append(x)

        y -= y_displacement
        ys.append(y)

    return clicks, xs, ys


def draw(clicks, xs, ys, draw_moves=True, mousedown_only=True, draw_clicks=False, animate=False):
    global PAUSED
    cur_x, cur_y = xs[0], ys[0]
    mousedown = False

    plt.axis((min(xs) - 50, max(xs) + 50, min(ys) - 50, max(ys) + 50))

    for click, x, y in zip(clicks, xs, ys):
        # Resume animation on <SPACE>
        if PAUSED:
            keyboard.wait('space')
            PAUSED = False

        left, right, middle = click & 0b1, (click & 0b10) >> 1, (click & 0b100) >> 2
        color = (left * 0.8, middle * 0.8, right * 0.8) if click else 'lightgray'

        if draw_clicks and click and not mousedown:
            plt.plot(x, y, '+', color=color, markersize=8, zorder=1)

        if draw_moves:
            if click or not mousedown_only:
                plt.plot((cur_x, x), (cur_y, y), '-', color=color, linewidth=2 if click else 1, zorder=0)

        if animate:
            # Use larger delay on new clicks
            if draw_clicks and click and not mousedown:
                plt.pause(2)

            # Use small delay for any other drawn mouse movement as a crude animation
            elif draw_moves and (click or not mousedown_only):
                plt.pause(0.01)

        cur_x, cur_y = x, y
        mousedown = click

    plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description='Visualize USB Mouse data', epilog='Press <SPACE> during animation to pause/resume or q to quit', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', type=argparse.FileType('r'), help='mouse data file')
    parser.add_argument('-a', '--animate', action='store_true', help='animate mouse movement')
    parser.add_argument('-c', '--clicks', action='store_true', help='show mouse clicks explicitly')
    parser.add_argument('-m', '--mode', type=int, choices=range(3), default=1, metavar='0-2', help='''display mode for mouse movement, from less to more verbose [0-2] (default: %(default)s)
\t0: hide mouse movements (use with -c for clicks only)
\t1: show mouse movements while any mouse button is held
\t2: show all mouse movements''')
    return parser.parse_args()


def main():
    args = parse_args()
    mouse_data = [''.join(d.strip().split(':')) for d in args.file.read().split('\n') if d]
    clicks, xs, ys = decode(mouse_data)

    draw(
        clicks, xs, ys,
        draw_moves=args.mode > 0,
        mousedown_only=args.mode == 1,
        draw_clicks=args.clicks,
        animate=args.animate
    )


if __name__ == '__main__':
    main()
