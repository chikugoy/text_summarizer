# CLAUDE.md

このファイルはClaude Codeがこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

書籍画像要約サービス - 複数の書籍ページ画像をアップロードするとOCRでテキスト抽出し、AIで要約するウェブアプリケーション。

## 技術スタック

### フロントエンド (client/)
- **React 19** + **Vite 7** + **TypeScript**
- **Tailwind CSS 4** + **shadcn/ui**
- **React Router 7** でルーティング
- **React Hook Form** + **Zod 4** でフォームバリデーション
- **Zustand 5** で状態管理
- **Axios** でAPI通信

### バックエンド (server/)
- **FastAPI** + **Python 3.11**
- **SQLAlchemy 2** ORM + **Alembic** マイグレーション
- **PostgreSQL 17** データベース
- **Redis** キャッシュ
- **PaddleOCR** / **Google Cloud Vision** でOCR処理
- **LiteLLM** でマルチAIプロバイダー対応（OpenAI, Anthropic, Google, Cohere）

## 開発コマンド

### サーバー起動 (Docker)
```bash
docker compose up -d          # 全サービス起動
docker compose logs -f api    # APIログ確認
docker compose down           # 停止
docker compose build api      # イメージ再ビルド
```

### フロントエンド開発
```bash
cd client
npm install                   # 依存関係インストール
npm run dev                   # 開発サーバー起動 (localhost:5173)
npm run build                 # プロダクションビルド
npx tsc --noEmit              # TypeScript型チェック
```

### DBマイグレーション
```bash
docker compose exec api alembic revision --autogenerate -m "説明"
docker compose exec api alembic upgrade head
```

## アーキテクチャ

### サーバー構成 (server/app/)
```
app/
├── api/endpoints/          # APIエンドポイント
│   ├── images.py           # 画像アップロードAPI
│   ├── ocr.py              # OCR処理API
│   └── summaries.py        # 要約CRUD API
├── models/                 # SQLAlchemyモデル
│   ├── summary.py          # Summaryモデル
│   └── image.py            # Imageモデル
├── schemas/                # Pydanticスキーマ
│   ├── summary.py          # 要約リクエスト/レスポンス
│   └── image.py            # 画像リクエスト/レスポンス
├── services/               # ビジネスロジック（単一責任の原則）
│   ├── interfaces.py       # サービスインターフェース（Protocol）
│   ├── summary_service.py  # AI要約処理
│   ├── ocr_service.py      # OCR処理（Google Vision/PaddleOCR）
│   ├── ocr_orchestrator.py # OCR処理統合オーケストレーター
│   ├── job_manager.py      # OCRジョブ管理
│   ├── file_service.py     # ファイル操作
│   ├── prompts.py          # プロンプトテンプレート
│   └── text_utils.py       # テキスト分割ユーティリティ
├── utils/                  # ユーティリティ
│   ├── constants.py        # 定数定義
│   └── db_helpers.py       # DB操作ヘルパー
├── exceptions.py           # カスタム例外クラス
├── dependencies.py         # 依存性注入（サービスファクトリ）
├── config.py               # 環境変数設定
└── database.py             # DB接続
```

### クライアント構成 (client/src/)
```
src/
├── components/
│   ├── pages/              # ページコンポーネント
│   │   ├── UploadPage.tsx          # 画像アップロード
│   │   ├── SummaryResultPage.tsx   # 要約結果表示
│   │   ├── SummaryListPage.tsx     # 要約一覧
│   │   └── SummaryDetailPage.tsx   # 要約詳細
│   ├── organisms/          # 複合コンポーネント
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── EditSummaryModal.tsx
│   │   └── DeleteConfirmModal.tsx
│   ├── templates/          # レイアウト
│   └── ui/                 # shadcn/ui + 汎用コンポーネント
│       └── Modal.tsx       # 汎用モーダル
├── hooks/                  # カスタムフック（ロジック抽出）
│   ├── index.ts            # エクスポート
│   ├── useOCRProcessing.ts # OCR処理・要約生成
│   ├── useSummary.ts       # 要約詳細取得・更新・削除
│   ├── useSummaries.ts     # 要約一覧取得・検索・ページネーション
│   └── useClipboard.ts     # クリップボードコピー
├── stores/                 # Zustand状態管理
│   ├── index.ts
│   └── summaryStore.ts     # 要約キャッシュ・最近の履歴
├── services/               # API通信
│   ├── api.ts              # Axiosインスタンス
│   ├── summaryService.ts   # 要約API
│   ├── imageService.ts     # 画像API
│   └── ocrService.ts       # OCR API
└── lib/                    # ユーティリティ
    └── utils.ts            # cn(), formatDate(), formatTime(), isValidUUID()
```

## 設計パターン

### サーバー側
- **依存性注入**: `dependencies.py`でサービスファクトリ関数を定義
- **カスタム例外**: `exceptions.py`で具体的な例外クラスを定義
- **プロトコル**: `interfaces.py`でサービスインターフェースを定義
- **単一責任**: 各サービスは一つの責任に集中

### クライアント側
- **カスタムフック**: データフェッチング・ビジネスロジックをフックに抽出
- **コンポーネント分離**: ページを小さなサブコンポーネントに分割
- **Zustand**: グローバル状態管理とキャッシュ

## 主要ファイル

### サーバー側
| ファイル | 説明 |
|----------|------|
| `server/app/exceptions.py` | カスタム例外（AppException, OCRProcessingError等） |
| `server/app/dependencies.py` | サービスファクトリ（get_summary_service等） |
| `server/app/services/summary_service.py` | AI要約処理（LiteLLM統合） |
| `server/app/services/ocr_service.py` | OCR処理（Google Vision/PaddleOCR） |
| `server/app/services/ocr_orchestrator.py` | OCRジョブ統合処理 |
| `server/app/services/job_manager.py` | OCRジョブ状態管理 |
| `server/app/utils/constants.py` | 定数定義（AIConstants, ErrorMessages等） |

### クライアント側
| ファイル | 説明 |
|----------|------|
| `client/src/hooks/useOCRProcessing.ts` | OCR処理・要約生成ロジック |
| `client/src/hooks/useSummaries.ts` | 要約一覧取得（検索・ページネーション） |
| `client/src/hooks/useClipboard.ts` | クリップボードコピー |
| `client/src/stores/summaryStore.ts` | Zustand要約ストア |
| `client/src/components/ui/Modal.tsx` | 汎用モーダルコンポーネント |
| `client/src/lib/utils.ts` | ユーティリティ関数 |

## API概要

- `POST /api/images/upload` - 画像アップロード
- `POST /api/ocr/process` - OCR処理実行
- `POST /api/summaries/generate` - 要約生成
- `GET /api/summaries` - 要約一覧
- `GET /api/summaries/{id}` - 要約詳細
- `PUT /api/summaries/{id}` - 要約更新
- `DELETE /api/summaries/{id}` - 要約削除

APIドキュメント: http://localhost:8000/api/docs

## 環境変数

`server/.env`に設定:
- `AI_API_KEY` - AIプロバイダーのAPIキー（必須）
- `AI_MODEL` - 使用モデル（例: gpt-4o, claude-3-opus）
- `DATABASE_URL` - PostgreSQL接続URL
- `OCR_LANGUAGE` - OCR言語（ja）

## コーディング規約

### Python (server/)
- PEP 8準拠
- 型ヒント必須
- Pydanticでバリデーション
- 非同期処理はasync/await
- ロギングは`logging`モジュール使用（print禁止）
- 例外は`exceptions.py`のカスタム例外を使用

### TypeScript (client/)
- コンポーネントは関数コンポーネント
- propsはインターフェースで型定義
- データフェッチングはカスタムフックに抽出
- 重複コードはユーティリティ関数・フックに統合
- 状態管理はZustandストアを使用

## 注意事項

- DBスキーマ変更時は必ずAlembicマイグレーション作成
- 新しいAPIエンドポイント追加時はスキーマも定義
- フロントエンドのメジャーアップデート（React 19, Tailwind 4等）により、一部の古いパターンは動作しない可能性あり
- AI APIキーは`.env`で管理、コミットしない
- サービス追加時は`interfaces.py`にインターフェースを定義し、`dependencies.py`にファクトリ関数を追加
- apiのコマンドを実行する時は、「docker compose」を介すか、docker内でで実行してください
- 本プロジェクトでされた指示に対しては基本日本語でレスポンスしてください