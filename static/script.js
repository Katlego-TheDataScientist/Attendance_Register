const BASE_URL = ''; // Leave empty if running on same host

function registerStudent() {
  const data = {
    first_name: document.getElementById("first_name").value,
    last_name: document.getElementById("last_name").value,
    parent_email: document.getElementById("parent_email").value
  };

  fetch(`${BASE_URL}/students`, {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(data => alert("Student registered:\n" + JSON.stringify(data)));
}

function createSession() {
  const data = {
    class_name: document.getElementById("class_name").value
  };

  fetch(`${BASE_URL}/sessions`, {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(data => alert("Session created:\n" + JSON.stringify(data)));
}

function markAttendance() {
  const data = {
    student_id: parseInt(document.getElementById("student_id_attend").value),
    session_id: parseInt(document.getElementById("session_id_attend").value),
    attended: document.getElementById("attended").value === "true"
  };

  fetch(`${BASE_URL}/attendance`, {
    method: "POST",
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(res => res.json())
    .then(data => alert("Attendance marked:\n" + JSON.stringify(data)));
}

function getReport() {
  const id = document.getElementById("student_id_report").value;

  fetch(`${BASE_URL}/report/${id}`)
    .then(res => res.json())
    .then(data => {
      document.getElementById("report_output").textContent = JSON.stringify(data, null, 2);
    });
}

