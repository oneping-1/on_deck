"""
This file contains the server for the scoreboard. It is used to
communicate with the scoreboard and the redis database. It is
used to fetch the current games, change the settings of the
scoreboard, and reboot the Raspberry Pi.
"""
from typing import List
import os
import sys
import json
import redis
from flask import Flask, request, Response

from at_bat.scoreboard_data import ScoreboardData

class Server:
    """
    This class contains the server for the scoreboard. It is used to
    communicate with the scoreboard and the redis database. It is
    used to fetch the current games, change the settings of the
    scoreboard, and reboot the Raspberry Pi.
    """
    def __init__(self):
        self.redis = redis.Redis(host='192.168.1.90', port=6379, db=0, password='on_deck')

        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home, methods=['GET'])
        self.app.add_url_rule('/reboot', 'reboot', self.reboot, methods=['GET'])
        self.app.add_url_rule('/settings', 'settings', self.settings, methods=['GET'])
        self.app.add_url_rule('/<int:gamepk>', 'gamepk', self.gamepk, methods=['GET'])
        self.app.add_url_rule('/gamecast', 'gamecast', self.gamecast, methods=['GET'])


    def home(self):
        """
        Prints the home page of the server. Used to make sure the server
        is running correctly. It returns the current games in the redis
        database.

        Returns:
            Response: HTML Response
        """
        num_games = self.redis.get('num_games')
        games: List[dict] = []

        if (num_games == 0) or (num_games is None):
            return Response(json.dumps({}, indent=4), status=200, mimetype='application/json')

        for i in range(int(num_games)):
            game = self.redis.get(str(i))
            game = json.loads(game)
            games.append(game)

        return Response(json.dumps(games, indent=4), status=200, mimetype='application/json')


    def reboot(self):
        """
        Hard reboots the Raspberry Pi
        """
        sys.stdout.flush()
        os.system('sudo reboot')


    def _parse_mode(self, mode: str):
        if mode is None:
            return
        if mode in ('overview', '0'):
            mode = 'overview'
        elif mode in ('gamecast', '1'):
            mode = 'gamecast'
        else:
            return
        self.redis.set('mode', mode)
        self.redis.publish('mode', mode)


    def _parse_delay_delta(self, delay: str) -> int:
        if delay is None or delay[0] not in ('p', 'm'):
            return int(delay)
        old_delay = int(self.redis.get('delay'))
        delay_delta = int(delay[1:])
        if delay[0] == 'p':
            return int(old_delay + delay_delta)
        if delay[0] == 'm':
            return max(0, int(old_delay - delay_delta))
        return


    def _parse_delay(self, delay: str):
        if delay is None:
            return
        if delay[0] in ('p', 'm'):
            delay = self._parse_delay_delta(delay)
        delay = max(0, int(delay))
        self.redis.set('delay', delay)
        self.redis.publish('delay', delay)
        return


    def _parse_brightness(self, brightness: str):
        if brightness is None:
            return
        brightness = int(brightness)
        if not (0 <= brightness <= 3):
            return # brightness not in range
        self.redis.set('brightness', brightness)
        self.redis.publish('brightness', brightness)
        return


    def _parse_gamecast_id(self, gamecast_id: str):
        if gamecast_id is None:
            return
        gamecast_id = int(gamecast_id)
        max_gamecast_id = int(self.redis.get('num_games')) - 1
        if not (0 <= gamecast_id <= max_gamecast_id):
            return
        self.redis.set('gamecast_id', gamecast_id)
        self.redis.publish('gamecast_id', gamecast_id)
        return


    def settings(self):
        """
        Fetches settings from the flask server. Allows the user to
        change various aspects of the scoreboard.

        Returns:
            Response: HTML Response
        """
        mode = request.args.get('mode', default=None)
        delay = request.args.get('delay', default=None)
        brightness = request.args.get('brightness', default=None)
        gamecast_id = request.args.get('gamecast_id', default=None)

        self._parse_mode(mode)
        self._parse_delay(delay)
        self._parse_brightness(brightness)
        self._parse_gamecast_id(gamecast_id)

        mode = self.redis.get('mode')
        if mode is not None:
            mode = mode.decode('utf-8')

        delay = self.redis.get('delay')
        if delay is not None:
            delay = int(delay)

        brightness = self.redis.get('brightness')
        if brightness is not None:
            brightness = int(brightness)

        gamecast_id = self.redis.get('gamecast_id')
        if gamecast_id is not None:
            gamecast_id = int(gamecast_id)

        num_games = self.redis.get('num_games')
        if num_games is not None:
            num_games = int(num_games)

        return_dict = {
            'mode': mode,
            'delay': delay,
            'brightness': brightness,
            'gamecast_id': gamecast_id,
            'num_games': num_games
        }

        return Response(json.dumps(return_dict, indent=4), status=200, mimetype='text/plain')


    def gamepk(self, gamepk: int):
        """
        Allows a user to fetch scoreboard data for a specific game.
        This game does not have to be one that is currently in the
        daily gamepks list

        Args:
            gamepk (int): Gamepk of the game

        Returns:
            Response: HTML Response
        """
        game = ScoreboardData(gamepk, 0)
        game = game.to_dict()

        return Response(json.dumps(game, indent=4), status=200, mimetype='text/plain')


    def gamecast(self):
        """
        Allows a user to fetch gamecast data for the current game.
        This game does not have to be one that is currently in the
        daily gamepks list
        This is used to fetch gamecast data for the current game.

        Returns:
            Response: HTML Response
        """
        gamecast_game = self.redis.get('gamecast')
        gamecast_game = json.loads(gamecast_game)
        self.redis.publish('gamecast_reset', 'gamecast_reset')

        return Response(json.dumps(gamecast_game, indent=4), status=200, mimetype='text/plain')


server = Server()
app = server.app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
