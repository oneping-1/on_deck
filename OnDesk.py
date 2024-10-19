from typing import List
import threading
import time
import platform

from at_bat.statsapi_plus import get_daily_gamepks
from at_bat.scoreboard_data import ScoreboardData

from on_deck.colors import Colors
from on_deck.fonts import Fonts
from on_deck.display_manager import DisplayManager

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrixOptions # pylint: disable=E0401
else:
    from rgbmatrix import RGBMatrixOptions # pylint: disable=E0401

ABV_A = 'CLE'
ABV_B = 'TEX'

TEAM_A = 'Cleveland Guardians'
TEAM_B = 'Texas Rangers'

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    if platform.system() == 'Windows':
        options.rows = int(64)
        options.cols = int(128)
    else:
        options.cols = 64
        options.rows = 64
        options.chain_length = 2
        options.disable_hardware_pulsing = True
        options.gpio_slowdown = 4

    return options


class GameHandler:
    """
    This class is used to handle the games
    """
    def __init__(self, games: List[ScoreboardData]):
        self.games = games

    def start(self):
        """
        This method is used to start the game updater
        """
        gamepks = get_daily_gamepks()
        games = [ScoreboardData(gamepk) for gamepk in gamepks]

        for game in games:
            if ABV_A in (game.away.abv, game.home.abv):
                self.games[0] = game
            if ABV_B in (game.away.abv, game.home.abv):
                self.games[1] = game

    def loop(self):
        while True:
            self.update()
            time.sleep(60)

    def update(self):
        """
        This method is used to update the games
        """
        for game in self.games:
            game.update()

class Scoreboard:
    def __init__(self, games: List[ScoreboardData]):
        self.display_manager = DisplayManager(get_options())
        self.display_manager.swap_frame()

        self.games = games

    def start(self):
        while True:
            for i, game in enumerate(self.games):
                self.print_game(i, game)
                self.display_manager.swap_frame()

    def print_game(self, i, game):
        """
        Prints the page
        """
        if game is None:
            return

        self.display_manager.clear_section(0, i*32, 64, 32+32*i)

        if game.game_state == 'P':
            self._print_teams(i, game)
            self._print_start_time(i, game)
            self._print_standings(i, game)
        if game.game_state == 'L':
            self._print_teams(i, game)
            self._print_score(i, game)
            self._print_inning(i, game)
            self._print_standings(i, game)
        if game.game_state == 'F':
            self._print_teams(i, game)
            self._print_score(i, game)
            self._print_inning(i, game)
            self._print_standings(i, game)

    def _get_color(self, i):
        if i == 0:
            return Colors.red
        return Colors.blue

    def _get_offset(self, i):
        if i == 0:
            return 0
        return 32

    def _print_teams(self, i, game):
        color = self._get_color(i)
        offset = self._get_offset(i)

        self.display_manager.draw_text(Fonts.ter_u22b, 0, 15 + offset, color, game.away.abv)
        self.display_manager.draw_text(Fonts.ter_u22b, 0, 31 + offset, color, game.home.abv)

    def _print_start_time(self, i, game):
        color = self._get_color(i)
        offset = self._get_offset(i)

        start_time = game.start_time

        if i == 1:
            start_time = '10:10'

        if len(start_time) < 5:
            start_time = ' ' + start_time

        hour = start_time[:2]
        minute = start_time[3:]

        # eliminates some of the wasted space in : since using
        # monospaced font
        self.display_manager.draw_text(Fonts.ter_u18b, 35, 22 + offset, color, hour)
        self.display_manager.draw_text(Fonts.ter_u18b, 53, 22 + offset, color, ':')
        self.display_manager.draw_text(Fonts.ter_u18b, 60, 22 + offset, color, minute)

    def _print_standings(self, i, game):
        wins = game.away.wins
        losses = game.away.losses
        streak = game.away.streak
        division_rank = game.away.division_rank
        games_back = game.away.games_back
        self._print_standing(i, False, wins, losses, streak, division_rank, games_back)

        wins = game.home.wins
        losses = game.home.losses
        streak = game.home.streak
        division_rank = game.home.division_rank
        games_back = game.home.games_back
        self._print_standing(i, True, wins, losses, streak, division_rank, games_back)

    def _print_standing(self, i, is_home: bool, wins, losses, streak, division_rank, games_back):
        color = self._get_color(i)
        offset = self._get_offset(i)

        if is_home is True:
            offset += 16

        if games_back == 0:
            games_back = '  0.0'
        elif games_back < 10:
            games_back = f' -{games_back:.1f}'
        else:
            games_back = f'-{games_back:.1f}'

        record = f'{wins}-{losses} {streak}'
        gb = f'P{division_rank} {games_back}'

        self.display_manager.draw_text(Fonts.f6x10, 80, 8 + offset, color, record)
        self.display_manager.draw_text(Fonts.f6x10, 80, 16 + offset, color, gb)

    def _print_score(self, i, game):
        color = self._get_color(i)
        offset = self._get_offset(i)

        away = str(game.away_score)
        home = str(game.home_score)

        if len(away) > 1:
            self.display_manager.draw_text(Fonts.ter_u22b, 35, 15 + offset, color, away)
        else:
            self.display_manager.draw_text(Fonts.ter_u22b, 40, 15 + offset, color, away)

        if len(home) > 1:
            self.display_manager.draw_text(Fonts.ter_u22b, 35, 31 + offset, color, home)
        else:
            self.display_manager.draw_text(Fonts.ter_u22b, 40, 31 + offset, color, home)

    def _print_inning(self, i, game):
        color = self._get_color(i)
        offset = self._get_offset(i)

        inning = str(game.inning)

        if game.game_state == 'F':
            inning = 'F'

        if len(inning) > 1:
            self.display_manager.draw_text(Fonts.ter_u22b, 57, 23 + offset, color, inning)
        else:
            self.display_manager.draw_text(Fonts.ter_u22b, 62, 23 + offset, color, inning)

def start_game_handler(game_handler: GameHandler):
    """
    Starts the game handler
    """
    game_handler.start()

def start_scoreboard(scoreboard: Scoreboard):
    """
    Starts the scoreboard
    """
    scoreboard.start()

def main():
    """
    Description: This function is used to start the scoreboard
    """
    games: List[ScoreboardData] = [None, None]

    game_handler = GameHandler(games)
    scoreboard = Scoreboard(games)

    game_handler_thread = threading.Thread(target=start_game_handler, args=(game_handler,))
    scoreboard_thread = threading.Thread(target=start_scoreboard, args=(scoreboard,))

    game_handler_thread.start()
    scoreboard_thread.start()

if __name__ == '__main__':
    main()
