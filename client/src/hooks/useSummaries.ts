/**
 * 要約一覧を取得・管理するカスタムフック
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { getSummaries, getSummaryDetail, SummaryBase } from '@/services/summaryService';

export interface SummaryListItem {
  id: string;
  title: string;
  description: string | null;
  createdAt: string;
  summarizedText: string;
}

export interface UseSummariesState {
  items: SummaryListItem[];
  loading: boolean;
  error: string | null;
  totalItems: number;
}

export interface UseSummariesActions {
  refetch: () => Promise<void>;
  setPage: (page: number) => void;
  setSearchTerm: (term: string) => void;
}

export interface UseSummariesOptions {
  pageSize?: number;
}

export type UseSummariesResult = UseSummariesState & UseSummariesActions & {
  page: number;
  searchTerm: string;
  totalPages: number;
};

/**
 * 要約一覧を取得・管理するフック
 * @param options オプション設定
 * @returns 要約一覧と操作関数
 */
export const useSummaries = (options: UseSummariesOptions = {}): UseSummariesResult => {
  const { pageSize = 10 } = options;

  const [allItems, setAllItems] = useState<SummaryListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchAllSummaries = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // まず全件数を取得
      const countResponse = await getSummaries(1, 1);
      const totalCount = countResponse.total;

      // 全データを取得（100件ずつ）
      const allPages = Math.ceil(totalCount / 100);
      const fetchPromises = [];

      for (let p = 1; p <= allPages; p++) {
        fetchPromises.push(getSummaries(p, 100));
      }

      const allResponses = await Promise.all(fetchPromises);
      const rawItems = allResponses.flatMap(r => r.items);

      // 各要約の詳細情報を取得
      const detailPromises = rawItems.map(async (item: SummaryBase) => {
        try {
          const detail = await getSummaryDetail(item.id);
          return {
            id: item.id,
            title: item.title,
            description: item.description,
            createdAt: item.created_at,
            summarizedText: detail.summarized_text,
          };
        } catch {
          return {
            id: item.id,
            title: item.title,
            description: item.description,
            createdAt: item.created_at,
            summarizedText: '要約テキストの取得に失敗しました',
          };
        }
      });

      const formattedItems = await Promise.all(detailPromises);
      setAllItems(formattedItems);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(`要約一覧の取得に失敗しました: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllSummaries();
  }, [fetchAllSummaries]);

  // 検索フィルタリング
  const filteredItems = useMemo(() => {
    if (!searchTerm) return allItems;

    const lowerSearchTerm = searchTerm.toLowerCase();
    return allItems.filter(
      item =>
        item.title.toLowerCase().includes(lowerSearchTerm) ||
        (item.description && item.description.toLowerCase().includes(lowerSearchTerm)) ||
        item.summarizedText.toLowerCase().includes(lowerSearchTerm)
    );
  }, [allItems, searchTerm]);

  // ページネーション適用
  const paginatedItems = useMemo(() => {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return filteredItems.slice(start, end);
  }, [filteredItems, page, pageSize]);

  const totalPages = useMemo(
    () => Math.ceil(filteredItems.length / pageSize),
    [filteredItems.length, pageSize]
  );

  // 検索語が変わったらページを1に戻す
  useEffect(() => {
    setPage(1);
  }, [searchTerm]);

  return {
    items: paginatedItems,
    loading,
    error,
    totalItems: filteredItems.length,
    page,
    searchTerm,
    totalPages,
    refetch: fetchAllSummaries,
    setPage,
    setSearchTerm,
  };
};
