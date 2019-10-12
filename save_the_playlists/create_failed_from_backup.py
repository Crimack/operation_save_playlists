import logging
import sys

from save_the_playlists.backup import read_backup
from save_the_playlists.update import dump_playlist_with_uris


def main():
    playlist_name = sys.argv[1]

    playlist, tracks = read_backup(playlist_name)

    dump_playlist_with_uris('failed', playlist, list(map(lambda t: t.uri, tracks)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
