#!/bin/sh

# 静的ファイルを収集
python manage.py collectstatic --noinput

# uWSGI を起動
uwsgi --ini /code/uwsgi.ini
