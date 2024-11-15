import math

from on_deck2.display_manager import DisplayManager
from on_deck2.colors import Colors
from on_deck2.fonts import Fonts

class Overview:
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager

        self.ter_u28b = Fonts.ter_u28b

        self._ddo = 7 # double digit offset
        self._games_per_column = 6

    def _calculate_offset(self, i):
        column = math.floor(i / self._games_per_column) # column number
        column_offset = column * 128

        row_offset = 20
        row_offset += (i - self._games_per_column * column) * 42
        return (column_offset, row_offset)

    def _calculate_color(self, i):
        column = math.floor(i / self._games_per_column)
        middle_column = column & 1

        if i % 2 == middle_column:
            return Colors.white
        return Colors.green

    def _print_scores(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 50

        away_score = str(game['away']['runs'])
        home_score = str(game['home']['runs'])

        if len(away_score) > 1:
            self.display_manager.draw_text(self.ter_u28b, column_offset-self._ddo,
                row_offset, color, away_score)
        else:
            self.display_manager.draw_text(self.ter_u28b, column_offset,
                row_offset, color, away_score)

        if len(home_score) > 1:
            self.display_manager.draw_text(self.ter_u28b, column_offset-self._ddo,
                row_offset+20, color, home_score)
        else:
            self.display_manager.draw_text(self.ter_u28b, column_offset,
                row_offset+20, color, home_score)

    def _print_inning(self, game: dict, i: int, text: str = None):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 74
        row_offset += 10

        if text is not None:
            self.display_manager.draw_text(self.ter_u28b, column_offset,
                row_offset, color, text)
            return

        inning = game['inning']
        inning = str(inning)

        if len(inning) > 1:
            self.display_manager.draw_text(self.ter_u28b, column_offset-self._ddo,
                row_offset, color, inning)
        else:
            self.display_manager.draw_text(self.ter_u28b, column_offset,
                row_offset, color, inning)
        return

    def _print_inning_arrows(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 80

        inning_state = game['inning_state']

        if inning_state == 'T':
            self.display_manager.draw_inning_arrow(column_offset, row_offset-11, 7, True, color)
        elif inning_state == 'B':
            self.display_manager.draw_inning_arrow(column_offset, row_offset+12, 7, False, color)

    def _print_bases(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 109
        row_offset -= 8

        radius = 6
        thickness = 2
        delta = radius + 2 # could set this to 0 to make the bases touch

        runners_int = game['runners']
        runners = [False, False, False]
        for j in range(3):
            if runners_int & (1 << i):
                runners[j] = True

        self.display_manager.draw_diamond(column_offset+delta, row_offset+delta, radius,
            thickness, runners[0], color)
        self.display_manager.draw_diamond(column_offset, row_offset, radius,
            thickness, runners[1], color)
        self.display_manager.draw_diamond(column_offset-delta, row_offset+delta, radius,
            thickness, runners[2], color)

    def _print_outs(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 109
        row_offset += 12

        radius = 3
        thickness = 1
        delta = radius + 5

        outs_int = game['count']['outs']

        if outs_int is None:
            return

        outs = [False, False, False]
        for j in range(3):
            if outs_int > j:
                outs[j] = False

        self.display_manager.draw_circle(column_offset+delta, row_offset, radius,
            thickness, outs[0], color)
        self.display_manager.draw_circle(column_offset, row_offset, radius,
            thickness, outs[1], color)
        self.display_manager.draw_circle(column_offset-delta, row_offset, radius,
            thickness, outs[2], color)
        return

    def print_game(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        away_team = game['away']['abv']
        home_team = game['home']['abv']

        self.display_manager.draw_text(self.ter_u28b, column_offset,
            row_offset, color, away_team)
        self.display_manager.draw_text(self.ter_u28b, column_offset,
            row_offset+20, color, home_team)

        game_state = game['game_state']

        self._print_scores(game, i)
        # self._print_inning(game, i, 'F') if game['inning'] == 9 else self._print_inning(game, i, f'F/{game["inning"]}')
        self._print_inning(game, i)
        self._print_inning_arrows(game, i)
        self._print_bases(game, i)
        self._print_outs(game, i)

if __name__ == '__main__':
    print('wrong module dummy')
