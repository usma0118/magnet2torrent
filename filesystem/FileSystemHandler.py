import os
from pathlib import Path
from watchdog.events import PatternMatchingEventHandler
from decouple import config

class FileSystemHandler(PatternMatchingEventHandler):
    def __init__(self,tclient,logger):
        PatternMatchingEventHandler.__init__(self,patterns=['*.magnet'],ignore_directories=True)
        self.logger=logger
        self.client=tclient

    def on_created(self, event):
        self.logger.debug(event)
        self.on_action(self,event.src_path)

    def on_moved(self,event):
        self.logger.debug(event)
        self.on_action(event.dest_path)

    def on_action(self,src):
        self.logger.info('Processing file: {0}'.format(os.path.basename(src)))
        magnet_contents=Path(src).read_text()
        self.client.magnet2torrent(magnet_contents,config('torrent_blackhole',os.path.dirname(src)))