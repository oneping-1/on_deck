from typing import List
import os
import sys
import json
import redis
from flask import Flask, request, Response

from at_bat.scoreboard_data import ScoreboardData

class Server:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home, methods=['GET'])
        self.app.add_url_rule('/reset', 'reset', self.reset, methods=['GET'])
        self.app.add_url_rule('/settings', 'settings', self.settings, methods=['GET'])
        self.app.add_url_rule('/<int:gamepk>', 'gamepk', self.gamepk, methods=['GET'])
        # self.app.add_url_rule('/gamecast', 'gamecast', self.gamecast, methods=['GET'])

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

    def reset(self):
        """
        Hard resets the Raspberry Pi
        """
        sys.stdout.flush()
        os.system('sudo reboot')

    def settings(self):
        """
        Fetches settings from the flask server. Allows the user to
        change various aspects of the scoreboard.

        Returns:
            Response: HTML Response
        """
        mode = request.args.get('mode', default=None)
        delay = request.args.get('delay', default=None)

        if mode is not None:
            self.redis.set('mode', mode)
        if delay is not None:
            self.redis.set('delay', delay)

        mode = self.redis.get('mode')
        delay = self.redis.get('delay')

        return_dict = {
            'mode': mode,
            'delay': delay
        }

        return Response(json.dumps(return_dict, indent=4), status=200, mimetype='application/json')

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

    def start(self):
        self.app.run(host='0.0.0.0', port=5123)

if __name__ == '__main__':
    server = Server()
    server.start()
