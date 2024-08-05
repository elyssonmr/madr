from http import HTTPStatus

from madr.schemas import UserPublic, UserSchema


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
    user_schema = UserSchema.model_validate(user).model_dump()
    response = client.post(
        '/accounts',
        json=user_schema
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {'detail': 'Username already exists'}


def test_update_user_should_update_user(client, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    user_schema['username'] = 'updatedname'
    user_request = {
        'username': user_schema['username'],
        'email': user.email,
        'password': user.clean_password,
    }
    response = client.put(
        f'/accounts/{user.id}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_update_user_should_return_forbidden(client, other_user, token):
    user_request = {
        'username': 'updatedusername',
        'email': other_user.email,
        'password': other_user.clean_password,
    }
    response = client.put(
        f'/accounts/{other_user.id}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}


def test_update_user_should_return_conflict(client, user, other_user, token):
    user_request = {
        'username': other_user.username,
        'email': other_user.email,
        'password': other_user.clean_password,
    }
    response = client.put(
        f'/accounts/{user.id}',
        json=user_request,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Resource already exists'}


def test_delete_user_should_delete_user(client, user, token):
    response = client.delete(
        f'/accounts/{user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User successfully removed'}


def test_delete_user_should_return_forbidden(client, other_user, token):
    response = client.delete(
        f'/accounts/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not enough permission'}
