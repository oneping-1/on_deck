# OnDeck Scoreboard
This project is a MLB scoreboard built using Hub75 matrix displays, controlled by a Raspberry Pi. The Pi uses [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) as the backbone for controlling the displays. Data is sent via POST requests to the Pi with the endpoint indicating which game the data is for.

## Setup
To install and start the OnDeck scoreboard the following should be typed into the console

Go to this link: https://davesteele.github.io/comitup/ppa.html. Right click on "davesteele-comitup-apt-source deb" and copy link address

In the console of the Pi:
```
wget # paste link here and enter
sudo dpkg -i davesteele-comitup-apt-source*.deb
sudo apt-get update
sudo apt-get install comitup git pip nginx python3-dev python3-redis cython3 redis-server -y
sudo apt-get upgrade -y
rm davesteele-comitup-apt-source*.deb

git clone https://github.com/hzeller/rpi-rgb-led-matrix
git clone https://github.com/oneping-1/OnDeck-RaspberryPi
git clone https://github.com/oneping-1/at_bat

python3 -m venv venv
. venv/bin/activate

cd at_bat
pip install -e .
pip install -r requirements.txt

cd ..
cd OnDeck-RaspberryPi
pip install -e .
pip install -r requirements.txt
sudo pip install -e . --break-system-packages

deactivate
cd ..
cd rpi-rgb-led-matrix
make build-python
sudo make install-python

# Debugging
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

sudo rm /etc/nginx/sites-enabled/default

sudo nano /etc/redis/redis.conf
```

Change the following to and save:
```
bind 0.0.0.0
protected-mode yes
requirepass your_password
```

```
sudo systemctl restart redis

Open crontab by
```
crontab -e
```
Select nano option
Add the following to the end of the file
```
@reboot sleep 40; /home/ondeck/venv/bin/python /home/ondeck/OnDeck-RaspberryPi/on_deck_fetcher.py >> /home/ondeck/fetcher.log 2>&1
@reboot sleep 40; cd /home/ondeck/OnDeck-RaspberryPi; sudo /home/ondeck/venv/bin/gunicorn -w 2 -b 0.0.0.0:80 on_deck_server:app >> /home/ondeck/server.log 2>&1
@reboot sleep 40; sudo python /home/ondeck/OnDeck-RaspberryPi/on_deck_display.py >> /home/ondeck/display.log 2>&1
```

Edit cmdline.txt by
```
sudo nano /boot/firmware/cmdline.txt
```
Add the following and save
```
isolcpus=3
```
Then finally in the console
```
sudo reboot
```