from http import HTTPStatus


def test_create_account_should_create_user(client):
    response = client.post(
        '/accounts',
        json={
            'username': 'Sbroubous',
            'email': 'sbroubous@transamerica.com',
            'password': 'passwd',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'sbroubous',
        'email': 'sbroubous@transamerica.com',
    }


def test_create_user_should_not_duplicate_user(client, user):
    response = client.post(
        '/accounts',
        json={
            'username': user.username,
            'email': user.email,
            'password': user.clean_password,
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}
