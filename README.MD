# Avaliação técnica TimeSaver

Estrutura base para sistema de agendamento de consultas médicas desenvolvido com **Flask**.

## Executando o Projeto **(Ambiente de desenvolvimento)**

```bash
docker compose up --build
```

- Debug habilitado
- Hot reload
- Código montado como volume
- `flask run` simples, ao invés de servidor WSGI como `gunicorn`
- Disponível em <http://localhost:5000/>
- Migrations executadas automaticamente antes da aplicação iniciar

## Modelos

### Doctor (Médico)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | String(255) | Nome completo |
| specialty | String(100) | Especialidade médica |
| crm | String(20) | Registro profissional (único) |

### Patient (Paciente)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | String(255) | Nome completo |
| email | String(255) | Email de contato |
| birth_date | Date | Data de nascimento |

### Appointment (Consulta)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| doctor_id | FK | Referência ao médico |
| patient_id | FK | Referência ao paciente |
| scheduled_at | DateTime | Data/hora agendada |
| status | Enum | SCHEDULED, CANCELED, COMPLETED |
| notes | Text | Observações (opcional) |