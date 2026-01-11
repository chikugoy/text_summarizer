/**
 * クリップボード操作を管理するカスタムフック
 */

import { useCallback, useState } from 'react';
import { toast } from '@/components/ui/use-toast';

export interface UseClipboardResult {
  copied: boolean;
  copyToClipboard: (text: string) => Promise<boolean>;
}

/**
 * クリップボードへのコピー機能を提供するフック
 * @returns コピー状態と操作関数
 */
export const useClipboard = (): UseClipboardResult => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = useCallback(async (text: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      toast({
        title: 'クリップボードにコピーしました',
      });

      // 2秒後にコピー状態をリセット
      setTimeout(() => setCopied(false), 2000);
      return true;
    } catch {
      setCopied(false);
      toast({
        title: 'コピーに失敗しました',
        variant: 'destructive',
      });
      return false;
    }
  }, []);

  return {
    copied,
    copyToClipboard,
  };
};
