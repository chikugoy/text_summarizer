import { useState } from 'react';
import { toast } from '@/components/ui/use-toast';

interface DeleteConfirmModalProps {
  summaryTitle: string;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

const DeleteConfirmModal = ({ summaryTitle, onClose, onConfirm }: DeleteConfirmModalProps) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    setIsDeleting(true);
    try {
      await onConfirm();
      onClose();
    } catch (error) {
      console.error('Delete summary error:', error);
      toast({
        title: '削除に失敗しました',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-background/80 flex items-center justify-center z-50">
      <div className="bg-card border rounded-md p-6 max-w-md w-full space-y-4 shadow-lg">
        <h3 className="text-lg font-semibold">要約を削除</h3>
        
        <p className="text-sm">
          「{summaryTitle}」を削除しますか？この操作は元に戻せません。
        </p>
        
        <div className="flex justify-end space-x-2">
          <button
            onClick={onClose}
            className="px-4 py-2 border rounded-md text-sm"
            disabled={isDeleting}
          >
            キャンセル
          </button>
          <button
            onClick={handleConfirm}
            disabled={isDeleting}
            className="bg-destructive text-destructive-foreground px-4 py-2 rounded-md text-sm disabled:opacity-50"
          >
            {isDeleting ? '削除中...' : '削除'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmModal;