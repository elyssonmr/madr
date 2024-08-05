from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr import security
from madr.database import get_session
from madr.models import User
from madr.schemas import MessageSchema, UserPublic, UserSchema

router = APIRouter(prefix='/accounts', tags=['Accounts'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(security.get_current_user)]


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


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    session: T_Session,
    user: UserSchema,
    user_id: int,
    current_user: T_CurrentUser
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission'
        )

    current_user.username = user.username
    current_user.email = user.email
    current_user.password = security.get_password_hash(user.password)

    try:
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Resource already exists'
        )

    return current_user


@router.delete('/{user_id}', response_model=MessageSchema)
async def delete_user(
    user_id: int, session: T_Session, current_user: T_CurrentUser
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not enough permission'
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User successfully removed'}
