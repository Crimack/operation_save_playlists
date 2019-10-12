import json
import logging

from save_the_playlists import LOCAL_URI
from utils.directories import make_failed_dir, make_success_dir


def update_playlist(client, username, playlist, fixed_track_uris):
    # Spotipy currently fails with local URIs
    if any(uri.startswith(LOCAL_URI) for uri in fixed_track_uris) or not fixed_track_uris:
        logging.info(f'Failed to update {playlist.name}!')
        make_failed_dir()
        result = 'failed'
    else:
        first_batch = fixed_track_uris[:100]
        client.user_playlist_replace_tracks(username, playlist.uri,
                                            first_batch)
        offset = 100
        while offset < len(fixed_track_uris):
            batch = fixed_track_uris[offset:offset + 100]
            client.user_playlist_add_tracks(username, playlist.uri, batch)
            offset += 100

        make_success_dir()
        logging.info(f'Updated {playlist.name}!')
        result = 'success'

    dump_playlist_with_uris(result, playlist, fixed_track_uris)


def dump_playlist_with_uris(dir_name, playlist, track_uris):
    with open(f'{dir_name}/{playlist.name}', 'w+') as f:
        f.write(json.dumps(playlist.__dict__))
        f.write('\n')
        f.write(json.dumps(track_uris))
        f.write('\n')
