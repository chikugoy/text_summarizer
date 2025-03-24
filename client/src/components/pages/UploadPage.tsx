import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { toast } from '@/components/ui/use-toast';
import { uploadImages, processOCR } from '@/services';

const UploadPage = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // 画像ファイルのみを受け入れる
    const imageFiles = acceptedFiles.filter(file => 
      file.type.startsWith('image/')
    );
    
    if (imageFiles.length !== acceptedFiles.length) {
      toast({
        title: '画像ファイルのみアップロード可能です',
        variant: 'destructive',
      });
    }
    
    setFiles(prev => [...prev, ...imageFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': []
    }
  });

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      toast({
        title: 'アップロードする画像を選択してください',
        variant: 'destructive',
      });
      return;
    }

    setIsUploading(true);
    
    try {
      // 画像をアップロードし、画像情報を取得
      const uploadedImages = await uploadImages(files);
      
      if (uploadedImages.length === 0) {
        throw new Error('画像のアップロードに失敗しました');
      }
      
      // OCR処理を実行 (日本語テキストを想定)
      const imageIds = uploadedImages.map(image => image.id);
      const ocrResponse = await processOCR(imageIds, 'ja');
      
      // 要約結果ページに遷移
      navigate(`/result/${ocrResponse.job_id}`);
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: 'アップロードに失敗しました',
        description: '後でもう一度お試しください',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">画像アップロード</h1>
        <p className="text-muted-foreground">
          書籍のページ画像をアップロードして、テキストを抽出し要約します
        </p>
      </div>

      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-primary/50'
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center space-y-4">
          <Upload className="h-12 w-12 text-muted-foreground" />
          <div>
            <p className="font-medium">
              {isDragActive 
                ? 'ここにファイルをドロップ' 
                : 'クリックまたはドラッグ＆ドロップでファイルをアップロード'
              }
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              画像ファイル（JPG, PNG, GIF, BMP）のみ対応
            </p>
          </div>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">アップロード予定ファイル ({files.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {files.map((file, index) => (
              <div key={index} className="flex items-center bg-card p-3 rounded-md shadow-sm">
                <div className="bg-muted rounded-md p-2 mr-3">
                  <ImageIcon className="h-5 w-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(file.size / 1024).toFixed(1)} KB
                  </p>
                </div>
                <button 
                  onClick={() => removeFile(index)}
                  className="ml-2 text-muted-foreground hover:text-destructive"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-center">
        <button
          onClick={handleUpload}
          disabled={isUploading || files.length === 0}
          className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isUploading ? 'アップロード中...' : 'アップロードして要約する'}
        </button>
      </div>
    </div>
  );
};

export default UploadPage;
