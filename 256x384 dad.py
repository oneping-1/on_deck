from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
from PIL import Image

def get_options() -> RGBMatrixOptions:
    options = RGBMatrixOptions()

    options.rows = 256
    options.cols = int(384/1)

    return options


def main():
    options = get_options()

    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()
    canvas.Fill(20, 20, 20)

    arial = graphics.Font()
    arial.LoadFont("ttf2bdf/Arial Narrow-21-r.bdf")

    my_green = graphics.Color(0, 255, 0)
    my_white = graphics.Color(255, 255, 255)

    b = Image.open("symbols/b.png")
    b = b.resize((16, 16))

    O = Image.open("symbols/O.png")
    O = O.resize((12, 12))

    graphics.DrawText(canvas, arial, 40, 21, my_white, "AL West")
    graphics.DrawText(canvas, arial, 22, 42, my_white, "TEX")
    graphics.DrawText(canvas, arial, 22, 63, my_white, "HOU")
    rangers = Image.open("logos/rangers.png")
    rangers = rangers.resize((21, 21))
    canvas.SetImage(rangers.convert("RGB"), 1, 21)
    graphics.DrawText(canvas, arial, 90, 42, my_white, "0")
    graphics.DrawText(canvas, arial, 90, 63, my_white, "2")
    graphics.DrawText(canvas, arial, 120, 53, my_white, "1")
    canvas.SetImage(b.convert("RGB"), 152, 32)
    canvas.SetImage(b.convert("RGB"), 162, 22)
    canvas.SetImage(b.convert("RGB"), 172, 32)
    canvas.SetImage(O.convert("RGB"), 150, 51)
    canvas.SetImage(O.convert("RGB"), 164, 51)
    canvas.SetImage(O.convert("RGB"), 178, 51)

    graphics.DrawText(canvas, arial, 22, 84, my_green, "TEX")
    graphics.DrawText(canvas, arial, 22, 105, my_green, "HOU")
    astros = Image.open("logos/astros.png")
    astros = astros.resize((21, 21))
    canvas.SetImage(astros.convert("RGB"), 1, 84)
    graphics.DrawText(canvas, arial, 90, 84, my_green, "4")
    graphics.DrawText(canvas, arial, 90, 105, my_green, "6")
    graphics.DrawText(canvas, arial, 120, 95, my_white, "3")
    canvas.SetImage(b.convert("RGB"), 152, 74)
    canvas.SetImage(b.convert("RGB"), 162, 64)
    canvas.SetImage(b.convert("RGB"), 172, 74)
    canvas.SetImage(O.convert("RGB"), 150, 93)
    canvas.SetImage(O.convert("RGB"), 164, 93)
    canvas.SetImage(O.convert("RGB"), 178, 93)


    graphics.DrawText(canvas, arial, 22, 126, my_white, "SEA")
    graphics.DrawText(canvas, arial, 22, 147, my_white, "NYY")
    mariners = Image.open("logos/mariners.png")
    mariners = mariners.resize((21, 21))
    canvas.SetImage(mariners.convert("RGB"), 1, 105)
    graphics.DrawText(canvas, arial, 90, 126, my_white, "8")
    graphics.DrawText(canvas, arial, 83, 147, my_white, "10")
    graphics.DrawText(canvas, arial, 120, 137, my_white, "5")
    canvas.SetImage(b.convert("RGB"), 152, 116)
    canvas.SetImage(b.convert("RGB"), 162, 106)
    canvas.SetImage(b.convert("RGB"), 172, 116)
    canvas.SetImage(O.convert("RGB"), 150, 135)
    canvas.SetImage(O.convert("RGB"), 164, 135)
    canvas.SetImage(O.convert("RGB"), 178, 135)


    graphics.DrawText(canvas, arial, 22, 168, my_green, "CLE")
    graphics.DrawText(canvas, arial, 22, 189, my_green, "LAA")
    angels = Image.open("logos/angels.png")
    angels = angels.resize((21, 21))
    canvas.SetImage(angels.convert("RGB"), 1, 168)
    graphics.DrawText(canvas, arial, 83, 168, my_green, "12")
    graphics.DrawText(canvas, arial, 83, 189, my_green, "14")
    graphics.DrawText(canvas, arial, 120, 179, my_white, "7")
    canvas.SetImage(b.convert("RGB"), 152, 158)
    canvas.SetImage(b.convert("RGB"), 162, 148)
    canvas.SetImage(b.convert("RGB"), 172, 158)
    canvas.SetImage(O.convert("RGB"), 150, 177)
    canvas.SetImage(O.convert("RGB"), 164, 177)
    canvas.SetImage(O.convert("RGB"), 178, 177)


    graphics.DrawText(canvas, arial, 22, 210, my_white, "OAK")
    graphics.DrawText(canvas, arial, 22, 231, my_white, "BOS")
    athletics = Image.open("logos/as.png")
    athletics = athletics.resize((21, 21))
    canvas.SetImage(athletics.convert("RGB"), 1, 189)
    graphics.DrawText(canvas, arial, 83, 210, my_white, "16")
    graphics.DrawText(canvas, arial, 83, 231, my_white, "18")
    graphics.DrawText(canvas, arial, 120, 221, my_white, "9")
    canvas.SetImage(b.convert("RGB"), 152, 200)
    canvas.SetImage(b.convert("RGB"), 162, 190)
    canvas.SetImage(b.convert("RGB"), 172, 200)
    canvas.SetImage(O.convert("RGB"), 150, 219)
    canvas.SetImage(O.convert("RGB"), 164, 219)
    canvas.SetImage(O.convert("RGB"), 178, 219)



    graphics.DrawText(canvas, arial, 252, 21, my_green, "NL West")

    graphics.DrawText(canvas, arial, 218, 42, my_white, "CIN")
    graphics.DrawText(canvas, arial, 218, 63, my_white, "LAD")
    dodgers = Image.open("logos/dodgers.png")
    dodgers = dodgers.resize((21, 21))
    canvas.SetImage(dodgers.convert("RGB"), 200, 42)
    graphics.DrawText(canvas, arial, 274, 42, my_white, "20")
    graphics.DrawText(canvas, arial, 274, 63, my_white, "22")
    graphics.DrawText(canvas, arial, 311, 53, my_white, "11")
    canvas.SetImage(b.convert("RGB"), 343, 32)
    canvas.SetImage(b.convert("RGB"), 353, 22)
    canvas.SetImage(b.convert("RGB"), 363, 32)
    canvas.SetImage(O.convert("RGB"), 341, 51)
    canvas.SetImage(O.convert("RGB"), 355, 51)
    canvas.SetImage(O.convert("RGB"), 369, 51)


    graphics.DrawText(canvas, arial, 218, 84, my_green, "SF")
    graphics.DrawText(canvas, arial, 218, 105, my_green, "PIT")
    giants = Image.open("logos/giants.png")
    giants = giants.resize((21, 21))
    canvas.SetImage(giants.convert("RGB"), 200, 84)
    graphics.DrawText(canvas, arial, 274, 84, my_green, "24")
    graphics.DrawText(canvas, arial, 274, 105, my_green, "26")
    graphics.DrawText(canvas, arial, 311, 95, my_white, "13")
    canvas.SetImage(b.convert("RGB"), 343, 74)
    canvas.SetImage(b.convert("RGB"), 353, 64)
    canvas.SetImage(b.convert("RGB"), 363, 74)
    canvas.SetImage(O.convert("RGB"), 341, 93)
    canvas.SetImage(O.convert("RGB"), 355, 93)
    canvas.SetImage(O.convert("RGB"), 369, 93)


    graphics.DrawText(canvas, arial, 218, 126, my_white, "AZ")
    graphics.DrawText(canvas, arial, 218, 147, my_white, "STL")
    diamondbacks = Image.open("logos/dbacks.png")
    diamondbacks = diamondbacks.resize((21, 21))
    canvas.SetImage(diamondbacks.convert("RGB"), 200, 105)
    graphics.DrawText(canvas, arial, 274, 126, my_white, "28")
    graphics.DrawText(canvas, arial, 274, 147, my_white, "30")
    graphics.DrawText(canvas, arial, 311, 137, my_white, "15")
    canvas.SetImage(b.convert("RGB"), 343, 116)
    canvas.SetImage(b.convert("RGB"), 353, 106)
    canvas.SetImage(b.convert("RGB"), 363, 116)
    canvas.SetImage(O.convert("RGB"), 341, 135)
    canvas.SetImage(O.convert("RGB"), 355, 135)
    canvas.SetImage(O.convert("RGB"), 369, 135)


    graphics.DrawText(canvas, arial, 218, 168, my_green, "COL")
    graphics.DrawText(canvas, arial, 218, 189, my_green, "SD")
    padres = Image.open("logos/padres.png")
    padres = padres.resize((21, 21))
    canvas.SetImage(padres.convert("RGB"), 200, 168)
    graphics.DrawText(canvas, arial, 274, 168, my_green, "32")
    graphics.DrawText(canvas, arial, 274, 189, my_green, "34")
    graphics.DrawText(canvas, arial, 311, 179, my_white, "17")
    canvas.SetImage(b.convert("RGB"), 343, 158)
    canvas.SetImage(b.convert("RGB"), 353, 148)
    canvas.SetImage(b.convert("RGB"), 363, 158)
    canvas.SetImage(O.convert("RGB"), 341, 177)
    canvas.SetImage(O.convert("RGB"), 355, 177)
    canvas.SetImage(O.convert("RGB"), 369, 177)


    graphics.DrawText(canvas, arial, 218, 210, my_white, "COL")
    graphics.DrawText(canvas, arial, 218, 231, my_white, "SD")
    rockies = Image.open("logos/rockies.png")
    rockies = rockies.resize((21, 21))
    canvas.SetImage(rockies.convert("RGB"), 200, 189)
    graphics.DrawText(canvas, arial, 274, 210, my_white, "36")
    graphics.DrawText(canvas, arial, 274, 231, my_white, "38")
    graphics.DrawText(canvas, arial, 311, 221, my_white, "19")
    canvas.SetImage(b.convert("RGB"), 343, 200)
    canvas.SetImage(b.convert("RGB"), 353, 190)
    canvas.SetImage(b.convert("RGB"), 363, 200)
    canvas.SetImage(O.convert("RGB"), 341, 219)
    canvas.SetImage(O.convert("RGB"), 355, 219)
    canvas.SetImage(O.convert("RGB"), 369, 219)


    matrix.SwapOnVSync(canvas)

    while True:
        pass

if __name__ == '__main__':
    main()
