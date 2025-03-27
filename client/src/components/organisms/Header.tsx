import { Link } from 'react-router-dom';

const Header = () => {
  return (
    <header className="bg-primary text-primary-foreground shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/upload" className="text-2xl font-bold">書籍画像要約システム</Link>
          <nav>
            <ul className="flex space-x-6">
              <li>
                <Link to="/upload" className="hover:underline">アップロード</Link>
              </li>
              <li>
                <Link to="/summaries" className="hover:underline">要約履歴</Link>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </header>
  );
};

export default Header;
