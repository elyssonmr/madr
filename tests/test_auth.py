from http import HTTPStatus


def test_login_token_should_return_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    assert response.status_code == HTTPStatus.OK
    response_data = response.json()
    assert response_data.get('access_token')
    assert response_data['token_type'] == 'Bearer'
