"""
This module is used to manage the gamecast on the scoreboard. It is
used to print the gamecast on the scoreboard. The gamecast is a
detailed view of the game that includes the score, inning, count,
runners, umpire details, run expectancy, win probability, pitch
details, hit details, and more.
"""

from typing import List, Union
import copy
from on_deck.fonts import Fonts
from on_deck.colors import Colors
from on_deck.display_manager import DisplayManager

class Gamecast:
    """
    This class is used to manage the gamecast on the scoreboard
    """
    def __init__(self, display_manager: DisplayManager, games: List[dict], game_id: int = -1):
        self.display_manager = display_manager
        self.games = games
        self.game_id = game_id
        self.gamecast_game = copy.deepcopy(games[game_id])

        self._color = Colors.white

        self.ter_u18b = Fonts.ter_u18b
        self.symbols = Fonts.symbols

    def _clear_gamecast(self):
        self.display_manager.clear_section(193, 0, 384, 256)

    def _print_gamecast_line(self, line_num: int, text: Union[str, None]) -> bool:
        if text is None:
            return False

        row = 16 * (line_num + 1)

        self.display_manager.draw_text(self.ter_u18b, 193, row, self._color, text)
        return True

    def _print_gamecast_inning_arrows(self):
        if self.gamecast_game['inning_state'] == 'T':
            self.display_manager.draw_text(self.symbols, 320, 40, self._color, '_')
        elif self.gamecast_game['inning_state'] == 'B':
            self.display_manager.draw_text(self.symbols, 320, 61, self._color, 'w')

    def _print_gamecast_bases(self):
        second_base_column_offset = 347
        second_base_row_offset = 47
        base_length = 5
        base_gap = 2
        base_offset = base_length + base_gap

        bases_list = ['c', 'c', 'c']
        if self.gamecast_game['runners'] & 1:
            bases_list[0] = 'C'
        if self.gamecast_game['runners'] & 2:
            bases_list[1] = 'C'
        if self.gamecast_game['runners'] & 4:
            bases_list[2] = 'C'

        x0 = second_base_column_offset + base_offset
        y0 = second_base_row_offset + base_offset
        self.display_manager.draw_text(self.symbols, x0, y0, self._color, bases_list[0])

        x1 = second_base_column_offset
        y1 = second_base_row_offset
        self.display_manager.draw_text(self.symbols, x1, y1, self._color, bases_list[1])

        x2 = second_base_column_offset - base_offset
        y2 = second_base_row_offset + base_offset
        self.display_manager.draw_text(self.symbols, x2, y2, self._color, bases_list[2])

    def _print_gamecast_outs(self):
        outs_list = ['p', 'p', 'p']

        if self.gamecast_game['count']['outs'] is None:
            pass
        else:
            if self.gamecast_game['count']['outs'] > 0:
                outs_list[0] = 'P'
            if self.gamecast_game['count']['outs'] > 1:
                outs_list[1] = 'P'
            if self.gamecast_game['count']['outs'] > 2:
                outs_list[2] = 'P'

        self.display_manager.draw_text(self.symbols, 344, 60, self._color, outs_list[0])
        self.display_manager.draw_text(self.symbols, 350, 60, self._color, outs_list[1])
        self.display_manager.draw_text(self.symbols, 356, 60, self._color, outs_list[2])

    def _print_gamecast_count(self):
        count = f'{self.gamecast_game["count"]["balls"]}-{self.gamecast_game["count"]["strikes"]}'
        count += f' {self.gamecast_game["count"]["outs"]} Out'
        if self.gamecast_game['count']['outs'] != 1:
            count += 's'
        self._print_gamecast_line(2, count)

    def _print_gamecast_umpire_details(self) -> bool:
        game = self.gamecast_game

        if game['umpire']['num_missed'] is None:
            return False

        if game['umpire']['home_favor'] < 0:
            abv = game['away']['abv']
            favor = -1 * game['umpire']['home_favor']
        else:
            abv = game['home']['abv']
            favor = game['umpire']['home_favor']

        s = f'Ump:+{favor:.2f} {abv} ({game["umpire"]["num_missed"]})'
        self._print_gamecast_line(4, s)

        return True

    def _print_gamecast_run_expectancy_details(self) -> bool:
        game = self.gamecast_game

        if game['run_expectancy']['average_runs'] is None:
            return False

        prt_str = ''
        prt_str += f'Avg:{game["run_expectancy"]["average_runs"]:.2f}'
        prt_str += f'  1+:{game["run_expectancy"]["to_score"]*100:4.1f}%'

        self._print_gamecast_line(5, prt_str)

        return True

    def _print_gamecast_win_probability_details(self):
        game = self.gamecast_game

        if game['win_probability']['away'] is None:
            return False

        away_win = game['win_probability']['away'] * 100
        home_win = game['win_probability']['home'] * 100

        if away_win > home_win:
            win = away_win
            abv = game['away']['abv']
        else:
            win = home_win
            abv = game['home']['abv']

        s = f'Win Prob:{win:.1f}% {abv}'
        self._print_gamecast_line(6, s)

        return True

    def _print_gamecast_pitch_details(self):
        self._print_gamecast_line(8, self.gamecast_game['pitch_details']['description'])

        s = ''
        if self.gamecast_game['pitch_details']['speed'] is not None:
            # Both are either a value or None
            # None on no pitch like step off
            s += f'{self.gamecast_game["pitch_details"]["speed"]} MPH'
            s += f'  Zone:{self.gamecast_game["pitch_details"]["zone"]:>2d}'
        self._print_gamecast_line(9, s)

        self._print_gamecast_line(10, self.gamecast_game['pitch_details']['type'])

    def _print_gamecast_hit_details(self) -> bool:
        game = self.gamecast_game

        if game['hit_details']['distance'] is None:
            # Check for one of the hit details
            return False

        self._print_gamecast_line(12, f'Dist: {game["hit_details"]["distance"]:>5.1f} ft')
        self._print_gamecast_line(13, f'  EV: {game["hit_details"]["exit_velo"]:>5.1f} MPH')
        self._print_gamecast_line(14, f'  LA: {game["hit_details"]["launch_angle"]:>5.1f}°')
        count = f'{self.gamecast_game["count"]["balls"]}-{self.gamecast_game["count"]["strikes"]}'
        count += f' {self.gamecast_game["count"]["outs"]} Out'
        if self.gamecast_game['count']['outs'] != 1:
            count += 's'

        return True

    def print_gamecast(self) -> bool:
        """
        This method is used to print the gamecast on the scoreboard.
        """
        self._clear_gamecast()

        if self.gamecast_game['display_game'] is False:
            return False

        away_row_offset = 14
        home_row_offset = 30
        inning_row_offset = (away_row_offset + home_row_offset) / 2

        self._print_gamecast_line(0, self.gamecast_game['away']['name'])
        self._print_gamecast_line(1, self.gamecast_game['home']['name'])


        away_runs = str(self.gamecast_game['away']['runs'])
        home_runs = str(self.gamecast_game['home']['runs'])

        # Scores
        if len(away_runs) > 1:
            self.display_manager.draw_text(self.ter_u18b, 295, away_row_offset,
                Colors.yellow, away_runs)
        else:
            self.display_manager.draw_text(self.ter_u18b, 300, away_row_offset,
                Colors.yellow, away_runs)
        if len(home_runs) > 1:
            self.display_manager.draw_text(self.ter_u18b, 295, home_row_offset,
                Colors.yellow, home_runs)
        else:
            self.display_manager.draw_text(self.ter_u18b, 300, home_row_offset,
                Colors.yellow, home_runs)


        away_hits = str(self.gamecast_game['away']['hits'])
        home_hits = str(self.gamecast_game['home']['hits'])

        if len(away_hits) > 1:
            self.display_manager.draw_text(self.ter_u18b, 320, away_row_offset,
                self._color, away_hits)
        else:
            self.display_manager.draw_text(self.ter_u18b, 325, away_row_offset,
                self._color, away_hits)
        if len(home_hits) > 1:
            self.display_manager.draw_text(self.ter_u18b, 320, home_row_offset,
                self._color, home_hits)
        else:
            self.display_manager.draw_text(self.ter_u18b, 325, home_row_offset,
                self._color, home_hits)


        away_errors = str(self.gamecast_game['away']['errors'])
        home_errors = str(self.gamecast_game['home']['errors'])

        self.display_manager.draw_text(self.ter_u18b, 345, away_row_offset,
            self._color, away_errors)
        self.display_manager.draw_text(self.ter_u18b, 345, home_row_offset,
            self._color, home_errors)


        away_lob = str(self.gamecast_game['away']['left_on_base'])
        home_lob = str(self.gamecast_game['home']['left_on_base'])

        if len(away_lob) > 1:
            self.display_manager.draw_text(self.ter_u18b, 360, away_row_offset,
                self._color, away_lob)
        else:
            self.display_manager.draw_text(self.ter_u18b, 365, away_row_offset,
                self._color, away_lob)
        if len(home_lob) > 1:
            self.display_manager.draw_text(self.ter_u18b, 360, home_row_offset,
                self._color, home_lob)
        else:
            self.display_manager.draw_text(self.ter_u18b, 365, home_row_offset,
                self._color, home_lob)


        # Inning
        inning = str(self.gamecast_game['inning'])

        if len(inning) > 1:
            self.display_manager.draw_text(self.ter_u18b, 315, inning_row_offset+32,
                self._color, inning)
        else:
            self.display_manager.draw_text(self.ter_u18b, 320, inning_row_offset+32,
                self._color, inning)

        self._print_gamecast_inning_arrows()
        self._print_gamecast_bases()
        self._print_gamecast_outs()
        self._print_gamecast_count()
        self._print_gamecast_umpire_details()
        self._print_gamecast_run_expectancy_details()
        self._print_gamecast_win_probability_details()
        self._print_gamecast_pitch_details()
        self._print_gamecast_hit_details()

        self.display_manager.swap_frame()
        return True
