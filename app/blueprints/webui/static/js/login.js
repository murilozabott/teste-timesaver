// Autenticação: login e cadastro de usuários
import { getToken, API, showAlert } from './app.js';

// Redireciona para agendamentos se o usuário já estiver autenticado
if (getToken()) window.location.href = '/appointments';

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const jsonPayload = atob(base64Url);
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
}

// Formulário de login
document.getElementById('login-form').addEventListener('submit', async e => {
    e.preventDefault();
    try {
      const { data } = await axios.post(API + '/auth/login', {
        username: document.getElementById('login-username').value,
        password: document.getElementById('login-password').value,
      });
      const payload = parseJwt(data.access_token);
      localStorage.setItem('token',    data.access_token);
      localStorage.setItem('role',     payload?.role     || '');
      localStorage.setItem('username', payload?.username || '');
      window.location.href = '/appointments';
    } catch (err) {
      showAlert(err.response?.data?.message || 'Falha ao fazer login.');
    }
  });

// Formulário de cadastro
document.getElementById('register-form').addEventListener('submit', async e => {
  e.preventDefault();
  try {
    await axios.post(API + '/auth/register', {
      username: document.getElementById('reg-username').value,
      password: document.getElementById('reg-password').value,
      role:     document.getElementById('reg-role').value,
    });
    showAlert('Conta criada com sucesso! Faça login para continuar.', 'success');
    document.getElementById('register-form').reset();
    document.querySelector('[data-bs-target="#login-tab"]').click();
  } catch (err) {
    showAlert(err.response?.data?.message || 'Falha ao criar conta.');
  }
});
