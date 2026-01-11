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
npm run lint                  # ESLint実行
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
├── api/endpoints/      # APIエンドポイント（images, ocr, summaries）
├── models/             # SQLAlchemyモデル（Summary, Image）
├── schemas/            # Pydanticスキーマ（リクエスト/レスポンス）
├── services/           # ビジネスロジック
│   ├── summary_service.py  # AI要約処理
│   ├── ocr_service.py      # OCR処理
│   └── file_service.py     # ファイル操作
├── config.py           # 環境変数設定
└── database.py         # DB接続
```

### クライアント構成 (client/src/)
```
src/
├── components/
│   ├── pages/          # ページコンポーネント
│   ├── organisms/      # Header, Footer
│   ├── templates/      # レイアウト
│   └── ui/             # shadcn/uiコンポーネント
├── services/           # API通信（summaryService, imageService, ocrService）
└── lib/                # ユーティリティ
```

## 主要ファイル

| ファイル | 説明 |
|----------|------|
| `server/app/services/summary_service.py` | AI要約処理のコアロジック |
| `server/app/services/ocr_service.py` | OCR処理（PaddleOCR/Google Vision） |
| `server/app/api/endpoints/summaries.py` | 要約APIエンドポイント |
| `server/app/models/summary.py` | Summaryモデル定義 |
| `server/app/schemas/summary.py` | 要約リクエスト/レスポンススキーマ |
| `client/src/components/pages/UploadPage.tsx` | 画像アップロードページ |
| `client/src/components/pages/SummaryResultPage.tsx` | 要約結果表示ページ |
| `client/src/services/summaryService.ts` | 要約API通信 |

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

### TypeScript (client/)
- ESLint + Prettierで整形
- コンポーネントは関数コンポーネント
- propsはインターフェースで型定義
- APIレスポンスは型定義

## 注意事項

- DBスキーマ変更時は必ずAlembicマイグレーション作成
- 新しいAPIエンドポイント追加時はスキーマも定義
- フロントエンドのメジャーアップデート（React 19, Tailwind 4等）により、一部の古いパターンは動作しない可能性あり
- AI APIキーは`.env`で管理、コミットしない
