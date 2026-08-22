import { useState } from "react";

function Notifications() {
  const [notifications, setNotifications] = useState([
    {
      id: 1,
      title: "Leave request approved",
      message:
        "Your casual leave request for 18 Aug 2026 has been approved.",
      time: "2 hours ago",
      unread: true,
    },
    {
      id: 2,
      title: "Salary slip available",
      message:
        "Your August 2026 salary slip is now available.",
      time: "Yesterday",
      unread: true,
    },
    {
      id: 3,
      title: "Team announcement",
      message:
        "The next company town hall is scheduled for Friday.",
      time: "2 days ago",
      unread: false,
    },
    {
      id: 4,
      title: "Attendance reminder",
      message:
        "Remember to check out before leaving the office.",
      time: "3 days ago",
      unread: false,
    },
  ]);

  const markAllRead = () => {
    setNotifications((previous) =>
      previous.map((notification) => ({
        ...notification,
        unread: false,
      }))
    );
  };

  const unreadCount = notifications.filter(
    (notification) => notification.unread
  ).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Notifications</h2>

          <p>
            Stay updated with your latest employee activity.
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            className="secondary-button"
            onClick={markAllRead}
          >
            Mark all as read
          </button>
        )}
      </div>

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>
              All Notifications
            </h3>

            <p>
              {unreadCount} unread notification
              {unreadCount !== 1 ? "s" : ""}
            </p>
          </div>
        </div>

        {notifications.map((notification) => (
          <div
            className="notification-row"
            key={notification.id}
          >
            <div className="notification-icon">
              {notification.unread ? "!" : "✓"}
            </div>

            <div className="notification-content">
              <div className="notification-title-row">
                <strong>
                  {notification.title}
                </strong>

                {notification.unread && (
                  <span className="unread-dot"></span>
                )}
              </div>

              <p>
                {notification.message}
              </p>

              <div className="notification-meta">
                <span>
                  {notification.time}
                </span>
              </div>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

export default Notifications;