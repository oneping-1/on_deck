#!/bin/bash

# Clear previous log files
rm /home/on_deck/*.log

# Log git fetch/pull to the main log file
{
    echo "=== Updating at_bat repo ==="
    cd /home/on_deck/at_bat || exit
    git fetch
    git pull

    echo "=== Updating on_deck repo ==="
    cd /home/on_deck/on_deck || exit
    git fetch
    git pull
} >> /home/on_deck/on_deck.log 2>&1

cd /home/on_deck/on_deck/on_deck || exit

echo "Starting gunicorn..." >> /home/on_deck/on_deck.log
sudo /home/on_deck/venv/bin/gunicorn -w 2 -b 0.0.0.0:80 on_deck_server:app >> /home/on_deck/on_deck_server.log 2>&1 &

echo "Starting fetcher..." >> /home/on_deck/on_deck.log
/home/on_deck/venv/bin/python /home/on_deck/on_deck/on_deck/on_deck_fetcher.py >> /home/on_deck/on_deck_fetcher.log 2>&1 &

cd /home/on_deck || exit