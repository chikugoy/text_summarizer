/**
 * 要約結果ページ
 *
 * OCR処理と要約生成の結果を表示し、保存機能を提供する。
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Clipboard, Save, Loader2 } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { createSummary } from '@/services';
import { useOCRProcessing, useClipboard } from '@/hooks';
import { useSummaryStore } from '@/stores';

// ============================================
// 保存フォームコンポーネント
// ============================================

interface SaveFormProps {
  originalText: string;
  summarizedText: string;
  onSaved: (id: string) => void;
  onCancel: () => void;
}

const SaveForm = ({ originalText, summarizedText, onSaved, onCancel }: SaveFormProps) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);

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
      const summary = await createSummary({
        title,
        description: description || undefined,
        original_text: originalText,
        summarized_text: summarizedText,
      });

      toast({ title: '要約を保存しました' });
      onSaved(summary.id);
    } catch {
      toast({
        title: '保存に失敗しました',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
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
          onClick={onCancel}
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
  );
};

// ============================================
// メインコンポーネント
// ============================================

const SummaryResultPage = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const { copyToClipboard } = useClipboard();
  const { customInstructions, clearCustomInstructions } = useSummaryStore();

  const { loading, error, originalText, summarizedText } = useOCRProcessing(jobId, customInstructions);
  const [showSaveForm, setShowSaveForm] = useState(false);
  const [showOriginalText, setShowOriginalText] = useState(false);

  // 処理完了後にカスタム指示をクリア
  useEffect(() => {
    if (!loading && !error) {
      clearCustomInstructions();
    }
  }, [loading, error, clearCustomInstructions]);

  const handleCopyToClipboard = () => {
    copyToClipboard(summarizedText);
  };

  const handleSaved = (id: string) => {
    navigate(`/summaries/${id}`);
  };

  // ローディング表示
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <Loader2 className="h-12 w-12 animate-spin text-primary" />
        <h2 className="text-xl font-semibold">処理中...</h2>
        <p className="text-muted-foreground">OCR処理と要約を実行しています</p>
      </div>
    );
  }

  // エラー表示
  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-destructive mb-4">
          エラーが発生しました
        </h2>
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

  // 結果表示
  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">要約結果</h1>
        <p className="text-muted-foreground">OCR処理と要約が完了しました</p>
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
        <SaveForm
          originalText={originalText}
          summarizedText={summarizedText}
          onSaved={handleSaved}
          onCancel={() => setShowSaveForm(false)}
        />
      )}
    </div>
  );
};

export default SummaryResultPage;
