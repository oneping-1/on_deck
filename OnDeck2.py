"""
Main file for the OnDeck project. This file starts all the necessary
processes for the project to run. It uses processes instead of threading
because blocking processes can mess with the hub75 display timings.
"""

from multiprocessing import Process
import platform

from on_deck2.fetcher import Fetcher
from on_deck2.server import Server

if platform.system() == 'Windows':
    from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics # pylint: disable=E0401
else:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics # pylint: disable=E0401

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

def main():
    """
    Main function
    """
    try:
        fetcher_process = Process(target=start_fetcher)
        server_process = Process(target=start_server)

        print('fetcher start')
        fetcher_process.start()

        print('server start')
        server_process.start()

        # time.sleep?

    except KeyboardInterrupt:
        fetcher_process.terminate()
        server_process.terminate()

        fetcher_process.join()
        server_process.join()

if __name__ == '__main__':
    main()
