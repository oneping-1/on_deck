#!/bin/bash

# 1) Clear previous log files
rm /home/on_deck/*.log

# 2) Log and update the at_bat repo
{
    echo "=== Updating at_bat repo ==="
    cd /home/on_deck/at_bat || exit
    git fetch
    git pull

    # 3) Log and update the on_deck repo
    echo "=== Updating on_deck repo ==="
    cd /home/on_deck/on_deck || exit
    git fetch
    git pull
} >> /home/on_deck/on_deck.log 2>&1
