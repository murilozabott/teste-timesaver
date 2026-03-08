import pytest
from sqlalchemy.orm import scoped_session, sessionmaker

from app import create_app
from app.ext.database import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture(autouse=True)
def db_session(app):
    """
    Fornece sessão SQLAlchemy "aninhada" para testes, permitindo rollback após commit.

    PROBLEMA: Endpoints chamam session.commit() ao inserir/deletar/atualizar dados
    OBJETIVO: Banco de dados deve voltar ao estado original depois de cada teste para
    que um teste não polua o seguinte
    SOLUÇÃO: https://docs.sqlalchemy.org/en/21/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
    db.session maneja obter uma conexão, iniciar transação e fazer COMMIT ou ROLLBACK.
    Ao bindar session em uma conexão onde a transação já foi iniciada, commit/rollback
    irão operar com SAVEPOINTS. Dessa forma, para testes/endpoints, commit/rollback
    parecem funcionar normalmente, mas ainda é possível reverter as operações ao final
    """
    with app.app_context():
        connection = _db.engine.connect()
        transaction = connection.begin()
        Session = sessionmaker(
            bind=connection, join_transaction_mode="create_savepoint"
        )
        session = scoped_session(Session)
        original_session = _db.session
        _db.session = session

        try:
            yield session
        finally:
            session.remove()
            transaction.rollback()
            connection.close()
            _db.session = original_session


@pytest.fixture
def client(app, db_session):
    return app.test_client()
