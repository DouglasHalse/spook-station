#!/bin/bash

# Verify venv exists
if [[ ! -d ./venv ]]
then
    echo "Virtual environment not found"
    exit 1
fi

# Activate venv
source ./venv/bin/activate

# Verify venv was activated
if [[ "$VIRTUAL_ENV" == "" ]]
then
    echo "Virtual environment not activated"
    exit 1
fi

# Run GUI
python SpookStationGui/main.py