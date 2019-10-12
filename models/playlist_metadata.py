from dataclasses import dataclass


@dataclass(unsafe_hash=True, frozen=True)
class PlaylistMetadata:
    name: str
    uri: str
    length: int
