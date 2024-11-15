from typing import List, Union
import threading
import time
import json
import redis

from at_bat import statsapi_plus as ssp
from at_bat.scoreboard_data import ScoreboardData

def get_daily_gamepks() -> List[int]:
    """
    Returns a list of gamepks for a given date.

    Args:
        date (str): Date in the format 'YYYY-MM-DD'

    Returns:
        List[int]: List of gamepks
    """
    gamepks = ssp.get_daily_gamepks('2024-05-29')
    return gamepks

class Fetcher:
    """
    Class that fetches game data from the at_bat module. It stores the
    game data in a redis database and updates the data periodically.
    """
    def __init__(self):
        self.gamepks: List[int] = []
        self.games: List[ScoreboardData] = []
        self.delay = 60

        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('delay')

        self.initialize_games()

    def initialize_games(self):
        """
        Initializes the games list with the game data from the at_bat
        module. It stores the game data in the redis database.
        """
        self.gamepks = get_daily_gamepks()

        for i, gamepk in enumerate(self.gamepks):
            game = ScoreboardData(gamepk, self.delay)
            self.games.append(game)
            self.redis_set(str(i), game.to_dict())
            time.sleep(.1) # Multithreading Help

        num_games = len(self.games)
        self.redis_set('num_games', num_games)

    def update_games(self):
        """
        Updates the game data in the games list and redis database.
        """
        for i, game in enumerate(self.games):
            diff = game.update_return_difference(self.delay)
            if diff:
                self.redis_set(str(i), game.to_dict())
                self.redis_publish(str(i), diff)

    def redis_set(self, key: Union[str, int], value: Union[int, dict]):
        """
        Set a key-value pair in the redis database

        Args:
            key (Union[str, int]): Normally game id number
            value (Union[int, dict]): Value
        """
        key = str(key)
        value = json.dumps(value)

        self.redis.set(key, value)

    def redis_publish(self, key: Union[str, int], value: Union[int, dict]):
        """
        Publish a message to the redis database

        Args:
            key (Union[str, int]): Normally game id number
            value (Union[int, dict]): Value
        """
        key = str(key)
        value = json.dumps(value)

        self.redis.publish(key, value)

    def start(self):
        """
        Starts the fetcher and periodically updates the game data.
        """
        threading.Thread(target=self.listen_for_pubsub, daemon=True).start()
        while True:
            self.delay = self.redis.get('delay')
            self.update_games()
            # Check for user input from server
            time.sleep(30)

    def listen_for_pubsub(self):
        """
        Listens for user input from the server.
        """
        while True:
            for message in self.pubsub.listen():
                self._read_pubsub_message(message)
            time.sleep(1) # Multithreading Help

    def _read_pubsub_message(self, message):
        """
        Reads the pubsub message and sets the delay attribute.

        Args:
            message: Pubsub message
        """
        if message['type'] != 'message':
            return

        channel = message['channel'].decode('utf-8')

        if channel == 'delay':
            self.delay = int(message['data'])

        return

if __name__ == '__main__':
    fetcher = Fetcher()
    fetcher.start()
