from typing import List
import math
import time
import platform
from src.scoreboard_data import ScoreboardData
from src.statsapi_plus import get_daily_gamepks

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

def get_options() -> RGBMatrixOptions:
    options = RGBMatrixOptions()

    if platform.system() == 'Windows':
        options.rows = int(256)
        options.cols = int(384)
    else:
        options.cols = 128
        options.rows = 64
        options.hardware_mapping = 'V-mapper'
        options.chain_length = 3
        options.parallel = 4

        options.pwm_bits = 7
        # dither?

    return options


class Scoreboard:
    def __init__(self):
        self.games: List[ScoreboardData] = []

        self.GAMES_PER_COLUMN = 5

        # Matrix Setup
        self.options = get_options()
        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()
        self.text = graphics.Font()
        self.text.LoadFont('fonts/Terminus/ter-u32b.bdf')
        # ter-u32b.bdf:
        # Letter height = 20 pixels = 38 mm = 1.496 in
        # Slighly larger than OnDeck1 (36 mm)
        self.symbols = graphics.Font()
        self.symbols.LoadFont('fonts/symbols.bdf')

        # Matrix Colors
        self.my_white = graphics.Color(255, 255, 255)
        self.my_red = graphics.Color(255, 0, 0)
        self.my_green = graphics.Color(0, 255, 0)
        self.my_blue = graphics.Color(0, 0, 255)
        self.my_black = graphics.Color(0, 0, 0)
        self.my_grey = graphics.Color(20, 20, 20)
        self.matrix.Fill(20, 20, 20)

    def _calculate_offsets(self, index: int):
        row_offset = 50*index
        column_offset = 0

        if index >= self.GAMES_PER_COLUMN:
            column_offset = 384/2
            row_offset = 50*(index - self.GAMES_PER_COLUMN)

        return (row_offset, column_offset)

    def _clear_game(self, index: int):
        row_offset, column_offset = self._calculate_offsets(index)

        for i in range(50):
            graphics.DrawLine(self.canvas, 0 + column_offset, i + row_offset, 192 + column_offset, i + row_offset, self.my_grey)

    def _print_scores(self, row_offset, away_row_offset, home_row_offset, column_offset, game: ScoreboardData, color):
        # Team Scores
        if game.away_score > 9:
            graphics.DrawText(self.canvas, self.text, 55 + column_offset,
                away_row_offset + row_offset, color, str(game.away_score))
        else:
            graphics.DrawText(self.canvas, self.text, 63 + column_offset,
                away_row_offset + row_offset, color, str(game.away_score))

        if game.home_score > 9:
            graphics.DrawText(self.canvas, self.text, 55 + column_offset,
                home_row_offset + row_offset, color, str(game.home_score))
        else:
            graphics.DrawText(self.canvas, self.text, 63 + column_offset,
                home_row_offset + row_offset, color, str(game.home_score))

    def _print_inning(self, row_offset, column_offset, inning_row_offset, game: ScoreboardData, color):
        if game.game_state == 'F':
            if game.inning != 9:
                graphics.DrawText(self.canvas, self.text,  92 + column_offset,
                    inning_row_offset + row_offset, color, f'F/{game.inning}')
            else:
                graphics.DrawText(self.canvas, self.text, 100 + column_offset,
                    inning_row_offset + row_offset, color, 'F')
            return 0
        elif game.game_state == 'P':
            if len(game.start_time) > 4:
                graphics.DrawText(self.canvas, self.text, 100 - 18 - 20 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.start_time}')
            else:
                graphics.DrawText(self.canvas, self.text, 100 - 20 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.start_time}')
            return 0
        elif game.game_state == 'S':
            if game.inning != 9:
                graphics.DrawText(self.canvas, self.text,  92 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.inning} Susp')
            else:
                graphics.DrawText(self.canvas, self.text, 100 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.inning} Susp')
            return 0
        elif game.game_state == 'D':
            if game.inning != 9:
                graphics.DrawText(self.canvas, self.text,  92 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.inning} Dly')
            else:
                graphics.DrawText(self.canvas, self.text, 100 + column_offset,
                    inning_row_offset + row_offset, color, f'{game.inning} Dly')
            return 0

        if game.inning > 9:
            graphics.DrawText(self.canvas, self.text,  92 + column_offset,
                inning_row_offset + row_offset, color, f'{game.inning}')
        else:
            graphics.DrawText(self.canvas, self.text, 100 + column_offset,
                inning_row_offset + row_offset, color, f'{game.inning}')

        if game.inning_state == 'T':
            graphics.DrawText(self.canvas, self.symbols, 100 + column_offset,
                11 + row_offset, color, '^')
        elif game.inning_state == 'B':
            graphics.DrawText(self.canvas, self.symbols, 100 + column_offset,
                43 + row_offset, color, 'v')

    def _print_outs(self, row_offset, column_offset, game: ScoreboardData, color):
        outs_list = ['o', 'o', 'o']

        if game.outs is None:
            pass
        else:
            if game.outs > 0:
                outs_list[0] = 'O'
            if game.outs > 1:
                outs_list[1] = 'O'
            if game.outs > 2:
                outs_list[2] = 'O'

        # outs_column_offset = 177

        graphics.DrawText(self.canvas, self.symbols, 130 + column_offset, 43 + row_offset, color, outs_list[0])
        graphics.DrawText(self.canvas, self.symbols, 142 + column_offset, 43 + row_offset, color, outs_list[1])
        graphics.DrawText(self.canvas, self.symbols, 154 + column_offset, 43 + row_offset, color, outs_list[2])

    def _print_runners(self, row_offset, column_offset, game: ScoreboardData, color):
        second_base_column_offset = 137
        second_base_row_offset = 22
        base_length = 9
        base_gap = 2
        base_offset = base_length + base_gap

        bases_list = ['b', 'b', 'b']
        if game.runners & 1:
            bases_list[0] = 'B'
        if game.runners & 2:
            bases_list[1] = 'B'
        if game.runners & 4:
            bases_list[2] = 'B'

        graphics.DrawText(self.canvas, self.symbols, second_base_column_offset + base_offset + column_offset,
            second_base_row_offset + base_offset + row_offset, color, bases_list[0])

        graphics.DrawText(self.canvas, self.symbols, second_base_column_offset + column_offset,
            second_base_row_offset + row_offset, color, bases_list[1])

        graphics.DrawText(self.canvas, self.symbols, second_base_column_offset - base_offset + column_offset,
            second_base_row_offset + base_offset + row_offset, color, bases_list[2])

    def print_game(self, index: int, game: ScoreboardData):

        # graphics.DrawLine(canvas, 127, 0, 127, 384, my_red)
        # graphics.DrawLine(canvas, 128, 0, 128, 384, my_blue)

        self._clear_game(index)

        if game is None:
            return 0

        row_offset, column_offset = self._calculate_offsets(index)

        away_row_offset = 22
        home_row_offset = 44
        inning_row_offset = (away_row_offset + home_row_offset) / 2

        if index % 2 == 0:
            color = self.my_white
        else:
            color = self.my_green

        # Team Abvreviations
        graphics.DrawText(self.canvas, self.text, 0 + column_offset,
            away_row_offset + row_offset, color, game.away_abv)

        graphics.DrawText(self.canvas, self.text, 0 + column_offset,
            home_row_offset + row_offset, color, game.home_abv)

        if game.game_state == 'F':
            self._print_scores(row_offset, away_row_offset, home_row_offset, column_offset, game, color)
            # Printing F is handled in _print_inning
            self._print_inning(row_offset, column_offset, inning_row_offset, game, color)
        elif game.game_state == 'L':
            self._print_scores(row_offset, away_row_offset, home_row_offset, column_offset, game, color)
            self._print_inning(row_offset, column_offset, inning_row_offset, game, color)
            self._print_outs(row_offset, column_offset, game, color)
            self._print_runners(row_offset, column_offset, game, color)
        elif game.game_state == 'P':
            self._print_inning(row_offset, column_offset, inning_row_offset, game, color)
        elif game.game_state == 'S':
            self._print_scores(row_offset, away_row_offset, home_row_offset, column_offset, game, color)
            self._print_inning(row_offset, column_offset, inning_row_offset, game, color)
        elif game.game_state == 'D':
            self._print_scores(row_offset, away_row_offset, home_row_offset, column_offset, game, color)
            self._print_inning(row_offset, column_offset, inning_row_offset, game, color)

        # # Team Scores
        # self._print_scores(row_offset, away_row_offset, home_row_offset, column_offset, game, color)

        # # Inning
        # self._print_inning(row_offset, column_offset, inning_row_offset, game, color)

        # # Outs
        # self._print_outs(row_offset, column_offset, game, color)

        # # Print Runners
        # self._print_runners(row_offset, column_offset, game, color)

    def print_games(self, double_columns: bool = True):
        total_games = len(self.games)
        total_pages = math.ceil(total_games / self.GAMES_PER_COLUMN)

        if double_columns is True:
            max_games = self.GAMES_PER_COLUMN * 2
        else:
            max_games = self.GAMES_PER_COLUMN

        for page in range(total_pages):
            offset = page * self.GAMES_PER_COLUMN

            shifted_games = [None] * total_pages * self.GAMES_PER_COLUMN

            for i, game in enumerate(self.games):
                shifted_games[i] = game

            shifted_games = shifted_games[offset:] + shifted_games[:offset]
            shifted_games = shifted_games[:max_games]

            for i, game in enumerate(shifted_games):
                self.print_game(i, game)

            graphics.DrawLine(self.canvas, 0, 255, 5, 255, self.my_black)
            graphics.DrawLine(self.canvas, 0, 255, page, 255, self.my_white)
            self.matrix.SwapOnVSync(self.canvas)
            time.sleep(5)

    def start(self, delay_seconds: int):
        while True:
            self.games = self.games = [ScoreboardData(gamepk) for gamepk in get_daily_gamepks()]
            self.print_games()

if __name__ == '__main__':
    scoreboard = Scoreboard()
    scoreboard.start(0)
