import csv
import json
import logging
import os
import re
import sys

from models.blacklist_entry import NameBlacklistEntry, ArtistBlacklistEntry, AlbumBlacklistEntry
from models.playlist_metadata import PlaylistMetadata
from models.track import Track
from models.transformation import NameTransformation, AlbumTransformation, ArtistTransformation
from save_the_playlists import LOCAL_URI
from save_the_playlists.update import update_playlist
from utils.client import get_client
from utils.directories import make_backup_dir
from utils.prompt import prompt_for_input

FEATURING = re.compile('(- )?(\\()?[Ff]eat(\\.|uring)?.*')
REMASTERED = re.compile('(- )?(\\([Rr]emastered\\))')
REMOVALS = ['w/', 'with ', 'Live From', '[', ']']


def print_usage():
    logging.info(f"Usage: {sys.argv[0]} username")
    sys.exit()


def read_playlists():
    with open('results/target_playlists.csv', newline='') as f:
        reader = csv.reader(f)
        next(reader)
        return [
            PlaylistMetadata(line[0], line[1], int(line[2])) for line in reader
        ]


def read_transformations():
    with open('transformations.txt', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, escapechar='\\')
        next(reader)

        transformations = []
        for line in reader:
            if line[0] == 'NAME':
                transformations.append(NameTransformation(line[1], line[2]))
            elif line[0] == 'ALBUM':
                transformations.append(AlbumTransformation(line[1], line[2]))
            elif line[0] == 'ARTIST':
                transformations.append(ArtistTransformation(line[1], line[2]))

        return transformations


def read_blacklist():
    with open('blacklist.txt', newline='') as f:
        reader = csv.reader(f)
        next(reader)

        blacklist = []
        for line in reader:
            if line[0] == 'NAME':
                blacklist.append(NameBlacklistEntry(line[1]))
            elif line[0] == 'ALBUM':
                blacklist.append(AlbumBlacklistEntry(line[1]))
            elif line[0] == 'ARTIST':
                blacklist.append(ArtistBlacklistEntry(line[1]))

        return blacklist


def backup_playlist(playlist, tracks):
    make_backup_dir()

    backup_file_name = f'backup/{playlist.name}'

    # Don't overwrite existing backups
    if os.path.exists(backup_file_name):
        return

    with open(backup_file_name, 'w+') as f:
        f.write(json.dumps(playlist.__dict__))
        f.write('\n')
        for track in tracks:
            f.write(json.dumps(track.__dict__))
            f.write('\n')
        f.write('\n')


def fetch_tracks(client, username, playlist):
    tracks = []
    uri = playlist.uri
    total = playlist.length
    offset = 0

    while offset < total:
        playlist_tracks = client.user_playlist_tracks(username,
                                                      uri,
                                                      offset=offset)
        tracks.extend(
            Track(item['track'], item['track']['name'], item['track']
                  ['artists'][0]['name'], item['track']['album']['name'],
                  item['track']['uri']) for item in playlist_tracks['items'])
        offset += 100

    return tracks


def normalise_tracks(tracks, transformations):
    normalised = []

    for track in tracks:
        for transformation in transformations:
            track = transformation.apply(track)

        name = track.name
        name = re.sub(FEATURING, "", name)
        name = re.sub(REMASTERED, "", name)

        for removal in REMOVALS:
            name = name.replace(removal, "")

        normalised.append(
            Track(track.complete, name, track.artist, track.album, track.uri))

    return normalised


def fix_playlist_tracks(client, tracks, blacklist):
    updated_tracks = []
    for track in tracks:
        logging.info(
            f'Fixing track: {track.name}, {track.artist}, {track.album}')
        # If the track is already available on Spotify, just keep it
        if not track.uri.startswith(LOCAL_URI):
            updated_tracks.append(track)
            continue

        # If it's a weird bootleg version just don't bother.
        if any(entry.is_blacklisted(track) for entry in blacklist):
            continue

        exact_candidate_tracks = get_candidate_tracks(
            client, f'{track.name} {track.artist} {track.album}')

        # If we have a perfect match, have the confidence to not ask for help
        perfect_match = find_perfect_match(exact_candidate_tracks, track)
        if perfect_match is not None:
            updated_tracks.append(perfect_match)
            continue

        # If we don't, asking for help doesn't make you any less of a person
        candidate_tracks = get_candidate_tracks(
            client, f'{track.name} {track.artist}')
        chosen_candidate = prompt_for_input(track, candidate_tracks)
        if chosen_candidate is not None:
            updated_tracks.append(chosen_candidate)
            continue

        # If we still have nothing, swing for the fences and drop it if we find nothing
        fuzzy_candidate_tracks = get_candidate_tracks(client, f'{track.name}')
        chosen_fuzzy_candidate = prompt_for_input(track,
                                                  fuzzy_candidate_tracks)
        if chosen_fuzzy_candidate is not None:
            updated_tracks.append(chosen_fuzzy_candidate)

    return updated_tracks


def get_candidate_tracks(client, query_string, num_results=25):
    results = client.search(query_string, limit=num_results)
    candidate_tracks = [
        Track(item, item['name'], item['artists'][0]['name'],
              item['album']['name'], item['uri'])
        for item in results['tracks']['items']
    ]
    return candidate_tracks


def find_perfect_match(exact_candidate_tracks, track):
    perfect_match = None
    for candidate in exact_candidate_tracks:
        name_matches = candidate.name.lower() == track.name.lower() or (
            candidate.name.lower().startswith(track.name.lower()) and
            ('remaster' in candidate.name.lower()
             or 'live' in candidate.name.lower()[len(track.name):]))
        artist_matches = candidate.artist.lower() == track.artist.lower()
        album_matches = candidate.album.lower() == track.album.lower() or (
            candidate.album.lower().startswith(track.album.lower()) and
            ('remaster' in candidate.album.lower()
             or 'edition' in candidate.album.lower()[len(track.album):]))
        if name_matches and artist_matches and album_matches:
            perfect_match = candidate
    return perfect_match


def transform_and_update_playlist(client, username, playlist, tracks):
    # Remove features, /, with /, w/, featuring ( mark as help needed)
    # Perform transformations 'Gangnam Style 1' -> Gangnam Style, PSY-CO-BILLY -> PSY (transformations)
    transformations = read_transformations()
    normalised_tracks = normalise_tracks(tracks, transformations)
    # Replace tracks with 'spotify:local' UNLESS (for example) Garth Brooks (blacklist)
    # Try query with album first, without album second
    # Compare lower case names to see if valid replacement
    blacklist = read_blacklist()
    fixed_tracks = fix_playlist_tracks(client, normalised_tracks, blacklist)
    update_playlist(client, username, playlist,
                    list(map(lambda t: t.uri, fixed_tracks)))


def main():
    username = sys.argv[1]

    client = get_client(username)

    if os.path.exists('success'):
        success = os.listdir('success')

    playlists = filter(lambda y: y.name not in success,
                       sorted(read_playlists(), key=lambda p: p.length))

    for playlist in playlists:
        # Get list of all tracks
        logging.info(f'Fixing {playlist.name}')
        tracks = fetch_tracks(client, username, playlist)
        logging.info(f'Length: {len(tracks)}')
        logging.info(f'Tracks: {", ".join(map(lambda t: t.name, tracks))}')
        backup_playlist(playlist, tracks)
        transform_and_update_playlist(client, username, playlist, tracks)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
