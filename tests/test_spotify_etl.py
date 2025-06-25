import pytest
import pandas as pd
from unittest.mock import Mock, patch, mock_open
import os
import sys

sys.path.append('/Users/andreaaranda/Desktop/spotify-pipeline')
from scripts.spotify_etl import connection_api, get_top_tracks, get_audio_features

class TestSpotifyETL:
    
    @patch('scripts.spotify_etl.SpotifyOAuth')
    @patch('scripts.spotify_etl.spotipy.Spotify')
    @patch('scripts.spotify_etl.os.getenv')
    def test_connection_api(self, mock_getenv, mock_spotify, mock_oauth):
        """Test Spotify API connection setup"""
        # Setup mock environment variables
        mock_getenv.side_effect = lambda key: {
            'SPOTIPY_CLIENT_ID': 'test_client_id',
            'SPOTIPY_CLIENT_SECRET': 'test_secret',
            'SPOTIPY_REDIRECT_URI': 'test_uri'
        }.get(key)
        
        scope = "user-top-read"
        result = connection_api(scope)
        
        # Verify SpotifyOAuth was called with correct parameters
        mock_oauth.assert_called_once_with(
            scope=scope,
            client_id='test_client_id',
            client_secret='test_secret',
            redirect_uri='test_uri'
        )
        
        # Verify Spotify client was created
        mock_spotify.assert_called_once()
        assert result == mock_spotify.return_value
    
    @patch('scripts.spotify_etl.connection_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_top_tracks_success(self, mock_to_csv, mock_connection):
        """Test successful retrieval of top tracks"""
        # Setup mock Spotify client
        mock_sp = Mock()
        mock_connection.return_value = mock_sp
        
        # Mock API response
        mock_sp.current_user_top_tracks.return_value = {
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
        
        df, track_ids = get_top_tracks(50, 0, "medium_term")
        
        # Verify API call
        mock_sp.current_user_top_tracks.assert_called_once_with(50, 0, "medium_term")
        
        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == [
            'track_id', 'track_name', 'artists', 'artist_ids', 
            'album', 'album_id', 'release_date', 'popularity', 'spotify_url'
        ]
        
        # Verify data content
        assert df.iloc[0]['track_name'] == 'Test Track 1'
        assert df.iloc[0]['artists'] == 'Artist 1'
        assert df.iloc[0]['popularity'] == 85
        assert df.iloc[1]['track_name'] == 'Test Track 2'
        assert df.iloc[1]['artists'] == 'Artist 2'
        assert df.iloc[1]['popularity'] == 90
        
        # Verify track IDs
        assert track_ids == ['track1', 'track2']
        
        # Verify CSV was saved
        mock_to_csv.assert_called_once()
    
    @patch('scripts.spotify_etl.connection_api')
    def test_get_top_tracks_empty_response(self, mock_connection):
        """Test handling of empty API response"""
        mock_sp = Mock()
        mock_connection.return_value = mock_sp
        mock_sp.current_user_top_tracks.return_value = {'items': []}
        
        with patch('pandas.DataFrame.to_csv'):
            df, track_ids = get_top_tracks(50, 0, "medium_term")
        
        assert len(df) == 0
        assert track_ids == []
    
    @patch('scripts.spotify_etl.connection_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_audio_features_success(self, mock_to_csv, mock_connection):
        """Test successful retrieval of audio features"""
        mock_sp = Mock()
        mock_connection.return_value = mock_sp
        
        # Mock API response
        mock_sp.audio_features.return_value = [
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
        
        track_ids = ['track1', 'track2']
        df_features = get_audio_features(track_ids)
        
        # Verify API call
        mock_sp.audio_features.assert_called_once_with(track_ids)
        
        # Verify DataFrame
        assert isinstance(df_features, pd.DataFrame)
        assert len(df_features) == 2
        assert 'danceability' in df_features.columns
        assert 'energy' in df_features.columns
        assert 'valence' in df_features.columns
        assert 'tempo' in df_features.columns
        
        # Verify CSV was saved
        mock_to_csv.assert_called_once_with('data/audio_features.csv', index=False)
    
    @patch('scripts.spotify_etl.connection_api')
    @patch('pandas.DataFrame.to_csv')
    def test_get_audio_features_batch_processing(self, mock_to_csv, mock_connection):
        """Test audio features batch processing for large datasets"""
        mock_sp = Mock()
        mock_connection.return_value = mock_sp
        
        # Create 75 track IDs to test batching (should be processed in 2 batches of 50 and 25)
        track_ids = [f'track{i}' for i in range(75)]
        
        # Mock API responses for batches
        batch1_response = [{'id': f'track{i}', 'danceability': 0.8} for i in range(50)]
        batch2_response = [{'id': f'track{i}', 'danceability': 0.8} for i in range(50, 75)]
        
        mock_sp.audio_features.side_effect = [batch1_response, batch2_response]
        
        df_features = get_audio_features(track_ids)
        
        # Verify API was called twice (for batching)
        assert mock_sp.audio_features.call_count == 2
        
        # Verify DataFrame has all tracks
        assert len(df_features) == 75
    
    @patch('scripts.spotify_etl.connection_api')
    def test_get_audio_features_empty_list(self, mock_connection):
        """Test audio features with empty track list"""
        mock_sp = Mock()
        mock_connection.return_value = mock_sp
        mock_sp.audio_features.return_value = []
        
        with patch('pandas.DataFrame.to_csv'):
            df_features = get_audio_features([])
        
        assert len(df_features) == 0
    
    def test_connection_api_with_different_scopes(self):
        """Test connection API with different scopes"""
        # Test different scopes
        scopes = [
            "user-top-read",
            "user-read-recently-played",
            "user-top-read user-read-recently-played"
        ]
        
        with patch('scripts.spotify_etl.SpotifyOAuth') as mock_oauth:
            with patch('scripts.spotify_etl.spotipy.Spotify') as mock_spotify:
                with patch('scripts.spotify_etl.os.getenv') as mock_getenv:
                    mock_getenv.side_effect = lambda key: {
                        'SPOTIPY_CLIENT_ID': 'test_client_id',
                        'SPOTIPY_CLIENT_SECRET': 'test_secret',
                        'SPOTIPY_REDIRECT_URI': 'test_uri'
                    }.get(key)
                    
                    for scope in scopes:
                        result = connection_api(scope)
                        # Verify that the function works with different scopes
                        assert result == mock_spotify.return_value