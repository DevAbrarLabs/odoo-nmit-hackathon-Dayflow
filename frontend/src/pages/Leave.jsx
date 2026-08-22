import { useState } from "react";

function Leave() {
  const [leaveType, setLeaveType] = useState("Casual Leave");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [reason, setReason] = useState("");

  const [leaveRequests, setLeaveRequests] = useState([
    {
      id: 1,
      type: "Casual Leave",
      startDate: "18 Aug 2026",
      endDate: "18 Aug 2026",
      reason: "Personal work",
      days: 1,
      status: "Approved",
    },
    {
      id: 2,
      type: "Sick Leave",
      startDate: "05 Aug 2026",
      endDate: "06 Aug 2026",
      reason: "Not feeling well",
      days: 2,
      status: "Approved",
    },
    {
      id: 3,
      type: "Casual Leave",
      startDate: "28 Aug 2026",
      endDate: "29 Aug 2026",
      reason: "Family function",
      days: 2,
      status: "Pending",
    },
  ]);

  const calculateDays = () => {
    if (!startDate || !endDate) {
      return 0;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    const difference =
      Math.abs(end - start) / (1000 * 60 * 60 * 24);

    return difference + 1;
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (!startDate || !endDate || !reason.trim()) {
      alert("Please fill in all the required fields.");
      return;
    }

    if (new Date(endDate) < new Date(startDate)) {
      alert("End date cannot be before start date.");
      return;
    }

    const newRequest = {
      id: Date.now(),
      type: leaveType,
      startDate: new Date(startDate).toLocaleDateString(
        "en-GB",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }
      ),
      endDate: new Date(endDate).toLocaleDateString(
        "en-GB",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }
      ),
      reason,
      days: calculateDays(),
      status: "Pending",
    };

    setLeaveRequests((previous) => [
      newRequest,
      ...previous,
    ]);

    setStartDate("");
    setEndDate("");
    setReason("");

    alert("Leave application submitted successfully.");
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Leave</h2>

          <p>
            Apply for leave and track your requests.
          </p>
        </div>
      </div>

      {/* Leave Balance */}

      <div className="leave-summary">
        <div className="leave-card">
          <span>Casual Leave</span>

          <strong>8</strong>

          <small>Days remaining</small>
        </div>

        <div className="leave-card">
          <span>Sick Leave</span>

          <strong>6</strong>

          <small>Days remaining</small>
        </div>

        <div className="leave-card">
          <span>Earned Leave</span>

          <strong>12</strong>

          <small>Days remaining</small>
        </div>

        <div className="leave-card">
          <span>Pending Requests</span>

          <strong>
            {
              leaveRequests.filter(
                (request) => request.status === "Pending"
              ).length
            }
          </strong>

          <small>Awaiting approval</small>
        </div>
      </div>

      {/* Application Form */}

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>Apply for Leave</h3>

            <p>
              Submit a new leave request.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="leaveType">
                Leave Type
              </label>

              <select
                id="leaveType"
                value={leaveType}
                onChange={(event) =>
                  setLeaveType(event.target.value)
                }
              >
                <option>Casual Leave</option>
                <option>Sick Leave</option>
                <option>Earned Leave</option>
                <option>Unpaid Leave</option>
              </select>
            </div>

            <div className="form-group">
              <label>Number of Days</label>

              <input
                type="text"
                value={
                  calculateDays()
                    ? `${calculateDays()} day${
                        calculateDays() > 1
                          ? "s"
                          : ""
                      }`
                    : "Select dates"
                }
                readOnly
              />
            </div>

            <div className="form-group">
              <label htmlFor="startDate">
                Start Date
              </label>

              <input
                id="startDate"
                type="date"
                value={startDate}
                onChange={(event) =>
                  setStartDate(event.target.value)
                }
              />
            </div>

            <div className="form-group">
              <label htmlFor="endDate">
                End Date
              </label>

              <input
                id="endDate"
                type="date"
                value={endDate}
                onChange={(event) =>
                  setEndDate(event.target.value)
                }
              />
            </div>

            <div className="form-group form-group-full">
              <label htmlFor="reason">
                Reason
              </label>

              <textarea
                id="reason"
                rows="4"
                placeholder="Enter the reason for your leave..."
                value={reason}
                onChange={(event) =>
                  setReason(event.target.value)
                }
              />
            </div>
          </div>

          <button
            type="submit"
            className="primary-button"
          >
            Submit Leave Request
          </button>
        </form>
      </section>

      {/* Leave History */}

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>Leave History</h3>

            <p>
              Your previous and pending leave requests.
            </p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Leave Type</th>
                <th>Start Date</th>
                <th>End Date</th>
                <th>Days</th>
                <th>Reason</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              {leaveRequests.map((request) => (
                <tr key={request.id}>
                  <td>{request.type}</td>

                  <td>{request.startDate}</td>

                  <td>{request.endDate}</td>

                  <td>{request.days}</td>

                  <td>{request.reason}</td>

                  <td>
                    <span
                      className={`status-badge ${
                        request.status === "Approved"
                          ? "success"
                          : "pending"
                      }`}
                    >
                      {request.status}
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

export default Leave;