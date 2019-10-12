import csv
import json
import logging
import sys

from utils.client import get_client
from utils.directories import make_results_dir


def print_usage():
    print(f"Usage: {sys.argv[0]} username")
    sys.exit()


def get_top_tracks(target_user, target_range):
    client = get_client(target_user)
    results = client.current_user_top_tracks(limit=50, time_range=target_range)
    with open(f'top_tracks_{target_range}.json', 'w+', newline='') as f:
        json.dump(results, f)
    with open(f'top_tracks_{target_range}.csv', 'w+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Artist', 'Album', 'Popularity'])
        for result in results['items']:
            writer.writerow([
                result['name'], result['album']['artists'][0]['name'],
                result['album']['name'], result['popularity']
            ])


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print_usage()

    username = sys.argv[1]
    if not username:
        print_usage()

    make_results_dir()
    for time_range in ['short_term', 'medium_term', 'long_term']:
        get_top_tracks(username, time_range)
