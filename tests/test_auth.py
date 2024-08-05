from http import HTTPStatus

from freezegun import freeze_time


def test_login_token_should_return_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data.get('access_token')
    assert response_data['token_type'] == 'Bearer'


def test_login_token_should_return_bad_request(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'wrong_password'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_refresh_token_should_return_new_token(client, token):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    new_token = response.json()
    assert 'access_token' in new_token
    assert new_token['token_type'] == 'Bearer'


def test_get_current_user_should_return_unauthorized(client):
    response = client.post(
        '/auth/refresh_token', headers={'Authorization': 'Bearer wrong_token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_user_invalid_username_should_return_unauthorized(
    client, invalid_token
):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {invalid_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_current_no_valid_field_should_return_unauthorized(
    client, no_valid_field_token
):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {no_valid_field_token}'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_should_not_decode_expired_token(client, user):
    with freeze_time('2023-01-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-01-01 14:00:00'):
        response = client.post(
            '/auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
