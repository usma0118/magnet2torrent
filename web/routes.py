from importlib.metadata import files
from pathlib import Path
from decouple import config
import os
import os.path,time
from flask import render_template
from web import app

@app.route('/')
def index():
    folder_watch = os.path.join(config('magnet_watch',default='blackhole'))

    # Show directory contents
    magnets=Path(folder_watch).glob('*.magnet*')
    files=[]
    for magnet in magnets:
        files.append({'name':magnet.name,'created':time.ctime(os.path.getctime(magnet)),'modified':time.ctime(os.path.getmtime(magnet))})

    return render_template('index.html', files=files)

@app.route('/<name>')
def info(file):
    return ''