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
from madr.models import Author, Book, User, table_registry


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@email.com')
    password = factory.LazyAttribute(
        lambda obj: security.get_password_hash(f'{obj.username}-passwd')
    )


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f'author{n}')


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    year = factory.Sequence(lambda n: 1900 + n)
    title = factory.Sequence(lambda n: f'title{n}')
    author_id = factory.Sequence(lambda n: n)


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
async def author(session: AsyncSession):
    author = AuthorFactory()
    session.add(author)
    await session.commit()
    await session.refresh(author)

    return author


@pytest.fixture
async def book(session: AsyncSession, author):
    book = BookFactory(author_id=author.id)
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book


@pytest.fixture
async def other_book(session: AsyncSession, author):
    book = BookFactory(author_id=author.id)
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return book


@pytest.fixture
async def other_author(session: AsyncSession):
    author = AuthorFactory()
    session.add(author)
    await session.commit()
    await session.refresh(author)

    return author


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
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def invalid_token():
    data = {'sub': 'invalid_username@email.com'}
    return security.create_access_token(data)


@pytest.fixture
def no_valid_field_token():
    data = {'iss': 'invalid_username@email.com'}
    return security.create_access_token(data)
