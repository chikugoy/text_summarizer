import api from './api';

/**
 * 要約サービス
 * 要約の作成、取得、更新、削除に関する機能を提供
 */
export interface SummaryBase {
  id: string;
  title: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface SummaryDetail extends SummaryBase {
  original_text: string;
  summarized_text: string;
}

export interface SummaryList {
  items: SummaryBase[];
  total: number;
  page: number;
  page_size: number;
}

export interface SummaryCreate {
  title: string;
  description?: string;
  original_text: string;
  summarized_text: string;
}

export interface SummaryUpdate {
  title?: string;
  description?: string;
}

/*
 * OCR処理された文章から要約を生成して保存する
 * @param summary 要約データ
 * @returns 作成された要約
 */
export const createSummary = async (summary: SummaryCreate): Promise<SummaryDetail> => {
  const response = await api.post<SummaryDetail>('/summaries', summary);
  return response.data;
};

/**
 * 特定の要約IDに関連する画像からOCRテキストを抽出し、要約を生成する
 * @param summaryId 要約ID
 * @returns 生成された要約
 */
export const generateSummary = async (summaryId: string): Promise<SummaryDetail> => {
  console.log(`generateSummary 呼び出し: summaryId=${summaryId}, type=${typeof summaryId}`);
  
  // UUIDの形式を確認（正規表現）
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(summaryId)) {
    console.error(`summaryId が正しいUUID形式ではありません: ${summaryId}`);
    throw new Error('Invalid summary ID format');
  }

  try {
    const response = await api.post<SummaryDetail>(`/summaries/generate`, {
      summary_id: summaryId
    });
    return response.data;
  } catch (error) {
    console.error('要約生成エラー:', error);
    throw error;
  }
};

/**
 * 要約一覧を取得する（ページネーション付き）
 * @param page ページ番号（1から開始）
 * @param pageSize ページサイズ
 * @returns 要約一覧
 */
export const getSummaries = async (page = 1, pageSize = 10): Promise<SummaryList> => {
  const skip = (page - 1) * pageSize;
  const response = await api.get<SummaryList>('/summaries', {
    params: {
      skip,
      limit: pageSize,
    },
  });
  return response.data;
};

/**
 * 特定の要約詳細を取得する
 * @param summaryId 要約ID
 * @returns 要約詳細
 */
export const getSummaryDetail = async (summaryId: string): Promise<SummaryDetail> => {
  const response = await api.get<SummaryDetail>(`/summaries/${summaryId}`);
  return response.data;
};

/**
 * 既存の要約情報を更新する（タイトル、説明など）
 * @param summaryId 要約ID
 * @param update 更新データ
 * @returns 更新された要約
 */
export const updateSummary = async (
  summaryId: string,
  update: SummaryUpdate
): Promise<SummaryDetail> => {
  const response = await api.put<SummaryDetail>(`/summaries/${summaryId}`, update);
  return response.data;
};

/**
 * 要約を削除する
 * @param summaryId 削除する要約ID
 */
export const deleteSummary = async (summaryId: string): Promise<void> => {
  await api.delete(`/summaries/${summaryId}`);
};