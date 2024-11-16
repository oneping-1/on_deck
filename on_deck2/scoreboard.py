from typing import List
import threading
import time
import json
import platform
import redis

from on_deck2.display_manager import DisplayManager
from on_deck2.overview import Overview

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrixOptions # pylint: disable=E0401
else:
    from rgbmatrix import RGBMatrixOptions # pylint: disable=E0401

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
        options.pwm_bits = 1
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

        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()

        self.display_manager = DisplayManager(get_options())
        self.display_manager.swap_frame()

        self.overview = Overview(self.display_manager)

    def print_games(self):
        num_games = int(self.redis.get('num_games'))
        for i in range(num_games):
            self.overview.print_game(self.games[i], i)
            self.display_manager.swap_frame()

    def start(self):
        """
        Starts the scoreboard
        """
        num_games = int(self.redis.get('num_games'))

        while (num_games is None) or (num_games == 0):
            time.sleep(1)
            num_games = int(self.redis.get('num_games'))

        for i in range(num_games):
            # I'm a little conerned this will try to access a key that
            # doesn't exist yet because the fetcher hasn't finished
            self.games.append(json.loads(self.redis.get(str(i))))
            self.pubsub.subscribe(str(i))

        threading.Thread(target=self.listen_to_pubsub).start()
        while True:
            self.print_games()
            time.sleep(100)

    def listen_to_pubsub(self):
        """
        Listens to the pubsub channel for updates to the game
        """
        while True:
            for message in self.pubsub.listen():
                self._read_pubsub_message(message)
            time.sleep(1)

    def _read_pubsub_message(self, message):
        if message['type'] != 'message':
            return

        game_id = int(message['channel'])
        new_data = json.loads(message['data'])

        self.games[game_id] = recursive_update(self.games[game_id], new_data)

if __name__ == '__main__':
    scoreboard = Scoreboard()
    scoreboard.start()
