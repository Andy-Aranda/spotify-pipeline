import spotipy
from dotenv import load_dotenv
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def get_top_tracks(limit, offset, time_range):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-top-read user-read-recently-played",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")
))
    results = sp.current_user_top_tracks(limit, offset, time_range)

    data = []
    for item in results['items']:
        data.append({
            'track_name': item['name'],
            'artists' : ", ".join([artist['name'] for artist in item['artists']]),
            'album' : item['album']['name'],
            'release_date' : item['album']['release_date'],
            'popularity': item['popularity'],
            'spotify_url': item['external_urls']['spotify']
        })

    df = pd.DataFrame(data)
    return df

