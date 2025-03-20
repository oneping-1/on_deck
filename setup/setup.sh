#!/bin/bash

# setup comitup
wget https://davesteele.github.io/comitup/deb/davesteele-comitup-apt-source_1.2_all.deb
sudo dpkg -i davesteele-comitup-apt-source*.deb
sudo apt-get update
sudo apt-get install comitup pip nginx python3-dev python3-redis cython3 redis-server -y
sudo apt-get upgrade -y
rm davesteele-comitup-apt-source*.deb

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

# install rpi-rgb-led-matrix
deactivate
cd ..
cd rpi-rgb-led-matrix
make build-python
sudo make install-python
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)
sudo sed -i '1s/$/ isolcpus=3/' /boot/firmware/cmdline.txt # adds isolcpus=3 to the end of  cmdline.txt

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
sudo cp ~/on_deck/setup/display.service /etc/systemd/system/emulator.service
sudo systemctl daemon-reload
sudo systemctl enable emulator.service
sudo systemctl start emulator.service

# display script
sudo cp ~/on_deck/setup/display.service /etc/systemd/system/display.service
sudo systemctl daemon-reload
sudo systemctl enable display.service
sudo systemctl start display.service

# on_desk script
# sudo cp ~/on_deck/setup/on_desk.service /etc/systemd/system/on_desk.service
# sudo systemctl daemon-reload
# sudo systemctl enable on_desk.service
# sudo systemctl start on_desk.service

# menu-complete
bind -f /home/on_deck/on_deck/setup/.inputrc

# go back to home
cd /home/on_deck/