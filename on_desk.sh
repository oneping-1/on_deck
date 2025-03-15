#!/bin/bash
exec >> /home/ondeck/ondeck.log 2>&1

cd /home/ondeck/at_bat || exit
git fetch
git pull

cd /home/ondeck/OnDeck-RaspberryPi || exit
git fetch
git pull

/home/ondeck/new/bin/python /home/ondeck/OnDeck-RaspberryPi/on_desk.py