import os
from dotenv import load_dotenv
from pathlib import Path


os.environ.pop("SPOTIPY_CLIENT_ID", None)
os.environ.pop("SPOTIPY_CLIENT_SECRET", None)
os.environ.pop("SPOTIPY_REDIRECT_URI", None)

load_dotenv(dotenv_path=Path('.') / '.env')

print("CLIENT_ID:", os.getenv("SPOTIPY_CLIENT_ID"))
print("SECRET:", os.getenv("SPOTIPY_CLIENT_SECRET"))
print("REDIRECT_URI:", os.getenv("SPOTIPY_REDIRECT_URI"))
