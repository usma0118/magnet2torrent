from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Union, Optional

class Torrent():
    """
    Torrent is a class holding the data received from Transmission regarding a bittorrent transfer.
    All fetched torrent fields are accessible through this class using attributes.
    This class has a few convenience properties using the torrent data.
    """
    def __init__(self, fields: Dict[str, Any]):
        self._fields: Dict[str, fields] = {}

    def __init__(self,id: int, name: str, status: str, progress: float, peers: int, is_stalled: bool, totalSize: int, magnet_link: str, is_private: bool):
        self._fields["id"].value =id
        self._fields["name"].value=name
        self._fields["status"].value=status
        self._fields["progress"].value=progress
        self._fields["peers"].value=peers
        self._fields["is_stalled"].value=is_stalled
        self._fields["totalSize"].value=totalSize
        self._fields["magnetLink"].value=magnet_link
        self._fields["is_private"].value=is_private

    @property
    def id(self) -> int:
        """Returns the id for this torrent"""
        return self._fields["id"].value
    @property
    def name(self) -> str:
        """Returns the name of this torrent.

        Raise AttributeError if server don't return this field
        """
        return self.__getattr__("name")

    @property
    def status(self) -> str:
        """
        :rtype: Status

        Returns the torrent status. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        return self._fields["status"].value

    @property
    def progress(self) -> float:
        """
        Returns the torrent progress. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        return self._fields["progress"].value        
    @property
    def peers(self) -> int:
        """
        Returns the torrent peers. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        return self._fields["peers"].value        

    @property
    def is_stalled(self) -> bool:
        """
        Returns the torrent peers. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        # return false if  self._fields["progress"].value==100 | self._fields["is_stalled"].value        
        return self._fields["is_stalled"].value

    @property
    def totalSize(self) -> int:
        """
        Returns the torrent totalSize. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        return self._fields["totalSize"].value        

    @property
    def hash(self) -> str:
        """
        Returns the torrent hashString. Is either one of 'check pending', 'checking',
        'downloading', 'download pending', 'seeding', 'seed pending' or 'stopped'.
        The first two is related to verification.

        """
        return self._fields["hashString"].value        

    @property
    def magnet_link(self) -> int:
        """
        Returns the torrent magnetLink.
        """
        return self._fields["magnetLink"].value                        
    @property
    def isPrivate(self) -> bool:
        """
        Returns if torrent is private or public.
        """
        return self._fields["isPrivate"].value
    def sync_trackers(self, trackers):
        for tracker in trackers:
        #tr.update_trackers(tort.id,["udp://open.tracker.cl:1337/announce"])
            if tracker not in self.trackers:
                self.trackers.append(tracker)
