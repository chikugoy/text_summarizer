const Footer = () => {
  return (
    <footer className="bg-primary text-primary-foreground py-6">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-sm">© {new Date().getFullYear()} 書籍画像要約サービス. All rights reserved.</p>
          </div>
          <div className="flex space-x-4">
            <a href="#" className="text-sm hover:underline">利用規約</a>
            <a href="#" className="text-sm hover:underline">プライバシーポリシー</a>
            <a href="#" className="text-sm hover:underline">お問い合わせ</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
