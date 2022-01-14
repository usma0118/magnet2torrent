import os
from os import path
import shutil
import sys
import atexit
from pathlib import Path
from argparse import ArgumentParser
from time import sleep
import tempfile
import logging
import coloredlogs
import libtorrent as lt
from decouple import config
from filesystem.folderwatcher import folderwatcher
from filesystem.FileSystemHandler import FileSystemHandler



logger = logging.getLogger(__name__)
coloredlogs.install(level=config('log_level',default='debug'),logger=logger,fmt='[%(asctime)s] %(message)s')

trackers=[]

try:
    import requests
    #TODO: Cache trackers for 12 hours
    trackers_from = 'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_all.txt'
    trackers = requests.get(trackers_from).content.decode('utf8').split('\n\n')[:-1]
    logger.info('Loaded trackers: {0}'.format(len(trackers)))
except Exception as e:
    logger.debug('Failed to get trackers from {0}: {1}'.format(trackers_from, str(e)))
    trackers = []

def magnet2torrent(magnet_uri, output_name=None):
    '''
    Converts magnet links to torrent
    '''
    if output_name and \
            not path.isdir(output_name) and \
            not path.isdir(path.dirname(path.abspath(output_name))):
        logger.debug('Invalid output folder: {0}'.format(path.dirname(path.abspath(output_name))))
        sys.exit(0)

    settings = {
    'enable_dht': False,
    'use_dht_as_fallback': False,
    'enable_lsd': False,
    'enable_upnp': False,
    'enable_natpmp': True,
    'announce_to_all_tiers': True,
    'announce_to_all_trackers': True,
    'aio_threads': 4*2,
    }
    torrentclient = lt.session(settings)

    params=None
    try:
        params = lt.parse_magnet_uri(magnet_uri)
    except RuntimeError as re:
        logger.error('Invalid magnet uri: {0}, skipping'.format(magnet_uri))
        logger.error('Exception: {0}'.format(str(re)))
        return

    # prevent downloading
    # https://stackoverflow.com/q/45680113
    if isinstance(params, dict):
        params['flags'] |= lt.add_torrent_params_flags_t.flag_upload_mode
    else:
        params.flags |= lt.add_torrent_params_flags_t.flag_upload_mode
    # https://python.hotexamples.com/examples/libtorrent/-/parse_magnet_uri/python-parse_magnet_uri-function-examples.html
    tempdir = tempfile.mkdtemp()
    params.save_path=tempdir
    params.trackers += trackers

    # download = self.findTorrentByHash(info_hash)
    handle = torrentclient.add_torrent(params)
    logger.info('Acquiring torrent metadata for hash {}'.format(params.info_hash))
    max=5
    while not handle.has_metadata():
        try:
            sleep(0.1)
            max -=0.1
            if max <0:
                break
        except KeyboardInterrupt:
            logger.debug('Aborting...')
            torrentclient.pause()
            logger.debug('Cleanup dir ' + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    torrentclient.pause()

    if not handle.has_metadata():
        logger.error('Unable to get data for {0}'.format(params.name))
        torrentclient.remove_torrent(handle)
        shutil.rmtree(tempdir)
        return

    torinfo = handle.get_torrent_info()
    torfile = lt.create_torrent(torinfo)

    output = path.abspath(torinfo.name() + '.torrent')

    if output_name:
        if path.isdir(output_name):
            output = path.abspath(path.join(
                output_name, torinfo.name() + '.torrent'))
        elif path.isdir(path.dirname(path.abspath(output_name))):
            output = path.abspath(output_name)

    torcontent = lt.bencode(torfile.generate())
    with open(output, 'wb') as f:
        f.write(torcontent)
        logger.info('Torrent saved: {0}'.format(output))
    logger.debug('Cleaning up temp dir: {0}'.format(tempdir))
    torrentclient.remove_torrent(handle)
    shutil.rmtree(tempdir)
    return output

def main():
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
            torrent_path=magnet2torrent(magnet_contents,output)

            magnet_processed=str(os.path.abspath(magnet))
            if torrent_path is not None:
                magnet_processed+='.processed'
            else:
                magnet_processed+='.err'
            shutil.move(magnet,magnet_processed)

        folder_watcher=folderwatcher(folder_watch,FileSystemHandler(),logger)
        folder_watcher.start()
    elif args['magnet'] is not None:
        magnet2torrent(args['magnet'], output)


if __name__ == '__main__':
    #https://github.com/blind-oracle/transmission-trackers/blob/master/transmission-trackers.py
    main()

@atexit.register
def _exithandler():
    logger.error('[Main thread:] Program shutting down')