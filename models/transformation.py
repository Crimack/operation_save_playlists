from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class Transformation(ABC):
    original: str
    replacement: str

    @abstractmethod
    def apply(self, track):
        pass


class NameTransformation(Transformation):
    def apply(self, track):
        if track.name == self.original:
            track.name = self.replacement

        return track


class AlbumTransformation(Transformation):
    def apply(self, track):
        if track.album == self.original:
            track.album = self.replacement

        return track


class ArtistTransformation(Transformation):
    def apply(self, track):
        if track.artist == self.original:
            track.artist = self.replacement

        return track
