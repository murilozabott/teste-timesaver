// Gerenciamento de agendamentos — requer autenticação
import { getToken, api, showAlert, confirm } from './app.js';

// Redireciona usuário não autenticado
if (!getToken()) window.location.href = '/login';

// Cache local dos médicos e agendamentos carregados
let doctors = [];
let appts   = [];

const STATUS_BADGE = {
  scheduled: 'primary',
  completed: 'success',
  canceled:  'secondary',
};

// Carregamento de dados
async function loadDoctors() {
  const { data } = await api.get('/doctors');
  doctors = data;
  const sel = document.getElementById('appt-doctor');
  sel.innerHTML = doctors.map(d =>
    `<option value="${d.id}">${d.name} (${d.specialty})</option>`).join('');
}

async function loadAppointments() {
  const tbody = document.getElementById('appts-tbody');
  try {
    const { data } = await api.get('/appointments');
    appts = data;
    if (!appts.length) {
      tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Nenhum agendamento encontrado.</td></tr>';
      return;
    }
    tbody.innerHTML = appts.map(a => {
      const doc     = doctors.find(d => d.id === a.doctor_id);
      const docName = doc ? doc.name : `Médico #${a.doctor_id}`;
      const dt      = new Date(a.scheduled_at).toLocaleString('pt-BR');
      const badge   = STATUS_BADGE[a.status] || 'secondary';
      return `
        <tr>
          <td>${a.id}</td>
          <td>${docName}</td>
          <td>Paciente #${a.patient_id}</td>
          <td>${dt}</td>
          <td><span class="badge bg-${badge}">${a.status}</span></td>
          <td>${a.notes || '—'}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary me-1" data-action="edit" data-id="${a.id}">Editar</button>
            <button class="btn btn-sm btn-danger" data-action="delete" data-id="${a.id}">Remover</button>
          </td>
        </tr>`;
    }).join('');
  } catch {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Erro ao carregar agendamentos.</td></tr>';
  }
}

// Modal de agendamento
const apptModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('apptModal'));

document.getElementById('btn-add-appt').addEventListener('click', () => {
  document.getElementById('appt-form').reset();
  document.getElementById('appt-id').value = '';
  document.getElementById('appt-modal-title').textContent = 'Novo Agendamento';
  document.getElementById('status-field').classList.add('d-none');
  document.getElementById('modal-alert').innerHTML = '';
  apptModal.show();
});

function openEdit(a) {
  document.getElementById('appt-id').value = a.id;
  document.getElementById('appt-modal-title').textContent = `Editar Agendamento #${a.id}`;
  document.getElementById('appt-doctor').value  = a.doctor_id;
  document.getElementById('appt-patient').value = a.patient_id;
  // datetime-local requer formato YYYY-MM-DDTHH:MM
  document.getElementById('appt-datetime').value = a.scheduled_at.slice(0, 16);
  document.getElementById('appt-status').value   = a.status;
  document.getElementById('appt-notes').value    = a.notes || '';
  document.getElementById('status-field').classList.remove('d-none');
  document.getElementById('modal-alert').innerHTML = '';
  apptModal.show();
}

document.getElementById('btn-save-appt').addEventListener('click', async () => {
  const id = document.getElementById('appt-id').value;
  const payload = {
    doctor_id:    parseInt(document.getElementById('appt-doctor').value),
    patient_id:   parseInt(document.getElementById('appt-patient').value),
    scheduled_at: document.getElementById('appt-datetime').value + ':00',
    notes:        document.getElementById('appt-notes').value || null,
  };
  if (id) payload.status = document.getElementById('appt-status').value;

  try {
    await (id ? api.put(`/appointments/${id}`, payload) : api.post('/appointments', payload));
    apptModal.hide();
    showAlert(id ? 'Agendamento atualizado.' : 'Agendamento criado.', 'success');
    loadAppointments();
  } catch (err) {
    document.getElementById('modal-alert').innerHTML =
      `<div class="alert alert-danger">${err.response?.data?.message || 'Erro ao salvar.'}</div>`;
  }
});

// Delegação de eventos para ações na tabela (editar e remover)
document.getElementById('appts-tbody').addEventListener('click', async e => {
  const btn = e.target.closest('[data-action]');
  if (!btn) return;
  const { action, id } = btn.dataset;

  if (action === 'edit') {
    const appt = appts.find(a => a.id === parseInt(id));
    if (appt) openEdit(appt);
  } else if (action === 'delete') {
    if (!await confirm(`Remover agendamento #${id}?`)) return;
    try {
      await api.delete(`/appointments/${id}`);
      showAlert('Agendamento removido com sucesso.', 'success');
      loadAppointments();
    } catch (err) {
      showAlert(err.response?.data?.message || 'Erro ao remover agendamento.');
    }
  }
});

await loadDoctors();
await loadAppointments();