import requests
import json

url = 'http://127.0.0.1:5000'

def send_data(game_index: int, data: dict):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f'{url}/{game_index}', headers=headers, data=json.dumps(data), timeout=10)
    print(json.dumps(response.json()))

def main():
    game0a = {
        'game_state': 'L',
        'away_abv': 'NYM',
        'home_abv': 'TEX',
        'away_score': 0,
        'home_score': 0,
        'inning': 1,
        'inning_state': 'T',
        'outs': 0,
        'balls': 0,
        'strikes': 0,
        'runners': 0,
        'batter': 'Michael Conforto',
        'pitcher': 'Mike Minor',
    }

    game0b = {
        'away_score': 1,
        'home_score': 1
    }

    game1a = {
        'game_state': 'F',
        'away_abv': 'LAA',
        'home_abv': 'MIA',
        'away_score': 2,
        'home_score': 3,
        'inning': 9,
        'inning_state': 'T',
        'outs': 3
    }
    game2a = {
        'game_state': 'F',
        'away_abv': 'LAA',
        'home_abv': 'MIA',
        'away_score': 2,
        'home_score': 3,
        'inning': 10,
        'inning_state': 'T',
        'outs': 3
    }

    game3a = {
        'game_state': 'P',
        'away_abv': 'SEA',
        'home_abv': 'PIT',
        'inning': 1,
        'inning_state': 'T',
        'outs': 0,
        'balls': 0,
        'strikes': 0,
        'runners': 0,
        'start_time': '7:05'
    }

    game4a = {
        'flags' : {
            'no_hitter': True,
            'perfect_game': False,
        }
    }

    # send_data(1, game0a)
    # send_data(0, game0b)
    # send_data(1, game1a)
    # send_data(2, game2a)
    # send_data(3, game3a)
    send_data(0, game4a)
    # send_data(5, game4a)

def main2():
    data = {
        'inning_state': 'B'
    }

    send_data(0, game4a)

if __name__ == '__main__':
    main()
