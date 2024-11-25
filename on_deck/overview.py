import math
import datetime

from on_deck.display_manager import DisplayManager
from on_deck.colors import Colors
from on_deck.fonts import Fonts

class Overview:
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager

        self.ter_u28b = Fonts.ter_u28b

        self._ddo = 7 # double digit offset
        self._games_per_column = 6

    def clear_game(self, i: int):
        column_offset, row_offset = self._calculate_offset(i)

        row_offset -= 20

        self.display_manager.clear_section(column_offset, row_offset,
            column_offset + 128, row_offset + 42)

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

    def _print_text(self, text: str, column_offset: int, row_offset: int, font, i: int):
        c, r = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += c
        row_offset += r + 10

        self.display_manager.draw_text(font, column_offset,
            row_offset, color, text)

    def _print_inning(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 74
        row_offset += 10

        inning = game['inning']
        inning = str(inning)

        if len(inning) > 1:
            self.display_manager.draw_text(self.ter_u28b, column_offset-self._ddo,
                row_offset, color, inning)
        else:
            self.display_manager.draw_text(self.ter_u28b, column_offset,
                row_offset, color, inning)

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
            if runners_int & (1 << j):
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
                outs[j] = True

        self.display_manager.draw_circle(column_offset-delta, row_offset, radius,
            thickness, outs[0], color)
        self.display_manager.draw_circle(column_offset, row_offset, radius,
            thickness, outs[1], color)
        self.display_manager.draw_circle(column_offset+delta, row_offset, radius,
            thickness, outs[2], color)
        return

    def _print_start_time(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 50
        row_offset += 10

        start_time = game['start_time']
        if len(start_time) < 5:
            start_time = ' ' + start_time

        self.display_manager.draw_text(self.ter_u28b, column_offset,
            row_offset, color, start_time)

    def print_game(self, game: dict, i: int):
        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        self.clear_game(i)

        if game is None:
            return

        away_team = game['away']['abv']
        home_team = game['home']['abv']

        self.display_manager.draw_text(self.ter_u28b, column_offset,
            row_offset, color, away_team)
        self.display_manager.draw_text(self.ter_u28b, column_offset,
            row_offset+20, color, home_team)

        game_state = game['game_state']

        # Live
        if game_state == 'L':
            self._print_scores(game, i)
            self._print_inning(game, i)
            self._print_inning_arrows(game, i)
            self._print_bases(game, i)
            self._print_outs(game, i)

        # Final
        elif game_state == 'F':
            self._print_scores(game, i)
            inning = game['inning']
            if inning == 9:
                self._print_text('F', 74, 0, self.ter_u28b, i)
            else:
                # Multiple print statements to squeeze the text into
                # tight space
                self._print_text('F', 74, 0, self.ter_u28b, i)
                self._print_text('/', 84, 0, self.ter_u28b, i)
                self._print_text(f'{inning}', 94, 0, self.ter_u28b, i)

        # Pregame
        elif game_state == 'P':
            self._print_start_time(game, i)

        # Suspended / Postposed
        elif game_state == 'S':
            self._print_scores(game, i)
            self._print_inning(game, i)
            self._print_text('SUSP', 92, -4, Fonts.ter_u16b, i)

        # Delay
        elif game_state == 'D':
            self._print_scores(game, i)
            self._print_inning(game, i)
            self._print_inning_arrows(game, i)
            self._print_text('DLY', 92, -4, Fonts.ter_u16b, i)

    def _time_delta_strftime(self, delay: int) -> str:
        """
        Prints delay seconds in a format to the strftime("%I:%M:%S")
        to match current time and delay time

        Args:
            delay (int): Delay in seconds

        Returns:
            str: Formatted time string
        """
        hours = math.floor(delay / 3600)
        minutes = math.floor((delay - hours * 3600) / 60)
        seconds = delay - hours * 3600 - minutes * 60

        if hours == 0 and minutes == 0:
            return f'      {seconds:2}'
        if hours == 0:
            return f'   {minutes:2}:{seconds:02}'
        return f'{hours:2}:{minutes:02}:{seconds:02}'

    def print_time(self, delay: int, i: int):
        # Texts need to move to better looking location
        # But all the logic is here
        self.clear_game(i)

        column_offset, row_offset = self._calculate_offset(i)
        color = self._calculate_color(i)

        column_offset += 33

        current_time = datetime.datetime.now()
        delay_delta = datetime.timedelta(seconds=delay)
        delay_time = current_time - delay_delta

        current_time = current_time.strftime('%I:%M:%S')
        delay_time = delay_time.strftime('%I:%M:%S')
        delay = self._time_delta_strftime(delay)

        # gets rid of leading 0
        # but centers it like the 0 is still there
        if current_time[0] == '0':
            current_time = ' ' + current_time[1:]
        if delay_time[0] == '0':
            delay_time = ' ' + delay_time[1:]

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset,
            row_offset-6, color, current_time)

        self.display_manager.draw_text(Fonts.ter_u16b, column_offset,
            row_offset+6, color, delay_time)

        if len(delay) > 8:
            # incase delay is super large
            # like it is in offseason testing
            column_offset -= (8 * (len(delay) - 8))
        self.display_manager.draw_text(Fonts.ter_u16b, column_offset,
            row_offset+18, color, delay)

        self.display_manager.swap_frame()

if __name__ == '__main__':
    print('wrong module dummy')
