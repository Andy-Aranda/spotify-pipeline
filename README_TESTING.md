# Testing Guide for Spotify Pipeline

This document provides comprehensive information about the test suite for the Spotify Pipeline application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── test_spotify_etl.py        # Unit tests for ETL functions
├── test_visualizations.py     # Unit tests for visualization functions
├── test_flask_routes.py       # Integration tests for Flask routes
├── test_db_utils.py          # Unit tests for database utilities
└── test_integration.py        # End-to-end integration tests
```

## Configuration Files

- `pytest.ini` - Pytest configuration and markers
- `conftest.py` - Shared fixtures and test setup

## Running Tests

### Prerequisites

```bash
pip install pytest pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/test_spotify_etl.py

# Specific test function
pytest tests/test_spotify_etl.py::TestSpotifyETL::test_get_top_tracks_success
```

### Run with Coverage

```bash
pip install pytest-cov
pytest --cov=scripts --cov=app --cov-report=html
```

## Test Categories

### Unit Tests

**`test_spotify_etl.py`**
- Tests Spotify API connection setup
- Tests track data extraction and transformation
- Tests audio features retrieval
- Tests batch processing for large datasets
- Tests error handling and edge cases

**`test_visualizations.py`**
- Tests chart generation functions
- Tests data processing for visualizations
- Tests HTML output generation
- Tests empty data handling
- Tests chart configuration and styling

**`test_db_utils.py`**
- Tests database connection string creation
- Tests DataFrame to SQL operations
- Tests environment variable handling
- Tests error scenarios
- Tests data integrity

### Integration Tests

**`test_flask_routes.py`**
- Tests Flask route handlers
- Tests OAuth authentication flow
- Tests session management
- Tests database operations in routes
- Tests template rendering (with mocks)

**`test_integration.py`**
- Tests complete ETL pipeline
- Tests data flow between components
- Tests error propagation
- Tests end-to-end scenarios

## Test Fixtures

### Available Fixtures (in `conftest.py`)

- `mock_spotify_client` - Mocked Spotify API client
- `sample_tracks_df` - Sample tracks DataFrame
- `mock_env_vars` - Mocked environment variables
- `test_db_engine` - In-memory SQLite engine for testing
- `temp_csv_file` - Temporary CSV file for I/O tests
- `flask_app` - Flask test client

## Mocking Strategy

Tests use extensive mocking to isolate components:

- **External APIs**: Spotify API calls are mocked
- **Database**: Database connections and operations are mocked
- **File I/O**: CSV operations are mocked to avoid file system dependencies
- **Environment Variables**: Environment variables are mocked for consistent testing

## Key Test Scenarios

### Data Pipeline Tests
- Complete ETL flow from API to database
- Data transformation accuracy
- Batch processing for large datasets
- Error handling and recovery

### Web Application Tests
- OAuth authentication flow
- Session management
- Route parameter handling
- Database integration
- Visualization generation

### Error Handling Tests
- API failures
- Database connection errors
- Missing environment variables
- Invalid data formats
- Empty datasets

## Test Data

Tests use realistic sample data that matches the expected structure:

```python
sample_track = {
    'id': 'track1',
    'name': 'Test Track',
    'artists': [{'name': 'Test Artist', 'id': 'artist1'}],
    'album': {
        'name': 'Test Album',
        'release_date': '2023-01-01'
    },
    'popularity': 85,
    'external_urls': {'spotify': 'https://test.url'}
}
```

## Running Tests in Different Environments

### Local Development
```bash
# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x

# Run specific test pattern
pytest -k "test_spotify"
```

### CI/CD Pipeline
```bash
# Run with coverage and XML output
pytest --cov=. --cov-report=xml --junit-xml=test-results.xml
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `sys.path` includes project root
2. **Mock Issues**: Verify mock patch targets match actual import paths
3. **Environment Variables**: Use `@patch.dict(os.environ, {...})` for env var tests
4. **Async Issues**: Some Spotify API calls may be async - ensure proper mocking

### Debug Mode
```bash
# Run with pdb debugging
pytest --pdb

# Capture print statements
pytest -s
```

## Test Maintenance

- Update tests when adding new features
- Maintain test coverage above 80%
- Review and update mocks when external APIs change
- Add integration tests for new workflows
- Document complex test scenarios

## Security Considerations

- Never use real API credentials in tests
- Mock all external service calls
- Avoid committing sensitive test data
- Use temporary files for I/O operations
- Clear session data between tests