import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "playlist-read-private",
    "playlist-read-collaborative",
]

class SpotifyClient:
    def __init__(self):
        client_id = os.getenv("SPOTIPY_CLIENT_ID")
        client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIPY_REDIRECT_URI")

        missing = [
            name for name, value in {
                "SPOTIPY_CLIENT_ID": client_id,
                "SPOTIPY_CLIENT_SECRET": client_secret,
                "SPOTIPY_REDIRECT_URI": redirect_uri,
            }.items()
            if not value
        ]

        if missing:
            raise RuntimeError(
                "Missing environment variables: " + ", ".join(missing)
            )

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=" ".join(SCOPES),
                open_browser=True,
            )
        )

    def get_all_playlists(self):
        playlists = []
        results = self.sp.current_user_playlists(limit=50)

        while results:
            for item in results.get("items", []):
                if not item:
                    continue
                playlists.append({
                    "id": item["id"],
                    "name": item["name"],
                    "track_count": item.get("items", {}).get(
                        "total",
                        item.get("tracks", {}).get("total", 0)
                    ),
                    "url": item.get("external_urls", {}).get("spotify", ""),
                    "owner": (item.get("owner") or {}).get("display_name", ""),
                })

            if not results.get("next"):
                break
            results = self.sp.next(results)

        return playlists

    def get_playlist_tracks(self, playlist_id):
        tracks = []
        results = self.sp.playlist_items(
            playlist_id,
            limit=50,
            additional_types=("track",),
        )

        while results:
            for item in results.get("items", []):
                track = item.get("track") or item.get("item")
                if not track or not track.get("id"):
                    continue
                if track.get("type") != "track":
                    continue

                artists = track.get("artists") or []
                album = track.get("album") or {}

                tracks.append({
                    "id": track["id"],
                    "name": track.get("name", ""),
                    "artists": ", ".join(a.get("name", "") for a in artists),
                    "artist_list": [a.get("name", "") for a in artists],
                    "album": album.get("name", ""),
                    "album_id": album.get("id", ""),
                    "release_date": album.get("release_date", ""),
                    "duration_ms": track.get("duration_ms", 0),
                    "explicit": track.get("explicit", False),
                    "popularity": track.get("popularity", 0),
                    "spotify_url": (track.get("external_urls") or {}).get("spotify", ""),
                    "added_at": item.get("added_at", ""),
                })

            if not results.get("next"):
                break
            results = self.sp.next(results)

        return tracks
