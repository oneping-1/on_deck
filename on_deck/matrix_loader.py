import os
import platform

if (platform.system() == 'Windows') or (os.environ.get('use_emulator') == "1"):
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics