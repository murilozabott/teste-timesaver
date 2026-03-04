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

## API REST

Base URL: `/api/v1`

### Doctors

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/doctors` | Lista todos os médicos |
| POST | `/doctors` | Cadastra novo médico |
| GET | `/doctors/<crm>` | Busca médico pelo CRM |
| DELETE | `/doctors/<crm>` | Remove médico pelo CRM |

**POST /doctors** - Body:
```json
{
  "name": "Dr. João Silva",
  "specialty": "Cardiologia",
  "crm": "12345-SP"
}
```

### Patients

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/patients` | Lista todos os pacientes |
| POST | `/patients` | Cadastra novo paciente |
| GET | `/patients/<id>` | Busca paciente pelo ID |
| DELETE | `/patients/<id>` | Remove paciente pelo ID |

**POST /patients** - Body:
```json
{
  "name": "Maria Santos",
  "email": "maria@email.com",
  "birth_date": "1990-05-15"
}
```

### Erros

| Código | Descrição |
|--------|-----------|
| 400 | Erro de validação (campos obrigatórios, formato inválido) |
| 404 | Recurso não encontrado |
| 409 | Conflito de integridade (ex: CRM duplicado) |
| 500 | Erro interno do servidor |