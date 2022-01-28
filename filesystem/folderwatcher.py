import logging
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class folderwatcher:

    def __init__(self, directory='.', handler=PatternMatchingEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory
        self.logger=logging.getLogger('FolderWatcher')

    def start(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        self.logger.info('Folder watcher started')
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        self.logger.error('Watcher Shutting down')