/**
 * 要約サービス
 * 要約の作成、取得、更新、削除に関する機能を提供
 */

import api from './api';

// ============================================
// 型定義
// ============================================

/** 要約の基本情報 */
export interface SummaryBase {
  id: string;
  title: string;
  description: string | null;
  custom_instructions: string | null;
  created_at: string;
  updated_at: string;
}

/** 要約の詳細情報 */
export interface SummaryDetail extends SummaryBase {
  original_text: string;
  summarized_text: string;
}

/** 要約一覧レスポンス */
export interface SummaryList {
  items: SummaryBase[];
  total: number;
  page: number;
  page_size: number;
}

/** 要約作成リクエスト */
export interface SummaryCreate {
  title: string;
  description?: string;
  original_text: string;
  summarized_text: string;
}

/** 要約更新リクエスト */
export interface SummaryUpdate {
  title: string;
  description?: string;
}

/** 要約生成リクエスト */
export interface SummaryGenerateRequest {
  summary_id: string;
  custom_instructions?: string;
}

// ============================================
// UUID検証
// ============================================

const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/**
 * UUIDの形式を検証する
 * @param id 検証するID
 * @returns 有効なUUID形式の場合true
 */
const isValidUUID = (id: string): boolean => UUID_REGEX.test(id);

/**
 * UUIDの形式を検証し、無効な場合はエラーをスローする
 * @param id 検証するID
 * @param fieldName フィールド名（エラーメッセージ用）
 */
const validateUUID = (id: string, fieldName: string = 'ID'): void => {
  if (!isValidUUID(id)) {
    throw new Error(`${fieldName}が正しいUUID形式ではありません: ${id}`);
  }
};

// ============================================
// API関数
// ============================================

/**
 * 要約を新規作成する
 * @param summary 要約データ
 * @returns 作成された要約
 */
export const createSummary = async (summary: SummaryCreate): Promise<SummaryDetail> => {
  const response = await api.post<SummaryDetail>('/summaries', summary);
  return response.data;
};

/**
 * 画像からOCRテキストを抽出し、要約を生成する
 * @param summaryId 要約ID
 * @param customInstructions カスタム指示（省略時はデフォルトの要約指示）
 * @returns 生成された要約
 */
export const generateSummary = async (
  summaryId: string,
  customInstructions?: string
): Promise<SummaryDetail> => {
  validateUUID(summaryId, '要約ID');

  const requestBody: SummaryGenerateRequest = {
    summary_id: summaryId,
  };

  if (customInstructions) {
    requestBody.custom_instructions = customInstructions;
  }

  const response = await api.post<SummaryDetail>('/summaries/generate', requestBody);
  return response.data;
};

/**
 * 要約一覧を取得する（ページネーション付き）
 * @param page ページ番号（1から開始）
 * @param pageSize ページサイズ
 * @returns 要約一覧
 */
export const getSummaries = async (
  page: number = 1,
  pageSize: number = 10
): Promise<SummaryList> => {
  const skip = (page - 1) * pageSize;
  const response = await api.get<SummaryList>('/summaries', {
    params: { skip, limit: pageSize },
  });
  return response.data;
};

/**
 * 特定の要約詳細を取得する
 * @param summaryId 要約ID
 * @returns 要約詳細
 */
export const getSummaryDetail = async (summaryId: string): Promise<SummaryDetail> => {
  validateUUID(summaryId, '要約ID');
  const response = await api.get<SummaryDetail>(`/summaries/${summaryId}`);
  return response.data;
};

/**
 * 要約情報を更新する
 * @param summaryId 要約ID
 * @param update 更新データ
 * @returns 更新された要約
 */
export const updateSummary = async (
  summaryId: string,
  update: SummaryUpdate
): Promise<SummaryDetail> => {
  validateUUID(summaryId, '要約ID');
  const response = await api.put<SummaryDetail>(`/summaries/${summaryId}`, update);
  return response.data;
};

/**
 * 要約を削除する
 * @param summaryId 削除する要約ID
 */
export const deleteSummary = async (summaryId: string): Promise<void> => {
  validateUUID(summaryId, '要約ID');
  await api.delete(`/summaries/${summaryId}`);
};
