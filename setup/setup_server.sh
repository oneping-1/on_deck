#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt-get install python3-pip nginx python3-dev python3-redis cython3 redis-server -y

# download repositories
git clone https://github.com/hzeller/rpi-rgb-led-matrix
git clone https://github.com/oneping-1/at_bat

# create virtual environment
python3 -m venv venv
. venv/bin/activate

# install at_bat
cd at_bat
pip install -e .
pip install -r requirements.txt

# install on_deck
cd ..
cd on_deck
pip install -e .
pip install -r requirements.txt
sudo pip install -e . --break-system-packages
chmod +x setup/update.sh

# nginx
sudo rm /etc/nginx/sites-enabled/default

# redis
sudo cp ~/on_deck/setup/redis.conf /etc/redis/redis.conf
sudo systemctl restart redis
sudo systemctl restart redis-server

# update script
sudo cp ~/on_deck/setup/update.service /etc/systemd/system/update.service
sudo systemctl daemon-reload
sudo systemctl enable update.service
sudo systemctl start update.service

# server script
sudo cp ~/on_deck/setup/server.service /etc/systemd/system/server.service
sudo systemctl daemon-reload
sudo systemctl enable server.service
sudo systemctl start server.service

# fetcher script
sudo cp ~/on_deck/setup/fetcher.service /etc/systemd/system/fetcher.service
sudo systemctl daemon-reload
sudo systemctl enable fetcher.service
sudo systemctl start fetcher.service

# emulator script
sudo cp ~/on_deck/setup/emulator.service /etc/systemd/system/emulator.service
sudo systemctl daemon-reload
sudo systemctl enable emulator.service
sudo systemctl start emulator.service

# go back to home
cd /home/on_deck/