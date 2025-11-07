# 英語学習アプリケーション API

FastAPI + Nginx + MySQLで構築した英語学習問題管理システム

## 概要

ジャンル別に英語学習問題を管理し、最新の問題を取得できるREST APIです。Docker Composeを使用して、本番環境に近い構成で開発できます。

## アーキテクチャ

```
クライアント
    ↓
Nginx (ポート80) - リバースプロキシ
    ↓
FastAPI (ポート8000) - アプリケーションサーバー
    ↓
MySQL (ポート3306) - データベース
```

### 技術スタック

- **Webフレームワーク**: FastAPI 0.115+
- **ASGIサーバー**: Uvicorn
- **リバースプロキシ**: Nginx
- **データベース**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0 (非同期)
- **パッケージ管理**: uv
- **コンテナ**: Docker / Docker Compose

## ディレクトリ構造

```
.
├── app/                    # アプリケーションコード
│   ├── main.py            # FastAPIアプリケーション、エンドポイント定義
│   ├── models.py          # SQLAlchemyモデル定義
│   └── database.py        # データベース接続設定
├── db/                     # データベース関連
│   ├── schema.sql         # テーブル定義
│   └── data.sql           # 初期データ
├── nginx/                  # Nginx設定
│   └── nginx.conf         # プロキシ設定
├── docker-compose.yml      # Docker Compose設定
├── Dockerfile             # Pythonアプリケーション用イメージ
├── pyproject.toml         # Python依存関係管理
└── README.md              # このファイル
```

## データベース設計

### テーブル構成

#### users（ユーザー）
| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | BIGINT | 主キー |
| name | VARCHAR(255) | ユーザー名 |
| created_at | TIMESTAMP | 作成日時 |

#### genres（ジャンル）
| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | INT | 主キー |
| name | VARCHAR(100) | ジャンル識別子（例: grammar） |
| display_name | VARCHAR(255) | 表示名（例: 文法） |
| created_at | TIMESTAMP | 作成日時 |

#### problems（問題）
| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | BIGINT | 主キー |
| genre_id | INT | ジャンルID（外部キー） |
| text | TEXT | 問題文 |
| answer_file_path | VARCHAR(1024) | 解答ファイルパス |
| created_at | TIMESTAMP | 作成日時 |

#### results（結果）
| カラム名 | 型 | 説明 |
|---------|-----|------|
| id | BIGINT | 主キー |
| user_id | BIGINT | ユーザーID（外部キー） |
| problem_id | BIGINT | 問題ID（外部キー） |
| score | DECIMAL(5,2) | スコア |
| try_file_path | VARCHAR(1024) | 解答ファイルパス |
| created_at | TIMESTAMP | 作成日時 |

### ER図概念

- 1つのジャンルは複数の問題を持つ（1:N）
- 1人のユーザーは複数の結果を持つ（1:N）
- 1つの問題は複数の結果を持つ（1:N）

## API仕様

### エンドポイント一覧

#### `GET /`
動作確認用エンドポイント

**レスポンス例**
```json
{
  "message": "Hello World"
}
```

#### `GET /problems`
最新の問題30件を取得

**レスポンス例**
```json
{
  "problems": [
    {
      "id": 1,
      "genre_id": 1,
      "text": "Choose the correct verb form: She ___ to the store yesterday.",
      "answer_file_path": "/answers/problem_001.txt",
      "created_at": "2025-11-07T13:58:08"
    },
    ...
  ]
}
```

**仕様**
- 作成日時の降順でソート
- 最大30件を返却
- ジャンル情報は含まれない（genre_idのみ）

## 環境構築

### 必要な環境

- Docker
- Docker Compose

### 起動方法

```bash
# コンテナをビルドして起動
docker compose up --build -d

# ログを確認
docker compose logs -f

# 停止
docker compose down

# データベースも含めて完全削除
docker compose down -v
```

### 初回起動時の動作

1. MySQLコンテナが起動
2. `db/schema.sql`でテーブル作成
3. `db/data.sql`で初期データ投入（ジャンル5件、問題35件）
4. アプリケーションコンテナが起動
5. Nginxコンテナが起動

## 使用方法

### APIへのアクセス

```bash
# ルートエンドポイント
curl http://localhost/

# 問題一覧取得
curl http://localhost/problems

# 整形して表示
curl http://localhost/problems | python3 -m json.tool
```

### データベースへの直接アクセス

```bash
# MySQLクライアントで接続
mysql -h 127.0.0.1 -u user -ppassword genred_english

# またはDocker経由
docker compose exec db mysql -u user -ppassword genred_english
```

## 開発

### ローカル開発環境

コンテナ内で`uv`を使用して依存関係を管理しています。

```bash
# コンテナ内でシェル起動
docker compose exec app bash

# 依存関係の更新
uv add <パッケージ名>

# アプリケーション再起動
docker compose restart app
```

### ファイル変更の反映

ホストのファイルはコンテナにマウントされているため、コード変更は自動的に反映されます（ただし、現在は`--reload`オプションを無効化しているため、手動再起動が必要）。

```bash
# アプリケーションのみ再起動
docker compose restart app
```

## 設定

### 環境変数

`docker-compose.yml`で設定されている主な環境変数：

- `DATABASE_URL`: データベース接続文字列
- `MYSQL_DATABASE`: データベース名（genred_english）
- `MYSQL_USER`: MySQLユーザー（user）
- `MYSQL_PASSWORD`: MySQLパスワード（password）

### ポート設定

- `80`: Nginx（HTTP）
- `3306`: MySQL（ホストからアクセス可能）
- `8000`: FastAPI（コンテナ内部のみ、Nginx経由でアクセス）


## 本番環境デプロイ

EC2などの本番環境へのデプロイ時の注意点：

1. **環境変数の設定**: パスワードなどを環境変数で管理
2. **ボリュームの永続化**: MySQLデータの永続化
3. **HTTPSの設定**: Let's Encryptなどを使用
4. **ログ管理**: ログの集約と監視
5. **バックアップ**: データベースの定期バックアップ
