from asyncio.log import logger
from importlib.metadata import files
from pathlib import Path
from urllib import request
from decouple import config
import os
import os.path,time
from flask import render_template
from flask import Blueprint,redirect, url_for,request,flash
from flask_login import login_required, current_user
from torrent import transmission_client


main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    folder_watch = os.path.join(config('magnet_watch',default='blackhole'))

    # Show directory contents
    magnets=Path(folder_watch).glob('*.magnet*')
    files=[]
    for magnet in magnets:
        files.append({'name':magnet.name,'created':time.ctime(os.path.getctime(magnet)),'modified':time.ctime(os.path.getmtime(magnet))})

    return render_template('index.html', files=files)

@main.route('/torrents')
@login_required
def torrents():
    torrent_view=[]
    client=transmission_client(config("client_host"),config("client_username"),config("client_password"),port=config("client_port"))
    torrents=client.get_torrents()
    for torrent in torrents:
        torrent_view.append({'id':torrent.id,'name':torrent.name,'status':torrent.status,'progress':torrent.progress,"peers": torrent.peers, 'stalled':torrent.is_stalled,'size':torrent.totalSize,'hash':torrent.hashString,"magnet_url":torrent.magnetLink,"isPrivate":torrent.isPrivate})

    return render_template('torrents.html', torrents=torrent_view)

@main.route('/<path:path>')
@login_required
def info(path):
    return 'Not implemented'

@main.route('/delete', methods=['POST'])
@login_required
def remove_record():
    filename=request.form.get('file')
    filepath=os.path.normpath(os.path.join(config('magnet_watch',default='blackhole'),filename))
    if os.path.exists(filepath):
        os.remove(filepath)
    flash('File {0} deleted successfully'.format(filename),category='info')
    return redirect(url_for('main.index'))