import os
import pytest
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from ai_content_platform import create_app, db
from ai_content_platform.models.user import User
from ai_content_platform.models.content import Content

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'UPLOAD_FOLDER': '/tmp/test_uploads',
        'GENERATED_CONTENT_DIR': '/tmp/test_generated',
        'THUMBNAILS_DIR': '/tmp/test_thumbnails'
    })

    # Create test directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['GENERATED_CONTENT_DIR'], exist_ok=True)
    os.makedirs(app.config['THUMBNAILS_DIR'], exist_ok=True)

    return app

@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()

        # Create test user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpass')
        db.session.add(user)

        # Create test content
        content = Content(
            title='Test Content',
            content_type='photo_quote',
            input_text='Test quote',
            user_id=1
        )
        db.session.add(content)

        db.session.commit()

        yield db

        db.drop_all()


def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'AI Content Platform' in response.data


def test_register(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'newpass123',
        'confirm_password': 'newpass123'
    }, follow_redirects=True)
    assert b'Registration successful' in response.data


def test_login_logout(client, init_database):
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Successfully logged in' in response.data

    # Test logout
    response = client.get('/logout', follow_redirects=True)
    assert b'Successfully logged out' in response.data


def test_create_content(client, init_database):
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Test photo quote creation
    response = client.post('/create', data={
        'content_type': 'photo_quote',
        'title': 'Test Quote',
        'input_text': 'This is a test quote'
    }, follow_redirects=True)
    assert b'Content created successfully' in response.data


def test_view_content(client, init_database):
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Test viewing content
    response = client.get('/content/1')
    assert response.status_code == 200
    assert b'Test Content' in response.data


def test_delete_content(client, init_database):
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Test content deletion
    response = client.post('/content/1/delete', follow_redirects=True)
    assert b'Content deleted successfully' in response.data


def test_generate_prompts_api(client, init_database):
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    response = client.post('/api/generate-prompts',
                           json={'count': 3, 'theme': 'test'},
                           follow_redirects=True)
    json_data = response.get_json()
    assert json_data['success'] == True
    assert len(json_data['prompts']) == 3


def test_unauthorized_access(client):
    # Test accessing protected routes without login
    response = client.get('/dashboard', follow_redirects=True)
    assert b'Please log in to access this page' in response.data


def test_invalid_login(client, init_database):
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b'Invalid username or password' in response.data


def test_content_security(client, init_database):
    # Create second user
    with client.application.app_context():
        user2 = User(username='user2', email='user2@example.com')
        user2.set_password('pass2')
        db.session.add(user2)
        db.session.commit()

    # Login as second user
    client.post('/login', data={
        'username': 'user2',
        'password': 'pass2'
    })

    # Try to access first user's content
    response = client.get('/content/1', follow_redirects=True)
    assert b'You do not have permission to view this content' in response.data


def test_content_validation(client, init_database):
    # Login first
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })

    # Test creating content without required fields
    response = client.post('/create', data={
        'content_type': 'photo_quote',
        'title': ''  # Missing title
    }, follow_redirects=True)
    assert b'Title is required' in response.data


if __name__ == '__main__':
    pytest.main(['-v'])
