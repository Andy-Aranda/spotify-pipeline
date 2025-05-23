# main.py

from scripts.spotify_etl import get_top_tracks
from scripts.db_utils import save_tracks_to_db

def main():
    print("Obteniendo canciones más escuchadas de Spotify...")
    df = get_top_tracks(50, 0, "medium_term")
    
    print("Guardando en la base de datos...")
    save_tracks_to_db(df)
    
    print("✅ Proceso terminado.")

if __name__ == "__main__":
    main()
