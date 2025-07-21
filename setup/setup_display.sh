#!/bin/bash

sudo apt update
sudo apt upgrade -y

sudo apt-get install python3-pip nginx python3-dev python3-redis cython3 redis-server -y

# download repositories
git clone https://github.com/hzeller/rpi-rgb-led-matrix

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

# update script
sudo cp ~/on_deck/setup/update.service /etc/systemd/system/update.service
sudo systemctl daemon-reload
sudo systemctl enable update.service
sudo systemctl start update.service

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

# go back to home
cd /home/on_deck/