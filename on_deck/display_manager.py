"""
This module is used to manage the display of the scoreboard.
It is used to draw lines, text, and clear sections of the display.
"""

import os
import platform

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics # pylint: disable=E0401
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # pylint: disable=E0401

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    if platform.system() == 'Windows':
        options.rows = int(256)
        options.cols = int(384)
    else:
        options.cols = 128
        options.rows = 64
        options.pixel_mapper_config = 'V-mapper'
        options.chain_length = 4
        options.parallel = 3
        options.disable_hardware_pulsing = True
        options.pwm_bits = 1
        options.gpio_slowdown = 4

    return options

class Colors:
    """
    This class is used to store the colors used in the scoreboard.
    """
    def __init__(self):

        self.black = graphics.Color(0, 0, 0)
        self.white = graphics.Color(255, 255, 255)

        self.red = graphics.Color(255, 0, 0)
        self.green = graphics.Color(0, 255, 0)
        self.blue = graphics.Color(0, 0, 255)

        self.yellow = graphics.Color(255, 255, 0)
        self.magenta = graphics.Color(255, 0, 255)
        self.light_blue = graphics.Color(0, 255, 255)

        # These colors require pwm_bits >= 2
        self.orange = graphics.Color(255, 170, 0)

        # wont show on display due to pwm bits
        self.grey = graphics.Color(20, 20, 20)

class Fonts:
    """
    This class is used to store the fonts used in the scoreboard.
    """
    def __init__(self):
        scoreboard_path = os.path.dirname(os.path.abspath(__file__))
        fonts_path = os.path.join(scoreboard_path, '..', 'fonts')
        terminus_path = os.path.join(fonts_path, 'Terminus')

        self.ter_u32b = graphics.Font()
        self.ter_u32b.LoadFont(os.path.join(terminus_path, 'ter-u32b.bdf'))
        # ter-u32b.bdf:
        # Letter height = 20 pixels = 38 mm = 1.496 in
        # Slighly larger than OnDeck1 (36 mm)

        self.ter_u18b = graphics.Font()
        self.ter_u18b.LoadFont(os.path.join(terminus_path, 'ter-u18b.bdf'))

        self.symbols = graphics.Font()
        self.symbols.LoadFont(os.path.join(fonts_path, 'symbols.bdf'))

class DisplayManager:
    """
    This class is used to manage the display of the scoreboard.
    """
    def __init__(self):
        self.options = get_options()
        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.brightness = 255

        self.colors = Colors()
        self.fonts = Fonts()

        if platform.system() == 'Windows':
            # Fill the screen with grey so that the pixels can be seen
            # on the emulated display
            self.matrix.Fill(20, 20, 20)

    def set_brightness(self, brightness: int):
        """This method is used to change the brightness of the display."""
        if (brightness < 0) or (brightness > 255):
            raise ValueError(f'Brightness {brightness} not recognized')
        self.brightness = brightness
        self.matrix.brightness = brightness

    def swap_frame(self):
        """This method is used to swap the frame on the display."""
        self.matrix.SwapOnVSync(self.canvas)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        """This method is used to draw a line on the display."""
        graphics.DrawLine(self.canvas, x1, y1, x2, y2, color)

    def draw_text(self, font: graphics.Font, x: int, y: int,
        color: graphics.Color, text: str):
        """This method is used to draw text on the display."""
        graphics.DrawText(self.canvas, font, x, y, color, text)

    def clear_section(self, x1, y1, x2, y2):
        """This method is used to clear a section of the display."""
        num_rows = y2 - y1 + 1

        if platform.system() == 'Windows':
            color = self.colors.grey
        else:
            color = self.colors.black

        for i in range(num_rows):
            graphics.DrawLine(self.canvas, x1, y1 + i, x2, y1 + i, color)
