import sys
from os import path
import tempfile
from time import sleep
import libtorrent as lt
from decouple import config
import shutil
import math

class InternalClient:
    settings = {
        'enable_dht': False,
        'use_dht_as_fallback': False,
        'enable_lsd': False,
        'enable_upnp': False,
        'enable_natpmp': True,
        'announce_to_all_tiers': True,
        'announce_to_all_trackers': True,
        'aio_threads': 4*2
        }

    def __init__(self,logger,trackers):
        self.logger=logger
        self.trackers=trackers
        proxy_url={'hostname':config('proxy_hostname',default=''),
        'port':config('proxy_port',default=''),
        'username':config('proxy_username',default=''),
        'password':config('proxy_password',default='')
        }

        # proxy_url = urlparse(http_proxy)
        if proxy_url.get('hostname') and proxy_url.get('port'):
            self.logger.info('Applying proxy settings')
            self.settings.update({
                    'proxy_hostname': proxy_url.get('hostname'),
                    'proxy_port': int(proxy_url.get('port')),
                    'proxy_type': lt.proxy_type_t.http,
                    'force_proxy': True,
                    'anonymous_mode': True,
                })

        if proxy_url.get('username') or proxy_url.get('password'):
            self.settings.update({
                    'proxy_username': proxy_url.get('username'),
                    'proxy_password': proxy_url.get('password'),
                    'proxy_type': lt.proxy_type_t.http_pw
                })
        self.torrentclient = lt.session(self.settings)

    def magnet2torrent(self,magnet_uri, output_name=None):
        '''
        Converts magnet links to torrent
        '''
        if output_name and \
                not path.isdir(output_name) and \
                not path.isdir(path.dirname(path.abspath(output_name))):
            self.logger.debug('Invalid output folder: {0}'.format(path.dirname(path.abspath(output_name))))
            sys.exit(0)

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
        #if params.keys.cont not params.isPrivate:
        if isinstance(params, dict):
            params['trackers'] += self.trackers
        else:
            params.trackers += self.trackers

        # download = self.findTorrentByHash(info_hash)
        handle = self.torrentclient.add_torrent(params)
        self.logger.info('Acquiring torrent metadata for hash {}'.format(params.info_hash))
        max=10
        while not handle.has_metadata():
            try:
                sleep(0.1)
                max -=0.1
                if max <0:
                    break
            except KeyboardInterrupt:
                self.logger.debug('Aborting...')
                self.torrentclient.pause()
                self.logger.debug('Cleanup dir ' + tempdir)
                shutil.rmtree(tempdir)
                sys.exit(0)
        self.torrentclient.pause()

        if not handle.has_metadata():
            self.logger.error('Unable to get data for {0}'.format(params.name))
            self.torrentclient.remove_torrent(handle)
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
        self.torrentclient.remove_torrent(handle)
        shutil.rmtree(tempdir)
        return output

from array import array
from transmission_rpc import Client

class TransmissionClient:
    '''
    Transmission RPC client
    '''
    def __init__(self,host,username,password,port=9091,path='/transmission/rpc'):
        self._client=Client(host=host,path=path, port=port,username=username, password=password)

    def get_torrents(self):
        '''
        Returns a list of torrents
        '''
        return self._client.get_torrents()

    def get_torrent(self,torrent_id):
        '''
        Gets a torrent by id
        '''
        return self._client.get_torrent(torrent_id)

    def add_torrent(self,magnet:str):
        return self._client.add_torrent(magnet)


    def update_trackers(self,torrent_id:int,trackers):
        '''
        Update the trackers for a torrent
        '''
        tracker_slice=[]
        for item in trackers:
            tracker_slice.append(item)
            if len(tracker_slice) == 9:
                self._client.change_torrent(torrent_id,trackerAdd=tracker_slice)
                tracker_slice= []

    def reannounce_torrent(self,torrent_id):
        self._client.reannounce_torrent(torrent_id)
