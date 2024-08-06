from http import HTTPStatus

from tests.conftest import AuthorFactory


def test_create_author_should_return_create_author(client, token):
    author_data = {'name': 'Machado de Assis'}
    response = client.post(
        '/authors',
        json=author_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'name': 'machado de assis', 'id': 1}


def test_create_author_should_not_duplicate_author(client, author, token):
    author_data = {'name': author.name}
    response = client.post(
        '/authors',
        json=author_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author already exists'}


def test_delete_author_should_delete_author(client, author, token):
    response = client.delete(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Author successfully removed'}


def test_delete_author_should_return_not_found(client, token):
    response = client.delete(
        '/authors/100', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author does not exist'}


def test_update_author_should_update_author(client, author, token):
    update_data = {'name': 'updated name'}
    response = client.patch(
        f'/authors/{author.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'name': 'updated name', 'id': 1}


def test_update_author_should_return_not_found(client, token):
    update_data = {'name': 'updated name'}
    response = client.patch(
        '/authors/100',
        json=update_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author does not exist'}


def test_update_author_should_return_conflict(
    client, author, other_author, token
):
    update_data = {'name': author.name}
    response = client.patch(
        f'/authors/{other_author.id}',
        json=update_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Author already exists'}


def test_get_author_should_return_author(client, author):
    response = client.get(f'/authors/{author.id}')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'id': author.id, 'name': author.name}


def test_get_author_should_return_not_found(client):
    response = client.get('/authors/1')

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Author does not exist'}


async def test_get_authors_should_return_authors(client, session):
    authors_count = 5
    session.add_all(AuthorFactory.create_batch(authors_count))
    await session.commit()

    response = client.get('/authors')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['authors']) == authors_count


async def test_get_authors_should_return_default_limit_authors(
    client, session
):
    authors_count = 22
    default_limit = 20
    session.add_all(AuthorFactory.create_batch(authors_count))
    await session.commit()

    response = client.get('/authors')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['authors']) == default_limit


async def test_get_authors_should_return_filter_by_name(client, session):
    authors = AuthorFactory.create_batch(5)
    author = authors[0]
    author.name = 'sbroubous'
    session.add_all(authors)
    await session.commit()

    response = client.get(f'/authors?name={author.name[:3]}')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['authors'][0]['name'] == author.name


async def test_get_authors_should_return_offset_authors(client, session):
    authors_count = 10
    offset = 5
    session.add_all(AuthorFactory.create_batch(authors_count))
    await session.commit()

    response = client.get(f'/authors?offset={offset}')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['authors']) == authors_count - offset


async def test_get_authors_should_return_limited_authors(client, session):
    authors_count = 10
    limit = 5
    session.add_all(AuthorFactory.create_batch(authors_count))
    await session.commit()

    response = client.get(f'/authors?limit={limit}')

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['authors']) == limit


def test_get_authors_should_return_empty_authors(client):
    response = client.get('/authors')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'authors': []}
