FROM python:3.11.1

# 環境変数設定（標準出力のバッファリングを無効にする）
ENV PYTHONUNBUFFERED 1

# 作業ディレクトリを作成
RUN mkdir -p /code
WORKDIR /code

# 必要なパッケージをインストールするための requirements.txt をコピー
COPY requirements.txt /code/

# pip をアップグレードしてから依存関係をインストール
RUN pip install --upgrade pip && pip install -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . /code/

# entrypoint.sh をコンテナにコピー
COPY entrypoint.sh /code/entrypoint.sha

# entrypoint.sh に実行権限を付与
RUN chmod +x /code/entrypoint.sh

# コンテナ起動時に entrypoint.sh を実行
ENTRYPOINT ["/code/entrypoint.sh"]
