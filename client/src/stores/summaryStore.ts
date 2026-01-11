/**
 * 要約状態管理ストア
 *
 * Zustandを使用してアプリケーション全体の要約関連状態を管理する。
 */

import { create } from 'zustand';
import { SummaryDetail, SummaryBase } from '@/services/summaryService';

// ============================================
// 型定義
// ============================================

interface SummaryState {
  /** 現在表示中の要約 */
  currentSummary: SummaryDetail | null;
  /** 最近アクセスした要約のリスト */
  recentSummaries: SummaryBase[];
  /** キャッシュされた要約詳細 */
  summaryCache: Map<string, SummaryDetail>;
}

interface SummaryActions {
  /** 現在の要約を設定 */
  setCurrentSummary: (summary: SummaryDetail | null) => void;
  /** 要約をキャッシュに追加 */
  cacheSummary: (summary: SummaryDetail) => void;
  /** キャッシュから要約を取得 */
  getCachedSummary: (id: string) => SummaryDetail | undefined;
  /** 最近の要約リストに追加 */
  addToRecent: (summary: SummaryBase) => void;
  /** 要約を最近リストから削除 */
  removeFromRecent: (id: string) => void;
  /** キャッシュをクリア */
  clearCache: () => void;
}

type SummaryStore = SummaryState & SummaryActions;

// ============================================
// ストア定義
// ============================================

const MAX_RECENT_SUMMARIES = 10;
const MAX_CACHE_SIZE = 50;

export const useSummaryStore = create<SummaryStore>((set, get) => ({
  // 初期状態
  currentSummary: null,
  recentSummaries: [],
  summaryCache: new Map(),

  // アクション
  setCurrentSummary: (summary) => {
    set({ currentSummary: summary });
    if (summary) {
      get().cacheSummary(summary);
    }
  },

  cacheSummary: (summary) => {
    set((state) => {
      const newCache = new Map(state.summaryCache);

      // キャッシュサイズを制限
      if (newCache.size >= MAX_CACHE_SIZE) {
        const oldestKey = newCache.keys().next().value;
        if (oldestKey) {
          newCache.delete(oldestKey);
        }
      }

      newCache.set(summary.id, summary);
      return { summaryCache: newCache };
    });
  },

  getCachedSummary: (id) => {
    return get().summaryCache.get(id);
  },

  addToRecent: (summary) => {
    set((state) => {
      // 既存のアイテムを削除
      const filtered = state.recentSummaries.filter((s) => s.id !== summary.id);

      // 先頭に追加し、最大数を制限
      const updated = [summary, ...filtered].slice(0, MAX_RECENT_SUMMARIES);

      return { recentSummaries: updated };
    });
  },

  removeFromRecent: (id) => {
    set((state) => ({
      recentSummaries: state.recentSummaries.filter((s) => s.id !== id),
    }));
  },

  clearCache: () => {
    set({
      summaryCache: new Map(),
      currentSummary: null,
    });
  },
}));
