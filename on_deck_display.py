"""
This module handles all the logic for the display. It listens to the
pubsub channel for updates to the games and updates the display
accordingly.

Should run this module seperately as sudo for optimal performance.

This is the second version of this project. The first version was
similar to this one, but had many issues, mainly around the server
and nginx. This version is a complete rewrite of the project and
should fix those issues.

I should probably put gamecast logic into its own thread
"""

import socket
import copy
import math
from typing import List
import time
import json
import platform
import threading
import redis

from on_deck.display_manager import DisplayManager
from on_deck.colors import Colors
from on_deck.fonts import Fonts
from on_deck.overview import Overview
from on_deck.gamecast import Gamecast

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrixOptions
else:
    from rgbmatrix import RGBMatrixOptions

def get_options() -> RGBMatrixOptions:
    """
    Returns the RGBMatrixOptions object based on the platform.

    Returns:
        RGBMatrixOptions: RGBMatrixOptions object
    """
    options = RGBMatrixOptions()

    if platform.system() == 'Windows':
        options.cols = int(384)
        options.rows = int(256)
    else:
        options.cols = 128
        options.rows = 64
        options.pixel_mapper_config = 'V-mapper'
        options.chain_length = 4
        options.parallel = 3
        options.disable_hardware_pulsing = True
        options.pwm_bits = 2 # Can run at 2 with sudo, 1 without
        options.gpio_slowdown = 4

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

def get_ip_address() -> str:
    # Create a socket to get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually need to send data; we're just looking for the local IP
        s.connect(('8.8.8.8', 80))  # Using Google's DNS server
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = 'Unable to get IP address'
    finally:
        s.close()
    return ip_address

class Scoreboard:
    """
    This class is used to manage the scoreboard
    """
    def __init__(self):
        """
        Initializes the scoreboard

        Args:
            options (_type_): _description_
        """
        self.games: List[dict] = []
        self._page: int = None

        self.display_manager = DisplayManager(get_options())
        self.display_manager.swap_frame()

        self._print_welcome_message()
        if platform.system() != 'Windows':
            time.sleep(20) # Allow time for fetcher to get games

        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('brightness')
        self.pubsub.subscribe('mode')
        self.mode = self.redis.get('mode').decode('utf-8')

        self.overview = Overview(self.display_manager)
        self.gamecast = Gamecast(self.display_manager)

        brightness = self.redis.get('brightness')
        if brightness is not None:
            self._change_brightness(brightness)

        self.time_thread = threading.Thread(target=self._print_time_loop, daemon=True)
        self.pubsub_thread = threading.Thread(target=self.listen_to_pubsub, daemon=True)

    def _print_welcome_message(self):
        ip = get_ip_address()
        self.display_manager.draw_text(Fonts.ter_u18b, 0, 15, Colors.white, 'OnDeck')
        self.display_manager.draw_text(Fonts.ter_u18b, 0, 30, Colors.green, f'{ip}')
        self.display_manager.swap_frame()

    def _print_overview_page(self):
        """
        Prints the overview page of the scoreboard
        Only needs to be called once, either at start of module or
        when the mode changes
        """
        for i, game in enumerate(self.games):
            self.overview.print_game(game, i)

    def _get_shifted_games(self, column: int) -> List[dict]:
        offset = column * 6
        games = copy.deepcopy(self.games)

        while (len(games) % 6) != 0:
            games.append(None)

        new_games = copy.deepcopy(games[offset:]) + copy.deepcopy(games[:offset])
        return new_games

    def _print_gamecast_page(self):
        if self.mode != 'gamecast':
            return
        shifted_games = self._get_shifted_games(self._page)

        for i in range(6):
            self.overview.print_game(shifted_games[i], i)

    def _print_gamecast_pages(self):
        num_games = len(self.games)
        max_page = math.ceil(num_games / 6)

        for self._page in range(max_page):
            self._print_gamecast_page()
            self.gamecast.print_game(self.games[3])
            self.display_manager.swap_frame()
            time.sleep(5)

    def _loop_gamecast(self):
        while self.mode == 'gamecast':
            self._print_gamecast_pages()
        time.sleep(1)

    def _change_brightness(self, brightness):
        """
        Brightness levels (pwm_bits = 2)
        0: Off  ( 0 -  55)
        1: Low  (60 -  75)
        2: Mid  (80 -  85)
        3: High (90 - 100)
        """
        brightness = int(brightness)
        print(f'Brightness: {brightness}')

        if brightness == 0:
            self.display_manager.set_brightness(0)
        elif brightness == 1:
            self.display_manager.set_brightness(60)
        elif brightness == 2:
            self.display_manager.set_brightness(80)
        elif brightness == 3:
            self.display_manager.set_brightness(90)

        if self.mode == 'overview':
            self._print_overview_page()
        elif (self.mode == 'gamecast') and (self._page is not None):
            self._print_gamecast_page()

        self.print_time()

    def _change_mode(self, mode):
        mode = mode.decode('utf-8')
        self.mode = mode
        self.display_manager.clear_section(0, 0, 384, 256)

        if mode == 'overview':
            # dont need to do anything for gamecast
            # while True: in start should handle it
            self._print_overview_page()

    def _read_pubsub_message(self, message):
        if message['type'] != 'message':
            return

        if message['channel'] == b'brightness':
            self._change_brightness(message['data'])
            return

        if message['channel'] == b'mode':
            self._change_mode(message['data'])
            return

        game_id = int(message['channel'])
        new_data = json.loads(message['data'])

        self.games[game_id] = recursive_update(self.games[game_id], new_data)

        if self.mode == 'gamecast':
            page = math.floor(game_id / 6)
            if page == self._page:
                self.overview.print_game(self.games[game_id], game_id % 6)
        else:
            self.overview.print_game(self.games[game_id], game_id)
        self.display_manager.swap_frame()

    def listen_to_pubsub(self):
        """
        Listens to the pubsub channel for updates to the game
        """
        while True:
            message = self.pubsub.get_message(timeout=5)
            if message:
                self._read_pubsub_message(message)
            time.sleep(.1)

    def print_time(self):
        """
        Print the current time, time from delay number of seconds ago,
        and the current delay
        """
        delay = int(self.redis.get('delay'))
        self.overview.print_time(delay, 17)

    def _print_time_loop(self):
        while True:
            self.print_time()
            time.sleep(.1)

    def start(self):
        """
        Starts the scoreboard
        """
        num_games = int(self.redis.get('num_games'))

        while (num_games is None) or (num_games == 0):
            time.sleep(1)
            num_games = int(self.redis.get('num_games'))

        # Initializes game data
        for i in range(num_games):
            self.games.append(json.loads(self.redis.get(str(i))))
            self.pubsub.subscribe(str(i))

        self.time_thread.start()
        self.pubsub_thread.start()

        if self.mode == 'overview':
            self._print_overview_page()
        self.display_manager.swap_frame()

        while True:
            self._loop_gamecast()

if __name__ == '__main__':
    scoreboard = Scoreboard()
    scoreboard.start()
