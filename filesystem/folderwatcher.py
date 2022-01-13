import coloredlogs,logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class folderwatcher:

    def __init__(self, directory='.', handler=FileSystemEventHandler()):
        self.observer = Observer()
        self.handler = handler
        self.directory = directory
        logger = logging.getLogger(__name__)
        coloredlogs.install(level='DEBUG',logger=logger,fmt='[ %(levelname)-8s ] [%(asctime)s] %(message)s')
        self.logger=logger

    def start(self):
        self.observer.schedule(
            self.handler, self.directory, recursive=True)
        self.observer.start()
        self.logger.debug('\nWatcher Running in {}/\n'.format(self.directory))
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
        self.observer.join()
        self.logger.error('\nWatcher Terminated\n')