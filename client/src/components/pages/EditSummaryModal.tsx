import { useState } from 'react';
import { toast } from '@/components/ui/use-toast';
import { SummaryDetail, SummaryUpdate } from '@/services/summaryService';

interface EditSummaryModalProps {
  summary: SummaryDetail;
  onClose: () => void;
  onSave: (update: SummaryUpdate) => Promise<void>;
}

const EditSummaryModal = ({ summary, onClose, onSave }: EditSummaryModalProps) => {
  const [formData, setFormData] = useState<SummaryUpdate>({
    title: summary.title || '',
    description: summary.description ?? undefined
  });
  const [isSaving, setIsSaving] = useState(false);

  const handleSave = async () => {
    if (!formData.title.trim()) {
      toast({
        title: 'タイトルは必須です',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      await onSave(formData);
      onClose();
    } catch (error) {
      console.error('Update summary error:', error);
      toast({
        title: '更新に失敗しました',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
      <div className="bg-card border rounded-md p-6 max-w-md w-full space-y-4 shadow-lg">
        <h3 className="text-lg font-semibold">要約を編集</h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="edit-title" className="block text-sm font-medium mb-1">
              タイトル
            </label>
            <input
              id="edit-title"
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-3 py-2 border rounded-md"
              required
            />
          </div>
          
          <div>
            <label htmlFor="edit-description" className="block text-sm font-medium mb-1">
              説明
            </label>
            <textarea
              id="edit-description"
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-3 py-2 border rounded-md min-h-[100px]"
            />
          </div>
        </div>
        
        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-md text-sm"
            disabled={isSaving}
          >
            キャンセル
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
          >
            {isSaving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditSummaryModal;