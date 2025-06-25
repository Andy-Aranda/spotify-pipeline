import pytest
import os
import pandas as pd
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
import tempfile

@pytest.fixture
def mock_spotify_client():
    """Mock Spotify client for testing"""
    client = Mock()
    client.current_user_top_tracks.return_value = {
        'items': [
            {
                'id': 'track1',
                'name': 'Test Track 1',
                'artists': [{'name': 'Artist 1', 'id': 'artist1'}],
                'album': {
                    'name': 'Test Album',
                    'id': 'album1',
                    'release_date': '2023-01-01'
                },
                'popularity': 85,
                'external_urls': {'spotify': 'https://open.spotify.com/track/track1'}
            },
            {
                'id': 'track2',
                'name': 'Test Track 2',
                'artists': [{'name': 'Artist 2', 'id': 'artist2'}],
                'album': {
                    'name': 'Test Album 2',
                    'id': 'album2',
                    'release_date': '2023-02-01'
                },
                'popularity': 90,
                'external_urls': {'spotify': 'https://open.spotify.com/track/track2'}
            }
        ]
    }
    
    client.audio_features.return_value = [
        {
            'id': 'track1',
            'danceability': 0.8,
            'energy': 0.7,
            'valence': 0.6,
            'tempo': 120.0
        },
        {
            'id': 'track2',
            'danceability': 0.9,
            'energy': 0.8,
            'valence': 0.7,
            'tempo': 130.0
        }
    ]
    
    client.current_user.return_value = {
        'id': 'test_user',
        'display_name': 'Test User'
    }
    
    return client

@pytest.fixture
def sample_tracks_df():
    """Sample tracks DataFrame for testing"""
    return pd.DataFrame({
        'user_id': ['user1', 'user1', 'user2'],
        'track_name': ['Track A', 'Track B', 'Track C'],
        'artists': ['Artist 1', 'Artist 2', 'Artist 1'],
        'album': ['Album 1', 'Album 2', 'Album 3'],
        'release_date': ['2023-01-01', '2023-02-01', '2023-03-01'],
        'popularity': [85, 90, 75],
        'spotify_url': ['url1', 'url2', 'url3'],
        'time_range': ['medium_term', 'medium_term', 'short_term']
    })

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing"""
    env_vars = {
        'SPOTIPY_CLIENT_ID': 'test_client_id',
        'SPOTIPY_CLIENT_SECRET': 'test_client_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_password',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'test_db'
    }
    
    with patch.dict(os.environ, env_vars):
        yield env_vars

@pytest.fixture
def test_db_engine():
    """Create a test database engine using SQLite in memory"""
    engine = create_engine('sqlite:///:memory:')
    yield engine
    engine.dispose()

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        yield f.name
    os.unlink(f.name)

@pytest.fixture
def flask_app():
    """Create Flask app for testing"""
    import sys
    sys.path.append('/Users/andreaaranda/Desktop/spotify-pipeline')
    
    from run import app
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            yield client