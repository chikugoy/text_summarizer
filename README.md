# Text Summarizer

書籍画像要約サービス - 複数の書籍ページ画像をアップロードすると要約してくれるウェブアプリケーション

## プロジェクト概要

書籍のページを画像化して、画像化された複数ページをアップロードするとOCRにより文章抽出されて、抽出された文章を特定のAIモデルで要約できるウェブアプリケーション

### 主な機能

- 書籍ページ画像の複数アップロードページ
  - アップロード後にローディング表示されて、要約された文章が表示される
  - 表示された要約文章はボタンでクリップボードコピー可能
  - 要約元と要約結果文章はローカルのDBに、タイトルと内容を入力して保存ボタンで可能
- 要約履歴一覧ページ
  - 詳細ページでタイトル、内容、要約元文章、要約文章、要約日時を確認できる

## データモデル設計

### エンティティ関連図

```
Summary <-->> Image
```

### 主要テーブル設計

#### summaries
- id: UUID (PK)
- title: string
- description: text (nullable)
- original_text: text
- summarized_text: text
- created_at: timestamp
- updated_at: timestamp

#### images
- id: UUID (PK)
- summary_id: UUID (FK to summaries)
- file_path: string
- file_name: string
- file_size: integer
- mime_type: string
- ocr_text: text
- page_number: integer
- created_at: timestamp

## API仕様

### 画像アップロード関連

- `POST /api/images/upload` - 複数の書籍ページ画像をアップロード
- `GET /api/images/:summaryId` - 特定の要約に関連する画像一覧を取得

### OCR処理関連

- `POST /api/ocr/process` - アップロードされた画像のOCR処理を実行
- `GET /api/ocr/status/:jobId` - OCR処理のステータスを確認

### 要約関連

- `POST /api/summaries` - OCR処理された文章から要約を生成して保存
- `GET /api/summaries` - 要約一覧を取得（ページネーション付き）
- `GET /api/summaries/:id` - 特定の要約詳細を取得
- `PUT /api/summaries/:id` - 既存の要約情報を更新（タイトル、説明など）
- `DELETE /api/summaries/:id` - 要約を削除

## 画面構成とUI/UX

### 主要画面

1. **ホーム画面**
   - サービス説明
   - アップロードボタン
   - 最近の要約履歴プレビュー
   
2. **画像アップロード画面**
   - ドラッグ&ドロップエリア
   - 複数ファイル選択ボタン
   - アップロード済み画像のプレビュー
   - 処理開始ボタン
   
3. **要約結果画面**
   - OCR処理状況インジケーター
   - 抽出されたテキスト（折りたたみ可能）
   - 要約結果テキスト
   - コピーボタン
   - 保存フォーム（タイトル、説明入力）
   
4. **要約履歴一覧画面**
   - 要約リスト（日付、タイトル、プレビュー）
   - ソートとフィルター
   
5. **要約詳細画面**
   - タイトルと説明
   - 元のテキストと要約テキスト
   - 元の画像プレビュー
   - 編集・削除ボタン

## 技術スタック

### フロントエンド
- **フレームワーク**: Next.js
- **UIライブラリ**: Shadcn/ui
- **スタイリング**: Tailwind CSS
- **フォーム管理**: React Hook Form + Zod
- **状態管理**: Zustand
- **HTTP通信**: Axios

### バックエンド
- **フレームワーク**: FastAPI
- **言語**: Python
- **DB**: PostgreSQL
- **ORM**: SQLAlchemy
- **キャッシュ**: Redis
- **ファイルストレージ**: ローカルファイルシステム / AWS S3
- **OCR処理**: PaddleOCR
- **要約処理**: LangChain

## 開発環境構築

### 前提条件

- Node.js 18.x以上
- npm 9.x以上
- Docker および Docker Compose

### Docker Composeを使用した環境構築

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/text-summarizer.git
cd text-summarizer

# Docker Composeでサーバーとデータベースを起動
# 必要に応じてdocker-compose.ymlのOPENAI_API_KEYを設定
docker-compose up -d

# アップロードディレクトリを作成
mkdir -p uploads
```

バックエンドサーバーは`http://localhost:8000`で起動します。
APIドキュメントは`http://localhost:8000/api/docs`で確認できます。

### 開発モードでの実行（Docker Compose不使用）

```bash
# サーバー側の環境変数設定
cd server
cp .env.example .env
# 必要に応じて.envファイルを編集（OpenAI APIキーなど）

# サーバー側の依存パッケージをインストール
pip install -r requirements.txt

# サーバーを起動
python main.py
```

### フロントエンド開発環境の構築

```bash
# クライアント側の依存パッケージをインストール
cd client
npm install

# 開発モードで実行
npm run dev
```

フロントエンドサーバーは`http://localhost:3000`で起動します。

## ライセンス

MIT
