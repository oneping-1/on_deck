#!/bin/bash
exec >> /home/on_deck/ondeck.log 2>&1

cd /home/on_deck/at_bat || exit
git fetch
git pull

cd /home/on_deck/on_deck || exit
git fetch
git pull

/home/on_deck/venv/bin/python /home/on_deck/on_deck/on_deck/on_deck_fetcher.py >> /home/ondeck/on_deck_fetcher.log &
/home/on_deck/venv/bin/gunicorn -w 2 -b 0.0.0.0:80 on_deck_server:app >> /home/ondeck/on_deck_server.log &
sudo python /home/on_deck/on_deck/on_deck/on_deck_display.py >> /home/ondeck/on_deck_display.log &