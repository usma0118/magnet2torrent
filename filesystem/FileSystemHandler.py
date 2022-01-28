import os
from pathlib import Path
import shutil
from watchdog.events import PatternMatchingEventHandler
from decouple import config
import logging
class FileSystemHandler(PatternMatchingEventHandler):
    def __init__(self,tclient):
        PatternMatchingEventHandler.__init__(self,patterns=['*.magnet'],ignore_directories=True)
        self.logger=logging.getLogger('Worker')
        self.client=tclient

    def on_created(self, event):
        self.logger.debug(event)
        self.on_action(event.src_path)

    def on_moved(self,event):
        self.logger.debug(event)
        self.on_action(event.dest_path)

    def on_action(self,magnet):
        magnet_processed=str(os.path.abspath(magnet))
        self.logger.info('Processing file: {0}'.format(magnet))
        magnet_contents=Path(magnet).read_text()
        torrent_path=self.client.magnet2torrent(magnet_contents,config('torrent_blackhole',os.path.dirname(magnet)))
        if torrent_path is not None:
            magnet_processed+='.processed'
        else:
            magnet_processed+='.err'
        shutil.move(magnet,magnet_processed)
