from abc import abstractmethod, ABC
from dataclasses import dataclass


@dataclass
class BlacklistEntry(ABC):
    field_value: str

    @abstractmethod
    def is_blacklisted(self, track):
        pass


class NameBlacklistEntry(BlacklistEntry):
    def is_blacklisted(self, track):
        return self.field_value == track.name


class ArtistBlacklistEntry(BlacklistEntry):
    def is_blacklisted(self, track):
        return self.field_value == track.artist


class AlbumBlacklistEntry(BlacklistEntry):
    def is_blacklisted(self, track):
        return self.field_value == track.album
