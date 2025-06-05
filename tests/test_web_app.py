import pytest
import os
from io import BytesIO
# Add the parent directory to sys.path to allow imports from web_app
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from web_app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    # Set UPLOAD_FOLDER and GENERATED_AUDIO_FOLDER to temporary locations for testing
    # This is important if your app writes files during tests, though these specific tests might not.
    flask_app.config['UPLOAD_FOLDER'] = 'test_uploads'
    flask_app.config['GENERATED_AUDIO_FOLDER'] = 'test_generated_audio'
    
    # Create test directories if they don't exist
    if not os.path.exists(flask_app.config['UPLOAD_FOLDER']):
        os.makedirs(flask_app.config['UPLOAD_FOLDER'])
    if not os.path.exists(flask_app.config['GENERATED_AUDIO_FOLDER']):
        os.makedirs(flask_app.config['GENERATED_AUDIO_FOLDER'])

    with flask_app.test_client() as client:
        yield client
    
    # Clean up test directories after tests (optional, depending on needs)
    # import shutil
    # shutil.rmtree(flask_app.config['UPLOAD_FOLDER'], ignore_errors=True)
    # shutil.rmtree(flask_app.config['GENERATED_AUDIO_FOLDER'], ignore_errors=True)


def test_index_page_loads(client):
    """Test that the index page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Upload new File" in response.data
    assert b"Upload and Convert" in response.data

def test_upload_unsupported_file_type(client):
    """Test uploading an unsupported file type."""
    data = {
        'file': (BytesIO(b"this is a test file content"), 'test.txt')
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data', follow_redirects=True)
    
    assert response.status_code == 200 # After following redirect to result page
    assert b"Error" in response.data # General error heading
    assert b"Unsupported file type: &#39;.txt&#39;." in response.data # Updated for HTML escaping
    assert b"Upload another file" in response.data
