from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from madr import security
from madr.database import get_session
from madr.models import Book, User
from madr.schemas import (
    BookList,
    BookPublic,
    BookSchema,
    BookUpdateSchema,
    MessageSchema,
)

router = APIRouter(prefix='/books', tags=['Books'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(security.get_current_user)]


@router.post('/', response_model=BookPublic, status_code=HTTPStatus.CREATED)
async def create_book(
    session: T_Session, book: BookSchema, _: T_CurrentUser
):
    book_db = Book(**book.model_dump())

    try:
        session.add(book_db)
        await session.commit()
        await session.refresh(book_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book already exists'
        )

    return book_db


@router.delete('/{book_id}', response_model=MessageSchema)
async def delete_author(
    session: T_Session, book_id: int, _: T_CurrentUser
):
    book = await session.scalar(select(Book).where(Book.id == book_id))

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book does not exist'
        )

    await session.delete(book)
    await session.commit()

    return {'message': 'Book successfully removed'}


@router.patch('/{book_id}', response_model=BookPublic)
async def update_book(
    book: BookUpdateSchema,
    book_id: int,
    session: T_Session,
    _: T_CurrentUser,
):
    book_db = await session.scalar(select(Book).where(Book.id == book_id))

    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book does not exist'
        )

    for key, value in book.model_dump(exclude_unset=True).items():
        setattr(book_db, key, value)

    try:
        session.add(book_db)
        await session.commit()
        await session.refresh(book_db)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Book already exists'
        )

    return book_db


@router.get('/{book_id}', response_model=BookPublic)
async def get_book(book_id: int, session: T_Session):
    book_db = await session.scalar(select(Book).where(Book.id == book_id))

    if not book_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book does not exist'
        )

    return book_db


@router.get('/', response_model=BookList)
async def get_books(
    session: T_Session,
    title: str | None = None,
    year: int | None = None,
    offset: int | None = 0,
    limit: int | None = 20,
):
    query = select(Book)
    if title:
        query = query.filter(Book.title.contains(title))

    if year:
        query = query.filter(Book.year == year)

    books = await session.scalars(query.offset(offset).limit(limit))

    return {'books': books.all()}
