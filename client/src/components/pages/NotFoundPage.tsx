import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

const NotFoundPage = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-6 text-center">
      <h1 className="text-6xl font-bold text-primary">404</h1>
      <h2 className="text-2xl font-semibold">ページが見つかりません</h2>
      <p className="text-muted-foreground max-w-md">
        お探しのページは存在しないか、移動した可能性があります。
      </p>
      <Link 
        to="/" 
        className="inline-flex items-center bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors"
      >
        <Home className="mr-2 h-4 w-4" />
        ホームに戻る
      </Link>
    </div>
  );
};

export default NotFoundPage;
