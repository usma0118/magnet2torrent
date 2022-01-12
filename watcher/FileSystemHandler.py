import logging
import coloredlogs
from watchdog.events import FileSystemEventHandler

class FileSystemHandler(FileSystemEventHandler):
    def __init__(self):
        logger = logging.getLogger(__name__)
        coloredlogs.install(level='DEBUG',logger=logger,fmt='[ %(levelname)-8s ] [%(asctime)s] %(message)s')
        self.logger=logger

    def on_created(self, event):
        if event.is_directory or not event.src_path[-5:] == '.magnet':
            self.logger.debug(event.src)