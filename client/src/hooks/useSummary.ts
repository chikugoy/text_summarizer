/**
 * 要約詳細を取得・管理するカスタムフック
 */

import { useState, useEffect, useCallback } from 'react';
import {
  getSummaryDetail,
  updateSummary,
  deleteSummary,
  SummaryDetail,
  SummaryUpdate,
} from '@/services/summaryService';

export interface UseSummaryState {
  summary: SummaryDetail | null;
  loading: boolean;
  error: string | null;
}

export interface UseSummaryActions {
  refetch: () => Promise<void>;
  update: (data: SummaryUpdate) => Promise<SummaryDetail | null>;
  remove: () => Promise<boolean>;
}

export type UseSummaryResult = UseSummaryState & UseSummaryActions;

/**
 * 要約詳細を取得・管理するフック
 * @param summaryId 要約ID
 * @returns 要約データと操作関数
 */
export const useSummary = (summaryId: string | undefined): UseSummaryResult => {
  const [state, setState] = useState<UseSummaryState>({
    summary: null,
    loading: true,
    error: null,
  });

  const fetchSummary = useCallback(async () => {
    if (!summaryId) {
      setState({ summary: null, loading: false, error: null });
      return;
    }

    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const data = await getSummaryDetail(summaryId);
      setState({ summary: data, loading: false, error: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      setState({
        summary: null,
        loading: false,
        error: `要約の取得に失敗しました: ${errorMessage}`,
      });
    }
  }, [summaryId]);

  useEffect(() => {
    fetchSummary();
  }, [fetchSummary]);

  const update = useCallback(
    async (data: SummaryUpdate): Promise<SummaryDetail | null> => {
      if (!summaryId) return null;

      try {
        const updated = await updateSummary(summaryId, data);
        setState(prev => ({ ...prev, summary: updated }));
        return updated;
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        setState(prev => ({ ...prev, error: `更新に失敗しました: ${errorMessage}` }));
        return null;
      }
    },
    [summaryId]
  );

  const remove = useCallback(async (): Promise<boolean> => {
    if (!summaryId) return false;

    try {
      await deleteSummary(summaryId);
      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      setState(prev => ({ ...prev, error: `削除に失敗しました: ${errorMessage}` }));
      return false;
    }
  }, [summaryId]);

  return {
    ...state,
    refetch: fetchSummary,
    update,
    remove,
  };
};
