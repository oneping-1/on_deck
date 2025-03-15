#!/bin/bash
exec >> /home/ondeck/on_deck.log 2>&1

cd /home/on_deck/at_bat || exit
git fetch
git pull

cd /home/on_deck/on_deck || exit
git fetch
git pull

/home/ondeck/new/bin/python /home/ondeck/on_deck/on_deck/on_desk.py