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
    
    // エラーの詳細情報を出力
    if (error.response) {
      // サーバーからのレスポンスがある場合
      console.error('Error Response:', {
        status: error.response.status,
        statusText: error.response.statusText,
        data: error.response.data,
        headers: error.response.headers
      });
    } else if (error.request) {
      // リクエストは送信されたがレスポンスがない場合
      console.error('Error Request:', error.request);
    } else {
      // リクエスト設定中にエラーが発生した場合
      console.error('Error Message:', error.message);
    }
    
    // リクエスト設定を出力
    if (error.config) {
      console.error('Error Config:', {
        url: error.config.url,
        method: error.config.method,
        data: error.config.data,
        headers: error.config.headers
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;