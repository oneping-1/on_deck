# on_deck Scoreboard
This project is a MLB scoreboard built using Hub75 matrix displays, controlled by a Raspberry Pi. The Pi uses [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) as the backbone for controlling the displays. Data is sent via POST requests to the Pi with the endpoint indicating which game the data is for.

If you want to run the emulator instead of the real thing (either on a Pi or a PC) make sure to change USE_EMULATOR.txt to true

# Setup
Uncomment whichever startup script you want to run (lines 57-84)
run the following command from the ~ directory.
```
. /on_deck/setup/setup.sh
```
Wait for it to finish (takes a while)