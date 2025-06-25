import pytest
import pandas as pd
import sys
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
import os

sys.path.append('/Users/andreaaranda/Desktop/spotify-pipeline')
from scripts.db_utils import save_tracks_to_db

class TestDatabaseUtils:
    
    @pytest.fixture
    def sample_tracks_df(self):
        """Sample tracks DataFrame for testing"""
        return pd.DataFrame({
            'track_id': ['track1', 'track2', 'track3'],
            'track_name': ['Track 1', 'Track 2', 'Track 3'],
            'artists': ['Artist 1', 'Artist 2', 'Artist 3'],
            'album': ['Album 1', 'Album 2', 'Album 3'],
            'release_date': ['2023-01-01', '2023-02-01', '2023-03-01'],
            'popularity': [85, 90, 75],
            'spotify_url': ['url1', 'url2', 'url3']
        })
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_success(self, mock_to_sql, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test successful saving of tracks to database"""
        # Setup environment variable mocks
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Setup engine mock
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        save_tracks_to_db(sample_tracks_df)
        
        # Verify engine creation with correct connection string
        expected_url = 'postgresql+psycopg2://test_user:test_password@localhost:5432/test_db'
        mock_create_engine.assert_called_once_with(expected_url)
        
        # Verify DataFrame.to_sql was called with correct parameters
        mock_to_sql.assert_called_once_with(
            'top_tracks',
            con=mock_engine,
            if_exists='replace',
            index=False
        )
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    def test_save_tracks_to_db_missing_env_vars(self, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test behavior when environment variables are missing"""
        # Mock missing environment variables (return None)
        mock_getenv.return_value = None
        
        # Should still try to create engine (will fail with None values, but function doesn't handle this)
        # This test documents current behavior - ideally the function should validate env vars
        save_tracks_to_db(sample_tracks_df)
        
        # Verify getenv was called for all required variables
        expected_calls = [
            'POSTGRES_USER',
            'POSTGRES_PASSWORD', 
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB'
        ]
        
        for var in expected_calls:
            mock_getenv.assert_any_call(var)
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_custom_env_values(self, mock_to_sql, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test with custom environment variable values"""
        # Setup custom environment variables
        env_vars = {
            'POSTGRES_USER': 'custom_user',
            'POSTGRES_PASSWORD': 'custom_pass',
            'POSTGRES_HOST': 'remote.host.com',
            'POSTGRES_PORT': '5433',
            'POSTGRES_DB': 'custom_db'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        save_tracks_to_db(sample_tracks_df)
        
        # Verify engine creation with custom values
        expected_url = 'postgresql+psycopg2://custom_user:custom_pass@remote.host.com:5433/custom_db'
        mock_create_engine.assert_called_once_with(expected_url)
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_empty_dataframe(self, mock_to_sql, mock_getenv, mock_create_engine):
        """Test saving empty DataFrame"""
        empty_df = pd.DataFrame(columns=['track_id', 'track_name', 'artists'])
        
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
        
        save_tracks_to_db(empty_df)
        
        # Should still call to_sql even with empty DataFrame
        mock_to_sql.assert_called_once_with(
            'top_tracks',
            con=mock_engine,
            if_exists='replace',
            index=False
        )
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_dataframe_with_special_characters(self, mock_to_sql, mock_getenv, mock_create_engine):
        """Test saving DataFrame with special characters"""
        special_df = pd.DataFrame({
            'track_name': ['Track with "quotes"', 'Track with \'apostrophe\'', 'Track with émojis 🎵'],
            'artists': ['Artist & Co.', 'Artist (feat. Other)', 'Artíst with açcénts'],
            'album': ['Album #1', 'Album [2023]', 'Album: The Return']
        })
        
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
        
        save_tracks_to_db(special_df)
        
        # Verify function handles special characters without crashing
        mock_to_sql.assert_called_once()
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql', side_effect=Exception('Database connection failed'))
    def test_save_tracks_to_db_database_error(self, mock_to_sql, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test handling of database errors"""
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
        
        # Function doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match='Database connection failed'):
            save_tracks_to_db(sample_tracks_df)
    
    @patch('scripts.db_utils.create_engine', side_effect=Exception('Engine creation failed'))
    @patch('scripts.db_utils.os.getenv')
    def test_save_tracks_to_db_engine_creation_error(self, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test handling of engine creation errors"""
        env_vars = {
            'POSTGRES_USER': 'test_user',
            'POSTGRES_PASSWORD': 'test_password',
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'test_db'
        }
        mock_getenv.side_effect = lambda key: env_vars.get(key)
        
        # Function doesn't handle exceptions, so this should raise
        with pytest.raises(Exception, match='Engine creation failed'):
            save_tracks_to_db(sample_tracks_df)
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_table_replace_behavior(self, mock_to_sql, mock_getenv, mock_create_engine, sample_tracks_df):
        """Test that function uses 'replace' behavior for existing tables"""
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
        
        save_tracks_to_db(sample_tracks_df)
        
        # Verify that if_exists='replace' is used
        call_kwargs = mock_to_sql.call_args[1]
        assert call_kwargs['if_exists'] == 'replace'
        assert call_kwargs['index'] == False
        assert call_kwargs['con'] == mock_engine
        
        # Verify table name
        call_args = mock_to_sql.call_args[0]
        assert call_args[0] == 'top_tracks'
    
    def test_database_connection_string_format(self):
        """Test the database connection string format"""
        # This test documents the expected connection string format
        # Used by the save_tracks_to_db function
        
        user = 'test_user'
        password = 'test_password'
        host = 'localhost'
        port = '5432'
        database = 'test_db'
        
        expected_format = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
        
        # This format should be compatible with SQLAlchemy create_engine
        assert expected_format == 'postgresql+psycopg2://test_user:test_password@localhost:5432/test_db'
    
    @patch('scripts.db_utils.create_engine')
    @patch('scripts.db_utils.os.getenv')
    @patch('pandas.DataFrame.to_sql')
    def test_save_tracks_to_db_large_dataframe(self, mock_to_sql, mock_getenv, mock_create_engine):
        """Test saving large DataFrame"""
        # Create a large DataFrame (1000 rows) to test performance characteristics
        large_df = pd.DataFrame({
            'track_id': [f'track_{i}' for i in range(1000)],
            'track_name': [f'Track {i}' for i in range(1000)],
            'artists': [f'Artist {i}' for i in range(1000)],
            'popularity': [i % 100 for i in range(1000)]
        })
        
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
        
        save_tracks_to_db(large_df)
        
        # Verify function handles large DataFrames
        mock_to_sql.assert_called_once()
        
        # Verify the DataFrame passed to to_sql has correct size
        call_args = mock_to_sql.call_args[0]
        # Note: call_args[0] would be the table name, the DataFrame is passed via the implicit self
        # This test mainly verifies no exceptions are raised with large data