#!/usr/bin/env python3
import matplotlib.pyplot as plt
import os
import signal


signal.signal(signal.SIGINT, lambda signum, frame: os._exit(0))
listen_keypress = False

try:
    import keyboard

    # Check for non-root access on Linux
    keyboard.unhook_all()

    listen_keypress = True
except ModuleNotFoundError:
    print('Module \'keyboard\' not found, keypresses ignored')
except ImportError:
    print('Keyboard module requires root access, keypresses ignored')
except AssertionError:
    print('Keyboard module failed to create a device file (maybe you are running in WSL?), keypresses ignores')


if listen_keypress:
    # Force quit on q and sigint (e.g. Ctrl+C)
    keyboard.on_press_key('q', lambda _: os._exit(0))

    # Pause on <SPACE>
    PAUSE = False
    def pause(_):
        global PAUSE
        PAUSE = True
    keyboard.on_press_key('space', pause)


def draw_movement(clicks, xs, ys, draw_mode=1, draw_clicks=False, speed=0):
    cur_x, cur_y = xs[0], ys[0]
    mousedown = False

    # Clear plot on c
    def clear_screen():
        plt.cla()
        plt.axis((min(xs) - 50, max(xs) + 50, min(ys) - 50, max(ys) + 50))
    if listen_keypress:
        keyboard.on_press_key('c', lambda _: clear_screen())

    clear_screen()
    for step, (click, x, y) in enumerate(zip(clicks, xs, ys)):
        if listen_keypress:
            # Handle pause, resume on <SPACE>
            global PAUSE
            if PAUSE:
                keyboard.wait('space')
                PAUSE = False

        left, right, middle = click & 0b1, (click & 0b10) >> 1, (click & 0b100) >> 2
        color = (left * 0.8, middle * 0.8, right * 0.8) if click else 'lightgray'

        draw_click = draw_clicks and click and not mousedown
        draw_move = draw_mode == 2 or (draw_mode == 1 and click)

        if draw_click:
            plt.plot(x, y, '+', color=color, markersize=8, zorder=1)

        if draw_move:
            plt.plot((cur_x, x), (cur_y, y), '-', color=color, linewidth=2 if click else 1, zorder=0)

        # Animate using small plot pauses
        if speed > 0:
            # Pause on all new clicks, delay depends on speed
            if draw_click:
                plt.pause(2 ** (3 - speed))

            # Tiny pause on drawn mouse movement, skips some pauses depending on speed
            elif draw_move and step % 2**(speed - 1) == 0:
                plt.pause(0.01)

        cur_x, cur_y = x, y
        mousedown = click

    plt.show()
