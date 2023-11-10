#!/usr/bin/env bash
# exit on error
set -o errexit

/opt/render/project/src/.venv/bin/python -m pip install --upgrade pip

pip install -r requirements.txt
python manage.py collectstatic --noimput
python manage.py migrate