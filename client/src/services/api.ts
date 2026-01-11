/**
 * API クライアント設定
 * Axiosを使用したHTTPクライアントの設定とインターセプター
 */

import axios, { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// ============================================
// 設定
// ============================================

/** API のベースURL */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/** デバッグモード */
const DEBUG = import.meta.env.DEV;

// ============================================
// API クライアント作成
// ============================================

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5分（要約処理に時間がかかる場合があるため）
});

// ============================================
// インターセプター
// ============================================

/**
 * リクエストインターセプター
 * リクエスト送信前の処理
 */
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 認証トークンの追加など、必要に応じて処理を追加
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

/**
 * レスポンスインターセプター
 * レスポンス受信後の処理とエラーハンドリング
 */
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError) => {
    // 開発環境でのみ詳細なエラーログを出力
    if (DEBUG) {
      logError(error);
    }
    return Promise.reject(error);
  }
);

// ============================================
// ヘルパー関数
// ============================================

/**
 * エラー情報をログ出力する
 * @param error Axiosエラー
 */
const logError = (error: AxiosError): void => {
  console.error('API Error:', error.message);

  if (error.response) {
    // サーバーからのレスポンスがある場合
    console.error('Response:', {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data,
    });
  } else if (error.request) {
    // リクエストは送信されたがレスポンスがない場合
    console.error('No response received');
  }

  if (error.config) {
    console.error('Request:', {
      url: error.config.url,
      method: error.config.method,
    });
  }
};

export default api;
