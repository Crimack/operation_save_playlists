import csv
import logging
import sys

from models.playlist_metadata import PlaylistMetadata
from utils.client import get_client


def print_usage():
    logging.info(f"Usage: {sys.argv[0]} username whitelist?")
    sys.exit()


def read_whitelist(file_path):
    with open(file_path) as f:
        return [line.strip() for line in f.readlines()]


def get_target_playlists(target_user, playlist_whitelist):
    client = get_client(target_user)

    target_playlists = []
    for offset in range(0, 250, 50):
        playlists = client.current_user_playlists(offset=offset)
        logging.debug(f"Playlist API reuslts: {playlists}")
        for item in playlists['items']:
            if playlist_whitelist is None or item['name'] in playlist_whitelist:
                playlist = PlaylistMetadata(item['name'], item['uri'],
                                            item['tracks']['total'])
                target_playlists.append(playlist)

    with open('results/target_playlists.csv', 'w+', newline='') as g:
        logging.info(
            f"Writing information for {', '.join([out.name for out in target_playlists])}"
        )
        results_writer = csv.writer(g)
        results_writer.writerow(['name', 'playlist_uri', 'length'])
        for playlist in target_playlists:
            results_writer.writerow(
                [playlist.name, playlist.uri, playlist.length])


def get_whitelist():
    if len(sys.argv) > 2:
        whitelist_file = sys.argv[2]
        if whitelist_file:
            whitelist = read_whitelist(whitelist_file)
            logging.debug(
                f"Whitelisted playlist titles: {', '.join(whitelist)}")
            return whitelist

    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print_usage()

    username = sys.argv[1]
    if not username:
        print_usage()

    whitelist = get_whitelist()

    get_target_playlists(username, whitelist)
