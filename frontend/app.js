const API_BASE = "https://pontoai-api.onrender.com";

let selectedRole = null;
let token = null;
let selectedFile = null;

// Elementos DOM
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('pdf-file');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileRemove = document.getElementById('fileRemove');

// Controle de Navegação de Telas
function showSection(sectionId) {
  document.getElementById("landing-section").classList.add("hidden");
  document.getElementById("login-section").classList.add("hidden");
  document.getElementById("upload-section").classList.add("hidden");
  document.getElementById("jobs-section").classList.add("hidden");

  document.getElementById(sectionId).classList.remove("hidden");

  // Atualiza estados dos links de navegação
  document.getElementById("nav-about").classList.toggle("active", sectionId === "landing-section");
}

function openLogin() {
  if (token) {
    showSection("upload-section");
    document.getElementById("jobs-section").classList.remove("hidden");
  } else {
    showSection("login-section");
  }
}

function scrollToFeatures() {
  showSection("landing-section");
  document.getElementById("features").scrollIntoView({ behavior: "smooth" });
}

// Autenticação (Login)
async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const errorEl = document.getElementById("login-error");
  const alertErr = document.getElementById("login-alert-error");
  const spinner = document.getElementById("login-spinner");

  alertErr.classList.remove("show");
  errorEl.innerText = "";

  if (!email || !password) {
    errorEl.innerText = "Por favor, preencha o e-mail e a senha.";
    alertErr.classList.add("show");
    return;
  }

  spinner.classList.add("show");

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) throw new Error("Credenciais inválidas.");

    const data = await res.json();
    token = data.access_token;

    // Atualiza cabeçalho para usuário logado
    document.getElementById("nav-login-btn").classList.add("hidden");
    document.getElementById("nav-upload").classList.remove("hidden");
    document.getElementById("nav-jobs").classList.remove("hidden");
    document.getElementById("nav-logout").classList.remove("hidden");

    // Exibe telas do aplicativo
    showSection("upload-section");
    document.getElementById("jobs-section").classList.remove("hidden");

    loadJobs();
  } catch (err) {
    errorEl.innerText = err.message;
    alertErr.classList.add("show");
  } finally {
    spinner.classList.remove("show");
  }
}

function logout() {
  token = null;
  document.getElementById("nav-login-btn").classList.remove("hidden");
  document.getElementById("nav-upload").classList.add("hidden");
  document.getElementById("nav-jobs").classList.add("hidden");
  document.getElementById("nav-logout").classList.add("hidden");
  showSection("landing-section");
}

// Seleção de Roles / Modos
function selectRole(roleId) {
  selectedRole = roleId;
  document.querySelectorAll(".role-btn").forEach((btn) => {
    btn.classList.toggle("active", Number(btn.dataset.role) === roleId);
  });
}

// Drag and Drop e Tratamento de Arquivos
if (dropzone && fileInput) {
  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files.length) {
      fileInput.files = e.dataTransfer.files;
      handleFileSelect();
    }
  });

  fileInput.addEventListener('change', handleFileSelect);
}

function handleFileSelect() {
  const file = fileInput.files[0];
  if (!file) return;

  if (file.type !== 'application/pdf') {
    alert("Apenas arquivos PDF são permitidos.");
    resetFileInput();
    return;
  }

  selectedFile = file;
  fileName.textContent = file.name;
  fileSize.textContent = formatFileSize(file.size);
  filePreview.classList.add('show');
}

if (fileRemove) {
  fileRemove.addEventListener('click', (e) => {
    e.stopPropagation();
    resetFileInput();
  });
}

function resetFileInput() {
  fileInput.value = '';
  selectedFile = null;
  filePreview.classList.remove('show');
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Envio de PDF
async function uploadPdf() {
  const statusEl = document.getElementById("upload-status");
  const alertInfo = document.getElementById("upload-alert-info");
  const spinner = document.getElementById("upload-spinner");

  alertInfo.classList.remove("show");

  if (!selectedRole) {
    statusEl.innerText = "Selecione um modo (role) antes de enviar.";
    alertInfo.classList.add("show");
    return;
  }

  const file = selectedFile || (fileInput ? fileInput.files[0] : null);

  if (!file) {
    statusEl.innerText = "Selecione um arquivo PDF.";
    alertInfo.classList.add("show");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("role_id", selectedRole);

  statusEl.innerText = "Enviando e processando... isso pode levar alguns minutos.";
  alertInfo.classList.add("show");
  spinner.classList.add("show");

  try {
    const res = await fetch(`${API_BASE}/jobs/upload`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (!res.ok) throw new Error("Erro ao enviar arquivo.");

    const job = await res.json();
    statusEl.innerText = `Job #${job.id} criado com status: ${job.status}`;
    resetFileInput();
    loadJobs();
  } catch (err) {
    statusEl.innerText = err.message;
  } finally {
    spinner.classList.remove("show");
  }
}

// Listagem de Jobs
async function loadJobs() {
  if (!token) return;

  try {
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
        <td><strong>#${job.id}</strong></td>
        <td>Modo ${job.role_mode}</td>
        <td>${job.original_filename || "-"}</td>
        <td><span class="badge-status">${job.status}</span></td>
        <td>${
          job.status === "done"
            ? `<button onclick="downloadResult(${job.id})">Baixar resultado</button>`
            : "-"
        }</td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Erro ao carregar jobs:", err);
  }
}

// Download de Resultado
async function downloadResult(jobId) {
  try {
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
  } catch (err) {
    alert("Erro na requisição de download.");
  }
}