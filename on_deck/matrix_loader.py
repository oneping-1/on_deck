"""
This module loads the RGBMatrix and graphics classes from either the
emulator or the real hardware. It checks the platform and command line
arguments to determine which one to load.
"""

use_emulator = False

import os

if os.path.exists("on_deck/use_emulator.txt"):
    with open("on_deck/use_emulator.txt") as f:
        use_emulator = f.read().strip().lower() == "true"
else:
    print("Warning: 'on_deck/use_emulator.txt' not found. Defaulting to hardware.")
    use_emulator = False

if use_emulator:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    print('Using emulator')
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    print('Using hardware')
