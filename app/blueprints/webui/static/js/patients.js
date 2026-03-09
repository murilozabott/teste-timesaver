// Gerenciamento de pacientes — acesso restrito a administradores
import { getToken, getRole, api, showAlert, confirm } from './app.js';

// Redireciona usuário não autenticado
if (!getToken() || getRole() !== 'admin') window.location.href = '/appointments';

// Carregamento da tabela
async function loadPatients() {
  const tbody = document.getElementById('patients-tbody');
  try {
    const { data: patients } = await api.get('/patients');
    if (!patients.length) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum paciente encontrado.</td></tr>';
      return;
    }
    tbody.innerHTML = patients.map(p => `
      <tr>
        <td>${p.id}</td>
        <td>${p.name}</td>
        <td>${p.email}</td>
        <td>${p.birth_date}</td>
        <td><button class="btn btn-sm btn-danger" data-action="delete" data-id="${p.id}">Remover</button></td>
      </tr>`).join('');
  } catch {
    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erro ao carregar pacientes.</td></tr>';
  }
}

// Delegação de eventos para botões gerados dinamicamente na tabela
document.getElementById('patients-tbody').addEventListener('click', async e => {
  const btn = e.target.closest('[data-action="delete"]');
  if (!btn) return;
  const id = btn.dataset.id;
  if (!await confirm(`Remover paciente #${id}?`)) return;
  try {
    await api.delete(`/patients/${id}`);
    showAlert('Paciente removido com sucesso.', 'success');
    loadPatients();
  } catch (err) {
    showAlert(err.response?.data?.message || 'Erro ao remover paciente.');
  }
});

// Modal de cadastro
const addModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('addPatientModal'));

document.getElementById('btn-add-patient').addEventListener('click', () => {
  document.getElementById('add-patient-form').reset();
  document.getElementById('modal-alert').innerHTML = '';
  addModal.show();
});

document.getElementById('btn-save-patient').addEventListener('click', async () => {
  try {
    await api.post('/patients', {
      name:       document.getElementById('p-name').value,
      email:      document.getElementById('p-email').value,
      birth_date: document.getElementById('p-birth').value,
    });
    addModal.hide();
    showAlert('Paciente cadastrado com sucesso.', 'success');
    loadPatients();
  } catch (err) {
    document.getElementById('modal-alert').innerHTML =
      `<div class="alert alert-danger">${err.response?.data?.message || 'Erro ao salvar.'}</div>`;
  }
});

await loadPatients();
