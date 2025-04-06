import time
import platform
import argparse
import math
from on_deck.display_manager import DisplayManager
from on_deck.colors import Colors as c
from on_deck.fonts import Fonts
from on_deck.matrix_loader import graphics, RGBMatrixOptions

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    parser = argparse.ArgumentParser()
    parser.add_argument('--use-emulator', action='store_true')
    args = parser.parse_args()
    if args.use_emulator:
        use_emulator = True
        print('loading emulator')
    else:
        use_emulator = False

    if (platform.system() == 'Windows') or (use_emulator):
        options.cols = int(384)
        options.rows = int(256)
    else:
        options.cols = 128
        options.rows = 64
        options.pixel_mapper_config = 'V-mapper'
        options.chain_length = 4
        options.parallel = 3
        options.disable_hardware_pulsing = True
        options.pwm_bits = 2 # Can run 2 with sudo, 1 without
        options.gpio_slowdown = 4

    return options

def show_colors():
    display_manager = DisplayManager(get_options())
    # display_manager.set_brightness(255)

    bits = 2

    for red in range(bits ** 2):
        for green in range(bits ** 2):
            for blue in range(bits ** 2):
                i = red * 16 + green * 4 + blue
                column = math.floor(i / 10)
                row = i % 10
                # print(f'i: {i}, column: {column}, row: {row}')

                x = 10 + column * 22
                y = 10 + row * 22

                z = math.floor(255 / (bits ** 2))
                print(z)
                color = graphics.Color(red * z, green * z, blue * z)
                display_manager.draw_text(Fonts.ter_u12b, x, y, c.white, f'{red}{green}{blue}')
                display_manager.draw_box(x, y, x+10, y+10, color, fill=True)
    while True:
        time.sleep(1)
        display_manager.swap_frame()

if __name__ == "__main__":
    show_colors()
    while True:
        pass
