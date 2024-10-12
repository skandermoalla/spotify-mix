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

def make_playlist_oscillate(sp, tracks):
    # Reorder by bpm
    tracks.sort(key=lambda x: sp.audio_features(x)[0]['tempo'])
    # Reorder each playlist so that it oscillates in tempo
    # a cycle is 5 tracks (medium, medium+, fast, slow, medium-)

    # devide the playlist in 5
    assert len(tracks) % 5 == 0, "Playlist length must be multiple of 5"
    group_len  = len(tracks) // 5
    groups = [tracks[i:i + group_len] for i in range(0, len(tracks), group_len)]
    # reorder groups so that it starts in the middle
    groups = groups[2:] + groups[:2]
    # shuffle each group
    for group in groups:
        random.shuffle(group)
    # interleave the groups
    interleaved = [track for group in zip(*groups) for track in group]
    # Sanity check: print the bpm of the playlist
    # for track in interleaved:
    #     print(sp.audio_features(track)[0]['tempo'])
    return interleaved

def mix_playlists(sp, playlist1_id, playlist2_id, new_playlist_name):
    """Mix two Spotify playlists into a new playlist"""
    # Get tracks from both playlists
    playlist1_tracks = get_playlist_tracks(sp, playlist1_id)
    playlist2_tracks = get_playlist_tracks(sp, playlist2_id)

    # Filter only valid tracks
    playlist1_tracks = [track for track in playlist1_tracks if track.startswith("spotify:track:")]
    playlist2_tracks = [track for track in playlist2_tracks if track.startswith("spotify:track:")]

    # Shuffle the playlists
    random.shuffle(playlist1_tracks)
    random.shuffle(playlist2_tracks)

    # Select a subset of tracks from each playlist
    max_len = 50    # Enough for 3h+
    assert len(playlist1_tracks) >= max_len and len(playlist2_tracks) >= max_len, "Playlists are too short"
    playlist1_tracks = playlist1_tracks[:max_len]
    playlist2_tracks = playlist2_tracks[:max_len]

    # Make the playlists oscillate in tempo
    playlist1_tracks = make_playlist_oscillate(sp, playlist1_tracks)
    playlist2_tracks = make_playlist_oscillate(sp, playlist2_tracks)

    # Interleave the playlists
    mixed_tracks = []
    for t1, t2 in zip(playlist1_tracks, playlist2_tracks):
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