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