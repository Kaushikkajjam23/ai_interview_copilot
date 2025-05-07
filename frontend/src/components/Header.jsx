import { Link } from 'react-router-dom';

function Header() {
  return (
    <header className="app-header">
      <div className="header-container">
        <Link to="/" className="logo">
          AI Interview Co-Pilot
        </Link>
        <nav className="main-nav">
          <Link to="/">New Interview</Link>
        </nav>
      </div>
    </header>
  );
}

export default Header;