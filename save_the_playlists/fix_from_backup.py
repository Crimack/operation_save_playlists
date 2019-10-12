import logging
import sys

from save_the_playlists.backup import read_backup
from fix_playlists import transform_and_update_playlist
from utils.client import get_client


def print_usage():
    logging.info(f"Usage: {sys.argv[0]} username playlist_name")
    sys.exit()


def main():
    if len(sys.argv) < 3:
        print_usage()

    username = sys.argv[1]
    if not username:
        print_usage()

    playlist_name = sys.argv[2]
    if not playlist_name:
        print_usage()

    logging.info(f'Fixing {playlist_name}')

    client = get_client(username)
    playlist, tracks = read_backup(playlist_name)
    transform_and_update_playlist(client, username, playlist, tracks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
