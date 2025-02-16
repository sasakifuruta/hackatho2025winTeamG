#!/bin/sh
set -e

cd /code

# Django の環境変数を明示的に設定
export DJANGO_SETTINGS_MODULE=pomo_timer.settings

# 依存関係をインストール
pip install --no-cache-dir -r requirements.txt

# 静的ファイルを収集
python manage.py collectstatic --noinput

# マイグレーションを適用
python manage.py migrate

# uWSGI を起動
uwsgi --ini /code/uwsgi.ini
