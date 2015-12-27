#!/usr/bin/env python

import logging
import argparse
import threading
import subprocess

import mirte
import mirte.main
import mirte.mirteFile
import sarah.coloredLogging

# TODO Volume control via Joyce.

class Launcher(object):
    def __init__(self):
        self.sleep_event = threading.Event()

    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--verbose', '-v', action='count', dest='verbosity')
        parser.add_argument('--host', '-H', type=str, default='localhost')
        parser.add_argument('--port', '-p', type=int, default=8080)
        parser.add_argument('--path', '-P', type=str, default='/')
        self.args = parser.parse_args()

    def main(self):
        self.parse_args()
        if self.args.verbosity >= 1:
            sarah.coloredLogging.basicConfig(level=logging.DEBUG,
                                    formatter=mirte.main.MirteFormatter())
        subprocess.call(['amixer', 'set', 'Master', 'unmute'],
                            stdout=subprocess.PIPE)
        subprocess.call(['amixer', 'set', 'Master', '50%'],
                            stdout=subprocess.PIPE)
        subprocess.call(['amixer', 'set', 'PCM', 'unmute'],
                            stdout=subprocess.PIPE)
        subprocess.call(['amixer', 'set', 'PCM', '0dB'],
                            stdout=subprocess.PIPE)
        self.mirte_manager = m = mirte.get_a_manager()
        mirte.mirteFile.load_mirteFile('pynijmegen', m)
        mirte.mirteFile.load_mirteFile('joyce/comet', m)
        self.joyceClent = m.create_instance('joyceClient', 'cometJoyceClient',
                                        {'host': self.args.host,
                                         'port': self.args.port,
                                         'path': self.args.path})
        self.client = m.create_instance('pynijmegen', 'pynijmegen',
                                        {'joyceClent': 'joyceClient'})
        self.sleep_event.wait()

if __name__ == '__main__':
    Launcher().main()

# vim: et:sta:bs=2:sw=4:
