import factory
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from madr import security
from madr.app import app
from madr.database import get_session
from madr.models import User, table_registry


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(
        lambda obj: security.get_password_hash(f'{obj.username}-passwd')
    )


@pytest.fixture(scope='session')
async def engine():
    with PostgresContainer('postgres:16-alpine', driver='psycopg') as postgres:
        engine = create_async_engine(postgres.get_connection_url())
        yield engine


@pytest.fixture
async def session(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def user(session: AsyncSession):
    password = 'passwd'
    user = UserFactory(password=security.get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
async def other_user(session: AsyncSession):
    password = 'passwd'
    user = UserFactory(password=security.get_password_hash(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password
        }
    )

    return response.json()['access_token']
