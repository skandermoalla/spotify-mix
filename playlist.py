import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from dotenv import load_dotenv
from datetime import datetime

# Credentials loaded from .env
load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

REDIRECT_URI = 'http://localhost:8888/callback'
SCOPE = 'playlist-modify-public playlist-modify-private playlist-read-private'

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

# Example: Get your Spotify user ID
user_id = sp.me()['id']
print(f'Authenticated as: {user_id}')  

def get_playlist_tracks(sp, playlist_id):
    """Get tracks from a Spotify playlist"""
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return [track['track']['uri'] for track in tracks]

def mix_playlists(sp, playlist1_id, playlist2_id, new_playlist_name):
    """Mix two Spotify playlists into a new playlist"""
    # Get tracks from both playlists
    playlist1_tracks = get_playlist_tracks(sp, playlist1_id)
    playlist2_tracks = get_playlist_tracks(sp, playlist2_id)

    # Shuffle the playlists
    random.shuffle(playlist1_tracks)
    random.shuffle(playlist2_tracks)
    
    # Alternate between tracks from the two playlists
    mixed_tracks = []
    max_length = max(len(playlist1_tracks), len(playlist2_tracks))
    max_length = 100     # 5 hours already.
    
    for i in range(max_length//2):
        try:
            t1 = playlist1_tracks[i]
            t2 = playlist2_tracks[i]
        except IndexError:
            raise IndexError("Not enough valid tracks in one of the playlists")
        if t1.startswith("spotify:track:") and t2.startswith("spotify:track:"):
            mixed_tracks.append(t1)
            mixed_tracks.append(t2)

    new_playlist = sp.user_playlist_create(user=user_id, name=new_playlist_name, public=True)
    # Add mixed tracks to the new playlist
    sp.playlist_add_items(new_playlist['id'], mixed_tracks)
    
    # Return the URL of the newly created playlist
    return new_playlist['external_urls']['spotify']

# Function to list playlists
def list_user_playlists(sp):
    playlists = sp.current_user_playlists()
    print("Your playlists:")
    for idx, playlist in enumerate(playlists['items']):
        print(f"{idx + 1}. {playlist['name']} - ID: {playlist['id']}")

# Example usage
list_user_playlists(sp)
playlist1_id = '14blziMpYuvXgLYNcQr2RA'  # Replace with your first playlist's ID
playlist2_id = '1mILxJiwaAIeJwT39HeATc'  # Replace with your second playlist's ID
formatted_date = datetime.now().strftime("%d.%m.%Y")
new_playlist_name = f'CUBAliente Practica {formatted_date}'

# Create the mixed playlist and print its URL
new_playlist_url = mix_playlists(sp, playlist1_id, playlist2_id, new_playlist_name)
print(f'Mixed playlist created: {new_playlist_url}')