"""
Description: This module is used to create a scoreboard server.
Used to recieve data from the game and display it on the scoreboard.
"""

from typing import List, Union
import os
import threading
import platform
import math
import time
import copy
from flask import Flask, request, jsonify

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    if platform.system() == 'Windows':
        options.rows = int(256)
        options.cols = int(384)
    else:
        options.cols = 128
        options.rows = 64
        options.pixel_mapper_config = 'V-mapper'
        options.chain_length = 4
        options.parallel = 3
        options.disable_hardware_pulsing = True
        options.pwm_bits = 1
        options.gpio_slowdown = 5

    return options

def recursive_update(d: dict, u: dict) -> dict:
    """
    Recursively updates a dictionary.

    Args:
        d (dict): Dictionary 1
        u (dict): Dictionary 2

    Returns:
        dict: Updated dictionary
    """
    for k, v in u.items():
        if isinstance(v, dict):
            d[k] = recursive_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

class MainServer:
    """
    Description: This class is used to create a scoreboard server.
    Used to recieve data from the game and display it on the scoreboard.
    """
    def __init__(self, games: List[dict], scoreboard: 'Scoreboard'):
        self.games = games
        self.scoreboard = scoreboard

        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home, methods=['GET'])
        self.app.add_url_rule('/reset', 'reset_games', self.reset_games, methods=['GET'])
        self.app.add_url_rule('/settings', 'settings', self.settings, methods=['GET'])
        self.app.add_url_rule('/<int:game_index>', 'receive_data',
            self.receive_data, methods=['POST'])
        self.app.add_url_rule('/gamecast', 'gamecast', self.gamecast, methods=['POST'])

    def home(self):
        """
        Description: This function is the home page of the scoreboard.
        Used to make sure the server is running.
        """
        d = []

        for game in self.games:
            d.append(game)

        return jsonify(d), 200

    def reset_games(self):
        """
        Description: This function is used to reset all the games.
        """
        for game in self.games:
            game['display_game'] = False

        self.scoreboard.gamecast_game['display_game'] = False

        for i in range(10):
            self.scoreboard.clear_game(i)

        self.scoreboard.matrix.SwapOnVSync(self.scoreboard.canvas)

        return jsonify({'message': 'Games reset'}), 200

    def settings(self):
        """
        Description: This function is used to set the mode of the scoreboard.
        """
        mode = request.args.get('mode')
        gameid = request.args.get('id')

        return_dict = {
            'mode': self.scoreboard.mode,
            'new_mode': self.scoreboard.new_mode
        }

        if mode is None and gameid is None:
            return jsonify({'message': return_dict}), 200

        try:
            self.scoreboard.new_mode = mode
        except ValueError:
            return jsonify({'message': f'Mode {mode} not recognized'}), 200

        if gameid is not None:
            try:
                self.scoreboard.gamecast_gameid = int(gameid)
            except ValueError:
                return jsonify({'message': 'Game ID not recognized'}), 200

        return_dict = {
            'mode': self.scoreboard.mode,
            'new_mode': self.scoreboard.new_mode
        }

        return jsonify({'message': return_dict}), 200

    def receive_data(self, game_index: int):
        """
        Description: This function is used to receive data from the game.
        The data is in the form of a JSON object.
        """
        new_data = request.get_json()

        self.games[game_index] = recursive_update(self.games[game_index], new_data)
        self.games[game_index]['display_game'] = True

        return_dict = {'new_data': new_data, 'game': self.games[game_index]}

        self.print_game_if_on_page(game_index)

        # print(json.dumps(return_dict, indent=4))
        return jsonify(return_dict), 200

    def gamecast(self):
        """
        Description: This function is used to receive data from the gamecast.
        The data is in the form of a JSON object.
        """

        new_data = request.get_json()

        r = recursive_update(self.scoreboard.gamecast_game, new_data)
        self.scoreboard.gamecast_game = r
        self.scoreboard.gamecast_game['display_game'] = True

        if self.scoreboard.mode == 'gamecast':
            self.scoreboard.print_gamecast()

        return_data = {'new_data': new_data, 'game': self.scoreboard.gamecast_game}
        return jsonify(return_data), 200

    def print_game_if_on_page(self, game_index: int) -> bool:
        """
        This function is used to print the game if it is on the current page.

        Args:
            game_index (int): The index of the game to print.
        """
        games_per_page = 5
        shifted_game_index = game_index - (self.scoreboard.page * games_per_page)

        if self.scoreboard.mode in ('detailed', 'gamecast'):
            if shifted_game_index > 4:
                return False

        if self.scoreboard.mode == 'basic':
            if shifted_game_index > 9:
                return False

        self.scoreboard.print_game(shifted_game_index, self.games[game_index])
        self.scoreboard.matrix.SwapOnVSync(self.scoreboard.canvas)
        return True

    def start(self, port: int = 5000, debug: bool = False):
        """
        Starts the Flask server

        Args:
            port (int, optional): Flask server port. Defaults to 5000.
            debug (bool, optional): Debug mode. Defaults to False.
        """
        self.app.run(host='0.0.0.0', port=port, debug=debug)

class Scoreboard:
    """
    Description: This class is used to create a scoreboard.
    Used to display the data from the game on the scoreboard.
    """

    _acceptable_modes = ('basic', 'detailed', 'gamecast')
    def __init__(self, games: List[dict], mode: str = 'basic'):
        self.games = games

        # self.mode cannot be changed directly
        # change self.new_mode instead
        # problem occurs in self.start()
        self.mode = mode
        self._new_mode: str = mode
        self.num_pages: int = None

        # Copy of the game for gamecast (empty game)
        self.gamecast_game = copy.deepcopy(games[0])

        self.page: int = 0

        # Matrix Setup
        self.options = get_options()
        self.matrix = RGBMatrix(options=self.options)
        self.canvas = self.matrix.CreateFrameCanvas()

        # Emulated matrix server does not start until the first
        # SwapOnVSync is called
        self.matrix.SwapOnVSync(self.canvas)

        scoreboard_path = os.path.dirname(os.path.abspath(__file__))
        fonts_path = os.path.join(scoreboard_path, 'fonts')
        terminus_path = os.path.join(fonts_path, 'Terminus')

        self.ter_u32b = graphics.Font()
        self.ter_u32b.LoadFont(os.path.join(terminus_path, 'ter-u32b.bdf'))
        # ter-u32b.bdf:
        # Letter height = 20 pixels = 38 mm = 1.496 in
        # Slighly larger than OnDeck1 (36 mm)

        self.ter_u18b = graphics.Font()
        self.ter_u18b.LoadFont(os.path.join(terminus_path, 'ter-u18b.bdf'))

        self.symbols = graphics.Font()
        self.symbols.LoadFont(os.path.join(fonts_path, 'symbols.bdf'))

        # Matrix Colors
        self.my_white = graphics.Color(255, 255, 255)
        self.my_red = graphics.Color(255, 0, 0)
        self.my_green = graphics.Color(0, 255, 0)
        self.my_blue = graphics.Color(0, 0, 255)
        self.my_grey = graphics.Color(20, 20, 20)
        self.my_black = graphics.Color(0, 0, 0)

        if platform.system() == 'Windows':
            # Fill the screen with grey
            # Can see pixels in emulation
            self.matrix.Fill(20, 20, 20)

        # Scoreboard Offsets
        self.away_row_offset = 22
        self.home_row_offset = 44
        self.inning_row_offset = (self.away_row_offset + self.home_row_offset) / 2
        self.inning_column_offset = 100
        self.time_offset = -25

        # Detail Mode Offsets
        self.two_line_offset = 7

    @property
    def new_mode(self):
        return self._new_mode

    @new_mode.setter
    def new_mode(self, value: Union[str, None]) -> Union[str, None]:
        if value is None:
            return None
        if value not in Scoreboard._acceptable_modes:
            raise ValueError(f'Invalid mode: {value}')
        self._new_mode = value
        return value

    def _print_line_a(self, color, column_offset, row_offset, line_a):
        graphics.DrawText(self.canvas, self.ter_u18b, 175 + column_offset,
            14 + row_offset, color, line_a)

    def _print_line_b(self, color, column_offset, row_offset, line_b):
        graphics.DrawText(self.canvas, self.ter_u18b, 175 + column_offset,
            29 + row_offset, color, line_b)

    def _print_line_c(self, color, column_offset, row_offset, line_c):
        graphics.DrawText(self.canvas, self.ter_u18b, 175 + column_offset,
            44 + row_offset, color, line_c)

    def _calculate_offsets(self, index: int):
        row_offset = 50*index
        column_offset = 0

        if index >= 5:
            column_offset = 384/2
            row_offset = 50*(index - 5)

        return (row_offset, column_offset)

    def _calculate_color(self, index: int):
        if index % 2 == 0:
            return self.my_white
        return self.my_green

    def clear_game(self, index: int):
        """
        Clears the game from the scoreboard

        Args:
            index (int): The index of the game to clear
        """
        row_offset, column_offset = self._calculate_offsets(index)

        if platform.system() == 'Windows':
            color = self.my_grey
        else:
            color = self.my_black

        if self.mode in ('basic', 'gamecast'):
            length = 192
        elif self.mode == 'detailed':
            length = 384
        else:
            raise ValueError(f'Length not specified for mode: {self.mode}')

        for i in range(50):
            graphics.DrawLine(self.canvas, 0 + column_offset, i + row_offset,
                length + column_offset, i + row_offset, color)

    def _print_scores(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

        if game['away_score'] > 9:
            graphics.DrawText(self.canvas, self.ter_u32b, 55 + column_offset,
                self.away_row_offset + row_offset, color, str(game['away_score']))
        else:
            graphics.DrawText(self.canvas, self.ter_u32b, 63 + column_offset,
                self.away_row_offset + row_offset, color, str(game['away_score']))

        if game['home_score'] > 9:
            graphics.DrawText(self.canvas, self.ter_u32b, 55 + column_offset,
                self.home_row_offset + row_offset, color, str(game['home_score']))
        else:
            graphics.DrawText(self.canvas, self.ter_u32b, 63 + column_offset,
                self.home_row_offset + row_offset, color, str(game['home_score']))

    def _print_inning(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

        if game['inning'] > 9:
            graphics.DrawText(self.canvas, self.ter_u32b,  self.inning_column_offset - 8 + column_offset,
                self.inning_row_offset + row_offset, color, f'{game["inning"]}')
        else:
            graphics.DrawText(self.canvas, self.ter_u32b, self.inning_column_offset + column_offset,
                self.inning_row_offset + row_offset, color, f'{game["inning"]}')

        if game['inning_state'] == 'T':
            graphics.DrawText(self.canvas, self.symbols, self.inning_column_offset + column_offset,
                11 + row_offset, color, '^')
        elif game['inning_state'] == 'B':
            graphics.DrawText(self.canvas, self.symbols, self.inning_column_offset + column_offset,
                43 + row_offset, color, 'v')

    def _print_text(self, index: int, text: str, column_offset: int = 0):
        row_offset, column_offset2 = self._calculate_offsets(index)
        color = self._calculate_color(index)

        x = self.inning_column_offset + column_offset + column_offset2
        y = self.inning_row_offset + row_offset
        graphics.DrawText(self.canvas, self.ter_u32b, x, y, color, text)

    def _print_outs(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

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

        graphics.DrawText(self.canvas, self.symbols, 130 + column_offset,
            43 + row_offset, color, outs_list[0])
        graphics.DrawText(self.canvas, self.symbols, 142 + column_offset,
            43 + row_offset, color, outs_list[1])
        graphics.DrawText(self.canvas, self.symbols, 154 + column_offset,
            43 + row_offset, color, outs_list[2])

    def _print_runners(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

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
        graphics.DrawText(self.canvas, self.symbols, x0, y0, color, bases_list[0])

        x1 = second_base_column_offset + column_offset
        y1 = second_base_row_offset + row_offset
        graphics.DrawText(self.canvas, self.symbols, x1, y1, color, bases_list[1])

        x2 = second_base_column_offset - base_offset + column_offset
        y2 = second_base_row_offset + base_offset + row_offset
        graphics.DrawText(self.canvas, self.symbols, x2, y2, color, bases_list[2])

    def _print_batter_pitcher(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

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

    def _print_pitcher_decisions(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

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

    def _print_probable_pitchers(self, index, game):
        row_offset, column_offset = self._calculate_offsets(index)
        color = self._calculate_color(index)

        line_a = f'SP:{game["probables"]["away"]} ({game["probables"]["away_era"]})'
        line_c = f'SP:{game["probables"]["home"]} ({game["probables"]["home_era"]})'

        if line_a is not None:
            self._print_line_a(color, column_offset, row_offset + self.two_line_offset, line_a)

        if line_c is not None:
            self._print_line_c(color, column_offset, row_offset - self.two_line_offset, line_c)

    def _print_page_indicator(self, page_num: int):
        graphics.DrawLine(self.canvas, 0, 255, 384, 255, self.my_black)

        line_length = 5
        gap = 2
        total_length = line_length + gap

        for i in range(page_num+1):
            x0 = 40 + ((i + 1) * total_length)
            x1 = x0 + line_length - 1 # -1 to account for extra character width

            graphics.DrawLine(self.canvas, x0, 255, x1, 255, self.my_white)

    def print_game(self, game_index: int, game: dict):
        self.clear_game(game_index)

        if game['display_game'] is False:
            return None

        row_offset, column_offset = self._calculate_offsets(game_index)

        color = self._calculate_color(game_index)

        # Team Abbreviations

        graphics.DrawText(self.canvas, self.ter_u32b, 0 + column_offset,
            self.away_row_offset + row_offset, color, game['away']['abv'])

        graphics.DrawText(self.canvas, self.ter_u32b, 0 + column_offset,
            self.home_row_offset + row_offset, color, game['home']['abv'])

        # Live
        if game['game_state'] == 'L':
            self._print_scores(game_index, game)
            self._print_inning(game_index, game)
            self._print_outs(game_index, game)
            self._print_runners(game_index, game)

        # Final
        elif game['game_state'] == 'F':
            self._print_scores(game_index, game)

            if game['inning'] != 9:
                self._print_text(game_index, f'F/{game["inning"]}')
            else:
                self._print_text(game_index, 'F')

        # Pre-Game
        elif game['game_state'] == 'P':
            if len(game['start_time']) > 4:
                # -16 to account for extra character width
                self._print_text(game_index, game['start_time'], self.time_offset - 6)
            else:
                self._print_text(game_index, game['start_time'], self.time_offset + 10)

        # Suspendend / Postponed
        elif game['game_state'] == 'S':
            self._print_scores(game_index, game)
            self._print_inning(game_index, game)

            if self.mode in ('basic', 'gamecast'):
                self._print_text(game_index, 'Susp', 25)

        # Delay
        elif game['game_state'] == 'D':
            self._print_scores(game_index, game)
            self._print_inning(game_index, game)

            if self.mode in ('basic', 'gamecast'):
                self._print_text(game_index, 'Dly', 32)

        # Detailed (2 Columns)
        if self.mode != 'detailed':
            return None

        # Live
        if game['game_state'] == 'L':
            self._print_batter_pitcher(game_index, game)

        # Final
        elif game['game_state'] == 'F':
            self._print_pitcher_decisions(game_index, game)

        # Pre-Game
        elif game['game_state'] == 'P':
            self._print_probable_pitchers(game_index, game)

        # Suspendend / Postponed
        elif game['game_state'] == 'S':
            self._print_text(game_index, 'Suspended', 75)
            self._print_inning(game_index, game)
            self._print_runners(game_index, game)
            self._print_outs(game_index, game)

        # Delay
        elif game['game_state'] == 'D':
            self._print_text(game_index, 'Delayed', 75)
            self._print_inning(game_index, game)
            self._print_runners(game_index, game)
            self._print_outs(game_index, game)

    def _clear_gamecast(self):
        if platform.system() == 'Windows':
            color = self.my_grey
        else:
            color = self.my_black

        for i in range(256):
            graphics.DrawLine(self.canvas, 192, i, 384, i, color)

    def _print_gamecast_line(self, line_num: int, text: Union[str, None]) -> bool:
        if text is None:
            return False

        row = 16 * (line_num + 1)

        graphics.DrawText(self.canvas, self.ter_u18b, 192, row, self.my_white, text)
        return True

    def print_gamecast(self):
        self._clear_gamecast()

        if self.gamecast_game['display_game'] is False:
            return None

        color = self.my_white

        away_row_offset = 14
        home_row_offset = 30
        inning_row_offset = (away_row_offset + home_row_offset) / 2

        self._print_gamecast_line(0, self.gamecast_game['away']['name'])
        self._print_gamecast_line(1, self.gamecast_game['home']['name'])

        graphics.DrawText(self.canvas, self.ter_u18b, 300, away_row_offset,
                          color, str(self.gamecast_game['away_score']))
        graphics.DrawText(self.canvas, self.ter_u18b, 300, home_row_offset,
                          color, str(self.gamecast_game['home_score']))

        graphics.DrawText(self.canvas, self.ter_u18b, 320, inning_row_offset,
                          color, str(self.gamecast_game['inning']))

        # Count
        count = f'{self.gamecast_game["count"]["balls"]}-{self.gamecast_game["count"]["strikes"]}'
        count += f'{self.gamecast_game["count"]["outs"]} Out'
        if self.gamecast_game['count']['outs'] != 1:
            count += 's'
        self._print_gamecast_line(2, count)

        # Pitch Details
        # Line 3 Empty
        # i think thse throw errors when they are None, so should add a check
        self._print_gamecast_line(4, self.gamecast_game['pitch_details']['description'])

        s = ''
        if self.gamecast_game['pitch_details']['speed'] is not None:
            # Both are either a value or None
            # None on no pitch like step off
            s += f'{self.gamecast_game["pitch_details"]["speed"]} MPH'
            s += f' | Zone: {self.gamecast_game["pitch_details"]["zone"]}'
        self._print_gamecast_line(5, s)

        self._print_gamecast_line(6, self.gamecast_game['pitch_details']['type'])

        # To be added next:
        # when pitch is in play: hit details (distance, exit velo, launch angle)
        # when pitch is not in play: run expectency, umpire, win probability

        self.matrix.SwapOnVSync(self.canvas)

    def print_page(self, page_num: int):
        max_games = 5 * self.num_pages
        shift_offset = page_num * 5

        shifted_games = [None] * max_games

        for i, game in enumerate(self.games[:max_games]):
            shifted_games[i] = game

        shifted_games = shifted_games[shift_offset:] + shifted_games[:shift_offset]

        if self.mode == 'basic':
            shifted_games = shifted_games[:10]
        else:
            shifted_games = shifted_games[:5]

        for i, game in enumerate(shifted_games):
            self.print_game(i, game)

        self._print_page_indicator(page_num)

        if self.mode == 'gamecast':
            self.print_gamecast()

        self.matrix.SwapOnVSync(self.canvas)
        time.sleep(10)

    def _count_games(self) -> int:
        count = 0

        for game in self.games:
            if game['display_game'] is True:
                count += 1

        return count

    def start(self):
        while True:
            self.num_pages = math.ceil(self._count_games() / 5)
            for self.page in range(self.num_pages):
                self.print_page(self.page)

            if self._new_mode != self.mode:
                # wait until after all pages are displayed to avoid
                # potential errors

                # but is a barrier that blocks changes directly to
                # self.mode. Not intentional but a good byproduct.
                self.mode = self._new_mode

def start_server(server):
    """Starts the server"""
    server.start()

def start_scoreboard(scoreboard):
    """Starts the scoreboard"""
    scoreboard.start()

def main():
    """
    Description: This function is used to start the scoreboard
    """
    game_template = {
        'game_state': None,
        'away_score': None,
        'home_score': None,
        'inning': None,
        'inning_state': None,
        'away': {
            'abv': None,
            'name': None,
            'location': None,
        },
        'home': {
            'abv': None,
            'name': None,
            'location': None
        },
        'count': {
            'balls': None,
            'strikes': None,
            'outs': None
        },
        'runners': None,
        'start_time': None,
        'matchup': {
            'batter': None,
            'batter_summary': None,
            'pitcher': None,
            'pitcher_summary': None
        },
        'decisions': {
            'win': None,
            'win_summary': None,
            'loss': None,
            'loss_summary': None,
            'save': None,
            'save_summary': None
        },
        'probables': {
            'away': None,
            'away_era': None,
            'home': None,
            'home_era': None
        },
        'pitch_details': {
            'description': None,
            'speed': None,
            'type': None,
            'zone': None,
            'spin_rate': None,
        },
        'display_game': False
    }

    games = [copy.deepcopy(game_template) for _ in range(20)]

    scoreboard = Scoreboard(games)
    main_server = MainServer(games, scoreboard)

    server_thread = threading.Thread(target=start_server, args=(main_server,))
    scoreboard_thread = threading.Thread(target=start_scoreboard, args=(scoreboard,))

    server_thread.start()
    scoreboard_thread.start()

if __name__ == '__main__':
    main()
