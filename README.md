# 学習時間管理アプリ
## ハッカソン2025冬の陣 Gチーム

### ディレクトリ構成
├── src/ 
|     ├── nginx.conf
|     ├── uwsgi_params
|     ├── .env                      # 環境変数ファイル
|     ├── .gitignore                # Git無視リスト
|     ├── Dockerfile                # Dockerイメージ構成ファイル
|     ├── docker-compose.yml        # Dockerコンテナ設定
|     ├── requirements.txt          # Python依存パッケージ一覧
│     ├── manage.py             # Django管理コマンド
│     ├── pomo_timer/            # Djangoプロジェクトフォルダ（設定ファイルなど）
│     │       ├── settings.py       # Django設定ファイル
│     │       ├── urls.py           # ルーティング設定
│     │       ├── wsgi.py           # WSGIアプリケーション
│     │       ├── asgi.py           # ASGIアプリケーション（WebSocket対応）
│     ├── app/                  # Djangoアプリケーションフォルダ
│      ├── migrations/       # マイグレーションファイル
│      ├── models.py         # モデル定義
│      ├── views.py          # ビュー（ロジック処理）
│      ├── urls.py           # アプリ内ルーティング
│      ├── templates/        # HTMLテンプレート
│      ├── static/           # 静的ファイル（CSS, JS, 画像など）
└── README.md                 # このファイル（プロジェクト説明）

### 環境構築
- srcフォルダに入る
cd ./src
- コンテナ起動
docker comspose up -d
-　コンテナが起動したか確認（Django,MySQL,Nginx コンテナの３つ）
docker compose ps
- Djangoコンテナに入る
docker exec -it app bash
-　静的ファイルを収集
 python manage.py collectstatic --noinput
- マイグレーション実行
python manage.py migrate
- 初期データ投入
python manage.py loaddata fixture_02.json
- ブラウザで　localhost にアクセス


