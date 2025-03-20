import platform

from on_deck.matrix_loader import graphics

class Colors:
    """
    This class is used to store the colors used in the scoreboard.
    """
    if platform.system() == 'Windows':
        black = graphics.Color(20, 20, 20)
    else:
        black = graphics.Color(0, 0, 0)
    white = graphics.Color(255, 255, 255)

    red = graphics.Color(255, 0, 0)
    green = graphics.Color(0, 255, 0)
    blue = graphics.Color(0, 0, 255)

    yellow = graphics.Color(255, 255, 0)
    magenta = graphics.Color(255, 0, 255)
    light_blue = graphics.Color(0, 255, 255)

    x = graphics.Color(0, 64, 255)

    # These colors require pwm_bits >= 2
    orange = graphics.Color(255, 170, 0)
    middle_blue = graphics.Color(0, 85, 255)

    # wont show on display due to pwm bits
    grey = graphics.Color(20, 20, 20)
