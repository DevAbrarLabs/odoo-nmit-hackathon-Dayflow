import { useState } from "react";

function Dashboard() {
  const [isCheckedIn, setIsCheckedIn] = useState(true);
  const [checkInTime, setCheckInTime] = useState("09:02 AM");

  const handleAttendance = () => {
    if (isCheckedIn) {
      setIsCheckedIn(false);
      return;
    }

    const now = new Date();

    const time = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    setCheckInTime(time);
    setIsCheckedIn(true);
  };

  const upcomingItems = [
    {
      title: "Team Meeting",
      time: "10:30 AM",
      description: "Weekly engineering sync",
    },
    {
      title: "Project Review",
      time: "02:00 PM",
      description: "Dayflow sprint review",
    },
    {
      title: "HR Check-in",
      time: "04:30 PM",
      description: "Monthly employee check-in",
    },
  ];

  const notifications = [
    {
      title: "Leave request approved",
      description:
        "Your casual leave request for 18 Aug has been approved.",
      time: "2 hours ago",
    },
    {
      title: "Salary slip available",
      description:
        "Your August 2026 salary slip is now available.",
      time: "Yesterday",
    },
    {
      title: "Team announcement",
      description:
        "The next company town hall is scheduled for Friday.",
      time: "2 days ago",
    },
  ];

  return (
    <div className="page">
      {/* Header */}

      <div className="page-header">
        <div>
          <h2>Good morning, Abrar 👋</h2>

          <p>
            Here's what's happening with your work today.
          </p>
        </div>

        <div className="date-display">
          Saturday, 22 August 2026
        </div>
      </div>

      {/* Statistics */}

      <div className="dashboard-grid">
        <div className="stat-card">
          <span className="stat-label">
            Attendance
          </span>

          <strong className="stat-value">
            18 / 21
          </strong>

          <span className="stat-description">
            Working days this month
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-label">
            Leave Balance
          </span>

          <strong className="stat-value">
            26 days
          </strong>

          <span className="stat-description">
            Total remaining leave
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-label">
            Hours This Month
          </span>

          <strong className="stat-value">
            142h
          </strong>

          <span className="stat-description">
            Across 18 working days
          </span>
        </div>

        <div className="stat-card">
          <span className="stat-label">
            Next Salary
          </span>

          <strong className="stat-value">
            ₹52,000
          </strong>

          <span className="stat-description">
            Expected on 31 Aug
          </span>
        </div>
      </div>

      {/* Attendance + Schedule */}

      <div className="dashboard-sections">
        <section className="dashboard-card">
          <div className="section-header">
            <div>
              <h3>Today's Attendance</h3>

              <p>
                Track your working hours today.
              </p>
            </div>

            <span
              className={`status-badge ${
                isCheckedIn
                  ? "success"
                  : "pending"
              }`}
            >
              {isCheckedIn
                ? "Currently Working"
                : "Checked Out"}
            </span>
          </div>

          <div className="attendance-summary">
            <div className="attendance-card">
              <span>Check-in</span>

              <strong>{checkInTime}</strong>

              <small>Today</small>
            </div>

            <div className="attendance-card">
              <span>Check-out</span>

              <strong>
                {isCheckedIn ? "--:--" : "06:00 PM"}
              </strong>

              <small>
                {isCheckedIn
                  ? "Not checked out"
                  : "Completed"}
              </small>
            </div>
          </div>

          <button
            className={
              isCheckedIn
                ? "secondary-button"
                : "primary-button"
            }
            onClick={handleAttendance}
          >
            {isCheckedIn
              ? "Check Out"
              : "Check In"}
          </button>
        </section>

        {/* Upcoming */}

        <section className="dashboard-card">
          <div className="section-header">
            <div>
              <h3>Today's Schedule</h3>

              <p>
                Your upcoming activities.
              </p>
            </div>
          </div>

          {upcomingItems.map((item) => (
            <div
              className="schedule-item"
              key={item.title}
            >
              <div>
                <strong>{item.title}</strong>

                <span>
                  {item.description}
                </span>
              </div>

              <span>{item.time}</span>
            </div>
          ))}
        </section>
      </div>

      {/* Notifications */}

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>Recent Notifications</h3>

            <p>
              Stay updated with your latest activity.
            </p>
          </div>
        </div>

        {notifications.map((notification) => (
          <div
            className="notification-row"
            key={notification.title}
          >
            <div className="notification-icon">
              ✓
            </div>

            <div className="notification-content">
              <div className="notification-title-row">
                <strong>
                  {notification.title}
                </strong>

                <span className="unread-dot"></span>
              </div>

              <p>
                {notification.description}
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

export default Dashboard;