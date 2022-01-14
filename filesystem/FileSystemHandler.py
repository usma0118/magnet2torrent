import logging
import coloredlogs
from watchdog.events import PatternMatchingEventHandler

class FileSystemHandler(PatternMatchingEventHandler):
    def __init__(self):
        PatternMatchingEventHandler.__init__(self,patterns=['*.magnet'],ignore_directories=True)
        logger = logging.getLogger(__name__)
        coloredlogs.install(level='DEBUG',logger=logger,fmt='[ %(levelname)-8s ] [%(asctime)s] %(message)s')
        self.logger=logger

    def on_created(self, event):
            self.logger.debug(event)

    def on_moved(self,event):
            self.logger.debug(event)