/**
 * OCR処理と要約生成を管理するカスタムフック
 */

import { useState, useEffect, useCallback } from 'react';
import { getOCRStatus, waitForOCRCompletion, OCRResponse } from '@/services/ocrService';
import { generateSummary } from '@/services/summaryService';
import { getImageDetail } from '@/services/imageService';

export interface OCRProcessingState {
  loading: boolean;
  error: string | null;
  originalText: string;
  summarizedText: string;
  status: 'idle' | 'processing' | 'completed' | 'failed';
}

export interface UseOCRProcessingResult extends OCRProcessingState {
  retry: () => void;
}

/**
 * OCR処理と要約生成を管理するフック
 * @param jobId OCRジョブID
 * @param customInstructions カスタム要約指示（省略時はデフォルトの要約指示）
 * @returns OCR処理状態と操作関数
 */
export const useOCRProcessing = (
  jobId: string | undefined,
  customInstructions?: string
): UseOCRProcessingResult => {
  const [state, setState] = useState<OCRProcessingState>({
    loading: true,
    error: null,
    originalText: '',
    summarizedText: '',
    status: 'idle',
  });

  const processOCRAndSummarize = useCallback(async () => {
    if (!jobId) return;

    setState(prev => ({ ...prev, loading: true, error: null, status: 'processing' }));

    try {
      // OCR処理のステータスを確認
      const ocrStatus = await getOCRStatus(jobId);

      if (ocrStatus.status === 'failed') {
        setState(prev => ({
          ...prev,
          loading: false,
          error: 'OCR処理に失敗しました',
          status: 'failed',
        }));
        return;
      }

      // 完了していない場合は待機
      let finalStatus: OCRResponse = ocrStatus;
      if (ocrStatus.status === 'processing') {
        try {
          finalStatus = await waitForOCRCompletion(jobId);
          if (finalStatus.status === 'failed') {
            setState(prev => ({
              ...prev,
              loading: false,
              error: 'OCR処理に失敗しました',
              status: 'failed',
            }));
            return;
          }
        } catch (waitError) {
          setState(prev => ({
            ...prev,
            loading: false,
            error: 'OCR処理の完了待機中にエラーが発生しました',
            status: 'failed',
          }));
          return;
        }
      }

      // OCR結果から画像IDを取得し、要約を生成
      const imageId = finalStatus.results[0]?.image_id;
      if (!imageId) {
        setState(prev => ({
          ...prev,
          loading: false,
          error: '要約の生成に失敗しました',
          status: 'failed',
        }));
        return;
      }

      // 画像の詳細情報を取得して要約IDを取得
      const imageDetail = await getImageDetail(imageId);
      const summaryId = imageDetail.summary_id;

      // 要約を生成（カスタム指示がある場合は渡す）
      const summary = await generateSummary(summaryId, customInstructions || undefined);

      setState({
        loading: false,
        error: null,
        originalText: summary.original_text,
        summarizedText: summary.summarized_text,
        status: 'completed',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : String(error);
      setState(prev => ({
        ...prev,
        loading: false,
        error: `要約の生成中にエラーが発生しました: ${errorMessage}`,
        status: 'failed',
      }));
    }
  }, [jobId, customInstructions]);

  useEffect(() => {
    processOCRAndSummarize();
  }, [processOCRAndSummarize]);

  const retry = useCallback(() => {
    processOCRAndSummarize();
  }, [processOCRAndSummarize]);

  return {
    ...state,
    retry,
  };
};
