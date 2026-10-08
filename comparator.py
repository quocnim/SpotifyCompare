from collections import Counter
import pandas as pd

def _dedupe_by_id(tracks):
    result = {}
    for track in tracks:
        result.setdefault(track["id"], track)
    return result

def _track_rows(track_map, ids):
    rows = []
    for track_id in ids:
        track = track_map[track_id]
        rows.append({
            "track": track["name"],
            "artists": track["artists"],
            "album": track["album"],
            "release_date": track["release_date"],
            "popularity": track["popularity"],
            "explicit": track["explicit"],
            "spotify_url": track["spotify_url"],
        })
    return sorted(rows, key=lambda x: (x["artists"].lower(), x["track"].lower()))

def _duplicates(tracks):
    counts = Counter(t["id"] for t in tracks if t.get("id"))
    lookup = _dedupe_by_id(tracks)
    rows = []
    for track_id, count in counts.items():
        if count > 1:
            track = lookup[track_id]
            rows.append({
                "track": track["name"],
                "artists": track["artists"],
                "occurrences": count,
            })
    return sorted(rows, key=lambda x: -x["occurrences"])

def _artist_comparison(tracks_a, tracks_b):
    a = Counter()
    b = Counter()

    for track in tracks_a:
        for artist in track["artist_list"]:
            if artist:
                a[artist] += 1

    for track in tracks_b:
        for artist in track["artist_list"]:
            if artist:
                b[artist] += 1

    artists = sorted(set(a) | set(b), key=str.lower)

    rows = []
    for artist in artists:
        rows.append({
            "artist": artist,
            "playlist_a_tracks": a.get(artist, 0),
            "playlist_b_tracks": b.get(artist, 0),
            "in_both": artist in a and artist in b,
        })
    return rows

def compare_playlists(playlist_a, playlist_b, tracks_a, tracks_b):
    map_a = _dedupe_by_id(tracks_a)
    map_b = _dedupe_by_id(tracks_b)

    ids_a = set(map_a)
    ids_b = set(map_b)

    common = ids_a & ids_b
    only_a = ids_a - ids_b
    only_b = ids_b - ids_a

    denominator = len(ids_a | ids_b)
    overlap = (len(common) / denominator * 100) if denominator else 0

    common_rows = _track_rows({**map_a, **map_b}, common)

    summary = {
        "playlist_a": playlist_a["name"],
        "playlist_b": playlist_b["name"],
        "playlist_a_tracks": len(tracks_a),
        "playlist_b_tracks": len(tracks_b),
        "playlist_a_unique": len(ids_a),
        "playlist_b_unique": len(ids_b),
        "common_tracks": len(common),
        "only_a": len(only_a),
        "only_b": len(only_b),
        "overlap_percent": overlap,
    }

    return {
        "summary": summary,
        "common_tracks": common_rows,
        "only_a_tracks": _track_rows(map_a, only_a),
        "only_b_tracks": _track_rows(map_b, only_b),
        "artist_comparison": _artist_comparison(tracks_a, tracks_b),
        "duplicates_a": _duplicates(tracks_a),
        "duplicates_b": _duplicates(tracks_b),
    }

def results_to_dataframes(results):
    return {
        "Summary": pd.DataFrame([results["summary"]]),
        "Common Tracks": pd.DataFrame(results["common_tracks"]),
        "Only Playlist A": pd.DataFrame(results["only_a_tracks"]),
        "Only Playlist B": pd.DataFrame(results["only_b_tracks"]),
        "Artists": pd.DataFrame(results["artist_comparison"]),
        "Duplicates A": pd.DataFrame(results["duplicates_a"]),
        "Duplicates B": pd.DataFrame(results["duplicates_b"]),
    }
