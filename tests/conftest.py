import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from testcontainers.postgres import PostgresContainer
from fastapi.testclient import TestClient

from src.database.models import Base
from src.database.config import get_db
from src.carrito.api import app


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        image="postgres:16-alpine",
        username="test_user",
        password="test_pass",
        dbname="test_db",
    ) as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    url = postgres_container.get_connection_url()
    engine = create_engine(url, echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine) -> Session:
    connection = db_engine.connect()
    transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
    )
    session = TestingSessionLocal()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction_obj):
        if transaction_obj.nested and not transaction_obj._parent.nested:
            session.begin_nested()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def api_client(db_session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()