import atexit
import logging
import os
import shutil
import sys
import threading
from argparse import ArgumentParser
from pathlib import Path

import coloredlogs
import requests
from cachetools import TTLCache, cached
from decouple import config

import web
from filesystem.FileSystemHandler import FileSystemHandler
from filesystem.folderwatcher import folderwatcher
from torrents.clients import InternalClient, TransmissionClient
from torrents.trackers import TrackerManager
from web import start


class Monitor:
    '''
    Main class for monitoring
    '''
    def __init__(self):
        self.logger = logging.getLogger('Monitor worker')
        uid = os.getuid()
        self.logger.debug('Running as uid: {0}'.format(uid))
        folder_watch = config('magnet_watch')
        # Make sure we have read permissions to
        if not os.access(folder_watch, os.R_OK):
            self.logger.error(
                "Watch directory: '{0}' doesn't exit or not readable by user {1}".format(
                    folder_watch, uid))
            sys.exit("Unable to read: '{0}' ".format(folder_watch))
        else:
            self.logger.debug(
                "Watch directory: '{0}' is readable".format(folder_watch))

        torrent_blackhole = config('torrent_blackhole', default=folder_watch)
        # Make sure we have read permissions to
        if not os.access(torrent_blackhole, os.W_OK):
            self.logger.error(
                "Blackhole: '{0}' doesn't exit or not writeable by user: {1}".format(
                    torrent_blackhole, uid))
            sys.exit(
                "Unable to read/write to: '{0}' ".format(torrent_blackhole))
        else:
            self.logger.debug(
                "Blackhole directory: '{0}' is writeable ".format(torrent_blackhole))

    @cached(cache=TTLCache(maxsize=500, ttl=86400))
    def load_trackers(self):
        trackers_from = config(
            'trackers',
            'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt')
        trackers = requests.get(trackers_from).content.decode(
            'utf8').split('\n\n')[:-1]
        self.logger.info('{0} trackers loaded.'.format(len(trackers)))
        return trackers

    def start(self):
        parser = ArgumentParser(
            description='A tool to convert magnet links to .torrent files')
        monitorparser = parser.add_argument_group(
            'Watch folder for magnet files and conver to torrent')
        monitorparser.add_argument(
            '--monitor', default=True, action='store_true')

        magnetparser = parser.add_argument_group('Process single magnet file')
        magnetparser.add_argument('-m', '--magnet', help='The magnet url')
        magnetparser.add_argument(
            '-o', '--output', help='The output torrent file name')

        args = vars(parser.parse_known_args()[0])

        output = None
        if args['output'] is not None:
            output = args['output']

        if len(sys.argv) == 1:
            self.logger.warning(
                'No arguments passed, defaulting to monitor mode')
            args['monitor'] = 'monitor'

        client = InternalClient(self.logger, self.load_trackers())
        if args['monitor'] is not None and args['monitor'] == 'monitor':
            self.logger.info('Starting monitor mode')
            folder_watch = config('magnet_watch')
            self.logger.info(
                'Blackhole folder: {0}'.format(
                    os.path.abspath(folder_watch)))
            output = config('torrent_blackhole', default=folder_watch)

            self.logger.info(
                'Processing existing files: {0}'.format(
                    os.path.abspath(folder_watch)))
            magnets = Path(folder_watch).glob('*.magnet')
            for magnet in magnets:
                self.logger.info(
                    'Processing file: {0}'.format(
                        os.path.basename(magnet)))
                magnet_contents = Path(magnet).read_text()
                self.logger.debug('Loading magnet: {0}'.format(magnet.name))
                torrent_path = client.magnet2torrent(magnet_contents, output)

                magnet_processed = str(os.path.abspath(magnet))
                if torrent_path is not None:
                    magnet_processed += '.processed'
                else:
                    magnet_processed += '.err'
                shutil.move(magnet, magnet_processed)

            folder_watcher = folderwatcher(
                folder_watch, FileSystemHandler(client))
            folder_watcher.start()
        elif args['magnet'] is not None:
            client.magnet2torrent(args['magnet'], output)


def main():
    # set thread name
    threading.current_thread().name = 'MAIN'
    logger = logging.getLogger('MAIN')
    coloredlogs.install(
        level=config(
            'log_level',
            default='debug'),
        fmt='[%(asctime)s] %(name)s[%(process)d]: %(message)s')
    logger.info('Starting program version: {0}')
    global APP
    try:
        logger.info(
            'Setting log level: {0}'.format(
                config(
                    'log_level',
                    default='debug')))

        webserver = threading.Thread(target=web.start, daemon=True)
        webserver.name = 'Web'
        webserver.start()

        if not config('transmission_host', default='') == '':
            client = TransmissionClient(
                config('transmission_host'), config(
                    'transmission_user', default=''), config(
                    'transmission_password', default=''), config(
                    'transmission_port', default=9091))
            tmanager = TrackerManager(
                client=client, interval=config(
                    'tracker_sync_interval', default=30 * 3600))
            trackerthread = threading.Thread(
                target=tmanager.start, daemon=True)
            trackerthread.name = 'Tracker Manager'
            trackerthread.start()
        APP = Monitor()
        appthread = threading.Thread(target=APP.start, daemon=True)
        appthread.name = 'Monitor'
        appthread.start()
        logger.info('Thread loading completed')
        appthread.join()
        logger.info('Program started')

    except SystemExit as sysex:
        logger.error('Critical error: {0}'.format(sysex))
    except KeyboardInterrupt as kex:
        logger.error('Keyboard interrupt: {0}'.format(kex))


if __name__ == '__main__':
    main()


@atexit.register
def _exithandler():
    logging.getLogger('MAIN').error('Program shutting down')
