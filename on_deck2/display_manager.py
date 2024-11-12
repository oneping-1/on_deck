"""
This module is used to manage the display of the scoreboard.
It is used to draw lines, text, and clear sections of the display.
"""

import platform
from on_deck.colors import Colors
import time
import math

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

    options.cols = int(100)
    options.rows = int(100)

    return options

class DisplayManager:
    """
    This class is used to manage the display of the scoreboard.
    """
    def __init__(self, options: RGBMatrixOptions = None):
        self.options = options
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

    def draw_pixel(self, x: int, y: int, color: graphics.Color):
        """This method is used to draw a pixel on the display."""
        # graphics.SetPixel(self.canvas, x, y, color.red, color)
        self.canvas.SetPixel(x, y, color.red, color.green, color.blue)

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, color: graphics.Color):
        """This method is used to draw a line on the display."""
        graphics.DrawLine(self.canvas, x1, y1, x2, y2, color)

    def draw_text(self, font: graphics.Font, x: int, y: int,
        color: graphics.Color, text: str):
        """This method is used to draw text on the display."""
        graphics.DrawText(self.canvas, font, x, y, color, text)

    def draw_circle(self, x: int, y: int, radius: int, thickness: int,
        fill: bool, color: graphics.Color):
        """
        This method is used to draw a circle on the display.

        Args:
            x (int): X coordinate of the center of the circle
            y (int): Y coordinate of the center of the circle
            radius (int): Radius of the circle
            thickness (int): Thickness of the circle
            fill (bool): Whether or not to fill the circle
            color (graphics.Color): Color of the circle
        """

        start = radius
        stop = radius - thickness
        if fill:
            stop = 0
            self.draw_pixel(x, y, color) # Not included in the loops

        for degrees in range(0, 91, 10):
            # Dont need to go all the way around
            # because of rotational symmetry
            for r in range(start, stop, -1):
                r_eff = r - .01
                d1 = degrees
                d2 = d1 + 90
                d3 = d2 + 90
                d4 = d3 + 90

                a1 = math.radians(d1)
                a2 = math.radians(d2)
                a3 = math.radians(d3)
                a4 = math.radians(d4)

                x1 = x + r_eff * math.cos(a1)
                y1 = y + r_eff * math.sin(a1)
                x1 = round(x1)
                y1 = round(y1)
                self.draw_pixel(x1, y1, color)

                x2 = x + r_eff * math.cos(a2)
                y2 = y + r_eff * math.sin(a2)
                x2 = round(x2)
                y2 = round(y2)
                self.draw_pixel(x2, y2, color)

                x3 = x + r_eff * math.cos(a3)
                y3 = y + r_eff * math.sin(a3)
                x3 = round(x3)
                y3 = round(y3)
                self.draw_pixel(x3, y3, color)

                x4 = x + r_eff * math.cos(a4)
                y4 = y + r_eff * math.sin(a4)
                x4 = round(x4)
                y4 = round(y4)
                self.draw_pixel(x4, y4, color)


    def draw_diamond(self, x: int, y: int, radius: int, thickness: int,
        fill: bool, color: graphics.Color):
        """
        This method is used to draw a diamond on the display.

        Args:
            x (int): X coordinate of the center of the diamond
            y (int): Y coordinate of the center of the diamond
            radius (int): Distance between center and corners
            thickness (int): Thickness of the diamond
            fill (bool): Whether or not to fill the diamond
            color (graphics.Color): Color of the diamond
        """

        start = radius
        stop = radius - thickness
        if fill:
            stop = 0
            self.draw_pixel(x, y, color) # Not included in the loop

        for i in range(start, stop, -1):
            x1 = x
            y1 = y - i

            x2 = x + i
            y2 = y

            x3 = x
            y3 = y + i

            x4 = x - i
            y4 = y

            self.draw_line(x1, y1, x2, y2, color)
            self.draw_line(x2, y2, x3, y3, color)
            self.draw_line(x3, y3, x4, y4, color)
            self.draw_line(x4, y4, x1, y1, color)

    def clear_section(self, x1, y1, x2, y2):
        """This method is used to clear a section of the display."""
        num_rows = y2 - y1 + 1

        if platform.system() == 'Windows':
            color = Colors.grey
        else:
            color = Colors.black

        for i in range(num_rows):
            graphics.DrawLine(self.canvas, x1, y1 + i, x2, y1 + i, color)

if __name__ == '__main__':
    from colors import Colors

    display = DisplayManager(get_options())
    R = 5
    display.draw_circle(10, 10, R, 1, False, Colors.red)
    display.draw_circle(30, 10, R, 2, False, Colors.green)
    display.draw_circle(50, 10, R, 3, False, Colors.light_blue)
    display.draw_circle(70, 10, R, 1, True, Colors.yellow)

    display.draw_diamond(10, 30, R, 1, False, Colors.red)
    display.draw_diamond(30, 30, R, 2, False, Colors.green)
    display.draw_diamond(50, 30, R, 3, False, Colors.light_blue)
    display.draw_diamond(70, 30, R, 1, True, Colors.yellow)
    display.swap_frame()

    while True:
        time.sleep(10)
