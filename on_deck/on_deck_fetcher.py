"""
This module is responsible for fetching data from the MLB Stats API
and updating the Redis database with the fetched data. It also listens
for changes to the settings and updates the Redis database accordingly.
"""

import time
from typing import List, Union
import json
import threading
from datetime import datetime
import platform
import pytz
import redis

from at_bat import statsapi_plus as ssp
from at_bat.scoreboard_data import ScoreboardData

redis_ip = '192.168.1.90'
redis_password = 'on_deck'

def seconds_since_iso8601(iso_timestamp: str) -> int:
    """
    Calculate the number of seconds since a given ISO 8601 timestamp.

    Args:
        iso_timestamp (str): The ISO 8601 formatted timestamp (e.g., "2024-05-29T15:00:00-04:00").

    Returns:
        int: The number of seconds since the given timestamp.
    """
    # Parse the ISO 8601 string into a datetime object
    target_time = datetime.fromisoformat(iso_timestamp)

    # Check if the timestamp includes a timezone; if not, assume it's UTC
    if target_time.tzinfo is None:
        target_time = target_time.replace(tzinfo=pytz.UTC)

    # Get the current time in the same timezone as the target time
    current_time = datetime.now(pytz.utc).astimezone(target_time.tzinfo)

    # Adjust for DST if applicable
    if target_time.dst() != current_time.dst():
        target_time = target_time + target_time.dst() - current_time.dst()

    # Calculate the difference in seconds
    difference = current_time - target_time
    return int(difference.total_seconds())

def get_daily_gamepks() -> List[int]:
    """
    Returns a list of gamepks for a given date.

    Args:
        date (str): Date in the format 'YYYY-MM-DD'

    Returns:
        List[int]: List of gamepks
    """
    gamepks = ssp.get_daily_gamepks()
    return gamepks

class GamecastFetcher:
    """
    Class that fetches gamecast data from the Redis database and updates
    the gamecast data in the Redis database. It listens for changes to the
    settings and updates the gamecast data accordingly.
    """
    def __init__(self):
        self.redis = redis.Redis(host=redis_ip, port=6379, db=0, password=redis_password)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('delay')
        self.pubsub.subscribe('gamecast_id')

        self.gamepk: int = None
        self.game: ScoreboardData = None

    def initialize_gamecast(self):
        """
        Initializes the gamecast data by fetching the gamecast_id and delay
        from the Redis database and creating a ScoreboardData object for the
        corresponding game. It then updates the gamecast data in the Redis
        database.
        """
        delay = int(self.redis.get('delay'))

        try:
            gamecast_id = int(self.redis.get('gamecast_id'))
        except TypeError:
            gamecast_id = 0
            self.redis.set('gamecast_id', gamecast_id)

        game_dict = json.loads(self.redis.get(gamecast_id))
        gamepk = int(game_dict['gamepk'])

        self.game = ScoreboardData(gamepk, delay)
        self.redis.set('gamecast', json.dumps(self.game.to_dict()))

        print('Gamecast initialized')

    def update_gamecast(self):
        """
        Updates the gamecast data by fetching the delay from the Redis database
        and updating the ScoreboardData object with the new delay. It then
        updates the gamecast data in the Redis database and publishes the
        updated data to the 'gamecast' channel.
        """
        delay = int(self.redis.get('delay'))

        new_data = self.game.update_return_difference(delay)
        if new_data:
            # Update gamecast and cooresponding overview game
            gamecast_dict = json.dumps(self.game.to_dict())
            new_data = json.dumps(new_data)

            self.redis.set('gamecast', gamecast_dict)
            self.redis.publish('gamecast', new_data)

    def update_settings(self):
        """
        Listens for changes to the settings in the Redis database and updates
        the gamecast data accordingly. It listens for changes to the 'delay'
        and 'gamecast_id' channels.
        """
        message = self.pubsub.get_message(timeout=5)

        if not message:
            return

        if message['type'] != 'message':
            return

        if message['channel'] in (b'delay', b'gamecast_id'):
            self.initialize_gamecast()

    def start(self):
        """
        Starts the gamecast fetcher and listens for changes to the settings
        in the Redis database. It initializes the gamecast data and then
        updates the gamecast data in a loop.
        """
        self.initialize_gamecast()

        while True:
            self.update_settings()
            self.update_gamecast()
            time.sleep(.1)

class Fetcher:
    """
    Class that fetches scoreboard data from the MLB Stats API and updates
    the Redis database with the fetched data. It listens for changes to the
    settings and updates the Redis database accordingly. It also fetches
    gamecast data and updates the Redis database with the fetched data.
    """
    def __init__(self):
        self.gamepks: List[int] = []
        self.games: List[ScoreboardData] = []

        self.redis = redis.Redis(host=redis_ip, port=6379, db=0, password=redis_password)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('delay') # do i need this?

        self.gamecast_fetcher = GamecastFetcher()

    def redis_set_game(self, key: Union[str, int], full_game: dict):
        """
        Sets the game data in the Redis database.

        Args:
            key (Union[str, int]): key to set
            full_game (dict): full game data to set
        """
        key = f'{key}'
        full_game = json.dumps(full_game)
        self.redis.set(key, full_game)

    def redis_publish_game(self, key: Union[str, int], new_data: dict):
        """
        Publishes the updated game data to the corresponding channel in
        the Redis database.

        Args:
            key (Union[str, int]): key to publish to
            new_data (dict): updated game data
        """
        key = f'{key}'
        new_data = json.dumps(new_data)
        self.redis.publish(key, new_data)

    def initialize_games(self):
        """
        Initializes the games by fetching the gamepks for the current date
        and creating ScoreboardData objects for each game. It then updates
        the games in the Redis database and publishes the updated data to the
        corresponding channels.
        """
        self.gamepks = get_daily_gamepks()
        try:
            delay = int(self.redis.get('delay'))
        except TypeError:
            delay = 0
            self.redis.set('delay', delay)

        for i, gamepk in enumerate(self.gamepks):
            game = ScoreboardData(gamepk, delay)
            self.games.append(game)
            self.redis_set_game(i, game.to_dict())

        print(f'{delay=}')
        print('Overview initialized')
        num_games = len(self.games)
        self.redis.set('num_games', num_games)
        self.redis.publish('init_games', 'init_games')

    def update_games(self):
        """
        Updates the games by fetching the delay from the Redis database and
        updating the ScoreboardData objects with the new delay. It then updates
        the games in the Redis database and publishes the updated data to the
        corresponding channels.
        """
        for i, game in enumerate(self.games):
            delay = int(self.redis.get('delay'))
            new_data = game.update_return_difference(delay)
            if new_data:
                self.redis_set_game(i, game.to_dict())
                self.redis_publish_game(i, new_data)
            time.sleep(.1)

        # Check for new gamepks every 60 seconds
        last_check = time.time()
        if (time.time() - last_check) > 60:
            last_check = time.time()
            new_gamepks = get_daily_gamepks()
            if new_gamepks != self.gamepks:
                print('New gamepks detected, reinitializing games')
                self.initialize_games()

    def start(self):
        """
        Starts the fetcher and listens for changes to the settings in the
        Redis database. It initializes the games and then updates the games
        in a loop.
        """
        # date = '2024-05-29T14:37:00-04:00'
        # delay = seconds_since_iso8601(date)
        # self.redis.set('delay', delay)
        # self.redis.publish('delay', delay)

        self.initialize_games()
        threading.Thread(target=self.gamecast_fetcher.start, daemon=True).start()
        while True:
            self.update_games()

if __name__ == '__main__':
    if platform.system() != 'Windows':
        time.sleep(30) # Wait for Redis to start
    fetcher = Fetcher()
    fetcher.start()
