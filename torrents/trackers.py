import logging
import time

from cachetools import TTLCache, cached

from torrents.clients import TransmissionClient


class TrackerManager:
    def __init__(self, client: TransmissionClient, interval=30):
        '''
        interval: seconds between checks
        '''
        self.interval = interval
        self.client = client
        self.logger = logging.getLogger('Tracker sync')
        pass

    def start(self):
        self.logger.info('Tracker sync started')
        try:
            while True:
                self.sync()
                time.sleep(self.interval)
        except Exception as e:
            self.logger.error('Critical error: {0}'.format(e))
        except SystemExit as sysex:
            self.logger.error('Critical error: {0}'.format(sysex))
        except KeyboardInterrupt as kex:
            self.logger.error('Keyboard interrupt: {0}'.format(kex))
        self.logger.error('Tracker sync shutting down')

    def sync(self):
        torrents = self.client.get_torrents()
        global_trackers = self.load_trackers()
        for torrent in torrents:
            self.logger.info('Processing Torrent: {0}'.format(torrent.name))
            self.logger.debug(
                'torrent {0} with hash {1}'.format(
                    torrent.id, torrent.hashString))
            self.logger.debug('Torrent status: {0}'.format(torrent.status))
            if torrent.status != 'stopped' and torrent.status != 'seeding' and not torrent.is_finished and not torrent.isPrivate:
                torrent_trackers = torrent._fields.get('trackers')
                flatten_trackers = []
                for tracker_array in torrent_trackers:
                    if not isinstance(tracker_array, list):
                        continue
                    for tracker in tracker_array:
                        flatten_trackers.append(tracker['announce'])
                unique_trackers = []
                self.logger.debug(
                    'Existing tracker count: {0}'.format(
                        len(flatten_trackers)))
                for gtracker in global_trackers:
                    if gtracker not in flatten_trackers:
                        unique_trackers.append(gtracker)
                if len(unique_trackers) == 0:
                    self.logger.info('No new trackers to update')
                    continue
                try:
                    self.client.update_trackers(torrent.id, unique_trackers)
                    self.client.reannounce_torrent(torrent.id)
                    self.logger.info(
                        '{0} trackers to be added'.format(
                            len(unique_trackers)))
                    self.logger.debug(
                        'Expected count: {0}'.format(
                            len(unique_trackers) +
                            len(flatten_trackers)))
                except Exception as exeption:
                    self.logger.error(
                        'Failed to update trackers with error: {0}'.format(exeption))
            else:
                self.logger.debug('Expected count: {0}'.format(torrent.status))
            self.logger.info('---------')

    @cached(cache=TTLCache(maxsize=1500, ttl=86400))
    def load_trackers(self):
        try:
            import requests
            trackers_from = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt'
            trackers = requests.get(trackers_from).content.decode(
                'utf8').split('\n\n')[:-1]
            self.logger.info('{0} trackers loaded.'.format(len(trackers)))
            return trackers
        except Exception as exeption:
            self.logger.error(
                'Failed to get trackers from {0}: {1}'.format(
                    trackers_from, str(exeption)))
