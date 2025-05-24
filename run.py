from flask import Flask, redirect, request, session, url_for, render_template
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import plotly.graph_objects as go

from scripts.visualizations import generar_top_tracks, generar_popularidad_artistas

# Cargar variables de entorno
load_dotenv(dotenv_path=Path('.') / '.env')

app = Flask(__name__, template_folder='app/templates')
app.secret_key = os.urandom(24)

# Configuraciones de Spotify
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
SCOPE = "user-top-read"

# Configuración DB
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

engine = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    time_range = session.get("time_range", "medium_term")
    session["time_range"] = time_range

    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET'])
def profile():
    token_info = session.get('token_info')
    if not token_info:
        return redirect(url_for('login'))

    time_range = request.args.get("time_range", "medium_term")
    sp = spotipy.Spotify(auth=token_info['access_token'])

    user_profile = sp.current_user()
    user_id = user_profile['id']

    top_tracks = sp.current_user_top_tracks(limit=50, time_range=time_range)

    track_data = []
    for track in top_tracks['items']:
        track_data.append({
            "user_id": user_id,
            "track_name": track['name'],
            "artists": ", ".join([artist['name'] for artist in track['artists']]),
            "album": track['album']['name'],
            "release_date": track['album']['release_date'],
            "popularity": track['popularity'],
            "spotify_url": track['external_urls']['spotify'],
            "time_range": time_range
        })

    df = pd.DataFrame(track_data)

    # Eliminar anteriores
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM multiuser_tracks WHERE user_id = :uid AND time_range = :tr"),
            {"uid": user_id, "tr": time_range}
        )

    # Calcula el número de artistas únicos
    num_artistas_unicos = df['artists'].explode().nunique()
    df['artists_list'] = df['artists'].str.split(', ')
    num_artistas_unicos = df['artists_list'].explode().nunique()


    df.drop(columns=['artists_list'], inplace=True)
    df.to_sql('multiuser_tracks', engine, if_exists='append', index=False)

    graph_html = generar_top_tracks(df)
    graph_artistas_html = generar_popularidad_artistas(df)

    return render_template("success.html",
                           graph_html=graph_html,
                           graph_artistas_html=graph_artistas_html,
                           current_time_range=time_range,
                           num_artistas_unicos=num_artistas_unicos
)

if __name__ == '__main__':
    app.run(debug=True)
