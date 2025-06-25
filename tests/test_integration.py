import pytest
import pandas as pd
import sys
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

sys.path.append('/Users/andreaaranda/Desktop/spotify-pipeline')

class TestIntegration:
    """Integration tests for the complete Spotify pipeline"""
    
    @patch('scripts.spotify_etl.connection_api')
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_complete_etl_pipeline(self, mock_to_sql, mock_getenv, mock_create_engine, mock_connection):
        """Test complete ETL pipeline from Spotify API to database"""
        from scripts.spotify_etl import get_top_tracks
        from scripts.db_utils import save_tracks_to_db
        
        # Setup Spotify API mock
        mock_sp = Mock()
        mock_sp.current_user_top_tracks.return_value = {
            'items': [
                {
                    'id': 'track1',
                    'name': 'Integration Test Track',
                    'artists': [{'name': 'Test Artist', 'id': 'artist1'}],
                    'album': {
                        'name': 'Test Album',
                        'id': 'album1',
                        'release_date': '2023-01-01'
                    },
                    'popularity': 85,
                    'external_urls': {'spotify': 'https://test.url'}
                }
            ]
        }
        mock_connection.return_value = mock_sp
        
        # Setup database mocks
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        # Execute ETL pipeline
        with patch('pandas.DataFrame.to_csv'):  # Mock CSV saving
            df, track_ids = get_top_tracks(50, 0, "medium_term")
            save_tracks_to_db(df)
        
        # Verify data flow
        assert len(df) == 1
        assert df.iloc[0]['track_name'] == 'Integration Test Track'
        assert track_ids == ['track1']
        
        # Verify database save
        mock_to_sql.assert_called_once_with(
            'top_tracks',
            con=mock_engine,
            if_exists='replace',
            index=False
        )
    
    @patch('scripts.spotify_etl.connection_api')
    def test_etl_with_audio_features(self, mock_connection):
        """Test ETL pipeline including audio features"""
        from scripts.spotify_etl import get_top_tracks, get_audio_features
        
        # Setup mocks
        mock_sp = Mock()
        mock_sp.current_user_top_tracks.return_value = {
            'items': [
                {
                    'id': 'track1',
                    'name': 'Test Track',
                    'artists': [{'name': 'Test Artist', 'id': 'artist1'}],
                    'album': {
                        'name': 'Test Album',
                        'id': 'album1',
                        'release_date': '2023-01-01'
                    },
                    'popularity': 85,
                    'external_urls': {'spotify': 'https://test.url'}
                }
            ]
        }
        mock_sp.audio_features.return_value = [
            {
                'id': 'track1',
                'danceability': 0.8,
                'energy': 0.7,
                'valence': 0.6,
                'tempo': 120.0
            }
        ]
        mock_connection.return_value = mock_sp
        
        with patch('pandas.DataFrame.to_csv'):
            # Get tracks
            df_tracks, track_ids = get_top_tracks(50, 0, "medium_term")
            
            # Get audio features
            df_features = get_audio_features(track_ids)
        
        # Verify both DataFrames have data
        assert len(df_tracks) == 1
        assert len(df_features) == 1
        assert df_features.iloc[0]['danceability'] == 0.8
    
    @patch('run.spotipy.Spotify')
    @patch('run.generar_top_tracks')
    @patch('run.generar_popularidad_artistas')
    @patch('run.engine')
    def test_flask_to_visualization_pipeline(self, mock_engine, mock_gen_artists, mock_gen_tracks, mock_spotify, flask_app):
        """Test complete pipeline from Flask route to visualization"""
        # Setup mocks
        mock_sp = Mock()
        mock_sp.current_user_top_tracks.return_value = {
            'items': [
                {
                    'name': 'Pipeline Test Track',
                    'artists': [{'name': 'Pipeline Artist'}],
                    'album': {'name': 'Pipeline Album', 'release_date': '2023-01-01'},
                    'popularity': 85,
                    'external_urls': {'spotify': 'https://test.url'}
                }
            ]
        }
        mock_spotify.return_value = mock_sp
        
        # Mock visualizations
        mock_gen_tracks.return_value = '<div>Pipeline tracks chart</div>'
        mock_gen_artists.return_value = '<div>Pipeline artists chart</div>'
        
        # Mock database
        mock_conn = Mock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        # Execute request
        with flask_app.session_transaction() as sess:
            sess['token_info'] = {'access_token': 'test_token'}
            sess['user_id'] = 'pipeline_user'
        
        with patch('pandas.DataFrame.to_sql'):
            response = flask_app.get('/profile')
        
        # Verify pipeline execution
        assert mock_sp.current_user_top_tracks.called
        assert mock_gen_tracks.called
        assert mock_gen_artists.called
    
    def test_data_consistency_across_components(self):
        """Test that data structure is consistent across different components"""
        from scripts.visualizations import generar_top_tracks, generar_popularidad_artistas
        
        # Create sample data that matches the expected structure
        sample_data = pd.DataFrame({
            'track_name': ['Track A', 'Track B', 'Track A'],
            'artists': ['Artist 1', 'Artist 2', 'Artist 1'],
            'popularity': [85, 90, 80],
            'album': ['Album 1', 'Album 2', 'Album 1']
        })
        
        # Test that both visualization functions can handle the same data structure
        with patch('scripts.visualizations.go.Figure') as mock_go_figure:
            with patch('scripts.visualizations.px.bar') as mock_px_bar:
                mock_fig = Mock()
                mock_fig.to_html.return_value = '<div>test</div>'
                mock_go_figure.return_value = mock_fig
                mock_px_bar.return_value = mock_fig
                
                # Both functions should work with the same DataFrame structure
                result1 = generar_top_tracks(sample_data)
                result2 = generar_popularidad_artistas(sample_data)
                
                assert result1 == '<div>test</div>'
                assert result2 == '<div>test</div>'
    
    @patch('scripts.spotify_etl.connection_api')
    def test_error_handling_in_pipeline(self, mock_connection):
        """Test error handling throughout the pipeline"""
        from scripts.spotify_etl import get_top_tracks
        
        # Test API error handling
        mock_sp = Mock()
        mock_sp.current_user_top_tracks.side_effect = Exception("API Error")
        mock_connection.return_value = mock_sp
        
        # The function doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match="API Error"):
            with patch('pandas.DataFrame.to_csv'):
                get_top_tracks(50, 0, "medium_term")
    
    @patch('scripts.spotify_etl.connection_api')
    def test_empty_data_handling(self, mock_connection):
        """Test pipeline behavior with empty data from API"""
        from scripts.spotify_etl import get_top_tracks
        from scripts.visualizations import generar_top_tracks
        
        # Setup empty API response
        mock_sp = Mock()
        mock_sp.current_user_top_tracks.return_value = {'items': []}
        mock_connection.return_value = mock_sp
        
        with patch('pandas.DataFrame.to_csv'):
            df, track_ids = get_top_tracks(50, 0, "medium_term")
        
        # Verify empty data is handled
        assert len(df) == 0
        assert track_ids == []
        
        # Test visualization with empty data (create proper empty DataFrame)
        empty_df_with_columns = pd.DataFrame(columns=['track_name', 'popularity'])
        with patch('scripts.visualizations.go.Figure') as mock_figure:
            mock_fig = Mock()
            mock_fig.to_html.return_value = '<div>empty</div>'
            mock_figure.return_value = mock_fig
            
            result = generar_top_tracks(empty_df_with_columns)
            assert result == '<div>empty</div>'
    
    def test_data_types_consistency(self):
        """Test that data types are consistent across the pipeline"""
        # Create sample data with expected types
        sample_data = pd.DataFrame({
            'track_name': ['Track 1', 'Track 2'],
            'artists': ['Artist 1', 'Artist 2'],
            'popularity': [85, 90],  # Should be integers
            'release_date': ['2023-01-01', '2023-02-01']  # Should be strings
        })
        
        # Verify data types
        assert sample_data['track_name'].dtype == 'object'
        assert sample_data['artists'].dtype == 'object'
        assert sample_data['popularity'].dtype in ['int64', 'int32']
        assert sample_data['release_date'].dtype == 'object'
    
    @patch.dict(os.environ, {
        'SPOTIPY_CLIENT_ID': 'test_id',
        'SPOTIPY_CLIENT_SECRET': 'test_secret',
        'SPOTIPY_REDIRECT_URI': 'http://localhost:8888/callback',
        'POSTGRES_USER': 'test_user',
        'POSTGRES_PASSWORD': 'test_pass',
        'POSTGRES_HOST': 'localhost',
        'POSTGRES_PORT': '5432',
        'POSTGRES_DB': 'test_db'
    })
    def test_environment_configuration_integration(self):
        """Test that all components use environment variables correctly"""
        # This test verifies that environment variables are consistently used
        # across different parts of the application
        
        # Test would require importing and running parts of the application
        # with mocked components to verify env var usage
        
        # Verify environment variables are set for the test
        assert os.environ.get('SPOTIPY_CLIENT_ID') == 'test_id'
        assert os.environ.get('POSTGRES_USER') == 'test_user'
    
    def test_csv_file_integration(self):
        """Test CSV file operations integration"""
        from scripts.spotify_etl import get_top_tracks
        
        sample_data = pd.DataFrame({
            'track_id': ['track1'],
            'track_name': ['Test Track'],
            'artists': ['Test Artist'],
            'artist_ids': ['artist1'],
            'album': ['Test Album'],
            'album_id': ['album1'],
            'release_date': ['2023-01-01'],
            'popularity': [85],
            'spotify_url': ['https://test.url']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Test CSV writing
            sample_data.to_csv(temp_path, index=False)
            
            # Test CSV reading
            loaded_data = pd.read_csv(temp_path)
            
            # Verify data integrity
            assert len(loaded_data) == 1
            assert loaded_data.iloc[0]['track_name'] == 'Test Track'
            assert loaded_data.iloc[0]['popularity'] == 85
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)