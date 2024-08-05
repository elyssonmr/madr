from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from madr import security
from madr.database import get_session
from madr.models import User
from madr.schemas import Token

router = APIRouter(prefix='/auth', tags=['Authorization'])


T_FormData = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(security.get_current_user)]


@router.post('/token', response_model=Token)
async def login_for_token(session: T_Session, form_data: T_FormData):
    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user or not security.verify_password(
        form_data.password, user.password
    ):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    data = {'sub': user.email}
    access_token = security.create_access_token(data)

    return Token(access_token=access_token, token_type='Bearer')


@router.post('/refresh_token', response_model=Token)
def refresh_token(current_user: T_CurrentUser):
    new_access_token = security.create_access_token({
        'sub': current_user.email
    })

    return {'access_token': new_access_token, 'token_type': 'Bearer'}
