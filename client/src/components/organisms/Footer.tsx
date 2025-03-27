const Footer = () => {
  return (
    <footer className="bg-primary text-primary-foreground py-6">
      <div className="container mx-auto px-4">
        <div className="flex justify-center">
          <p className="text-sm">© {new Date().getFullYear()} 書籍画像要約システム. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
