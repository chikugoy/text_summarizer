# Text Summarizer

書籍画像要約サービス - 複数の書籍ページ画像をアップロードすると要約してくれるウェブアプリケーション

## プロジェクト概要

書籍のページを画像化して、画像化された複数ページをアップロードするとOCRにより文章抽出されて、抽出された文章を特定のAIモデルで要約できるウェブアプリケーション。

### 主な機能

- 書籍ページ画像の複数アップロード
  - ドラッグ&ドロップまたはファイル選択でアップロード
  - アップロード後にローディング表示されて、要約された文章が表示される
  - 表示された要約文章はボタンでクリップボードコピー可能
  - 要約元と要約結果文章はDBに、タイトルと説明を入力して保存可能
  - カスタム指示による柔軟な処理（要約以外の指示も可能）
- 要約履歴一覧ページ
  - 詳細ページでタイトル、説明、要約元文章、要約文章、要約日時を確認
  - 要約の編集・削除機能

## プロジェクト構成

```
text_summarizer/
├── client/                    # フロントエンド (Vite + React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── organisms/     # Header, Footer
│   │   │   ├── pages/         # 各ページコンポーネント
│   │   │   ├── templates/     # レイアウトテンプレート
│   │   │   └── ui/            # UIコンポーネント (shadcn/ui)
│   │   ├── services/          # API通信サービス
│   │   ├── lib/               # ユーティリティ
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── server/                    # バックエンド (FastAPI)
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints/     # APIエンドポイント
│   │   ├── models/            # SQLAlchemyモデル
│   │   ├── schemas/           # Pydanticスキーマ
│   │   ├── services/          # ビジネスロジック
│   │   ├── config.py          # 設定
│   │   └── database.py        # DB接続
│   ├── alembic/               # DBマイグレーション
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## データモデル設計

### エンティティ関連図

```
Summary 1 <-->> * Image
```

### 主要テーブル設計

#### summaries

| カラム | 型 | 説明 |
|--------|------|------|
| id | UUID (PK) | 主キー |
| title | string | 要約のタイトル |
| description | text | 要約の説明（任意） |
| custom_instructions | text | カスタム指示（任意） |
| original_text | text | 要約元のテキスト |
| summarized_text | text | 要約されたテキスト |
| created_at | timestamp | 作成日時 |
| updated_at | timestamp | 更新日時 |

#### images

| カラム | 型 | 説明 |
|--------|------|------|
| id | UUID (PK) | 主キー |
| summary_id | UUID (FK) | 要約への外部キー |
| file_path | string | ファイルパス |
| file_name | string | ファイル名 |
| file_size | integer | ファイルサイズ |
| mime_type | string | MIMEタイプ |
| ocr_text | text | OCR抽出テキスト |
| page_number | integer | ページ番号 |
| created_at | timestamp | 作成日時 |

## API仕様

### 画像関連

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | `/api/images/upload` | 複数の書籍ページ画像をアップロード |
| GET | `/api/images/{summary_id}` | 特定の要約に関連する画像一覧を取得 |

### OCR関連

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | `/api/ocr/process` | アップロードされた画像のOCR処理を実行 |

### 要約関連

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | `/api/summaries` | 要約を新規作成 |
| POST | `/api/summaries/generate` | OCR処理された文章から要約を生成 |
| GET | `/api/summaries` | 要約一覧を取得（ページネーション付き） |
| GET | `/api/summaries/{id}` | 特定の要約詳細を取得 |
| PUT | `/api/summaries/{id}` | 要約情報を更新 |
| DELETE | `/api/summaries/{id}` | 要約を削除 |

APIドキュメント: `http://localhost:8000/api/docs`

## 技術スタック

### フロントエンド

| 技術 | バージョン | 用途 |
|------|-----------|------|
| React | 19.x | UIライブラリ |
| Vite | 7.x | ビルドツール |
| TypeScript | 5.x | 型安全性 |
| Tailwind CSS | 4.x | スタイリング |
| shadcn/ui | - | UIコンポーネント |
| React Router | 7.x | ルーティング |
| React Hook Form | 7.x | フォーム管理 |
| Zod | 4.x | バリデーション |
| Zustand | 5.x | 状態管理 |
| Axios | 1.x | HTTP通信 |

### バックエンド

| 技術 | バージョン | 用途 |
|------|-----------|------|
| FastAPI | 0.128.x | Webフレームワーク |
| Python | 3.11 | プログラミング言語 |
| PostgreSQL | 17 | データベース |
| SQLAlchemy | 2.x | ORM |
| Alembic | 1.x | DBマイグレーション |
| Redis | - | キャッシュ |
| PaddleOCR | 3.x | OCR処理 |
| Google Cloud Vision | 3.x | OCR処理（代替） |
| LiteLLM | 1.x | AI API統合 |

### 対応AIモデル

LiteLLMを使用して以下のAIプロバイダーに対応:

- **OpenAI**: gpt-4o, gpt-4, gpt-3.5-turbo
- **Anthropic**: claude-3-opus, claude-3-sonnet, claude-3-haiku
- **Google**: gemini-pro, gemini-1.5-pro
- **Cohere**: command-r-plus, command-r

## 開発環境構築

### 前提条件

- Node.js 20.x以上
- npm 10.x以上
- Docker および Docker Compose
- Python 3.11以上（ローカル開発の場合）

### Docker Composeを使用した環境構築（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/text-summarizer.git
cd text-summarizer

# 環境変数ファイルを作成
cp server/.env.example server/.env
# server/.envファイルを編集してAI_API_KEYを設定

# Docker Composeでサーバーとデータベースを起動
docker compose up -d

# ログを確認
docker compose logs -f api
```

バックエンドサーバー: `http://localhost:8000`
APIドキュメント: `http://localhost:8000/api/docs`

### フロントエンド開発環境

```bash
# クライアントディレクトリに移動
cd client

# 依存パッケージをインストール
npm install

# 開発モードで実行
npm run dev
```

フロントエンドサーバー: `http://localhost:5173`

### 開発モードでの実行（Docker Compose不使用）

```bash
# サーバー側の環境変数設定
cd server
cp .env.example .env
# .envファイルを編集

# サーバー側の依存パッケージをインストール
pip install -r requirements.txt

# サーバーを起動
python main.py
```

## 環境変数

### server/.env

```bash
# アプリケーション設定
APP_NAME=TextSummarizer
DEBUG=True

# データベース設定
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/text_summarizer_db

# ファイルストレージ設定
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# OCR設定
OCR_LANGUAGE=ja

# AI設定
AI_API_KEY=your-api-key-here
AI_MODEL=gpt-4o  # 使用するAIモデル
```

## ライセンス

MIT
