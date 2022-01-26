from email.policy import default
import os
import atexit
from pathlib import Path
from argparse import ArgumentParser
import shutil
import sys
import threading
from time import sleep
import logging
import coloredlogs
from decouple import config
from filesystem.folderwatcher import folderwatcher
from filesystem.FileSystemHandler import FileSystemHandler
from torrent import torrentclient
from cachetools import cached, TTLCache

class monitor:
    def __init__(self,logger):
        self.logger=logger

    @cached(cache=TTLCache(maxsize=500,ttl=86400))
    def load_trackers(self):
        try:
            import requests
            #TODO: Cache trackers for 12 hours
            trackers_from = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt'
            trackers = requests.get(trackers_from).content.decode('utf8').split('\n\n')[:-1]
            self.logger.info('Loaded trackers: {0}'.format(len(trackers)))
            return trackers
        except Exception as e:
            self.logger.error('Failed to get trackers from {0}: {1}'.format(trackers_from, str(e)))

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
            self.logger.warning('No arguments passed, defaulting to monitor mode')
            args['monitor']='monitor'

        client=torrentclient(self.logger,self.load_trackers())
        if args['monitor'] is not None:
            self.logger.info('Starting monitor mode')
            folder_watch=config('magnet_watch')
            self.logger.info('Blackhole folder: {0}'.format(os.path.abspath(folder_watch)))
            output=config('torrent_blackhole',default=folder_watch)

            self.logger.info('Processing existing files: {0}'.format(os.path.abspath(folder_watch)))
            magnets=Path(folder_watch).glob('*.magnet')
            for magnet in magnets:
                self.logger.info('Processing file: {0}'.format(os.path.basename(magnet)))
                magnet_contents=Path(magnet).read_text()
                self.logger.debug('Loading magnet: {0}'.format(magnet.name))
                torrent_path=client.magnet2torrent(magnet_contents,output)

                magnet_processed=str(os.path.abspath(magnet))
                if torrent_path is not None:
                    magnet_processed+='.processed'
                else:
                    magnet_processed+='.err'
                shutil.move(magnet,magnet_processed)

            folder_watcher=folderwatcher(folder_watch,FileSystemHandler(client,self.logger),self.logger)
            folder_watcher.start()
        elif args['magnet'] is not None:
            client.magnet2torrent(args['magnet'], output)

    def run_web(self):
        from web import app
        from waitress import serve
        self.logger.info('[Main thread]: Started waitress server on port: *:{0}{1}'.format(config('webserver_port',default='8080'),config('webserver_basepath',default='/')))
        #serve(app, host='127.0.0.1',port=config('webserver_port',default='8080'),url_prefix=config('webserver_basepath',default=''))
        app.run(host='127.0.0.1',port=config('webserver_port',default='8080'),debug=True)

if __name__ == '__main__':

    logger = logging.getLogger(__name__)
    coloredlogs.install(level=config('log_level',default='debug'),logger=logger,fmt='[%(asctime)s] %(message)s')
    logger.info('[Main thread]: Starting program version: {0}')
    logger.info('[Main thread]: Setting log level: {0}'.format(config('log_level',default='debug')))

    program=monitor(logger)
    thread=threading.Thread(target=program.run_web, daemon=True)
    thread.start()
    program.main()

@atexit.register
def _exithandler():
    logger.error('[Main thread]: Program shutting down')