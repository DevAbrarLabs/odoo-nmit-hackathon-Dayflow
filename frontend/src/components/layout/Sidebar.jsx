import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  User,
  Clock3,
  CalendarDays,
  Wallet,
  Bell,
  LogOut,
} from "lucide-react";

const navigation = [
  {
    name: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    name: "Profile",
    path: "/profile",
    icon: User,
  },
  {
    name: "Attendance",
    path: "/attendance",
    icon: Clock3,
  },
  {
    name: "Leave",
    path: "/leave",
    icon: CalendarDays,
  },
  {
    name: "Salary",
    path: "/salary",
    icon: Wallet,
  },
  {
    name: "Notifications",
    path: "/notifications",
    icon: Bell,
  },
];

function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {isOpen && (
        <div
          className="sidebar-overlay"
          onClick={onClose}
        />
      )}

      <aside
        className={`sidebar ${
          isOpen ? "sidebar-open" : ""
        }`}
      >
        <div className="sidebar-brand">
          <div className="brand-logo">D</div>

          <div>
            <h1>Dayflow</h1>
            <span>Employee Portal</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `sidebar-link ${
                    isActive ? "sidebar-link-active" : ""
                  }`
                }
              >
                <Icon size={20} />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        <button className="sidebar-logout">
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </aside>
    </>
  );
}

export default Sidebar;