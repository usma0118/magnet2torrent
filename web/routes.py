from importlib.metadata import files
from pathlib import Path
from urllib import request
from decouple import config
import os
import os.path,time
from flask import render_template
from flask import Blueprint,redirect, url_for,request,flash
from flask_login import login_required, current_user



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

@main.route('/<path:path>')
@login_required
def info(path):
    return 'Not implemented'

@main.route('/delete', methods=['POST'])
@login_required
def remove_record():
    filename=request.form.get('file')
    filename=os.path.join(config('magnet_watch',default='blackhole'),filename)
    if os.path.exists(filename):
        os.remove(filename)
    flash('File {0} deleted successfully'.format(request.form.get('file')),category='info')
    return redirect(url_for('main.index'))