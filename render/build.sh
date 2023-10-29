#!/usr/bin/env bash
# exit on error
set -o errexit

/opt/render/project/src/.venv/bin/python -m pip install --upgrade pip
/opt/render/project/src/.venv/bin/python -m apt update
/opt/render/project/src/.venv/bin/python -m apt upgrade python3

pip install -r requirements.txt
python manage.py collectstatic --no-imput
python manage.py migrate