from cachetools import cached, TTLCache
import logging
import time
from torrents.clients.transmissionclient import TransmissionClient
import numpy

class Worker:
    def __init__(self,client:TransmissionClient,interval=30):
        '''
        interval: seconds between checks
        '''
        self.interval=interval
        self.client=client
        self.logger=logging.getLogger('Tracker sync')
        pass

    def run(self):
        self.logger.info('Tracker sync started')
        try:
            while True:
                time.sleep(self.interval)
        except:
            pass
            # self.observer.stop()
        self.logger.error('Tracker sync shutting down')
    
    def synch(self):
       torrents= self.client.get_torrents()
       global_trackers=self.load_trackers()
       for torrent in torrents:
           self.logger.debug('Processing torrent {0} with hash {1}'.format(torrent.id,torrent.hashString))
           self.logger.info('Checking torrent {0}'.format(torrent.name))
           if torrent.status != 'stopped' and not torrent.is_finished and not torrent.isPrivate :
               torrent_trackers=torrent._fields.get("trackers")
               t=[]
               for tracker_array in torrent_trackers:
                   if not type(tracker_array) is list:
                       continue
                   for tracker in tracker_array:
                    t.append(tracker['announce'])                    
               uniquelist=set(global_trackers).intersection(t)
               self.client.update_trackers(torrent.id,numpy.array(list(uniquelist)))

    @cached(cache=TTLCache(maxsize=1500,ttl=86400))
    def load_trackers(self):
        try:
            import requests
            trackers_from = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt'
            trackers = requests.get(trackers_from).content.decode('utf8').split('\n\n')[:-1]
            self.logger.info('{0} trackers loaded.'.format(len(trackers)))
            return trackers
        except Exception as e:
            self.logger.error('Failed to get trackers from {0}: {1}'.format(trackers_from, str(e)))
