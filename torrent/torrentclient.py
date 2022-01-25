import sys
import os
from os import path
import logging
import tempfile
from time import sleep
import libtorrent as lt
import shutil

class torrentclient:
    def __init__(self,logger,trackers):
        self.logger=logger
        self.trackers=trackers

    def magnet2torrent(self,magnet_uri, output_name=None):
        '''
        Converts magnet links to torrent
        '''
        if output_name and \
                not path.isdir(output_name) and \
                not path.isdir(path.dirname(path.abspath(output_name))):
            self.logger.debug('Invalid output folder: {0}'.format(path.dirname(path.abspath(output_name))))
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
            self.logger.error('Invalid magnet uri: {0}, skipping'.format(magnet_uri))
            self.logger.error('Exception: {0}'.format(str(re)))
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
        # TODO: Only add missing trackers
        params.trackers += self.trackers

        # download = self.findTorrentByHash(info_hash)
        handle = torrentclient.add_torrent(params)
        self.logger.info('Acquiring torrent metadata for hash {}'.format(params.info_hash))
        max=5
        while not handle.has_metadata():
            try:
                sleep(0.1)
                max -=0.1
                if max <0:
                    break
            except KeyboardInterrupt:
                self.logger.debug('Aborting...')
                torrentclient.pause()
                self.logger.debug('Cleanup dir ' + tempdir)
                shutil.rmtree(tempdir)
                sys.exit(0)
        torrentclient.pause()

        if not handle.has_metadata():
            self.logger.error('Unable to get data for {0}'.format(params.name))
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
            self.logger.info('Torrent saved: {0}'.format(output))
        self.logger.debug('Cleaning up temp dir: {0}'.format(tempdir))
        torrentclient.remove_torrent(handle)
        shutil.rmtree(tempdir)
        return output