function Profile() {
  const employee = {
    name: "Abrar",
    employeeId: "EMP001",
    email: "abrar@example.com",
    phone: "+91 98765 43210",
    department: "Engineering",
    designation: "Software Engineer",
    manager: "Rahul Sharma",
    joiningDate: "01 July 2026",
    location: "Bangalore, India",
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h2>My Profile</h2>
          <p>View your personal and employment information.</p>
        </div>
      </div>

      <div className="profile-layout">
        <section className="profile-card profile-summary">
          <div className="profile-avatar-large">A</div>

          <h3>{employee.name}</h3>
          <p>{employee.designation}</p>

          <span className="status-badge success">
            Active Employee
          </span>
        </section>

        <section className="profile-card">
          <div className="section-header">
            <div>
              <h3>Personal Information</h3>
              <p>Your basic employee information.</p>
            </div>
          </div>

          <div className="profile-grid">
            <div className="profile-field">
              <span>Full Name</span>
              <strong>{employee.name}</strong>
            </div>

            <div className="profile-field">
              <span>Employee ID</span>
              <strong>{employee.employeeId}</strong>
            </div>

            <div className="profile-field">
              <span>Email</span>
              <strong>{employee.email}</strong>
            </div>

            <div className="profile-field">
              <span>Phone</span>
              <strong>{employee.phone}</strong>
            </div>

            <div className="profile-field">
              <span>Department</span>
              <strong>{employee.department}</strong>
            </div>

            <div className="profile-field">
              <span>Designation</span>
              <strong>{employee.designation}</strong>
            </div>

            <div className="profile-field">
              <span>Manager</span>
              <strong>{employee.manager}</strong>
            </div>

            <div className="profile-field">
              <span>Joining Date</span>
              <strong>{employee.joiningDate}</strong>
            </div>

            <div className="profile-field">
              <span>Location</span>
              <strong>{employee.location}</strong>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Profile;