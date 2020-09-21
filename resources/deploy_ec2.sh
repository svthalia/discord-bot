#!/bin/bash

git fetch
git reset --hard origin/master

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py --output get-poetry.py
python3.8 get-poetry.py --version 1.0.9 -y
source $HOME/.poetry/env

python3.8 ./run.py bot/main.py