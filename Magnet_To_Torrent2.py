#!/usr/bin/env python

import shutil
import tempfile
import os.path as pt
import sys
import libtorrent as lt
from time import sleep
from argparse import ArgumentParser
import coloredlogs, logging


def magnet2torrent(magnet, output_name=None):
    '''
    Converts magnet links to torrent
    '''
    if output_name and \
            not pt.isdir(output_name) and \
            not pt.isdir(pt.dirname(pt.abspath(output_name))):
        print("Invalid output folder: " + pt.dirname(pt.abspath(output_name)))
        print("")
        sys.exit(0)

    tempdir = tempfile.mkdtemp()
    ses = lt.session()
    params = {
        'save_path': tempdir,
        'storage_mode': lt.storage_mode_t(2)
    }
    handle = lt.add_magnet_uri(ses, magnet, params)

    print("Downloading Metadata (this may take a while)")
    while (not handle.has_metadata()):
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Aborting...")
            ses.pause()
            print("Cleanup dir " + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    ses.pause()
    print("Done")

    torinfo = handle.get_torrent_info()
    torfile = lt.create_torrent(torinfo)

    output = pt.abspath(torinfo.name() + ".torrent")

    if output_name:
        if pt.isdir(output_name):
            output = pt.abspath(pt.join(
                output_name, torinfo.name() + ".torrent"))
        elif pt.isdir(pt.dirname(pt.abspath(output_name))):
            output = pt.abspath(output_name)

    print("Saving torrent file here : " + output + " ...")
    torcontent = lt.bencode(torfile.generate())
    f = open(output, "wb")
    f.write(lt.bencode(torfile.generate()))
    f.close()
    print("Saved! Cleaning up dir: " + tempdir)
    ses.remove_torrent(handle)
    shutil.rmtree(tempdir)

    return output

def main():        
    logger = logging.getLogger(__name__)
    coloredlogs.install(level='DEBUG',logger=logger,fmt="[ %(levelname)-8s ] [%(asctime)s] %(message)s")
    
    parser = ArgumentParser(description="A tool to convert magnet links to .torrent files")
    monitorparser=parser.add_argument_group("Watch folder for magnet files and conver to torrent")
    monitorparser.add_argument("--monitor",default=True,action="store_true")

    magnetparser=parser.add_argument_group("Process single magnet file")
    magnetparser.add_argument('-m','--magnet', help='The magnet url')
    magnetparser.add_argument('-o','--output', help='The output torrent file name')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    args = vars(parser.parse_known_args()[0])
    
    magnet = None
    magnet=""
    output_name = None

    if args['monitor'] is not None:
        logger.info('Start folder watcher')
        sys.exit(0)
    else:
        if args['magnet'] is not None:
            magnet = args['magnet']
        if args['output'] is not None:
            output_name = args['output']
    magnet2torrent(magnet, output_name)


if __name__ == "__main__":
    main()
