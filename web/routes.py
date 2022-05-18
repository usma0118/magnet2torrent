from pathlib import Path
from urllib import request
import os
import os.path
import time
from decouple import config
from flask import render_template
from flask import Blueprint,redirect, url_for,flash
from flask_login import login_required
from torrents.clients import TransmissionClient

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    '''
    Index method
    '''
    folder_watch = os.path.join(config('magnet_watch',default='blackhole'))

    # Show directory contents
    torrent_extensions = ['*.magnet*', '*.torrent*']
    magnets = []
    for torrent_extension in torrent_extensions:
        files=Path(folder_watch).glob(torrent_extension)
        magnets += files
    files=[]
    for magnet in magnets:
        if '.torrent' in magnet.name:
            files.append({'name':magnet.name,'magnet_url': '', 'created':time.ctime(os.path.getctime(magnet)),'modified':time.ctime(os.path.getmtime(magnet))})
        else:
            files.append({'name':magnet.name,'magnet_url': magnet.read_text(),'created':time.ctime(os.path.getctime(magnet)),'modified':time.ctime(os.path.getmtime(magnet))})

    return render_template('index.html', files=files)

@main.route('/torrents')
@login_required
def torrents():
    torrent_view=[]
    client=TransmissionClient(config('transmission_host'),config('transmission_user'),config('transmission_password'),port=config('transmission_port'),path=config('transmission_path',default='/transmission/rpc'))
    client_torrents=client.get_torrents()
    for trt in client_torrents:
        torrent_view.append({'id':trt.id,'name':trt.name,'status':trt.status,'progress': round(float(trt.progress)),'peers': trt.peers, 'stalled':trt.is_stalled,'size':trt.totalSize,'hash':trt.hashString,'magnet_url':trt.magnetLink,'isPrivate':trt.isPrivate})

    return render_template('torrents.html', torrents=torrent_view)

#@main.route('/torrent/<torrent_id:int>')
@login_required
def get_torrent(torrent_id):
    torrent_view=[]
    return render_template('torrents.html', torrents=torrent_view)

@main.route('/<path:path>')
@login_required
def info(path):
    return 'Not implemented'

@main.route('/delete', methods=['POST'])
@login_required
def remove_record():
    filename=request.form.get('file')
    filepath=os.path.normpath(os.path.join(config('magnet_watch', default='blackhole'),filename))
    if os.path.exists(filepath):
        os.remove(filepath)
    flash('File {0} deleted successfully'.format(filename), category='info')
    return redirect(url_for('main.index'))