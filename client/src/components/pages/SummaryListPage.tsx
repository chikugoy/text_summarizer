/**
 * 要約一覧ページ
 *
 * 保存した要約の一覧を表示し、検索とページネーション機能を提供する。
 */

import { Link } from 'react-router-dom';
import { Search, Calendar, Clock, ChevronRight } from 'lucide-react';
import { useSummaries, SummaryListItem } from '@/hooks';
import { formatDate, formatTime } from '@/lib/utils';

// ============================================
// サブコンポーネント
// ============================================

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

const SearchBar = ({ value, onChange }: SearchBarProps) => (
  <div className="relative">
    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
    <input
      type="text"
      placeholder="タイトルや内容で検索..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full pl-10 pr-4 py-2 border rounded-md"
    />
  </div>
);

interface SummaryCardProps {
  summary: SummaryListItem;
}

const SummaryCard = ({ summary }: SummaryCardProps) => (
  <Link
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
);

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination = ({ page, totalPages, onPageChange }: PaginationProps) => (
  <div className="flex justify-center items-center gap-4 mt-8">
    <button
      onClick={() => onPageChange(Math.max(1, page - 1))}
      disabled={page === 1}
      className="px-4 py-2 border rounded-md disabled:opacity-50"
    >
      前へ
    </button>
    <span className="text-sm">
      {page} / {totalPages}
    </span>
    <button
      onClick={() => onPageChange(page + 1)}
      disabled={page >= totalPages}
      className="px-4 py-2 border rounded-md disabled:opacity-50"
    >
      次へ
    </button>
  </div>
);

interface EmptyStateProps {
  searchTerm: string;
  onClearSearch: () => void;
}

const EmptyState = ({ searchTerm, onClearSearch }: EmptyStateProps) => (
  <div className="text-center py-12 bg-muted rounded-md">
    <p className="text-muted-foreground">
      {searchTerm
        ? '検索条件に一致する要約が見つかりませんでした'
        : '保存された要約がありません'}
    </p>
    {searchTerm ? (
      <button
        onClick={onClearSearch}
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
);

// ============================================
// メインコンポーネント
// ============================================

const SummaryListPage = () => {
  const {
    items,
    loading,
    totalItems,
    page,
    searchTerm,
    totalPages,
    setPage,
    setSearchTerm,
  } = useSummaries({ pageSize: 10 });

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">要約履歴</h1>
        <p className="text-muted-foreground">保存した要約の一覧を表示します</p>
      </div>

      <SearchBar value={searchTerm} onChange={setSearchTerm} />

      {loading ? (
        <div className="text-center py-12">
          <p className="text-muted-foreground">読み込み中...</p>
        </div>
      ) : items.length === 0 ? (
        <EmptyState searchTerm={searchTerm} onClearSearch={() => setSearchTerm('')} />
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            {totalItems}件の要約が見つかりました
          </p>
          <div className="divide-y border rounded-md overflow-hidden">
            {items.map((summary) => (
              <SummaryCard key={summary.id} summary={summary} />
            ))}
          </div>

          {totalPages > 1 && (
            <Pagination
              page={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default SummaryListPage;
