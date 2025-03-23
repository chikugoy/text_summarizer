import axios from 'axios';

// APIクライアントの基本設定
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
api.interceptors.request.use(
  (config) => {
    // リクエスト前の処理（認証トークンの追加など）
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター
api.interceptors.response.use(
  (response) => {
    // レスポンス後の処理
    return response;
  },
  (error) => {
    // エラーハンドリング
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default api;