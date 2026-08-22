import { useState } from "react";

function Attendance() {
  const [isCheckedIn, setIsCheckedIn] = useState(true);
  const [checkInTime, setCheckInTime] = useState("09:02 AM");
  const [checkOutTime, setCheckOutTime] = useState(null);

  const attendanceHistory = [
    {
      date: "22 Aug 2026",
      day: "Saturday",
      checkIn: checkInTime,
      checkOut: checkOutTime || "-",
      hours: checkOutTime ? "8h 02m" : "Working...",
      status: isCheckedIn ? "Present" : "Completed",
    },
    {
      date: "21 Aug 2026",
      day: "Friday",
      checkIn: "08:56 AM",
      checkOut: "06:12 PM",
      hours: "8h 16m",
      status: "Present",
    },
    {
      date: "20 Aug 2026",
      day: "Thursday",
      checkIn: "09:10 AM",
      checkOut: "06:05 PM",
      hours: "7h 55m",
      status: "Present",
    },
    {
      date: "19 Aug 2026",
      day: "Wednesday",
      checkIn: "09:04 AM",
      checkOut: "06:20 PM",
      hours: "8h 16m",
      status: "Present",
    },
    {
      date: "18 Aug 2026",
      day: "Tuesday",
      checkIn: "-",
      checkOut: "-",
      hours: "-",
      status: "Leave",
    },
  ];

  const handleCheckIn = () => {
    const now = new Date();

    const time = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    setCheckInTime(time);
    setCheckOutTime(null);
    setIsCheckedIn(true);
  };

  const handleCheckOut = () => {
    const now = new Date();

    const time = now.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    setCheckOutTime(time);
    setIsCheckedIn(false);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Attendance</h2>
          <p>
            Track your working hours and attendance history.
          </p>
        </div>

        <div>
          {isCheckedIn ? (
            <button
              className="secondary-button"
              onClick={handleCheckOut}
            >
              Check Out
            </button>
          ) : (
            <button
              className="primary-button"
              onClick={handleCheckIn}
            >
              Check In
            </button>
          )}
        </div>
      </div>

      <div className="attendance-summary">
        <div className="attendance-card">
          <span>Today's Status</span>

          <strong>
            {isCheckedIn ? "Present" : "Completed"}
          </strong>

          <small>
            {isCheckedIn
              ? `Checked in at ${checkInTime}`
              : `Checked out at ${checkOutTime}`}
          </small>
        </div>

        <div className="attendance-card">
          <span>Check-in</span>

          <strong>{checkInTime}</strong>

          <small>Today</small>
        </div>

        <div className="attendance-card">
          <span>Check-out</span>

          <strong>{checkOutTime || "--:--"}</strong>

          <small>
            {isCheckedIn ? "Currently working" : "Completed"}
          </small>
        </div>

        <div className="attendance-card">
          <span>This Month</span>

          <strong>18 / 21</strong>

          <small>Working days</small>
        </div>
      </div>

      <section className="dashboard-card attendance-history">
        <div className="section-header">
          <div>
            <h3>Attendance History</h3>
            <p>Your recent attendance records</p>
          </div>

          <button className="secondary-button">
            This Month
          </button>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Check-in</th>
                <th>Check-out</th>
                <th>Hours</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {attendanceHistory.map((record) => (
                <tr key={record.date}>
                  <td>{record.date}</td>
                  <td>{record.day}</td>
                  <td>{record.checkIn}</td>
                  <td>{record.checkOut}</td>
                  <td>{record.hours}</td>

                  <td>
                    <span
                      className={`status-badge ${
                        record.status === "Present" ||
                        record.status === "Completed"
                          ? "success"
                          : "pending"
                      }`}
                    >
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Attendance;