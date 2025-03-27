import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Search, Calendar, Clock, ChevronRight } from 'lucide-react';
import { getSummaries, SummaryBase, getSummaryDetail } from '@/services';

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
  // 要約データの型定義
  type SummaryItem = {
    id: string;
    title: string;
    description: string | null;
    createdAt: string;
    summarizedText: string;
  };

  const [allSummaries, setAllSummaries] = useState<SummaryItem[]>([]);
  const [displayedSummaries, setDisplayedSummaries] = useState<SummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // 全要約データを取得
  useEffect(() => {
    const fetchAllSummaries = async () => {
      try {
        // まず全件数を取得
        const countResponse = await getSummaries(1, 1);
        const totalCount = countResponse.total;
        setTotalItems(totalCount);

        // 全データを取得
        const allPages = Math.ceil(totalCount / 100);
        const fetchPromises = [];
        
        for (let p = 1; p <= allPages; p++) {
          fetchPromises.push(getSummaries(p, 100));
        }

        const allResponses = await Promise.all(fetchPromises);
        const allItems = allResponses.flatMap(r => r.items);

        // 各要約の詳細情報を取得
        const detailPromises = allItems.map(async (item) => {
          try {
            const detail = await getSummaryDetail(item.id);
            return {
              id: item.id,
              title: item.title,
              description: item.description,
              createdAt: item.created_at,
              summarizedText: detail.summarized_text
            };
          } catch (err) {
            console.error(`Failed to fetch detail for summary ${item.id}:`, err);
            return {
              id: item.id,
              title: item.title,
              description: item.description,
              createdAt: item.created_at,
              summarizedText: '要約テキストの取得に失敗しました'
            };
          }
        });

        const formattedSummaries = await Promise.all(detailPromises);
        setAllSummaries(formattedSummaries);
      } catch (error) {
        console.error('Failed to fetch summaries:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllSummaries();
  }, []);

  // 検索とページネーションを適用
  useEffect(() => {
    const filtered = allSummaries.filter(summary =>
      summary.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (summary.description && summary.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      summary.summarizedText.toLowerCase().includes(searchTerm.toLowerCase())
    );

    setTotalItems(filtered.length);
    
    // ページネーション適用
    const start = (page - 1) * 10;
    const end = start + 10;
    setDisplayedSummaries(filtered.slice(start, end));
  }, [allSummaries, searchTerm, page]);

  const filteredSummaries = displayedSummaries;

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
          
          {/* ページネーションコントロール */}
          <div className="flex justify-center items-center gap-4 mt-8">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              前へ
            </button>
            <span className="text-sm">
              {page} / {Math.ceil(totalItems / 10)}
            </span>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= Math.ceil(totalItems / 10)}
              className="px-4 py-2 border rounded-md disabled:opacity-50"
            >
              次へ
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryListPage;
