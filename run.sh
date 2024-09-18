#!/bin/sh

VENV_PATH=./venv

setup() {
	python3 -m venv "$VENV_PATH"
	. "$VENV_PATH/bin/activate"
	pip install -r ./requirements.txt
}

[ -d "$VENV_PATH" ] || setup

# Sourceing venv
[ -z "$VIRTUAL_ENV" ] &&
	. "$VENV_PATH/bin/activate"

python3 app.py
