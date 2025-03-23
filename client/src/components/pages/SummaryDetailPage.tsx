import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Clock, Clipboard, Trash2, Edit } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { getSummaryDetail, deleteSummary, SummaryDetail } from '@/services';

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};

const SummaryDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  // 要約データの型定義
  type FormattedSummary = {
    id: string;
    title: string;
    description: string | null;
    originalText: string;
    summarizedText: string;
    createdAt: string;
  };
  
  const [summary, setSummary] = useState<FormattedSummary | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showOriginalText, setShowOriginalText] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const fetchSummaryDetail = async () => {
      if (!id) return;
      
      try {
        const data = await getSummaryDetail(id);
        
        // APIレスポンスを適切な形式に変換
        const formattedSummary: FormattedSummary = {
          id: data.id,
          title: data.title,
          description: data.description,
          originalText: data.original_text,
          summarizedText: data.summarized_text,
          createdAt: data.created_at
        };
        
        setSummary(formattedSummary);
      } catch (err) {
        console.error('Failed to fetch summary detail:', err);
        setError('要約の取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };

    fetchSummaryDetail();
  }, [id]);

  const handleCopyToClipboard = () => {
    if (!summary) return;
    
    navigator.clipboard.writeText(summary.summarizedText)
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

  const handleDelete = async () => {
    if (!summary || !id) return;
    
    setIsDeleting(true);
    
    try {
      // 要約を削除
      await deleteSummary(id);
      
      toast({
        title: '要約を削除しました',
      });
      navigate('/summaries');
    } catch (err) {
      console.error('Delete summary error:', err);
      toast({
        title: '削除に失敗しました',
        variant: 'destructive',
      });
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-destructive mb-4">エラーが発生しました</h2>
        <p className="text-muted-foreground mb-6">{error || '要約が見つかりませんでした'}</p>
        <Link
          to="/summaries"
          className="inline-flex items-center text-primary hover:underline"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          要約一覧に戻る
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <Link
          to="/summaries"
          className="inline-flex items-center text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          要約一覧に戻る
        </Link>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCopyToClipboard}
            className="inline-flex items-center text-sm bg-secondary text-secondary-foreground px-3 py-1.5 rounded-md hover:bg-secondary/80"
          >
            <Clipboard className="h-4 w-4 mr-1" />
            コピー
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="inline-flex items-center text-sm bg-destructive text-destructive-foreground px-3 py-1.5 rounded-md hover:bg-destructive/90"
          >
            <Trash2 className="h-4 w-4 mr-1" />
            削除
          </button>
        </div>
      </div>

      <div>
        <h1 className="text-3xl font-bold mb-2">{summary.title}</h1>
        {summary.description && (
          <p className="text-muted-foreground mb-4">{summary.description}</p>
        )}
        <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-6">
          <span className="flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            {formatDate(summary.createdAt)}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">要約テキスト</h2>
          <div className="bg-card text-card-foreground p-4 rounded-md shadow-sm whitespace-pre-line">
            {summary.summarizedText}
          </div>
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
                {summary.originalText}
              </div>
            </div>
          )}
        </div>
      </div>

      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
          <div className="bg-card border rounded-md p-6 max-w-md w-full space-y-4 shadow-lg">
            <h3 className="text-lg font-semibold">要約を削除しますか？</h3>
            <p className="text-muted-foreground">
              この操作は元に戻せません。本当に「{summary.title}」を削除しますか？
            </p>
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                className="px-4 py-2 border rounded-md text-sm"
                disabled={isDeleting}
              >
                キャンセル
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="bg-destructive text-destructive-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
              >
                {isDeleting ? '削除中...' : '削除する'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SummaryDetailPage;
