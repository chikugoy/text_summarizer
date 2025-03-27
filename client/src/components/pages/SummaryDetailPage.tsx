import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Calendar, Clipboard, Trash2, Edit } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { getSummaryDetail, deleteSummary, updateSummary } from '@/services/summaryService';
import type { SummaryDetail, SummaryUpdate } from '@/services/summaryService';
import { formatDateTime } from '@/lib/utils';
import EditSummaryModal from './EditSummaryModal';
import DeleteConfirmModal from './DeleteConfirmModal';

interface SummaryViewState {
  loading: boolean;
  error: string | null;
  showOriginalText: boolean;
  isDeleting: boolean;
}

const SummaryDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [summary, setSummary] = useState<SummaryDetail | null>(null);
  const [viewState, setViewState] = useState<SummaryViewState>({
    loading: true,
    error: null,
    showOriginalText: false,
    isDeleting: false
  });
  const [modalState, setModalState] = useState({
    edit: false,
    delete: false
  });

  useEffect(() => {
    const fetchSummaryDetail = async () => {
      if (!id) return;
      
      try {
        const data = await getSummaryDetail(id);
        setSummary(data);
        setViewState(prev => ({ ...prev, loading: false }));
      } catch (err) {
        console.error('Failed to fetch summary detail:', err);
        setViewState(prev => ({
          ...prev,
          loading: false,
          error: '要約の取得中にエラーが発生しました'
        }));
      }
    };

    fetchSummaryDetail();
  }, [id]);

  const handleCopyToClipboard = () => {
    if (!summary) return;
    
    navigator.clipboard.writeText(summary.summarized_text)
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
    
    setViewState(prev => ({ ...prev, isDeleting: true }));
    
    try {
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
      setViewState(prev => ({ ...prev, isDeleting: false }));
      setModalState(prev => ({ ...prev, delete: false }));
    }
  };

  const handleUpdate = async (updateData: SummaryUpdate) => {
    if (!summary || !id) return;
    
    try {
      const updated = await updateSummary(id, updateData);
      setSummary(updated);
      setModalState(prev => ({ ...prev, edit: false }));
      toast({
        title: '要約を更新しました',
      });
    } catch (error) {
      console.error('Update summary error:', error);
      toast({
        title: '更新に失敗しました',
        variant: 'destructive',
      });
    }
  };

  if (viewState.loading) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">読み込み中...</p>
      </div>
    );
  }

  if (viewState.error || !summary) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-destructive mb-4">エラーが発生しました</h2>
        <p className="text-muted-foreground mb-6">{viewState.error || '要約が見つかりませんでした'}</p>
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
            onClick={() => setModalState(prev => ({ ...prev, edit: true }))}
            className="inline-flex items-center text-sm bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90"
          >
            <Edit className="h-4 w-4 mr-1" />
            編集
          </button>
          <button
            onClick={() => setModalState(prev => ({ ...prev, delete: true }))}
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
            {formatDateTime(summary.created_at)}
          </span>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-4">要約テキスト</h2>
          <div className="bg-card text-card-foreground p-4 rounded-md shadow-sm whitespace-pre-line">
            {summary.summarized_text}
          </div>
        </div>

        <div>
          <button
            onClick={() => setViewState(prev => ({
              ...prev,
              showOriginalText: !prev.showOriginalText
            }))}
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            {viewState.showOriginalText ? '元のテキストを隠す' : '元のテキストを表示'}
          </button>
          
          {viewState.showOriginalText && (
            <div className="mt-4">
              <h3 className="text-lg font-medium mb-2">元のテキスト</h3>
              <div className="bg-muted p-4 rounded-md whitespace-pre-line text-sm">
                {summary.original_text}
              </div>
            </div>
          )}
        </div>
      </div>

      {modalState.edit && summary && (
        <EditSummaryModal
          summary={summary}
          onClose={() => setModalState(prev => ({ ...prev, edit: false }))}
          onSave={handleUpdate}
        />
      )}

      {modalState.delete && summary && (
        <DeleteConfirmModal
          summaryTitle={summary.title}
          onClose={() => setModalState(prev => ({ ...prev, delete: false }))}
          onConfirm={handleDelete}
        />
      )}
    </div>
  );
};

export default SummaryDetailPage;
