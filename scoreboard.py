"""
This module is used to start the scoreboard. It creates a new
scoreboard object and starts it. It also creates a new main server
object and starts it.
"""

import copy
import threading
from on_deck.main_server import MainServer
from on_deck.scoreboard import Scoreboard

def start_server(server):
    """Starts the server"""
    server.start()

def start_scoreboard(scoreboard):
    """Starts the scoreboard"""
    scoreboard.start()

def main():
    """
    Description: This function is used to start the scoreboard
    """
    game_template = {
        'game_state': None,
        'away_score': None,
        'home_score': None,
        'inning': None,
        'inning_state': None,
        'away': {
            'abv': None,
            'name': None,
            'location': None,
        },
        'home': {
            'abv': None,
            'name': None,
            'location': None
        },
        'count': {
            'balls': None,
            'strikes': None,
            'outs': None
        },
        'runners': None,
        'start_time': None,
        'matchup': {
            'batter': None,
            'batter_summary': None,
            'pitcher': None,
            'pitcher_summary': None
        },
        'decisions': {
            'win': None,
            'win_summary': None,
            'loss': None,
            'loss_summary': None,
            'save': None,
            'save_summary': None
        },
        'probables': {
            'away': None,
            'away_era': None,
            'home': None,
            'home_era': None
        },
        'pitch_details': {
            'description': None,
            'speed': None,
            'type': None,
            'zone': None,
            'spin_rate': None,
        },
        'hit_details': {
            'distance': None,
            'exit_velo': None,
            'launch_angle': None
        },
        'umpire': {
            'num_missed': None,
            'home_favor': None,
            'home_wpa': None
        },
        'run_expectancy': {
            'average_runs': None
        },
        'win_probability':{
            'away': None,
            'home': None,
            'extras': None
        },
        'flags': {
            'no_hitter': None,
            'perfect_game': None
        },
        'display_game': False
    }

    games = [copy.deepcopy(game_template) for _ in range(20)]

    scoreboard = Scoreboard(games)
    main_server = MainServer(games, scoreboard)

    server_thread = threading.Thread(target=start_server, args=(main_server,))
    scoreboard_thread = threading.Thread(target=start_scoreboard, args=(scoreboard,))

    server_thread.start()
    scoreboard_thread.start()

if __name__ == '__main__':
    main()
