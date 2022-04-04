from array import array
from transmission_rpc import Client

class TransmissionClient:
    def __init__(self,host,username,password,port=9091,path='/transmission/rpc'):
        self._client=Client(host=host,path=path, port=port,username=username, password=password)
    
    def get_torrents(self):
        return self._client.get_torrents()

    def get_torrent(self,torrent_id):
        return self._client.get_torrent(torrent_id)

    def update_trackers(self,torrent_id:int,trackers:array):
        self._client.change_torrent(torrent_id,trackerAdd=trackers)
        self._client.reannounce_torrent(torrent_id)