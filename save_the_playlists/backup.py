import json

from models.playlist_metadata import PlaylistMetadata
from models.track import Track


def read_backup(playlist_name):
    with open(f'backup/{playlist_name}') as f:
        lines = f.readlines()

        playlist_json = json.loads(lines[0])
        playlist = PlaylistMetadata(playlist_json['name'],
                                    playlist_json['uri'],
                                    playlist_json['length'])

        tracks = list(map(lambda l: Track(l['complete'], l['name'], l['artist'], l['album'], l['uri']), (json.loads(line) for line in lines[1:])))

    return playlist, tracks
