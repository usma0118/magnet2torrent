import os
import atexit
from pathlib import Path
from argparse import ArgumentParser
import shutil
import sys
from time import sleep
import logging
import coloredlogs
from decouple import config
from filesystem.folderwatcher import folderwatcher
from filesystem.FileSystemHandler import FileSystemHandler
from torrent import torrentclient

class monitor:
    def __init__(self,logger):
        self.logger=logger
        try:
            import requests
            #TODO: Cache trackers for 12 hours
            trackers_from = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt'
            self.trackers = requests.get(trackers_from).content.decode('utf8').split('\n\n')[:-1]
            logger.info('Loaded trackers: {0}'.format(len(self.trackers)))
        except Exception as e:
            logger.error('Failed to get trackers from {0}: {1}'.format(trackers_from, str(e)))
            self.trackers = []

    def main(self):
        parser = ArgumentParser(description='A tool to convert magnet links to .torrent files')
        monitorparser=parser.add_argument_group('Watch folder for magnet files and conver to torrent')
        monitorparser.add_argument('--monitor',default=True,action='store_true')

        magnetparser=parser.add_argument_group('Process single magnet file')
        magnetparser.add_argument('-m','--magnet', help='The magnet url')
        magnetparser.add_argument('-o','--output', help='The output torrent file name')

        args = vars(parser.parse_known_args()[0])

        output = None
        if args['output'] is not None:
            output = args['output']

        if len(sys.argv) == 1:
            logger.warning('No arguments passed, defaulting to monitor mode')
            args['monitor']='monitor'

        client=torrentclient(logger,self.trackers)
        if args['monitor'] is not None:
            logger.info('Starting monitor mode')
            folder_watch=config('magnet_watch')
            logger.info('Blackhole folder: {0}'.format(os.path.abspath(folder_watch)))
            output=config('torrent_blackhole',default=folder_watch)

            logger.info('Processing existing files: {0}'.format(os.path.abspath(folder_watch)))
            magnets=Path(folder_watch).glob('*.magnet')
            for magnet in magnets:
                logger.info('Processing file: {0}'.format(os.path.basename(magnet)))
                magnet_contents=Path(magnet).read_text()
                logger.debug('Loading magnet: {0}'.format(magnet.name))
                torrent_path=client.magnet2torrent(magnet_contents,output)

                magnet_processed=str(os.path.abspath(magnet))
                if torrent_path is not None:
                    magnet_processed+='.processed'
                else:
                    magnet_processed+='.err'
                shutil.move(magnet,magnet_processed)

            folder_watcher=folderwatcher(folder_watch,FileSystemHandler(client),logger)
            folder_watcher.start()
        elif args['magnet'] is not None:
            client.magnet2torrent(args['magnet'], output)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    coloredlogs.install(level=config('log_level',default='debug'),logger=logger,fmt='[%(asctime)s] %(message)s')

    #https://github.com/blind-oracle/transmission-trackers/blob/master/transmission-trackers.py
    main=monitor(logger)
    main.main()

@atexit.register
def _exithandler():
    logger.error('[Main thread:] Program shutting down')