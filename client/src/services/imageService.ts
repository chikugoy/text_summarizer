import api from './api';

/**
 * 画像サービス
 * 画像のアップロードと取得に関する機能を提供
 */
export interface ImageBase {
  id: string;
  summary_id: string;
  file_path: string;
  file_name: string;
  file_size: number;
  mime_type: string;
  page_number: number;
  created_at: string;
}

export interface ImageDetail extends ImageBase {
  ocr_text: string | null;
}

export interface ImageList {
  items: ImageBase[];
  total: number;
}

/**
 * 複数の書籍ページ画像をアップロードする
 * @param files アップロードする画像ファイルの配列
 * @param summaryId 関連付ける要約ID（オプション）
 * @returns アップロードされた画像情報の配列
 */
export const uploadImages = async (files: File[], summaryId?: string): Promise<ImageBase[]> => {
  const formData = new FormData();
  
  // ファイルを追加
  files.forEach(file => {
    formData.append('files', file);
  });
  
  // 要約IDがある場合は追加
  if (summaryId) {
    formData.append('summary_id', summaryId);
  }
  
  const response = await api.post<ImageBase[]>('/images/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

/**
 * 特定の要約に関連する画像一覧を取得する
 * @param summaryId 要約ID
 * @returns 画像一覧
 */
export const getImagesBySummary = async (summaryId: string): Promise<ImageList> => {
  const response = await api.get<ImageList>(`/images/${summaryId}`);
  return response.data;
};

/**
 * 特定の画像の詳細情報を取得する
 * @param imageId 画像ID
 * @returns 画像詳細情報
 */
export const getImageDetail = async (imageId: string): Promise<ImageDetail> => {
  const response = await api.get<ImageDetail>(`/images/${imageId}/detail`);
  return response.data;
};

/**
 * 画像を削除する
 * @param imageId 削除する画像ID
 */
export const deleteImage = async (imageId: string): Promise<void> => {
  await api.delete(`/images/${imageId}`);
};