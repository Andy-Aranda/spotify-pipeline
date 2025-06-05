import spotipy
from dotenv import load_dotenv
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

def connection_api(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope,
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI")
))
    return sp

def get_top_tracks(limit, offset, time_range):
    sp = connection_api("user-top-read user-read-recently-played")
    results = sp.current_user_top_tracks(limit, offset, time_range)

    tracks_ids = []
    data = []
    for item in results['items']:
        data.append({
            'track_id': item['id'],
            'track_name': item['name'],
            'artists' : ", ".join([artist['name'] for artist in item['artists']]),
            'artist_ids': ", ".join([artist['id'] for artist in item['artists']]),
            'album' : item['album']['name'],
            'album_id': item['album']['id'],
            'release_date' : item['album']['release_date'],
            'popularity': item['popularity'],
            'spotify_url': item['external_urls']['spotify']
        })
        tracks_ids.append(item['id'])

    df = pd.DataFrame(data)
    df.to_csv('/Users/andreaaranda/Desktop/spotify-pipeline/data/top_tracks.csv', index=False)
    return df, tracks_ids

def get_audio_features(tracks):
    sp = connection_api("user-top-read")  # este scope es suficiente

    features = []
    # La API acepta máximo 100 ids por petición
    for i in range(0, len(tracks), 50):
        batch = tracks[i:i + 50]
        audio_features = sp.audio_features(batch)
        features.extend(audio_features)

    df_features = pd.DataFrame(features)
    df_features.to_csv('data/audio_features.csv', index=False)
    return df_features



df, tracks_ids = get_top_tracks(50, 0, "medium_term")
get_audio_features(tracks_ids)