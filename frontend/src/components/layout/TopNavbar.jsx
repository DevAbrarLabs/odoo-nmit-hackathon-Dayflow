import { Menu, Bell, Search } from "lucide-react";

function TopNavbar({ onMenuClick }) {
  return (
    <header className="top-navbar">
      <button
        className="mobile-menu-button"
        onClick={onMenuClick}
        aria-label="Open menu"
      >
        <Menu size={24} />
      </button>

      <div className="top-search">
        <Search size={18} />

        <input
          type="text"
          placeholder="Search..."
        />
      </div>

      <div className="top-actions">
        <button className="notification-button">
          <Bell size={21} />
          <span className="notification-dot" />
        </button>

        <div className="user-menu">
          <div className="user-avatar">
            AS
          </div>

          <div className="user-info">
            <strong>Arjun Sharma</strong>
            <span>Employee</span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default TopNavbar;