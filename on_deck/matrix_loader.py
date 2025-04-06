"""
This module loads the RGBMatrix and graphics classes from either the
emulator or the real hardware. It checks the platform and command line
arguments to determine which one to load.
"""
import platform
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--use-emulator', action='store_true')
args = parser.parse_args()
if args.use_emulator:
    USE_EMULATOR = True
    print('loading emulator')
else:
    USE_EMULATOR = False

if (platform.system() == 'Windows') or USE_EMULATOR:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
    print('emulator')
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
    print('real')
