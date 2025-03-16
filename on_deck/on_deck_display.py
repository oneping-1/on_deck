"""
Description: This module is the main module for the scoreboard. It
connects all the other modules together and starts the scoreboard.
The scoreboard is split into two modes: overview and gamecast. The
overview mode shows all the games in a small format. The gamecast
mode shows the current game in a large format. The scoreboard will
listen for messages from the redis server and update the data based
on the message received. The scoreboard will also listen for changes
in the mode and brightness and update the display based on the
changes.
"""

from typing import Union, List
import json
import platform
import threading
import time
import math
import redis

from on_deck.display_manager import DisplayManager
from on_deck.overview import Overview
from on_deck.gamecast import Gamecast

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrixOptions
else:
    from rgbmatrix import RGBMatrixOptions

brightness_dict_2pwm = {0: 0, 1: 60, 2: 80, 3: 90}
redis_ip = '192.168.1.90'
redis_password = 'on_deck'

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

class TimeHandler:
    """
    Handles all the logic to print the time on the scoreboard. The time
    is the delay time for the current game. This class will listen for
    messages from the redis server and update the time based on the
    message received.
    """
    def __init__(self, display_manager: DisplayManager, overview: Overview):
        self.display_manager = display_manager
        self.overview = overview

        self.redis = redis.Redis(redis_ip, port=6379, db=0, password=redis_password)

    def start(self):
        """
        Continuously prints the time on the scoreboard. The time is the
        delay time for the current game. This function will print the
        time and then wait 100ms before printing the time again
        """
        while True:
            delay = int(self.redis.get('delay'))
            self.overview.print_time(delay, 17)
            time.sleep(.1)

class GamecastHandler:
    """
    Handles all the logic for the gamecast data for the scoreboard. The
    gamecast data is the large display that shows all the stats for the
    current game. This class will listen for messages from the redis
    server and update the gamecast data based on the message received.
    """
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.game: dict = None

        self.redis = redis.Redis(redis_ip, port=6379, db=0, password=redis_password)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('gamecast')
        self.pubsub.subscribe('brightness')
        self.pubsub.subscribe('gamecast_id')
        self.pubsub.subscribe('mode')

        try:
            brightness = int(self.redis.get('brightness'))
        except TypeError:
            brightness = 3

        self.display_manager.set_brightness(brightness_dict_2pwm[brightness])

        self.gamecast: Gamecast = Gamecast(self.display_manager)
        self.gamecast_game: dict = None

    def load_gamecast(self) -> dict:
        """
        Loads the gamecast data from the redis server.

        Returns:
            dict: The gamecast game data
        """
        game = self.redis.get('gamecast')
        game = json.loads(game)
        self.gamecast_game = game
        return game

    def change_settings(self, message: dict):
        """
        Changes the settings based on the message received from the
        pubsub listener. The settings that can be changed are the mode
        and the brightness. This function will also call the appropriate
        function to print the correct data based on the mode to ahcieve
        maximum speed.

        Args:
            message (dict): Message received from the pubsub listener
        """
        channel = message['channel']

        if channel in (b'gamecast_id', b'delay'):
            print('waiting')
            time.sleep(2) # delay to let fetcher update gamecast
            new_data = self.redis.get('gamecast')
            new_data = json.loads(new_data)
            self.gamecast_game = new_data
            self.gamecast.print_game(self.gamecast_game)
            return

        if channel == b'brightness':
            brightness = int(message['data'])
            self.display_manager.set_brightness(brightness_dict_2pwm[brightness])
            self.gamecast.print_game(self.gamecast_game)
            return

        mode = self.redis.get('mode')
        if channel == b'mode':
            mode = message['data']

        if mode == b'gamecast':
            self.display_manager.clear_section(129, 0, 384, 256)
            self.gamecast.print_game(self.gamecast_game)
            return

    def update_gamecast(self) -> Union[bool, dict]:
        """
        Updates the gamecast data based on the message received from the
        pubsub listener. This function will only update the gamecast data
        if the message is a gamecast message. If the message is not a
        gamecast message, the function will return False.

        Returns:
            Union[bool, dict]: The new data received from the pubsub
                or False if the message is not a gamecast message
        """
        message = self.pubsub.get_message(timeout=5)

        if not message:
            return False

        if message['type'] != 'message':
            return False

        if message['channel'] in (b'gamecast_id', b'brightness', b'mode', b'delay'):
            self.change_settings(message)
            return False

        new_data = json.loads(message['data'])
        print(f'{new_data=}\n')
        if new_data == {}:
            return False

        self.gamecast_game = recursive_update(self.gamecast_game, new_data)
        return new_data

    def print_gamecast_game(self) -> bool:
        """
        Prints the current gamecast game. This function will only print
        the game if the mode is gamecast.

        Returns:
            bool: True if the game was printed, False otherwise
        """
        new_data = self.update_gamecast()

        if new_data is False:
            return False

        mode = self.redis.get('mode')
        if mode != b'gamecast':
            return False

        self.gamecast.print_game(self.gamecast_game)
        return True

    def start(self):
        """
        Starts the gamecast handler. This function will load the gamecast
        data from the redis server, print the gamecast game, and then
        wait for new data to be received. If new data is received, the
        gamecast game will be updated and printed. This function will
        continue to wait for new data until the mode is changed.
        """
        game = self.load_gamecast()
        self.gamecast.print_game(game)

        while True:
            self.print_gamecast_game()

class OverviewHandler:
    """
    Handles all the logic for the overview data for the scoreboard. The
    overview data is the small display that just shows scores, inning,
    bases, and outs.
    """
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.overview = Overview(self.display_manager)

        self.redis = redis.Redis(redis_ip, port=6379, db=0, password=redis_password)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('brightness')
        self.pubsub.subscribe('mode')

        self.games: List[dict] = []

        self._page: int = None

    def _initialize_games(self):
        num_games = int(self.redis.get('num_games'))

        for i in range(num_games):
            self.pubsub.subscribe(f'{i}')
            game = self.redis.get(f'{i}')
            game = json.loads(game)
            self.games.append(game)

    def print_overview(self):
        """
        Prints all the games in the overview mode. It prints all games
        in three columns. This function only needs to be called when the
        mode is changed. When new data is received, the pubsub_listener
        function will update the data.
        """
        num_games = len(self.games)

        for i in range(num_games):
            self.overview.print_game(self.games[i], i)

    def print_gamecast_page(self):
        """
        Prints the current page of games in the gamecast mode. It prints
        all games in one columns. This function can be called anytime
        and will only print the current page of games.
        """
        self.display_manager.clear_section(0, 0, 128, 256)
        for i in range(6):
            game = self._page * 6 + i
            if game >= len(self.games):
                return
            self.overview.print_game(self.games[game], i)
        self.display_manager.swap_frame()

    def print_gamecast_pages(self):
        """
        Cycles through all the pages of games when in the gamecast mode.
        The iterator is stored in the self._page variable. This function
        will only print the current page of games and will wait 5 seconds
        """
        num_games = len(self.games)
        num_pages = math.ceil(num_games / 6)

        for self._page in range(num_pages):
            mode = self.redis.get('mode')
            if mode != b'gamecast':
                return
            self.print_gamecast_page()
            time.sleep(5)

    def change_settings(self, message: dict):
        """
        Changes the settings based on the message received from the
        pubsub listener. The settings that can be changed are the mode
        and the brightness. This fucntion will also call the appropriate
        function to print the correct data based on the mode to ahcieve
        maximum speed.

        Args:
            message (dict): Message received from the pubsub listener
        """
        channel = message['channel']

        if channel == b'mode':
            if message['data'] == b'overview':
                self.display_manager.clear_section(0, 0, 384, 256)
            elif message['data'] == b'gamecast':
                self.display_manager.clear_section(0, 0, 128, 256)
            self._page = 0

        if channel == b'brightness':
            x = int(message['data'])
            self.display_manager.set_brightness(brightness_dict_2pwm[x])

        if channel == b'init':
            self._initialize_games()

        mode = self.redis.get('mode')
        if mode == b'overview':
            self.print_overview()
        elif mode == b'gamecast':
            self.print_gamecast_page()

    def pubsub_listener(self):
        """
        Listens for messages from the pubsub and updates the games
        based on the message received.
        """
        message = self.pubsub.get_message(timeout=5)

        if not message:
            return

        if message['type'] != 'message':
            return

        if message['channel'] in (b'mode', b'brightness', b'init'):
            self.change_settings(message)
            return

        # print(f'{message=}\n')

        game_id = int(message['channel'])
        new_data = message['data'].decode('utf-8')
        new_data = json.loads(new_data)
        self.games[game_id] = recursive_update(self.games[game_id], new_data)

        mode = self.redis.get('mode')
        if mode == b'overview':
            self.overview.print_game(self.games[game_id], game_id)
        elif mode == b'gamecast':
            page = math.floor(game_id / 6)
            if page == self._page:
                self.overview.print_game(self.games[game_id], game_id % 6)

    def pubsub_thread(self):
        """
        Starts the pubsub listener thread that listens for messages
        from the redis server and updates the games based on the
        message received.
        """
        while True:
            self.pubsub_listener()

    def start(self):
        """
        Starts the overview handler. This function will initialize the
        games, print the overview, start the pubsub listener thread, and
        then print the gamecast pages.
        """
        self._initialize_games()
        self.display_manager.clear_section(0, 0, 128, 256)
        mode = self.redis.get('mode')
        if mode == b'overview':
            self.print_overview()

        threading.Thread(target=self.pubsub_thread, daemon=True).start()
        while True:
            self.print_gamecast_pages()

class Scoreboard:
    """
    Main class that connects all the aspects of the scoreboard together.
    """
    def __init__(self):
        self.display_manager = DisplayManager(get_options())

        self.overview = Overview(self.display_manager)

        self.time_handler = TimeHandler(self.display_manager, self.overview)
        self.overview_handler = OverviewHandler(self.display_manager)
        self.gamecast_handler = GamecastHandler(self.display_manager)

    def start(self):
        """
        Starts all the scoreboard elements in seperate threads.
        """

        threading.Thread(target=self.overview_handler.start, daemon=True).start()
        threading.Thread(target=self.gamecast_handler.start, daemon=True).start()

        # Easy main thread that runs continuously
        self.time_handler.start()

if __name__ == '__main__':
    scoreboard = Scoreboard()
    scoreboard.start()
