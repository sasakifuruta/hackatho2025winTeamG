FROM python:3.11.1
ENV PYTHONUNBUFFERED=1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
# uWSGI用ユーザーを作成
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi

COPY . /code/