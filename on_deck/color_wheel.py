from on_deck.display_manager import DisplayManager
from on_deck.matrix_loader import RGBMatrixOptions, graphics
from on_deck.emulator_checker import is_emulator
from on_deck.colors import Colors
from on_deck.fonts import Fonts

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    if is_emulator() is True:
        options.cols = int(384)
        options.rows = int(256)
    else:
        options.cols = 128
        options.rows = 64
        options.pixel_mapper_config = 'V-mapper'
        options.chain_length = 4
        options.parallel = 3
        options.disable_hardware_pulsing = True
        options.pwm_bits = 4
        options.gpio_slowdown = 4
        options.pwm_dither_bits = 2
        options.pwm_lsb_nanoseconds = 130

    return options

display_manager = DisplayManager(get_options())

pwm_bits = 4
offset = 20
spacing = 20
box_size = 18

# G=
for i in range(pwm_bits):
    x = offset-20
    y = offset+(spacing*i)+13

    display_manager.draw_text(Fonts.ter_u12b, x, y, Colors.white, f'G={i}')

# R=
for i in range(pwm_bits):
    for j in range(pwm_bits):
        x = offset + (spacing*i) + ((spacing+1)*pwm_bits*j)
        y = offset

        display_manager.draw_text(Fonts.ter_u12b, x, y, Colors.white, f'R={i}')

# B=
for i in range(pwm_bits):
    x = offset + ((spacing+1)*pwm_bits*i) + 30
    y = offset-10

    display_manager.draw_text(Fonts.ter_u12b, x, y, Colors.white, f'B={i}')


for i in range(pwm_bits):
    for j in range(pwm_bits):
        for k in range(pwm_bits):
            x1 = offset + spacing*i
            y1 = offset + spacing*j
            x2 = x1 + box_size
            y2 = y1 + box_size

            x1 += ((spacing+1)*pwm_bits*k)
            x2 += ((spacing+1)*pwm_bits*k)

            color = graphics.Color(255*i/(pwm_bits-1), 255*j/(pwm_bits-1), 255*k/(pwm_bits-1))

            display_manager.draw_box(x1, y1, x2, y2, color, True)

display_manager.set_brightness(255)

while True:
    display_manager.swap_frame()
