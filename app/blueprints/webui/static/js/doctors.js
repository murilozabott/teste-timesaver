// Gerenciamento da lista de médicos
// Usuários não autenticados podem visualizar a lista, mas não adicionar ou remover
import { getToken, getRole, api, showAlert, confirm } from './app.js';

const isAdmin = !!(getToken() && getRole() === 'admin');
const colspan = isAdmin ? 4 : 3;

// Oculta controles de edição para usuários sem permissão de admin
if (!isAdmin) {
  document.getElementById('btn-add-doctor').classList.add('d-none');
  document.getElementById('actions-header').classList.add('d-none');
}

// Carregamento da tabela
async function loadDoctors() {
  const tbody = document.getElementById('doctors-tbody');
  try {
    const { data: doctors } = await api.get('/doctors');
    if (!doctors.length) {
      tbody.innerHTML = `<tr><td colspan="${colspan}" class="text-center text-muted">Nenhum médico encontrado.</td></tr>`;
      return;
    }
    tbody.innerHTML = doctors.map(d => `
      <tr>
        <td>${d.crm}</td>
        <td>${d.name}</td>
        <td>${d.specialty}</td>
        ${isAdmin ? `<td><button class="btn btn-sm btn-danger" data-action="delete" data-crm="${d.crm}">Remover</button></td>` : ''}
      </tr>`).join('');
  } catch {
    tbody.innerHTML = `<tr><td colspan="${colspan}" class="text-center text-danger">Erro ao carregar médicos.</td></tr>`;
  }
}

// Delegação de eventos para botões gerados dinamicamente na tabela
document.getElementById('doctors-tbody').addEventListener('click', async e => {
  const btn = e.target.closest('[data-action="delete"]');
  if (!btn) return;
  const crm = btn.dataset.crm;
  if (!await confirm(`Remover médico CRM ${crm}?`)) return;
  try {
    await api.delete(`/doctors/${crm}`);
    showAlert('Médico removido com sucesso.', 'success');
    loadDoctors();
  } catch (err) {
    showAlert(err.response?.data?.message || 'Erro ao remover médico.');
  }
});

// Modal de cadastro
const addModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('addDoctorModal'));

document.getElementById('btn-add-doctor').addEventListener('click', () => {
  document.getElementById('add-doctor-form').reset();
  document.getElementById('modal-alert').innerHTML = '';
  addModal.show();
});

document.getElementById('btn-save-doctor').addEventListener('click', async () => {
  try {
    await api.post('/doctors', {
      name:      document.getElementById('d-name').value,
      specialty: document.getElementById('d-specialty').value,
      crm:       document.getElementById('d-crm').value,
    });
    addModal.hide();
    showAlert('Médico cadastrado com sucesso.', 'success');
    loadDoctors();
  } catch (err) {
    document.getElementById('modal-alert').innerHTML =
      `<div class="alert alert-danger">${err.response?.data?.message || 'Erro ao salvar.'}</div>`;
  }
});

await loadDoctors();
