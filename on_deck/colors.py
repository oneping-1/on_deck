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

    # 1 PWM Bit
    # RGB Colors
    red = graphics.Color(255, 0, 0)
    green = graphics.Color(0, 255, 0)
    blue = graphics.Color(0, 0, 255)

    # CYM Colors
    yellow = graphics.Color(255, 255, 0)
    magenta = graphics.Color(255, 0, 255)
    cyan = graphics.Color(0, 255, 255)


    # 2 PWM Bits
    # what to name these?
    pink = graphics.Color(255, 85, 255)
    orange = graphics.Color(255, 170, 0)
    middle_blue = graphics.Color(0, 85, 255)

    # wont show on display due to pwm bits
    grey = graphics.Color(20, 20, 20)
