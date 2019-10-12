from dataclasses import dataclass
from typing import List

from models.track import Track


@dataclass
class Playlist:
    name: str
    uri: str
    tracks: List[Track]
