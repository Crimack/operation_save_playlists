import spotipy
from spotipy import util

# Hard coding all the scopes this app needs
SCOPES = "playlist-read-private playlist-modify-private playlist-modify-public user-top-read"


def get_client(username):
    auth_token = util.prompt_for_user_token(username, SCOPES)
    return spotipy.Spotify(auth_token)
