"""
This module is used to manage the display of the scoreboard.
It is used to draw lines, text, and clear sections of the display.
"""

import platform
from on_deck.colors import Colors

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

class DisplayManager:
    """
    This class is used to manage the display of the scoreboard.
    """
    def __init__(self):
        self.options = get_options()
        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.brightness = 255

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
            color = Colors.grey
        else:
            color = Colors.black

        for i in range(num_rows):
            graphics.DrawLine(self.canvas, x1, y1 + i, x2, y1 + i, color)
