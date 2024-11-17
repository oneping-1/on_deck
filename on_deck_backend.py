"""
This module starts the fetcher and server processes of the scoreboard.
The fetcher is responsible for fetching the data from the MLB API and
the server is responsible for obtaining user input. All the processes
communicate with each other through a Redis server.

The scoreboard should be started seperately as sudo for optimal
performance (ie reduce flickering)
"""

from multiprocessing import Process
import time

from on_deck.fetcher import Fetcher
from on_deck.server import Server
from on_deck_frontend import Scoreboard

def start_fetcher():
    """
    Starts the fetcher
    """
    fetcher = Fetcher()
    fetcher.start()

def start_server():
    """
    Starts the server
    """
    server = Server()
    server.start()

def start_scoreboard():
    """
    Starts the scoreboard
    """
    scoreboard = Scoreboard()
    scoreboard.start()

def main():
    """
    Main function
    """
    try:
        fetcher_process = Process(target=start_fetcher)
        server_process = Process(target=start_server)

        fetcher_process.start()
        server_process.start()

        print('Make sure to start the scoreboard manually as sudo')

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        fetcher_process.terminate()
        server_process.terminate()

        fetcher_process.join()
        server_process.join()

if __name__ == '__main__':
    main()
