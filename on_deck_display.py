from typing import Union, List
import json
import redis
import platform
import threading
import time
import math

from on_deck.display_manager import DisplayManager
from on_deck.overview import Overview
from on_deck.gamecast import Gamecast

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrixOptions
else:
    from rgbmatrix import RGBMatrixOptions

brightness_dict_2pwm = {0: 0, 1: 60, 2: 80, 3: 90}

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
    def __init__(self, display_manager: DisplayManager, overview: Overview):
        self.display_manager = display_manager
        self.overview = overview

        self.redis = redis.Redis('192.168.1.83', port=6379, db=0, password='ondeck')

    def start(self):
        while True:
            delay = int(self.redis.get('delay'))
            self.overview.print_time(delay, 17)
            time.sleep(.1)

class GamecastHandler:
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.game: dict = None

        self.redis = redis.Redis('192.168.1.83', port=6379, db=0, password='ondeck')
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('gamecast')
        self.pubsub.subscribe('brightness')
        self.pubsub.subscribe('gamecast_id')
        self.pubsub.subscribe('mode')

        self.gamecast: Gamecast = Gamecast(self.display_manager)
        self.gamecast_game: dict = None

        self._mode: str = None

    def _load_gamecast(self) -> dict:
        game = self.redis.get('gamecast')
        game = json.loads(game)
        self.gamecast_game = game
        return game

    def _change_settings(self, message):
        channel = message['channel']

        if channel == b'gamecast_id':
            new_data = self.redis.get('gamecast')
            new_data = json.loads(new_data)
            self.gamecast_game = new_data
            self.gamecast.print_game(self.gamecast_game)
            return

        if channel == b'brightness':
            brightness = int(message['data'])
            self.display_manager.set_brightness(brightness_dict_2pwm[brightness])
            if self._mode == b'gamecast':
                self.gamecast.print_game(self.gamecast_game)
            return

        if channel == b'mode':
            mode = message['data']
            self._mode = mode
            if self._mode == b'gamecast':
                self.gamecast.print_game(self.gamecast_game)
            elif self._mode == b'overview':
                self.display_manager.clear_section(129, 0, 384, 256)
                self.display_manager.swap_frame()
            return

    def _update_gamecast(self) -> Union[bool, dict]:
        message = self.pubsub.get_message(timeout=5)

        if not message:
            return False

        if message['type'] != 'message':
            return False

        if message['channel'] in (b'gamecast_id', b'brightness', b'mode'):
            self._change_settings(message)
            return

        new_data = json.loads(message['data'])
        print(f'{new_data=}\n')
        if new_data == {}:
            return False

        self.gamecast_game = recursive_update(self.gamecast_game, new_data)
        return new_data

    def print_gamecast_game(self):
        new_data = self._update_gamecast()

        if new_data is False:
            return False

        mode = self.redis.get('mode')
        if mode != b'gamecast':
            return False

        self.gamecast.print_game(self.gamecast_game)

    def start(self):
        self._gamecast_id = int(self.redis.get('gamecast_id'))
        self._brightness = int(self.redis.get('brightness'))
        self._mode = str(self.redis.get('mode'))

        game = self._load_gamecast()
        self.gamecast.print_game(game)

        while True:
            self.print_gamecast_game()

class OverviewHandler:
    def __init__(self, display_manager: DisplayManager):
        self.display_manager = display_manager
        self.overview = Overview(self.display_manager)

        self.redis = redis.Redis('192.168.1.83', port=6379, db=0, password='ondeck')
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('brightness')
        self.pubsub.subscribe('mode')

        self.games: List[dict] = []

        self._page: int = None
        self._mode: str = None

    def _initialize_games(self):
        num_games = int(self.redis.get('num_games'))

        for i in range(num_games):
            self.pubsub.subscribe(f'{i}')
            game = self.redis.get(f'{i}')
            game = json.loads(game)
            self.games.append(game)

    def print_overview(self):
        # function only needs to be called when mode is changed
        num_games = len(self.games)

        for i in range(num_games):
            self.overview.print_game(self.games[i], i)

    def print_gamecast_page(self):
        for i in range(6):
            game = self._page * 6 + i
            if game >= len(self.games):
                return
            self.overview.print_game(self.games[game], i)

    def print_gamecast_pages(self):
        if self._mode != b'gamecast':
            return

        num_games = len(self.games)
        num_pages = math.ceil(num_games / 6)

        for self._page in range(num_pages):
            if self._mode != b'gamecast':
                return
            self.display_manager.clear_section(0, 0, 128, 256)
            self.print_gamecast_page()
            self.display_manager.swap_frame()
            time.sleep(5)

    def change_settings(self, message: dict):
        channel = message['channel']

        if channel == b'mode':
            self.display_manager.clear_section(0, 0, 384, 256)
            self._mode = message['data']
            if self._mode == b'overview':
                self.print_overview()

        if channel == b'brightness':
            x = int(message['data'])
            self.display_manager.set_brightness(brightness_dict_2pwm[x])
            if self._mode == b'overview':
                self.print_overview()
            elif self._mode == b'gamecast':
                self.print_gamecast_page()

    def pubsub_listener(self):
        message = self.pubsub.get_message(timeout=5)

        if not message:
            return

        if message['type'] != 'message':
            return

        if message['channel'] in (b'mode', b'brightness'):
            self.change_settings(message)
            return

        print(f'{message=}\n')

        game_id = int(message['channel'])
        new_data = message['data'].decode('utf-8')
        new_data = json.loads(new_data)
        self.games[game_id] = recursive_update(self.games[game_id], new_data)

        if self._mode == b'overview':
            self.overview.print_game(self.games[game_id], game_id)
        elif self._mode == b'gamecast':
            page = math.floor(game_id / 6)
            if page == self._page:
                self.overview.print_game(self.games[game_id], game_id % 6)

    def pubsub_thread(self):
        while True:
            self.pubsub_listener()

    def start(self):
        self._initialize_games()
        self._mode = self.redis.get('mode')
        self.display_manager.clear_section(0, 0, 128, 256)
        if self._mode == b'overview':
            self.print_overview()

        threading.Thread(target=self.pubsub_thread, daemon=True).start()
        while True:
            self.print_gamecast_pages()

class Scoreboard:
    def __init__(self):
        self.display_manager = DisplayManager(get_options())

        self.overview = Overview(self.display_manager)

        self.time_handler = TimeHandler(self.display_manager, self.overview)
        self.overview_handler = OverviewHandler(self.display_manager)
        self.gamecast_handler = GamecastHandler(self.display_manager)

    def start(self):
        threading.Thread(target=self.overview_handler.start, daemon=True).start()
        threading.Thread(target=self.gamecast_handler.start, daemon=True).start()

        # Easy main thread that runs continuously
        self.time_handler.start()

if __name__ == '__main__':
    scoreboard = Scoreboard()
    scoreboard.start()
