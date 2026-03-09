# Avaliação técnica TimeSaver

Estrutura base para sistema de agendamento de consultas médicas desenvolvido com **Flask**.

## Pré-requisitos

Copie o arquivo de exemplo e ajuste as variáveis se necessário:

```bash
cp .env.example .env
```

O `.env` padrão já funciona sem alterações para desenvolvimento local.

## Executando o Projeto **(Ambiente de desenvolvimento)**

```bash
docker compose --profile dev up --build
```

- Debug habilitado
- Hot reload
- Código montado como volume
- `flask run` simples, ao invés de servidor WSGI como `gunicorn`
- Disponível em <http://localhost:5000/>
- Migrations executadas automaticamente antes da aplicação iniciar

## Executando os Testes

Os testes rodam em um banco separado (`healthcare_test`) criado automaticamente pelo script `docker/init-test-db.sh`.

```bash
docker compose --profile test run --rm test
```

- Cada teste roda em uma transação revertida ao final — sem poluição entre testes
- O banco de testes é migrado automaticamente antes de rodar o pytest
- Saída detalhada com `pytest -vv --tb=long`

## Frontend Web

A aplicação inclui uma interface web acessível em <http://localhost:5000/>.

### Páginas

| Rota | Descrição | Acesso |
|------|-----------|--------|
| `/login` | Login e cadastro de usuários | Público |
| `/appointments` | Lista e gerenciamento de agendamentos | Autenticado |
| `/doctors` | Lista e gerenciamento de médicos | Admin |
| `/patients` | Lista e gerenciamento de pacientes | Admin |

### Autenticação no Frontend

- O token JWT é armazenado no `localStorage` após o login
- A navbar exibe links e nome do usuário conforme o papel (role)
- Links de administração (`/doctors`, `/patients`) ficam ocultos para usuários `employee`
- Sessões expiradas redirecionam automaticamente para `/login`

---

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

### Appointments

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/appointments` | Lista todas as consultas |
| POST | `/appointments` | Agenda nova consulta |
| GET | `/appointments/<id>` | Busca consulta pelo ID |
| PUT | `/appointments/<id>` | Atualiza consulta pelo ID |
| DELETE | `/appointments/<id>` | Remove consulta pelo ID |

**POST /appointments** - Body:
```json
{
  "doctor_id": 1,
  "patient_id": 1,
  "scheduled_at": "2024-01-15T10:00:00",
  "notes": "Consulta de rotina"
}
```

**PUT /appointments/<id>** - Body (todos os campos são opcionais):
```json
{
  "doctor_id": 2,
  "patient_id": 1,
  "scheduled_at": "2024-01-15T11:00:00",
  "status": "completed",
  "notes": "Atualização de observações"
}
```

**Regras de negócio:**
- Um médico não pode ter duas consultas no mesmo horário
- Um paciente não pode ter duas consultas no mesmo horário
- Consultas canceladas não são consideradas para validação de conflito

### Auth

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/auth/register` | Registra novo usuário |
| POST | `/auth/login` | Realiza login e retorna token JWT |

**POST /auth/register** - Body:
```json
{
  "username": "joao_silva",
  "password": "senha_segura_123",
  "role": "employee"
}
```

**Resposta** (201 Created):
```json
{
  "id": 1,
  "username": "joao_silva",
  "role": "employee"
}
```

**POST /auth/login** - Body:
```json
{
  "username": "joao_silva",
  "password": "senha_segura_123"
}
```

**Resposta** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Autenticação:**
- Utilize o token retornado no header `Authorization` com o prefixo `Bearer `:
```bash
curl -H "Authorization: Bearer {access_token}" http://localhost:5000/api/v1/doctors
```

**Controle de Acesso por Função (Role):**

Alguns endpoints exigem funções específicas (definidas pelo decorator `@require_role`):

| Role | Nível | Descrição |
|------|-------|-----------|
| `employee` | 1 | Usuário padrão com acesso básico |
| `admin` | 2 | Administrador com acesso total |

Ao tentar acessar um endpoint que requer role superior à do usuário, a API retorna `403 Forbidden`.

### Erros

| Código | Descrição |
|--------|-----------|
| 400 | Erro de validação (campos obrigatórios, formato inválido) |
| 404 | Recurso não encontrado |
| 409 | Conflito de integridade (ex: CRM duplicado, double booking) |
| 500 | Erro interno do servidor |