import logging
import os
import coloredlogs
from watchdog.events import PatternMatchingEventHandler

import torrent

class FileSystemHandler(PatternMatchingEventHandler):
    def __init__(self,tclient):
        PatternMatchingEventHandler.__init__(self,patterns=['*.magnet'],ignore_directories=True)

        logger = logging.getLogger(__name__)
        coloredlogs.install(level='DEBUG',logger=logger,fmt='[ %(levelname)-8s ] [%(asctime)s] %(message)s')
        self.logger=logger
        self.client=tclient

    def on_created(self, event):
            self.logger.debug(event)
            self.logger.info('Processing file: {0}'.format(os.path.basename(event.src_path)))
            magnet_contents=os.path(event.src_path).read_text()
            self.client.magnet2torrent(magnet_contents,'')

    def on_moved(self,event):
            self.logger.debug(event)