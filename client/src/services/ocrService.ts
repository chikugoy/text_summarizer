import api from './api';

/**
 * OCRサービス
 * OCR処理に関する機能を提供
 */
export interface OCRResult {
  image_id: string;
  success: boolean;
  ocr_text?: string;
  error?: string;
}

export interface OCRResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  results: OCRResult[];
}

export interface OCRRequest {
  image_ids: string[];
}

/**
 * アップロードされた画像のOCR処理を実行する
 * @param imageIds OCR処理を行う画像IDの配列
 * @returns OCR処理の結果
 */
export const processOCR = async (imageIds: string[]): Promise<OCRResponse> => {
  const response = await api.post<OCRResponse>('/ocr/process', {
    image_ids: imageIds,
  });
  
  return response.data;
};

/**
 * OCR処理のステータスを確認する
 * @param jobId OCRジョブID
 * @returns OCR処理の結果
 */
export const getOCRStatus = async (jobId: string): Promise<OCRResponse> => {
  const response = await api.get<OCRResponse>(`/ocr/status/${jobId}`);
  return response.data;
};

/**
 * OCR処理の完了を待機する
 * @param jobId OCRジョブID
 * @param interval ポーリング間隔（ミリ秒）
 * @param timeout タイムアウト時間（ミリ秒）
 * @returns OCR処理の結果
 */
export const waitForOCRCompletion = async (
  jobId: string,
  interval = 2000,
  timeout = 60000
): Promise<OCRResponse> => {
  const startTime = Date.now();
  
  // ポーリング関数
  const poll = async (): Promise<OCRResponse> => {
    // タイムアウトチェック
    if (Date.now() - startTime > timeout) {
      throw new Error('OCR処理がタイムアウトしました');
    }
    
    const status = await getOCRStatus(jobId);
    
    // 処理が完了または失敗した場合
    if (status.status === 'completed' || status.status === 'failed') {
      return status;
    }
    
    // まだ処理中の場合は待機して再試行
    return new Promise((resolve) => {
      setTimeout(() => resolve(poll()), interval);
    });
  };
  
  return poll();
};