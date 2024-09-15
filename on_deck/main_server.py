"""
This module is used to create a scoreboard server. Used to recieve data
from the game and display it on the scoreboard. The MainServer class
is used to create the server and the recursive_update function is used
to update the dictionary recursively.
"""

from typing import List
from flask import Flask, request, jsonify
from on_deck.scoreboard import Scoreboard

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
    This class is used to create a scoreboard server. Used to recieve
    data from the game and display it on the scoreboard.
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

        self.scoreboard.gamecast.gamecast_game['display_game'] = False
        self.scoreboard.all_games.page = 0
        self.scoreboard.all_games.break_loop = True

        self.scoreboard.display_manager.clear_section(0, 0, 384, 256)
        self.scoreboard.print_welcome_message()
        self.scoreboard.display_manager.swap_frame()

        return jsonify({'message': 'Games reset'}), 200

    def settings(self):
        """
        Description: This function is used to set the mode of the scoreboard.
        """
        mode = request.args.get('mode', default=None)
        brightness = request.args.get('brightness', default=None)

        return_dict = {
            'mode': self.scoreboard.mode,
            'new_mode': self.scoreboard.new_mode,
            'brightness': self.scoreboard.display_manager.brightness
        }

        if mode is None and brightness is None:
            return jsonify({'message': return_dict}), 200

        if mode is not None:
            try:
                self.scoreboard.new_mode = mode
            except ValueError:
                return jsonify({'message': f'Mode {mode} not recognized'}), 200

        if brightness is not None:
            try:
                b = int(brightness)
                self.scoreboard.display_manager.set_brightness(b)
            except ValueError:
                return jsonify({'message': f'Brightness {brightness} not recognized'}), 200

        return_dict = {
            'mode': self.scoreboard.mode,
            'new_mode': self.scoreboard.new_mode,
            'brightness': self.scoreboard.display_manager.brightness
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

        r = recursive_update(self.scoreboard.gamecast.gamecast_game, new_data)
        self.scoreboard.gamecast.gamecast_game = r
        self.scoreboard.gamecast.gamecast_game['display_game'] = True

        if self.scoreboard.mode == 'gamecast':
            self.scoreboard.gamecast.print_gamecast()

        return_data = {'new_data': new_data, 'game': self.scoreboard.gamecast.gamecast_game}
        return jsonify(return_data), 200

    def print_game_if_on_page(self, game_index: int) -> bool:
        """
        This function is used to print the game if it is on the current page.

        Args:
            game_index (int): The index of the game to print.
        """
        games_per_page = 5
        num_pages = self.scoreboard.all_games.num_pages

        shifted_game_index = game_index - (self.scoreboard.all_games.page * games_per_page)

        if shifted_game_index < 0:
            shifted_game_index += num_pages * games_per_page

        if self.scoreboard.mode in ('basic', 'detailed', 'gamecast'):
            if shifted_game_index > 4:
                return False

        if self.scoreboard.mode == 'dual':
            if shifted_game_index > 9:
                return False

        self.scoreboard.all_games.print_game(shifted_game_index, self.games[game_index])
        self.scoreboard.display_manager.swap_frame()
        return True

    def start(self, port: int = 5000, debug: bool = False):
        """
        Starts the Flask server

        Args:
            port (int, optional): Flask server port. Defaults to 5000.
            debug (bool, optional): Debug mode. Defaults to False.
        """
        self.app.run(host='0.0.0.0', port=port, debug=debug)
