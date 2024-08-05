from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr import security
from madr.database import get_session
from madr.models import User
from madr.schemas import UserPublic, UserSchema

router = APIRouter(prefix='/accounts', tags=['Accounts'])

T_Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/', response_model=UserPublic, status_code=HTTPStatus.CREATED)
async def create_account(session: T_Session, user: UserSchema):
    user_db = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if user_db:
        field = 'Username' if user_db.username == user.username else 'Email'
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'{field} already exists',
        )

    user_db = User(
        username=user.username,
        email=user.email,
        password=security.get_password_hash(user.password),
    )

    session.add(user_db)
    await session.commit()
    await session.refresh(user_db)

    return user_db
