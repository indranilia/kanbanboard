import pytest
from kanbanr.db import get_db

#checking if the correct menus and outputs are displayed
def test_index(client, auth):
    response = client.get('/')
    assert b"LOG IN" in response.data
    assert b"REGISTER" in response.data

    auth.login()
    response = client.get('/')
    assert b'LOG OUT' in response.data
    assert b'test title' in response.data
    assert b'not_started' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/update',
    '/delete',
))

#checking if the login path is required for task actions
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_author_required(app, client, auth):
    # change the tasks author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE tasks SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # current user can't modify other user's tasks
    assert client.post('/update').status_code == 302
    assert client.post('/delete').status_code == 302
    # current user doesn't see edit link
    assert b'href="/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/update',
    '/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 302


