from array import array
from transmission_rpc import Client

class transmission_client:
    def __init__(self,logger,host,username,password,path="/transmission",port=9091):
        self.logger=logger
        self.client=Client(host=host,path=path, port=port,username=username, password=password)
    
    def get_torrents(self):
        return self.client.get_torrents()

    def get_torrent(self,torrent_id):
        return self.client.get_torrent(torrent_id)

    def update_trackers(self,torrent_id:int,trackers:array):
        self.client.change_torrent(torrent_id,trackerAdd=trackers)
        self.client.reannounce_torrent(torrent_id)
