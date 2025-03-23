import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clipboard, Save, Loader2 } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';

// OCR処理と要約のモックサービス
// 実際の実装では、APIサービスを使用します
const mockFetchJobStatus = async (jobId: string): Promise<{
  status: 'processing' | 'completed' | 'failed';
  progress?: number;
  originalText?: string;
  summarizedText?: string;
  error?: string;
}> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        status: 'completed',
        originalText: `これは、OCRによって抽出された元のテキストです。実際の実装では、アップロードされた画像から抽出されたテキストが表示されます。
        
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies tincidunt, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.
        
        サンプルテキストが続きます。これは長い文章の例です。実際のアプリケーションでは、ここに書籍のページから抽出されたテキストが表示されます。`,
        summarizedText: `これはAIによって要約されたテキストです。実際の実装では、抽出されたテキストをAIが要約した結果が表示されます。

        要約のポイント:
        1. 重要なポイント1
        2. 重要なポイント2
        3. 重要なポイント3
        
        この要約は元のテキストの主要な内容を簡潔にまとめています。`,
      });
    }, 2000);
  });
};

// 要約を保存するモックサービス
const mockSaveSummary = async (data: {
  title: string;
  description?: string;
  originalText: string;
  summarizedText: string;
}): Promise<{ id: string }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ id: 'summary-123456' });
    }, 1000);
  });
};

const SummaryResultPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [originalText, setOriginalText] = useState('');
  const [summarizedText, setSummarizedText] = useState('');
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const [showOriginalText, setShowOriginalText] = useState(false);

  useEffect(() => {
    const fetchJobStatus = async () => {
      if (!jobId) return;
      
      try {
        const result = await mockFetchJobStatus(jobId);
        
        if (result.status === 'failed') {
          setError(result.error || '処理に失敗しました');
        } else if (result.status === 'completed') {
          setOriginalText(result.originalText || '');
          setSummarizedText(result.summarizedText || '');
        }
      } catch (err) {
        setError('データの取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchJobStatus();
  }, [jobId]);

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(summarizedText)
      .then(() => {
        toast({
          title: 'クリップボードにコピーしました',
        });
      })
      .catch(() => {
        toast({
          title: 'コピーに失敗しました',
          variant: 'destructive',
        });
      });
  };

  const handleSave = async () => {
    if (!title.trim()) {
      toast({
        title: 'タイトルを入力してください',
        variant: 'destructive',
      });
      return;
    }

    setSaving(true);
    
    try {
      const result = await mockSaveSummary({
        title,
        description,
        originalText,
        summarizedText,
      });
      
      toast({
        title: '要約を保存しました',
      });
      
      // 保存した要約の詳細ページに遷移
      navigate(`/summaries/${result.id}`);
    } catch (err) {
      toast({
        title: '保存に失敗しました',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <h2 className="text-xl font-semibold">処理中...</h2>
        <p className="text-muted-foreground">OCR処理と要約を実行しています</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-destructive mb-4">エラーが発生しました</h2>
        <p className="text-muted-foreground mb-6">{error}</p>
        <button
          onClick={() => navigate('/upload')}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-md"
        >
          アップロードページに戻る
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">要約結果</h1>
        <p className="text-muted-foreground">
          OCR処理と要約が完了しました
        </p>
      </div>

      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">要約テキスト</h2>
          <div className="flex space-x-2">
            <button
              onClick={handleCopyToClipboard}
              className="inline-flex items-center text-sm bg-secondary text-secondary-foreground px-3 py-1.5 rounded-md hover:bg-secondary/80"
            >
              <Clipboard className="h-4 w-4 mr-1" />
              コピー
            </button>
            <button
              onClick={() => setShowSaveForm(!showSaveForm)}
              className="inline-flex items-center text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90"
            >
              <Save className="h-4 w-4 mr-1" />
              保存
            </button>
          </div>
        </div>

        <div className="bg-card text-card-foreground p-4 rounded-md shadow-sm whitespace-pre-line">
          {summarizedText}
        </div>

        <div>
          <button
            onClick={() => setShowOriginalText(!showOriginalText)}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            {showOriginalText ? '元のテキストを隠す' : '元のテキストを表示'}
          </button>
          
          {showOriginalText && (
            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">元のテキスト</h3>
              <div className="bg-muted p-4 rounded-md whitespace-pre-line text-sm">
                {originalText}
              </div>
            </div>
          )}
        </div>
      </div>

      {showSaveForm && (
        <div className="bg-card border rounded-md p-6 space-y-4">
          <h3 className="text-lg font-semibold">要約を保存</h3>
          
          <div className="space-y-2">
            <label htmlFor="title" className="block text-sm font-medium">
              タイトル <span className="text-destructive">*</span>
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full p-2 border rounded-md"
              placeholder="要約のタイトルを入力"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="description" className="block text-sm font-medium">
              説明 (任意)
            </label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full p-2 border rounded-md h-24"
              placeholder="要約の説明を入力（任意）"
            />
          </div>
          
          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowSaveForm(false)}
              className="px-4 py-2 border rounded-md text-sm"
            >
              キャンセル
            </button>
            <button
              onClick={handleSave}
              disabled={saving || !title.trim()}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
            >
              {saving ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryResultPage;
