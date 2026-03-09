// Utilitários globais compartilhados por todas as páginas da aplicação

export const API = '/api/v1';

// Autenticação
export const getToken    = () => localStorage.getItem('token');
export const getRole     = () => localStorage.getItem('role');
export const getUsername = () => localStorage.getItem('username');

export function logout() {
  localStorage.clear();
  window.location.href = '/login';
}
window.logout = logout;

// Instância do axios configurada com interceptores de autenticação
export const api = axios.create({ baseURL: API });

// Injeta o token de autorização em todas as requisições autenticadas
api.interceptors.request.use(config => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Redireciona para login caso o servidor retorne token inválido ou expirado
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) logout();
    return Promise.reject(err);
  }
);

// Alertas de feedback ao usuário
export function showAlert(msg, type = 'danger', containerId = 'alert-container') {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.innerHTML = `
    <div class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${msg}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;
}

// Modal de confirmação
// Retorna uma Promise que resolve para true (confirmado) ou false (cancelado)
export function confirm(message) {
  return new Promise(resolve => {
    document.getElementById('confirm-message').textContent = message;
    const modalEl = document.getElementById('confirmModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

    // Substitui o botão para evitar acúmulo de event listeners entre chamadas
    const btnOk = document.getElementById('confirm-ok');
    const newBtn = btnOk.cloneNode(true);
    btnOk.replaceWith(newBtn);

    let confirmed = false;
    newBtn.addEventListener('click', () => { confirmed = true; modal.hide(); });
    modalEl.addEventListener('hidden.bs.modal', () => resolve(confirmed), { once: true });
    modal.show();
  });
}

// Navbar: exibe links conforme estado de autenticação
function initNav() {
  const authenticated = !!getToken();

  document.getElementById('nav-links').classList.toggle('d-none', !authenticated);
  document.getElementById('nav-user').classList.toggle('d-none', !authenticated);
  document.getElementById('nav-logout').classList.toggle('d-none', !authenticated);
  document.getElementById('nav-login-link').classList.toggle('d-none', authenticated);

  if (authenticated) {
    document.getElementById('nav-username').textContent = `${getUsername()} (${getRole()})`;

    // Links de administração ficam ocultos para usuários com papel comum
    if (getRole() !== 'admin') {
      document.getElementById('nav-doctors-link')?.classList.add('d-none');
      document.getElementById('nav-patients-link')?.classList.add('d-none');
    }
  }
}

initNav();
