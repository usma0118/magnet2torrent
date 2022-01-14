import coloredlogs,logging
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class folderwatcher:

    def __init__(self, directory='.', handler=PatternMatchingEventHandler(),logger=logging.Logger):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory
        logger = logging.getLogger(__name__)
        self.logger=logger

    def start(self):
        self.logger.error('Folder watcher is buggy and not stable')
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        self.logger.debug('Folder watcher started monitoring on: {}'.format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        self.logger.error('Watcher Terminated')