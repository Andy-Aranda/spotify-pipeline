# Spotify Pipeline: Top Tracks Analysis  
This project extracts your most listened-to songs from Spotify, stores them in a PostgreSQL database (hosted on AWS RDS), and enables visual analysis in Power BI.

## 🚀 What does this project do?
1. Connects to the Spotify API to retrieve your top tracks.

2. Transforms the data into a tabular format using pandas.

3. Loads the data into PostgreSQL, either locally or in a cloud-based database (like RDS).

4. Allows you to visualize the data in Power BI for analyses such as:

   - Most frequent artists  
   - Most popular songs  
   - Release date distribution  
   - Evolution of your musical taste

## 🧱 Tech Stack
- Python (with Spotipy, Pandas, SQLAlchemy)  
- PostgreSQL (Docker container or AWS RDS)  
- Power BI (for visualization)  
- GitHub Actions (coming soon for pipeline automation)

## 📁 Project Structure
```bash
spotify-pipeline/
├── main.py               # Runs the full pipeline
├── spotify_etl.py        # Functions for extracting and transforming data
├── db_utils.py           # Saves data into PostgreSQL
├── .env                  # Environment variables (API and DB credentials)
├── requirements.txt      # Project dependencies
└── README.md             # This file 🙂
```

## ⚙️ Setup
1. Clone the repo:

```bash
git clone https://github.com/yourusername/spotify-pipeline.git
cd spotify-pipeline
```

2. Create a `.env` file with your credentials:
```bash
SPOTIPY_CLIENT_ID=your-client-id
SPOTIPY_CLIENT_SECRET=your-client-secret
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback

POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=spotify
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Run the pipeline:

```bash
python main.py
```

5. Open Power BI and connect to your PostgreSQL database to visualize the data.

## 🧠 Power BI Analysis Ideas
- Bar charts by artist  
- Word cloud with track titles  
- Popularity trends over time  
- Comparison of new vs classic tracks  
- Genre dashboard (if that data is added)

## 🔒 Security Notes
- Never commit your `.env` file to a public repository.  
- If using RDS, make sure to set up security groups to only allow necessary IPs.

## 🧪 Testing

This project includes a comprehensive test suite covering all major components:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run tests with coverage
python run_tests.py --coverage

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
```

The test suite includes:
- **Unit Tests**: ETL functions, visualizations, database utilities
- **Integration Tests**: Flask routes, complete data pipeline
- **Mocking**: All external APIs and database connections
- **Coverage**: Comprehensive code coverage reporting

See [README_TESTING.md](README_TESTING.md) for detailed testing documentation.

## ✨ Coming Soon
- Daily automation with GitHub Actions  
- Public dashboard via Power BI Web  
- Include genres and track duration
