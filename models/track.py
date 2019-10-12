from dataclasses import dataclass


@dataclass
class Track:
    complete: dict
    name: str
    artist: str
    album: str
    uri: str = None

    def pretty_string(self):
        return f'Track: {self.name}, Artist: {self.artist}, Album: {self.album}'
