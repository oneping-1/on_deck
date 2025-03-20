import os
import platform

from on_deck.matrix_loader import graphics

class Fonts:
    """
    This class is used to store the fonts used in the scoreboard.
    B = Bold
    N = Normal
    V = Not sure
    """
    f6x10 = None
    ter_u12b = None
    ter_u12n = None

    ter_u14b = None
    ter_u14n = None
    ter_u14v = None

    ter_u16b = None
    ter_u16n = None
    ter_u16v = None

    ter_u18b = None
    ter_u22b = None
    ter_u24b = None
    ter_u28b = None
    ter_u32b = None
    symbols = None

    # Class initialization block
    @classmethod
    def _initialize_fonts(cls):
        if cls.ter_u32b is None:  # Load the fonts only if they are not already loaded
            scoreboard_path = os.path.dirname(os.path.abspath(__file__))
            fonts_path = os.path.join(scoreboard_path, '..', 'fonts')
            rpi_rgb_path = os.path.join(fonts_path, 'rpi-rgb-led-matrix')
            terminus_path = os.path.join(fonts_path, 'Terminus')

            cls.f6x10 = graphics.Font()
            cls.f6x10.LoadFont(os.path.join(rpi_rgb_path, '6x10.bdf'))
            # cls.test.LoadFont(os.path.join(terminus_path, 'ter-u12b.bdf'))

            cls.ter_u12b = graphics.Font()
            cls.ter_u12b.LoadFont(os.path.join(terminus_path, 'ter-u12b.bdf'))

            cls.ter_u12n = graphics.Font()
            cls.ter_u12n.LoadFont(os.path.join(terminus_path, 'ter-u12n.bdf'))

            cls.ter_u14b = graphics.Font()
            cls.ter_u14b.LoadFont(os.path.join(terminus_path, 'ter-u14b.bdf'))

            cls.ter_u14n = graphics.Font()
            cls.ter_u14n.LoadFont(os.path.join(terminus_path, 'ter-u14n.bdf'))

            cls.ter_u14v = graphics.Font()
            cls.ter_u14v.LoadFont(os.path.join(terminus_path, 'ter-u14v.bdf'))

            cls.ter_u16b = graphics.Font()
            cls.ter_u16b.LoadFont(os.path.join(terminus_path, 'ter-u16b.bdf'))

            cls.ter_u16n = graphics.Font()
            cls.ter_u16n.LoadFont(os.path.join(terminus_path, 'ter-u16n.bdf'))

            cls.ter_u16v = graphics.Font()
            cls.ter_u16v.LoadFont(os.path.join(terminus_path, 'ter-u16v.bdf'))

            cls.ter_u18b = graphics.Font()
            cls.ter_u18b.LoadFont(os.path.join(terminus_path, 'ter-u18b.bdf'))

            cls.ter_u22b = graphics.Font()
            cls.ter_u22b.LoadFont(os.path.join(terminus_path, 'ter-u22b.bdf'))

            cls.ter_u24b = graphics.Font()
            cls.ter_u24b.LoadFont(os.path.join(terminus_path, 'ter-u24b.bdf'))

            cls.ter_u28b = graphics.Font()
            cls.ter_u28b.LoadFont(os.path.join(terminus_path, 'ter-u28b.bdf'))

            cls.ter_u32b = graphics.Font()
            cls.ter_u32b.LoadFont(os.path.join(terminus_path, 'ter-u32b.bdf'))

            cls.symbols = graphics.Font()
            cls.symbols.LoadFont(os.path.join(fonts_path, 'symbols.bdf'))

# Automatically run the font initialization at the time of class definition
Fonts._initialize_fonts()
