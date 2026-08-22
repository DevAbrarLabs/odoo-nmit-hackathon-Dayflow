function Salary() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>Salary</h2>
          <p>View your salary details and monthly payslips.</p>
        </div>

        <button className="secondary-button">
          Download Payslip
        </button>
      </div>

      <div className="salary-summary">
        <div className="salary-card">
          <span>Gross Salary</span>
          <strong>₹60,000</strong>
          <small>Monthly</small>
        </div>

        <div className="salary-card">
          <span>Deductions</span>
          <strong>₹8,000</strong>
          <small>Monthly</small>
        </div>

        <div className="salary-card">
          <span>Net Salary</span>
          <strong>₹52,000</strong>
          <small>Monthly</small>
        </div>

        <div className="salary-card">
          <span>Pay Date</span>
          <strong>31 Aug</strong>
          <small>August 2026</small>
        </div>
      </div>

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>August 2026 Salary</h3>
            <p>Detailed breakdown of your monthly salary.</p>
          </div>
        </div>

        <div className="salary-breakdown-grid">
          <div className="salary-section">
            <h4>Earnings</h4>

            <div className="salary-row">
              <span>Basic Salary</span>
              <strong>₹30,000</strong>
            </div>

            <div className="salary-row">
              <span>House Rent Allowance</span>
              <strong>₹15,000</strong>
            </div>

            <div className="salary-row">
              <span>Special Allowance</span>
              <strong>₹10,000</strong>
            </div>

            <div className="salary-row">
              <span>Other Allowances</span>
              <strong>₹5,000</strong>
            </div>

            <div className="salary-row total">
              <span>Total Earnings</span>
              <strong>₹60,000</strong>
            </div>
          </div>

          <div className="salary-section">
            <h4>Deductions</h4>

            <div className="salary-row">
              <span>Provident Fund</span>
              <strong>₹3,600</strong>
            </div>

            <div className="salary-row">
              <span>Professional Tax</span>
              <strong>₹200</strong>
            </div>

            <div className="salary-row">
              <span>Income Tax</span>
              <strong>₹4,200</strong>
            </div>

            <div className="salary-row">
              <span>Other Deductions</span>
              <strong>₹0</strong>
            </div>

            <div className="salary-row total">
              <span>Total Deductions</span>
              <strong>₹8,000</strong>
            </div>
          </div>
        </div>

        <div className="net-salary">
          <span>Net Salary</span>
          <strong>₹52,000</strong>
        </div>
      </section>

      <section className="dashboard-card">
        <div className="section-header">
          <div>
            <h3>Previous Payslips</h3>
            <p>Your recent salary records.</p>
          </div>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Month</th>
                <th>Gross Salary</th>
                <th>Deductions</th>
                <th>Net Salary</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>July 2026</td>
                <td>₹60,000</td>
                <td>₹8,000</td>
                <td>₹52,000</td>
                <td>
                  <span className="status-badge success">
                    Paid
                  </span>
                </td>
                <td>
                  <button className="table-button">
                    View
                  </button>
                </td>
              </tr>

              <tr>
                <td>June 2026</td>
                <td>₹60,000</td>
                <td>₹8,000</td>
                <td>₹52,000</td>
                <td>
                  <span className="status-badge success">
                    Paid
                  </span>
                </td>
                <td>
                  <button className="table-button">
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default Salary;