#!/bin/bash
exec >> /home/ondeck/ondeck.log 2>&1

cd /home/ondeck/at_bat || exit
git fetch
git pull

cd /home/ondeck/OnDeck-RaspberryPi || exit
git fetch
git pull

/home/ondeck/venv/bin/python /home/ondeck/OnDeck-RaspberryPi/on_deck/on_deck_fetcher.py >> /home/ondeck/on_deck_fetcher.log &
/home/ondeck/venv/bin/gunicorn -w 2 -b 0.0.0.0:80 on_deck_server:app >> /home/ondeck/on_deck_server.log &
sudo python /home/ondeck/OnDeck-RaspberryPi/on_deck/on_deck_display.py >> /home/ondeck/on_deck_display.log &