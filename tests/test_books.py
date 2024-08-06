from http import HTTPStatus

from tests.conftest import BookFactory


def test_create_book_should_create_book(client, author, token):
    book = {'year': 2024, 'title': 'Sbroubous Book', 'author_id': author.id}
    response = client.post(
        '/books', json=book, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'year': 2024,
        'title': 'sbroubous book',
        'author_id': author.id,
    }


def test_create_book_should_return_conflict(client, book, token):
    book = {'year': 2024, 'title': book.title, 'author_id': book.author_id}
    response = client.post(
        '/books', json=book, headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already exists'}


def test_delete_book_should_delete_book(client, book, token):
    response = client.delete(
        f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Book successfully removed'}


def test_delete_book_should_return_not_found(client, token):
    response = client.delete(
        '/books/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book does not exist'}


def test_update_book_should_update_book(client, book, token):
    updated_book = {'title': 'Updated Sbroubous'}

    response = client.patch(
        f'/books/{book.id}',
        json=updated_book,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'year': book.year,
        'title': 'updated sbroubous',
        'author_id': book.author.id,
    }


def test_update_book_should_return_not_found(client, token):
    updated_book = {'title': 'Updated Sbroubous'}

    response = client.patch(
        '/books/1',
        json=updated_book,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book does not exist'}


def test_update_book_should_not_duplicate_book(
    client, book, other_book, token
):
    updated_book = {'title': book.title}

    response = client.patch(
        f'/books/{other_book.id}',
        json=updated_book,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Book already exists'}


def test_get_book_should_return_book(client, book):
    response = client.get(f'/books/{book.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': book.id,
        'year': book.year,
        'title': book.title,
        'author_id': book.author.id,
    }


def test_get_book_should_return_not_found(client):
    response = client.get('/books/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Book does not exist'}


async def test_get_books_should_return_books(client, author, session):
    books_count = 5
    session.add_all(BookFactory.create_batch(books_count, author_id=author.id))
    await session.commit()

    response = client.get('/books')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == books_count


async def test_get_books_should_return_default_limit_books(
    client, author, session
):
    books_count = 22
    default_limit = 20
    session.add_all(BookFactory.create_batch(books_count, author_id=author.id))
    await session.commit()

    response = client.get('/books')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == default_limit


async def test_get_books_should_return_filter_by_title(
    client, author, session
):
    books = BookFactory.create_batch(5, author_id=author.id)
    book = books[0]
    book.title = 'sbroubous'
    session.add_all(books)
    await session.commit()

    response = client.get(f'/books?title={book.title[:3]}')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['books'][0]['title'] == book.title


async def test_get_books_should_return_filter_by_year(
    client, author, session
):
    books = BookFactory.create_batch(5, author_id=author.id)
    book = books[0]
    book.year = 2024
    session.add_all(books)
    await session.commit()

    response = client.get(f'/books?year={book.year}')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['books'][0]['year'] == book.year


async def test_get_books_should_return_filter_by_title_year(
    client, author, session
):
    books = BookFactory.create_batch(5, author_id=author.id)
    book = books[0]
    book.title = 'sbroubous'
    book.year = 2024
    session.add_all(books)
    await session.commit()

    response = client.get(f'/books?title={book.title[:3]}&year={book.year}')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['books'][0]['title'] == book.title
    assert response.json()['books'][0]['year'] == book.year


async def test_get_books_should_return_offset_books(client, author, session):
    books_count = 10
    offset = 5
    session.add_all(BookFactory.create_batch(books_count, author_id=author.id))
    await session.commit()

    response = client.get(f'/books?offset={offset}')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == books_count - offset


async def test_get_books_should_return_limited_books(client, author, session):
    books_count = 10
    limit = 5
    session.add_all(BookFactory.create_batch(books_count, author_id=author.id))
    await session.commit()

    response = client.get(f'/books?limit={limit}')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['books']) == limit


def test_get_books_should_return_empty_books(client):
    response = client.get('/books')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'books': []}
