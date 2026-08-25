// const API_BASE = "http://localhost:8000";
const API_BASE = "https://pontoai-api.onrender.com";

let selectedRole = null;
let token = null;

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) throw new Error("Credenciais inválidas.");

    const data = await res.json();
    token = data.access_token;

    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("upload-section").classList.remove("hidden");
    document.getElementById("jobs-section").classList.remove("hidden");
    loadJobs();
  } catch (err) {
    document.getElementById("login-error").innerText = err.message;
  }
}

function selectRole(roleId) {
  console.log(roleId)
  selectedRole = roleId;
  document.querySelectorAll(".role-btn").forEach((btn) => {
    btn.classList.toggle("active", Number(btn.dataset.role) === roleId);
  });
}

async function uploadPdf() {
  const fileInput = document.getElementById("pdf-file");
  const statusEl = document.getElementById("upload-status");

  if (!selectedRole) {
    statusEl.innerText = "Selecione um modo (role) antes de enviar.";
    return;
  }
  if (!fileInput.files.length) {
    statusEl.innerText = "Selecione um arquivo PDF.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  formData.append("role_id", selectedRole);

  statusEl.innerText = "Enviando e processando... isso pode levar alguns minutos.";

  try {
    const res = await fetch(`${API_BASE}/jobs/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (!res.ok) throw new Error("Erro ao enviar arquivo.");

    const job = await res.json();
    statusEl.innerText = `Job #${job.id} criado com status: ${job.status}`;
    loadJobs();
  } catch (err) {
    statusEl.innerText = err.message;
  }
}

async function loadJobs() {
  const res = await fetch(`${API_BASE}/jobs/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) return;

  const jobs = await res.json();
  const tbody = document.querySelector("#jobs-table tbody");
  tbody.innerHTML = "";

  jobs.forEach((job) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${job.id}</td>
      <td>${job.role_mode}</td>
      <td>${job.original_filename || "-"}</td>
      <td>${job.status}</td>
      <td>${
        job.status === "done"
          ? `<button onclick="downloadResult(${job.id})">Baixar</button>`
          : "-"
      }</td>
    `;
    tbody.appendChild(tr);
  });
}

async function downloadResult(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    alert("Erro ao baixar resultado.");
    return;
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `resultado_job_${jobId}.xlsx`;
  a.click();
}
