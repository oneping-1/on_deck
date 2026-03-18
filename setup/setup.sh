#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt-get install python3-pip nginx python3-dev python3-redis python3-pil cython3 redis-server build-essential -y

echo 'export REDIS_HOST=192.168.7.100' | sudo tee /etc/profile.d/redis_host.sh

# download repositories
git clone https://github.com/hzeller/rpi-rgb-led-matrix
git clone https://github.com/oneping-1/at_bat

# install on_deck
cd ..
cd on_deck
sudo pip install -e .
pip install -r requirements.txt --break-system-packages
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

# display script
sudo cp ~/on_deck/setup/display.service /etc/systemd/system/display.service
sudo systemctl daemon-reload
sudo systemctl enable display.service
sudo systemctl start display.service

# go back to home
cd /home/on_deck/
