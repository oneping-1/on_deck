# setup comitup
wget https://davesteele.github.io/comitup/deb/davesteele-comitup-apt-source_1.2_all.deb
sudo dpkg -i davesteele-comitup-apt-source*.deb
sudo apt-get update
sudo apt-get install comitup git pip nginx python3-dev python3-redis cython3 redis-server -y
sudo apt-get upgrade -y
rm davesteele-comitup-apt-source*.deb

# download repositories
git clone https://github.com/hzeller/rpi-rgb-led-matrix
git clone https://github.com/oneping-1/OnDeck-RaspberryPi
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
cd OnDeck-RaspberryPi
pip install -e .
pip install -r requirements.txt
sudo pip install -e . --break-system-packages

# install rpi-rgb-led-matrix
deactivate
cd ..
cd rpi-rgb-led-matrix
make build-python
sudo make install-python
make build-python PYTHON=$(which python3)
sudo make install-python PYTHON=$(which python3)

# nginx
sudo rm /etc/nginx/sites-enabled/default
sudo nano /etc/redis/redis.conf