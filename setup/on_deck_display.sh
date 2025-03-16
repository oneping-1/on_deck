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

echo "Starting display..." >> /home/on_deck/on_deck.log
python /home/on_deck/on_deck/on_deck/on_deck_display.py >> /home/on_deck/on_deck_display.log 2>&1

cd /home/on_deck || exit