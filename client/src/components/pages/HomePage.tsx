import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

const HomePage = () => {
  return (
    <div className="space-y-12">
      <section className="text-center py-12">
        <h1 className="text-4xl font-bold mb-4">書籍画像要約サービス</h1>
        <p className="text-xl text-muted-foreground mb-8">
          複数の書籍ページ画像をアップロードすると要約してくれるウェブアプリケーション
        </p>
        <Link 
          to="/upload" 
          className="inline-flex items-center bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors"
        >
          今すぐ始める
          <ArrowRight className="ml-2 h-4 w-4" />
        </Link>
      </section>

      <section className="grid md:grid-cols-3 gap-8">
        <div className="bg-card text-card-foreground rounded-lg p-6 shadow-md">
          <h3 className="text-xl font-semibold mb-3">簡単アップロード</h3>
          <p>複数の書籍ページ画像を一度にアップロードできます。ドラッグ＆ドロップにも対応。</p>
        </div>
        <div className="bg-card text-card-foreground rounded-lg p-6 shadow-md">
          <h3 className="text-xl font-semibold mb-3">高精度OCR処理</h3>
          <p>最新のOCR技術で画像から正確にテキストを抽出します。</p>
        </div>
        <div className="bg-card text-card-foreground rounded-lg p-6 shadow-md">
          <h3 className="text-xl font-semibold mb-3">AIによる要約</h3>
          <p>抽出されたテキストを高度なAIモデルで要約し、重要なポイントを抽出します。</p>
        </div>
      </section>

      <section className="bg-muted p-8 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">使い方</h2>
        <ol className="space-y-4 list-decimal list-inside">
          <li>「アップロード」ページで書籍の画像をアップロードします</li>
          <li>OCR処理が完了するまで待ちます</li>
          <li>抽出されたテキストがAIによって要約されます</li>
          <li>要約結果をコピーしたり保存したりできます</li>
          <li>保存した要約は「要約履歴」ページでいつでも確認できます</li>
        </ol>
      </section>
    </div>
  );
};

export default HomePage;
