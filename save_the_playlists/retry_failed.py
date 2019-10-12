import json
import logging
import os
import sys

from models.playlist_metadata import PlaylistMetadata
from save_the_playlists.update import update_playlist
from utils.client import get_client


def read_playlist(playlist_name):
    with open(f'failed/{playlist_name}') as f:
        lines = f.readlines()

        playlist_json = json.loads(lines[0])
        playlist = PlaylistMetadata(playlist_json['name'],
                                    playlist_json['uri'],
                                    playlist_json['length'])

        uris = json.loads(lines[1])

        return playlist, uris


def main():
    username = sys.argv[1]

    client = get_client(username)

    # Get list of all tracks
    failed = []
    if os.path.exists('failed'):
        failed = os.listdir('failed')

    for playlist_name in failed:
        logging.info(f'Fixing {playlist_name}')
        playlist, uris = read_playlist(playlist_name)
        update_playlist(client, username, playlist, uris)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
