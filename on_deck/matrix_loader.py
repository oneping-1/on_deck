from on_deck.emulator_checker import is_emulator

if is_emulator() is True:
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
