// app.js - Core API client and shared utilities

const API_BASE = 'http://localhost:8000';

// ─── Auth Helpers ─────────────────────────────────────────────────────────────

const Auth = {
  getToken: () => localStorage.getItem('token'),
  getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
  getRole: () => localStorage.getItem('role'),

  setSession(data) {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('user', JSON.stringify({
      id: data.user_id,
      name: data.full_name,
      role: data.role,
    }));
  },

  clearSession() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('user');
  },

  isLoggedIn: () => !!localStorage.getItem('token'),

  requireAuth(redirectTo = '/login.html') {
    if (!this.isLoggedIn()) {
      window.location.href = redirectTo;
      return false;
    }
    return true;
  },

  requireRole(roles, redirectTo = '/dashboard.html') {
    const role = this.getRole();
    if (!roles.includes(role)) {
      window.location.href = redirectTo;
      return false;
    }
    return true;
  }
};

// ─── API Client ───────────────────────────────────────────────────────────────

const API = {
  async request(method, path, body = null, auth = true) {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const token = Auth.getToken();
      if (token) headers['Authorization'] = `Bearer ${token}`;
    }

    const config = { method, headers };
    if (body) config.body = JSON.stringify(body);

    const res = await fetch(`${API_BASE}${path}`, config);

    // Handle 401 - token expired
    if (res.status === 401) {
      Auth.clearSession();
      window.location.href = '/login.html';
      return;
    }

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Something went wrong');
    }
    return data;
  },

  get: (path, auth = true) => API.request('GET', path, null, auth),
  post: (path, body, auth = true) => API.request('POST', path, body, auth),
  put: (path, body) => API.request('PUT', path, body),
  delete: (path) => API.request('DELETE', path),
};

// ─── UI Helpers ───────────────────────────────────────────────────────────────

const UI = {
  // Show alert message
  showAlert(container, message, type = 'error') {
    const icons = { error: '✕', success: '✓', warning: '⚠', info: 'ℹ' };
    const el = document.createElement('div');
    el.className = `alert alert-${type}`;
    el.innerHTML = `<span>${icons[type]}</span> ${message}`;
    container.innerHTML = '';
    container.appendChild(el);
    if (type === 'success') {
      setTimeout(() => el.remove(), 4000);
    }
  },

  // Set loading state on button
  setLoading(btn, loading) {
    if (loading) {
      btn.dataset.originalText = btn.innerHTML;
      btn.innerHTML = '<span class="spinner"></span> Loading...';
      btn.disabled = true;
    } else {
      btn.innerHTML = btn.dataset.originalText || 'Submit';
      btn.disabled = false;
    }
  },

  // Format date nicely
  formatDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  },

  // Get day and month separately for date box
  getDateParts(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return {
      day: d.getDate(),
      month: d.toLocaleDateString('en-IN', { month: 'short' }),
    };
  },

  // Format 24h time to 12h
  formatTime(timeStr) {
    const [h, m] = timeStr.split(':').map(Number);
    const ampm = h >= 12 ? 'PM' : 'AM';
    const hour = h % 12 || 12;
    return `${hour}:${String(m).padStart(2,'0')} ${ampm}`;
  },

  // Get status badge HTML
  statusBadge(status) {
    return `<span class="status-badge status-${status}">${status}</span>`;
  },

  // Open/close modal
  openModal(id) {
    document.getElementById(id).classList.add('active');
  },

  closeModal(id) {
    document.getElementById(id).classList.remove('active');
  },
};

// ─── Setup Navbar ─────────────────────────────────────────────────────────────

function setupNavbar() {
  const nav = document.getElementById('navbar');
  if (!nav) return;

  const user = Auth.getUser();
  const role = Auth.getRole();

  if (!user) {
    nav.innerHTML = `
      <a href="/login.html" class="nav-brand">
        <div class="brand-icon">✚</div>
        MediBook
      </a>
      <div class="nav-user">
        <a href="/login.html" class="btn btn-outline btn-sm">Login</a>
        <a href="/register.html" class="btn btn-primary btn-sm">Register</a>
      </div>`;
    return;
  }

  let links = '';
  if (role === 'patient') {
    links = `
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/doctor_list.html">Find Doctors</a></li>
      <li><a href="/appointments.html">My Appointments</a></li>`;
  } else if (role === 'doctor') {
    links = `
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/appointments.html">Appointments</a></li>`;
  } else if (role === 'admin') {
    links = `
      <li><a href="/dashboard.html">Dashboard</a></li>
      <li><a href="/doctor_list.html">Doctors</a></li>
      <li><a href="/appointments.html">Appointments</a></li>
      <li><a href="/admin.html">Users</a></li>`;
  }

  nav.innerHTML = `
    <a href="/dashboard.html" class="nav-brand">
      <div class="brand-icon">✚</div>
      MediBook
    </a>
    <ul class="nav-links">${links}</ul>
    <div class="nav-user">
      <span class="user-name">${user.name}</span>
      <span class="role-badge ${role}">${role}</span>
      <button class="btn btn-outline btn-sm" onclick="logout()">Logout</button>
    </div>`;

  // Highlight active link
  const path = window.location.pathname.split('/').pop();
  nav.querySelectorAll('.nav-links a').forEach(a => {
    if (a.getAttribute('href') === `/${path}`) a.classList.add('active');
  });
}

function logout() {
  Auth.clearSession();
  window.location.href = '/login.html';
}

// Run navbar setup on every page
document.addEventListener('DOMContentLoaded', setupNavbar);
