#!/bin/bash

# activate the virutal environment
source activate ./venv/tele_bot

# add current directory to PATH
export PATH=$PATH:`pwd`

# Kill any telegram_bot processes running
pkill -f telegram_bot.py
python ./telegram_bot.py
