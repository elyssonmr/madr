import pytest
from sqlalchemy import select

from madr.models import User


@pytest.mark.asyncio
async def test_create_user(session):
    new_user = User(username='Alice', password='secret', email='test@test.com')
    session.add(new_user)
    await session.commit()

    user = await session.scalar(select(User).where(User.username == 'Alice'))

    assert user.username == new_user.username
