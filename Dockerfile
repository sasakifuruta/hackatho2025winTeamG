FROM python:3.11.1
ENV PYTHONUNBUFFERED 1

# /code ディレクトリを作成して作業ディレクトリにする
RUN mkdir /code
WORKDIR /code

# 必要なパッケージをインストール
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションのコードをコピー
COPY . /code/

# entrypoint.sh をコピーして実行権限を付与
COPY backend/entrypoint.sh /code/
RUN chmod +x /code/entrypoint.sh

# entrypoint.sh をシェルで実行
ENTRYPOINT ["/bin/sh", "/code/entrypoint.sh"]
