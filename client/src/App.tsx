import { Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';

// レイアウト
import MainLayout from '@/components/templates/MainLayout';

// ページ
import HomePage from '@/components/pages/HomePage';
import UploadPage from '@/components/pages/UploadPage';
import SummaryResultPage from '@/components/pages/SummaryResultPage';
import SummaryListPage from '@/components/pages/SummaryListPage';
import SummaryDetailPage from '@/components/pages/SummaryDetailPage';
import NotFoundPage from '@/components/pages/NotFoundPage';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="result/:jobId" element={<SummaryResultPage />} />
          <Route path="summaries" element={<SummaryListPage />} />
          <Route path="summaries/:id" element={<SummaryDetailPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}

export default App;
