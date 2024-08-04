import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Set up authentication
SPOTIPY_CLIENT_ID = '7b5c4863c0ef4e63941e18a2dfd8ea77'
SPOTIPY_CLIENT_SECRET = '6dce0bbd71c94564837c9f7cf2a91e46'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

def main():

    scope = 'playlist-read-private'

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                                client_secret=SPOTIPY_CLIENT_SECRET,
                                                redirect_uri=SPOTIPY_REDIRECT_URI,
                                                scope=scope))

    def get_playlist_tracks(playlist_id):
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        return [(track['track']['name'], track['track']['artists'][0]['name']) for track in tracks]

    def compare_playlists(playlist_id_1, playlist_id_2):
        tracks_1 = get_playlist_tracks(playlist_id_1)
        tracks_2 = get_playlist_tracks(playlist_id_2)
        
        set_tracks_1 = set(tracks_1)
        set_tracks_2 = set(tracks_2)
        
        common_tracks = set_tracks_1 & set_tracks_2
        
        return common_tracks

    # Replace with your playlist IDs
    playlist_id_1 = '1tSQiuSzSUA1LbNBXRLiTU'
    playlist_id_2 = '2pSjSZPfD8m83trf9m5xC1'

    common_tracks = compare_playlists(playlist_id_1, playlist_id_2)

    # Create a DataFrame for common tracks
    df_common_tracks = pd.DataFrame(list(common_tracks), columns=['Track Name', 'Artist'])

    # Print the DataFrame
    print(df_common_tracks)

if __name__ == "__main__":
    main()
