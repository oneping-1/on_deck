"""
This module is used to manage the scoreboard for the onDeck project.
The scoreboard is used to display game data on a 384x256 pixel screen.
The scoreboard can display games in a basic, dual, or detailed mode.
The scoreboard can also display a gamecast mode which shows detailed
information about a single game.

Raises:
    ValueError: If an invalid mode is passed
"""

from typing import List
import time
import math
from on_deck.display_manager import DisplayManager

class AllGames:
    """
    This class is used to manage all the games on the scoreboard
    """
    def __init__(self, display_manager: DisplayManager, games: List[dict], mode: str = 'basic'):
        self.display_manager = display_manager
        self.games = games

        self.mode: str = None

        self.ter_u32b = self.display_manager.fonts.ter_u32b
        self.ter_u18b = self.display_manager.fonts.ter_u18b
        self.symbols = self.display_manager.fonts.symbols

        self._new_mode: str = mode
        self.num_pages: int = None

        self.page: int = 0

        # Scoreboard Offsets
        self.away_row_offset = 22
        self.home_row_offset = 44
        self.inning_row_offset = (self.away_row_offset + self.home_row_offset) / 2
        self.inning_column_offset = 100
        self.time_offset = -25

        # Detail Mode Offsets
        self.two_line_offset = 7

        self._gamecast_color = self.display_manager.colors.white

    def _print_line_a(self, color, column_offset, row_offset, line_a):
        # graphics.DrawText(self.display_manager.canvas, self.ter_u18b,
        #     175 + column_offset, 14 + row_offset, color, line_a)

        self.display_manager.draw_text(self.ter_u18b, 175 + column_offset,
            14 + row_offset, color, line_a)

    def _print_line_b(self, color, column_offset, row_offset, line_b):
        # graphics.DrawText(self.display_manager.canvas, self.ter_u18b,
        #     175 + column_offset, 29 + row_offset, color, line_b)

        self.display_manager.draw_text(self.ter_u18b, 175 + column_offset,
            29 + row_offset, color, line_b)

    def _print_line_c(self, color, column_offset, row_offset, line_c):
        # graphics.DrawText(self.display_manager.canvas, self.ter_u18b,
        #     175 + column_offset, 44 + row_offset, color, line_c)

        self.display_manager.draw_text(self.ter_u18b, 175 + column_offset,
            44 + row_offset, color, line_c)

    def _calculate_offsets(self, index: int):
        row_offset = 50*index
        column_offset = 0

        if index >= 5:
            column_offset = 384/2
            row_offset = 50*(index - 5)

        return (row_offset, column_offset)

    def _calculate_color(self, index: int, game: dict = None):
        if game['flags']['no_hitter'] is True:
            return self.display_manager.colors.red
        if index % 2 == 0:
            return self.display_manager.colors.white
        return self.display_manager.colors.green

    def clear_game(self, index: int):
        """
        Clears the game from the scoreboard

        Args:
            index (int): The index of the game to clear
        """
        row_offset, column_offset = self._calculate_offsets(index)

        if self.mode in ('basic', 'dual', 'gamecast'):
            length = 192
        elif self.mode == 'detailed':
            length = 384
        else:
            raise ValueError(f'Length not specified for mode: {self.mode}')

        x1 = 0 + column_offset
        y1 = 0 + row_offset
        x2 = length + column_offset
        y2 = 50 + row_offset

        self.display_manager.clear_section(x1, y1, x2, y2)

    def _print_scores(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        if game['away_score'] > 9:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     55 + column_offset, self.away_row_offset + row_offset, color,
            #     str(game['away_score']))

            self.display_manager.draw_text(self.ter_u32b, 55 + column_offset,
                self.away_row_offset + row_offset, color, str(game['away_score']))
        else:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     63 + column_offset, self.away_row_offset + row_offset, color,
            #     str(game['away_score']))

            self.display_manager.draw_text(self.ter_u32b, 63 + column_offset,
                self.away_row_offset + row_offset, color, str(game['away_score']))

        if game['home_score'] > 9:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     55 + column_offset, self.home_row_offset + row_offset, color,
            #     str(game['home_score']))

            self.display_manager.draw_text(self.ter_u32b, 55 + column_offset,
                self.home_row_offset + row_offset, color, str(game['home_score']))
        else:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     63 + column_offset, self.home_row_offset + row_offset, color,
            #     str(game['home_score']))

            self.display_manager.draw_text(self.ter_u32b, 63 + column_offset,
                self.home_row_offset + row_offset, color, str(game['home_score']))

    def _print_inning(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        if game['inning'] > 9:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     self.inning_column_offset - 8 + column_offset,
            #     self.inning_row_offset + row_offset, color, f'{game["inning"]}')

            self.display_manager.draw_text(self.ter_u32b,
                self.inning_column_offset - 8 + column_offset,
                self.inning_row_offset + row_offset, color, f'{game["inning"]}')
        else:
            # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
            #     self.inning_column_offset + column_offset,
            #     self.inning_row_offset + row_offset, color, f'{game["inning"]}')

            self.display_manager.draw_text(self.ter_u32b,
                self.inning_column_offset + column_offset,
                self.inning_row_offset + row_offset, color, f'{game["inning"]}')

        if game['inning_state'] == 'T':
            # graphics.DrawText(self.display_manager.canvas, self.symbols,
            #     self.inning_column_offset + column_offset,
            #     11 + row_offset, color, '^')

            self.display_manager.draw_text(self.symbols,
                self.inning_column_offset + column_offset,
                11 + row_offset, color, '^')
        elif game['inning_state'] == 'B':
            # graphics.DrawText(self.display_manager.canvas, self.symbols,
            #     self.inning_column_offset + column_offset,
            #     43 + row_offset, color, 'v')

            self.display_manager.draw_text(self.symbols,
                self.inning_column_offset + column_offset,
                43 + row_offset, color, 'v')

    def _print_text(self, index: int, color, text: str, column_offset: int = 0):
        row_offset, column_offset2 = self._calculate_offsets(index)

        x = self.inning_column_offset + column_offset + column_offset2
        y = self.inning_row_offset + row_offset
        # graphics.DrawText(self.display_manager.canvas, self.ter_u32b, x, y, color, text)
        self.display_manager.draw_text(self.ter_u32b, x, y, color, text)

    def _print_outs(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        outs_list = ['o', 'o', 'o']

        if game['count']['outs'] is None:
            pass
        else:
            if game['count']['outs'] > 0:
                outs_list[0] = 'O'
            if game['count']['outs'] > 1:
                outs_list[1] = 'O'
            if game['count']['outs'] > 2:
                outs_list[2] = 'O'

        # graphics.DrawText(self.display_manager.canvas, self.symbols,
        #     130 + column_offset, 43 + row_offset, color, outs_list[0])
        # graphics.DrawText(self.display_manager.canvas, self.symbols,
        #     142 + column_offset, 43 + row_offset, color, outs_list[1])
        # graphics.DrawText(self.display_manager.canvas, self.symbols,
        #     154 + column_offset, 43 + row_offset, color, outs_list[2])

        self.display_manager.draw_text(self.symbols, 130 + column_offset,
            43 + row_offset, color, outs_list[0])
        self.display_manager.draw_text(self.symbols, 142 + column_offset,
            43 + row_offset, color, outs_list[1])
        self.display_manager.draw_text(self.symbols, 154 + column_offset,
            43 + row_offset, color, outs_list[2])

    def _print_runners(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        second_base_column_offset = 137
        second_base_row_offset = 22
        base_length = 9
        base_gap = 2
        base_offset = base_length + base_gap

        bases_list = ['b', 'b', 'b']
        if game['runners'] & 1:
            bases_list[0] = 'B'
        if game['runners'] & 2:
            bases_list[1] = 'B'
        if game['runners'] & 4:
            bases_list[2] = 'B'

        x0 = second_base_column_offset + base_offset + column_offset
        y0 = second_base_row_offset + base_offset + row_offset
        # graphics.DrawText(self.display_manager.canvas, self.symbols, x0, y0,
        #     color, bases_list[0])

        self.display_manager.draw_text(self.symbols, x0, y0, color, bases_list[0])

        x1 = second_base_column_offset + column_offset
        y1 = second_base_row_offset + row_offset
        # graphics.DrawText(self.display_manager.canvas, self.symbols, x1, y1,
        #     color, bases_list[1])

        self.display_manager.draw_text(self.symbols, x1, y1, color, bases_list[1])

        x2 = second_base_column_offset - base_offset + column_offset
        y2 = second_base_row_offset + base_offset + row_offset
        # graphics.DrawText(self.display_manager.canvas, self.symbols, x2, y2,
        #     color, bases_list[2])

        self.display_manager.draw_text(self.symbols, x2, y2, color, bases_list[2])

    def _print_batter_pitcher(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        line_a = None
        line_c = None

        is_top_inning = True if game['inning_state'] == 'T' else False

        if game['count']['outs'] == 3:
            # After the 3rd out is recorded, the data shows the
            # next half inning's batter and pitcher
            is_top_inning = not is_top_inning

        if is_top_inning is True:
            line_a = f'B:{game["matchup"]["batter"]} ({game["matchup"]["batter_summary"]})'
            line_c = f'P:{game["matchup"]["pitcher"]} ({game["matchup"]["pitcher_summary"]})'

        elif is_top_inning is False:
            line_a = f'P:{game["matchup"]["pitcher"]} ({game["matchup"]["pitcher_summary"]})'
            line_c = f'B:{game["matchup"]["batter"]} ({game["matchup"]["batter_summary"]})'

        if line_a is not None:
            self._print_line_a(color, column_offset, row_offset + self.two_line_offset, line_a)

        if line_c is not None:
            self._print_line_c(color, column_offset, row_offset - self.two_line_offset, line_c)

    def _print_pitcher_decisions(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        away_score = game['away_score']
        home_score = game['home_score']

        win = game['decisions']['win']
        loss = game['decisions']['loss']
        save = game['decisions']['save']

        win_summary = game['decisions']['win_summary']
        loss_summary = game['decisions']['loss_summary']
        save_summary = game['decisions']['save_summary']

        line_a = None
        line_b = None
        line_c = None

        if away_score > home_score:
            line_a = f'WP:{win} ({win_summary})'
            line_c = f'LP:{loss} ({loss_summary})'

            if save is not None:
                line_b = f'SV:{save} ({save_summary})'

        elif home_score > away_score:
            line_a = f'LP:{loss} ({loss_summary})'
            line_c = f'WP:{win} ({win_summary})'

            if save is not None:
                line_b = f'SV:{save} ({save_summary})'

        if line_b is not None:
            delta_y = 0
        else:
            delta_y = self.two_line_offset

        if line_a is not None:
            self._print_line_a(color, column_offset, row_offset + delta_y, line_a)

        if line_b is not None:
            self._print_line_b(color, column_offset, row_offset, line_b)

        if line_c is not None:
            self._print_line_c(color, column_offset, row_offset - delta_y, line_c)

    def _print_probable_pitchers(self, index, color, game):
        row_offset, column_offset = self._calculate_offsets(index)

        line_a = f'SP:{game["probables"]["away"]} ({game["probables"]["away_era"]})'
        line_c = f'SP:{game["probables"]["home"]} ({game["probables"]["home_era"]})'

        if line_a is not None:
            self._print_line_a(color, column_offset, row_offset + self.two_line_offset, line_a)

        if line_c is not None:
            self._print_line_c(color, column_offset, row_offset - self.two_line_offset, line_c)

    def _print_page_indicator(self, page_num: int):
        # graphics.DrawLine(self.display_manager.canvas, 0, 255, 384, 255,
        #     self.display_manager.colors.black)
        self.display_manager.draw_line(0, 255, 384, 255, self.display_manager.colors.black)

        line_length = 5
        gap = 2
        total_length = line_length + gap

        for i in range(page_num+1):
            x0 = 40 + ((i + 1) * total_length)
            x1 = x0 + line_length - 1 # -1 to account for extra character width

            # graphics.DrawLine(self.display_manager.canvas, x0, 255, x1, 255,
            #     self.display_manager.colors.white)
            self.display_manager.draw_line(x0, 255, x1, 255, self.display_manager.colors.white)

    def print_game(self, game_index: int, game: dict):
        """
        Description: This function is used to print a game on the scoreboard.

        Args:
            game_index (int): The index of the game to print
            game (dict): The game data to print
        """
        self.clear_game(game_index)

        if game['display_game'] is False:
            return

        row_offset, column_offset = self._calculate_offsets(game_index)

        color = self._calculate_color(game_index, game)

        # Team Abbreviations

        # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
        #     0 + column_offset, self.away_row_offset + row_offset, color,
        #     game['away']['abv'])

        self.display_manager.draw_text(self.ter_u32b,
            0 + column_offset, self.away_row_offset + row_offset, color,
            game['away']['abv'])

        # graphics.DrawText(self.display_manager.canvas, self.ter_u32b,
        #     0 + column_offset, self.home_row_offset + row_offset, color,
        #     game['home']['abv'])

        self.display_manager.draw_text(self.ter_u32b,
            0 + column_offset, self.home_row_offset + row_offset, color,
            game['home']['abv'])

        # Live
        if game['game_state'] == 'L':
            self._print_scores(game_index, color, game)
            self._print_inning(game_index, color, game)
            self._print_outs(game_index, color, game)
            self._print_runners(game_index, color, game)

        # Final
        elif game['game_state'] == 'F':
            self._print_scores(game_index, color, game)

            if game['inning'] != 9:
                self._print_text(game_index, color, f'F/{game["inning"]}')
            else:
                self._print_text(game_index, color, 'F')

        # Pre-Game
        elif game['game_state'] == 'P':
            if len(game['start_time']) > 4:
                # -16 to account for extra character width
                self._print_text(game_index, color, game['start_time'], self.time_offset - 6)
            else:
                self._print_text(game_index, color, game['start_time'], self.time_offset + 10)

        # Suspendend / Postponed
        elif game['game_state'] == 'S':
            self._print_scores(game_index, color, game)
            self._print_inning(game_index, color, game)

            if self.mode in ('basic', 'dual', 'gamecast'):
                self._print_text(game_index, 'Susp', 25)

        # Delay
        elif game['game_state'] == 'D':
            self._print_scores(game_index, color, game)
            self._print_inning(game_index, color, game)

            if self.mode in ('basic', 'dual', 'gamecast'):
                self._print_text(game_index, 'Dly', 32)

        # Detailed (2 Columns)
        if self.mode != 'detailed':
            return

        # Live
        if game['game_state'] == 'L':
            self._print_batter_pitcher(game_index, color, game)

        # Final
        elif game['game_state'] == 'F':
            self._print_pitcher_decisions(game_index, color, game)

        # Pre-Game
        elif game['game_state'] == 'P':
            self._print_probable_pitchers(game_index, color, game)

        # Suspendend / Postponed
        elif game['game_state'] == 'S':
            self._print_text(game_index, color, 'Suspended', 75)
            self._print_inning(game_index, color, game)
            self._print_runners(game_index, color, game)
            self._print_outs(game_index, color, game)

        # Delay
        elif game['game_state'] == 'D':
            self._print_text(game_index, color, 'Delayed', 75)
            self._print_inning(game_index, color, game)
            self._print_runners(game_index, color, game)
            self._print_outs(game_index, color, game)

    def print_page(self, page_num: int):
        """
        This method is used to print a page of games on the scoreboard.

        Args:
            page_num (int): The page number to print
        """
        max_games = 5 * self.num_pages
        shift_offset = page_num * 5

        shifted_games = [None] * max_games

        for i, game in enumerate(self.games[:max_games]):
            shifted_games[i] = game

        shifted_games = shifted_games[shift_offset:] + shifted_games[:shift_offset]

        if self.mode == 'dual':
            shifted_games = shifted_games[:10]
        else:
            shifted_games = shifted_games[:5]

        for i, game in enumerate(shifted_games):
            self.print_game(i, game)

        self._print_page_indicator(page_num)

        self.display_manager.swap_frame()
        time.sleep(10)

    def _count_games(self) -> int:
        count = 0

        for game in self.games:
            if game['display_game'] is True:
                count += 1

        return count

    def loop(self, mode: str):
        """
        This method is used to loop through the games on the scoreboard.

        Args:
            mode (str): The mode of the scoreboard
        """
        self.mode = mode
        self.num_pages = math.ceil(self._count_games() / 5)

        a = (self.num_pages <= 2) and (mode == 'dual')
        b = (self.num_pages <= 1) and (mode == 'basic')
        cycle_pages = not (a or b)

        if not cycle_pages:
            # No need to loop, all games fit. would just alternate
            # the one or two columns
            return

        for self.page in range(self.num_pages):
            self.print_page(self.page)
