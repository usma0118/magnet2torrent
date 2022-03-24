from transmission_rpc import Client

class transmission_client:
    def __init__(self):
        # self.logger=logger
        self.client=Client(host='transmission.antaresinc.home', port=80,username='secrets', password='alpha123')
    
    def get_torrents(self):
        return self.client.get_torrents()

    def get_torrent(self,torrent_id):
        return self.client.get_torrent(torrent_id)

    def update_trackers(self,torrent_id,trackers):
        self.client.change_torrent(torrent_id,trackerAdd=trackers)
        self.client.reannounce_torrent(torrent_id)
        return

# if __name__ == '__main__':
#     tr=transmission_client()
#     t=tr.list()
#     for tort in t:
#         print(tort.name)
#         print(tort.hashString)
#         trackers=tort._fields.get("trackers")
#         for t1 in trackers[0]:
#             print(t1.get("announce"))
#         tr.update_trackers(tort.id,["udp://open.tracker.cl:1337/announce"])
#         print()