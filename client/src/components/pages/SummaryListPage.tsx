import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Calendar, Clock, ChevronRight } from 'lucide-react';

// 要約一覧のモックデータ
// 実際の実装では、APIサービスを使用します
const mockFetchSummaries = async (): Promise<Array<{
  id: string;
  title: string;
  description: string | null;
  createdAt: string;
  summarizedText: string;
}>> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 'summary-1',
          title: '機械学習の基礎',
          description: '機械学習の基本概念と手法について',
          createdAt: '2025-03-20T10:30:00Z',
          summarizedText: '機械学習は、コンピュータがデータから学習し、予測や判断を行う技術です。教師あり学習、教師なし学習、強化学習などの手法があります。'
        },
        {
          id: 'summary-2',
          title: 'Webアプリケーションセキュリティ',
          description: null,
          createdAt: '2025-03-18T15:45:00Z',
          summarizedText: 'Webアプリケーションのセキュリティ対策として、入力検証、認証と認可、暗号化、XSS対策、CSRF対策などが重要です。'
        },
        {
          id: 'summary-3',
          title: 'クラウドコンピューティング入門',
          description: 'クラウドサービスの種類と特徴',
          createdAt: '2025-03-15T09:20:00Z',
          summarizedText: 'クラウドコンピューティングは、インターネットを通じてコンピュータリソースを提供するサービスです。IaaS、PaaS、SaaSの3つの主要なサービスモデルがあります。'
        },
        {
          id: 'summary-4',
          title: 'プログラミング言語の比較',
          description: '主要なプログラミング言語の特徴と用途',
          createdAt: '2025-03-10T14:15:00Z',
          summarizedText: 'プログラミング言語には、静的型付け言語と動的型付け言語、コンパイル言語とインタプリタ言語などの分類があります。用途に応じて適切な言語を選択することが重要です。'
        },
        {
          id: 'summary-5',
          title: 'データベース設計のベストプラクティス',
          description: null,
          createdAt: '2025-03-05T11:30:00Z',
          summarizedText: 'データベース設計では、正規化、インデックス設計、トランザクション管理、セキュリティなどを考慮する必要があります。'
        }
      ]);
    }, 1000);
  });
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const SummaryListPage = () => {
  const [summaries, setSummaries] = useState<Array<{
    id: string;
    title: string;
    description: string | null;
    createdAt: string;
    summarizedText: string;
  }>>([]);
  
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchSummaries = async () => {
      try {
        const data = await mockFetchSummaries();
        setSummaries(data);
      } catch (error) {
        console.error('Failed to fetch summaries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSummaries();
  }, []);

  const filteredSummaries = summaries.filter(summary => 
    summary.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (summary.description && summary.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
    summary.summarizedText.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">要約履歴</h1>
        <p className="text-muted-foreground">
          保存した要約の一覧を表示します
        </p>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
        <input
          type="text"
          placeholder="タイトルや内容で検索..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 border rounded-md"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      ) : filteredSummaries.length === 0 ? (
        <div className="text-center py-12 bg-muted rounded-md">
          <p className="text-muted-foreground">
            {searchTerm ? '検索条件に一致する要約が見つかりませんでした' : '保存された要約がありません'}
          </p>
          {searchTerm ? (
            <button
              onClick={() => setSearchTerm('')}
              className="mt-4 text-primary hover:underline"
            >
              検索条件をクリア
            </button>
          ) : (
            <Link to="/upload" className="mt-4 inline-block text-primary hover:underline">
              新しい要約を作成する
            </Link>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {filteredSummaries.length}件の要約が見つかりました
          </p>
          <div className="divide-y border rounded-md overflow-hidden">
            {filteredSummaries.map(summary => (
              <Link 
                key={summary.id} 
                to={`/summaries/${summary.id}`}
                className="block p-4 hover:bg-muted transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <h3 className="font-medium">{summary.title}</h3>
                    {summary.description && (
                      <p className="text-sm text-muted-foreground">{summary.description}</p>
                    )}
                    <p className="text-sm line-clamp-2">{summary.summarizedText}</p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        {formatDate(summary.createdAt)}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatTime(summary.createdAt)}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryListPage;
