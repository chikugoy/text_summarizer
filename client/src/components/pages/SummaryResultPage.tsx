import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clipboard, Save, Loader2 } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { getOCRStatus, waitForOCRCompletion, createSummary, generateSummary } from '@/services';
import { getImageDetail } from '@/services/imageService';

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
        // OCR処理のステータスを確認
        const ocrStatus = await getOCRStatus(jobId);
        
        if (ocrStatus.status === 'failed') {
          setError('OCR処理に失敗しました');
          setLoading(false);
          return;
        }
        
        if (ocrStatus.status === 'processing') {
          // 処理中の場合は完了を待機
          try {
            const completedStatus = await waitForOCRCompletion(jobId);
            
            if (completedStatus.status === 'failed') {
              setError('OCR処理に失敗しました');
              setLoading(false);
              return;
            }
            
            // OCR結果から画像IDを取得
            const imageId = completedStatus.results[0]?.image_id;
            if (imageId) {
              // 画像の詳細情報を取得して要約IDを取得
              const imageDetail = await getImageDetail(imageId);
              const summaryId = imageDetail.summary_id;
              
              // 要約を生成
              try {
                console.log(`要約生成開始: summaryId=${summaryId}, 型=${typeof summaryId}`);
                const summary = await generateSummary(summaryId);
                console.log(`要約生成完了:`, summary);
                setOriginalText(summary.original_text);
                setSummarizedText(summary.summarized_text);
              } catch (error) {
                console.error('要約生成エラー:', error);
                setError(`要約の生成中にエラーが発生しました: ${error instanceof Error ? error.message : String(error)}`);
              }
            } else {
              setError('要約の生成に失敗しました');
            }
          } catch (waitError) {
            console.error('Waiting for OCR completion failed:', waitError);
            setError('OCR処理の完了待機中にエラーが発生しました');
          }
        } else if (ocrStatus.status === 'completed') {
          // 既に完了している場合
          const imageId = ocrStatus.results[0]?.image_id;
          if (imageId) {
            // 画像の詳細情報を取得して要約IDを取得
            const imageDetail = await getImageDetail(imageId);
            const summaryId = imageDetail.summary_id;
            
            // 要約を生成
            try {
              console.log(`要約生成開始: summaryId=${summaryId}, 型=${typeof summaryId}`);
              const summary = await generateSummary(summaryId);
              console.log(`要約生成完了:`, summary);
              setOriginalText(summary.original_text);
              setSummarizedText(summary.summarized_text);
            } catch (error) {
              console.error('要約生成エラー:', error);
              setError(`要約の生成中にエラーが発生しました: ${error instanceof Error ? error.message : String(error)}`);
            }
          } else {
            setError('要約の生成に失敗しました');
          }
        }
      } catch (err) {
        console.error('Fetch job status error:', err);
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
      // 要約を保存
      const summary = await createSummary({
        title,
        description: description || undefined,
        original_text: originalText,
        summarized_text: summarizedText,
      });
      
      toast({
        title: '要約を保存しました',
      });
      
      // 保存した要約の詳細ページに遷移
      navigate(`/summaries/${summary.id}`);
    } catch (err) {
      console.error('Save summary error:', err);
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
