from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr import security
from madr.database import get_session
from madr.models import Author, User
from madr.schemas import AuthorList, AuthorPublic, AuthorSchema, MessageSchema

router = APIRouter(prefix='/authors', tags=['Authors'])


T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(security.get_current_user)]


@router.post('/', response_model=AuthorPublic, status_code=HTTPStatus.CREATED)
async def create_author(
    session: T_Session, author: AuthorSchema, current_user: T_CurrentUser
):
    author_db = Author(**author.model_dump())

    try:
        session.add(author_db)
        await session.commit()
        await session.refresh(author_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Author already exists'
        )

    return author_db


@router.delete('/{author_id}', response_model=MessageSchema)
async def delete_author(
    session: T_Session, author_id: int, current_user: T_CurrentUser
):
    author = await session.scalar(select(Author).where(Author.id == author_id))

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author does not exist'
        )

    await session.delete(author)
    await session.commit()

    return {'message': 'Author successfully removed'}


@router.patch('/{author_id}', response_model=AuthorPublic)
async def update_author(
    author_id: int,
    author: AuthorSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    author_db = await session.scalar(
        select(Author).where(Author.id == author_id)
    )

    if not author_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author does not exist'
        )

    author_db.name = author.name
    try:
        session.add(author_db)
        await session.commit()
        await session.refresh(author_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Author already exists'
        )

    return author_db


@router.get('/{author_id}', response_model=AuthorPublic)
async def get_author(session: T_Session, author_id: int):
    author_db = await session.scalar(
        select(Author).where(Author.id == author_id)
    )

    if not author_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author does not exist'
        )

    return author_db


@router.get('/', response_model=AuthorList)
async def get_authors(
    session: T_Session,
    name: str | None = None,
    offset: int | None = 0,
    limit: int | None = 20,
):
    query = select(Author)
    if name:
        query = query.filter(Author.name.contains(name))

    authors = await session.scalars(query.offset(offset).limit(limit))

    return {'authors': authors.all()}
