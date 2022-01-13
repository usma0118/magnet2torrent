#!/usr/bin/env python
import os
import shutil
import tempfile
import os.path as pt
import sys
import libtorrent as lt
from time import sleep
from argparse import ArgumentParser
import logging
import coloredlogs
from decouple import config
from pathlib import Path
from filesystem.folderwatcher import folderwatcher
from filesystem.FileSystemHandler import FileSystemHandler


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG',logger=logger,fmt='[ %(levelname)-8s ] [%(asctime)s] %(message)s')

def magnet2torrent(magnet_uri, output_name=None):
    '''
    Converts magnet links to torrent
    '''
    if output_name and \
            not pt.isdir(output_name) and \
            not pt.isdir(pt.dirname(pt.abspath(output_name))):
        logger.debug('Invalid output folder: {0}'.format(pt.dirname(pt.abspath(output_name))))
        sys.exit(0)

    tempdir = tempfile.mkdtemp()
    client = lt.session()
    options = {
        'save_path': tempdir,
        'storage_mode': lt.storage_mode_t(2)
    }
    params = lt.parse_magnet_uri(magnet_uri)
    # prevent downloading
    # https://stackoverflow.com/q/45680113
    if isinstance(params, dict):
        params['flags'] |= lt.add_torrent_params_flags_t.flag_upload_mode
    else:
        params.flags |= lt.add_torrent_params_flags_t.flag_upload_mode
    # https://python.hotexamples.com/examples/libtorrent/-/parse_magnet_uri/python-parse_magnet_uri-function-examples.html
    # params['info_hash'] = hex_to_hash(str(params['info_hash']).decode('hex'))
    params.save_path=tempdir

    # download = self.findTorrentByHash(info_hash)
    handle = client.add_torrent(params)
    logger.debug('Acquiring torrent metadata for hash {}'.format(params.info_hash))
    while not handle.has_metadata():
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            logger.debug('Aborting...')
            client.pause()
            logger.debug('Cleanup dir ' + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    client.pause()
    logger.debug('Processing torrent info')
    torinfo = handle.get_torrent_info()
    torfile = lt.create_torrent(torinfo)

    output = pt.abspath(torinfo.name() + '.torrent')

    if output_name:
        if pt.isdir(output_name):
            output = pt.abspath(pt.join(
                output_name, torinfo.name() + '.torrent'))
        elif pt.isdir(pt.dirname(pt.abspath(output_name))):
            output = pt.abspath(output_name)

    torcontent = lt.bencode(torfile.generate())
    with open(output, 'wb') as f:
        f.write(torcontent)
        logger.info('Torrent saved: {0}'.format(output))
    logger.debug('Cleaning up temp dir: {0}'.format(tempdir))
    client.remove_torrent(handle)
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

    magnet = None
    magnet=''
    output = None

    if args['output'] is not None:
        output = args['output']

    if len(sys.argv) == 1:
        logger.warning('No arguments passed, defaulting to monitor mode')
        args['monitor']='monitor'

    if args['monitor'] is not None:
        logger.info('Starting monitor mode')
        folder_watch=config('torrent_blackhole')
        logger.info('blackhole folder: {0}'.format(os.path.abspath(folder_watch)))
        output=config('torent_drop',default=folder_watch)

        #TODO: Process existing files 1st
        logger.info('Processing existing files: {0}'.format(os.path.abspath(folder_watch)))
        magnets=Path(folder_watch).glob('*.magnet')
        for magnet in magnets:
            logger.info('Processing file: {0}'.format(os.path.basename(magnet)))
            magnet_contents=Path(magnet).read_text()
            logger.debug('Loading magnet: {0}'.format(magnet_contents))
            torrent_path=magnet2torrent(magnet_contents,output)
            if torrent_path is not None:
                magnet_processed=str(os.path.abspath(magnet))+'.processed'
                shutil.move(magnet,magnet_processed)

        #TODO: Start file watcher to look for new files.
        logger.info('Start folder watcher on {0}'.format(folder_watch))
        folder_watcher=folderwatcher(folder_watch,FileSystemHandler())
        folder_watcher.start()
    else:
        if args['magnet'] is not None:
            magnet = args['magnet']
        magnet2torrent(magnet, output)


if __name__ == '__main__':
    main()
