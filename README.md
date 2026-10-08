# Spotify Playlist Analyzer V2

A Python desktop application for comparing Spotify playlists.

## Features

- Spotify OAuth authentication
- Automatically loads your accessible playlists
- Uses Spotify track IDs for reliable matching
- Handles paginated playlists
- Common tracks
- Tracks unique to Playlist A
- Tracks unique to Playlist B
- Artist comparison
- Duplicate detection
- Overlap percentage
- Excel export
- CSV bundle export
- Tkinter desktop GUI
- Secrets stored in environment variables

## Architecture

```text
Spotify API
    |
    v
spotify_client.py
    |
    v
Raw track metadata
    |
    v
comparator.py
    |
    +--> common tracks
    +--> only A
    +--> only B
    +--> artists
    +--> duplicates
    +--> statistics
    |
    v
exporter.py / app.py
    |
    +--> Excel
    +--> CSV
    +--> GUI
```

## 1. Create a Spotify Developer App

Create an application in the Spotify Developer Dashboard.

Set the redirect URI to:

```text
http://127.0.0.1:8888/callback
```

Use the exact URI configured in the developer dashboard.

## 2. Clone the project

```powershell
git clone https://github.com/quocnim/SpotifyCompare.git
cd SpotifyCompare
```

Then replace/add the V2 files from this project.

## 3. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

If `py` is unavailable:

```powershell
python -m venv .venv
```

## 4. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 5. Configure credentials

Copy:

```text
.env.example
```

to:

```text
.env
```

Then enter your Spotify application credentials.

Example:

```text
SPOTIPY_CLIENT_ID=abc123
SPOTIPY_CLIENT_SECRET=def456
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

Never commit `.env`.

## 6. Run

```powershell
python app.py
```

A browser window should open for Spotify authentication the first time.

## Notes

The application uses Spotipy's `playlist_items()` method rather than the deprecated `playlist_tracks()` helper.

Spotify playlist access depends on the scopes granted to the application. Private playlists require `playlist-read-private`; collaborative playlists require `playlist-read-collaborative`.

Spotify content should not be downloaded. This project only analyzes metadata returned through the Spotify Web API.

## Future V3 ideas

- Search/filter tracks
- Charts and visualizations
- Genre analysis
- Release-year analysis
- Playlist similarity scoring
- Dark mode
- Command-line mode
- Unit tests
- GitHub Actions CI
- Packaging as a Windows executable
