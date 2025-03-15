# on_deck Scoreboard
This project is a MLB scoreboard built using Hub75 matrix displays, controlled by a Raspberry Pi. The Pi uses [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) as the backbone for controlling the displays. Data is sent via POST requests to the Pi with the endpoint indicating which game the data is for.

# Setup
run the following command from the ~ directory.
```
. /on_deck/setup/setup.sh
```
Wait for it to finish (takes a while)

# on_desk
If you want to run on_desk instead of on_deck, change the following lines:
```
# startup scripts
sudo cp ~/on_deck/setup/on_deck.service /etc/systemd/system/on_deck.service
#sudo cp ~/on_deck/setup/on_desk.service /etc/systemd/system/on_deck.service
```
to:
```
# startup scripts
#sudo cp ~/on_deck/setup/on_deck.service /etc/systemd/system/on_deck.service
sudo cp ~/on_deck/setup/on_desk.service /etc/systemd/system/on_deck.service
```