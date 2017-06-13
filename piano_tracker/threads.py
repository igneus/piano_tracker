import time
import threading

import mido

class DisplayThread(threading.Thread):
    """ displays current stats """

    def __init__(self, stats):
        threading.Thread.__init__(self)
        self.stats = stats

    def run(self):
        while True:
            time.sleep(3)
            print self.stats.stats()

class IOThread(threading.Thread):
    """ reads MIDI events, computes stats """

    def __init__(self, stats):
        threading.Thread.__init__(self)
        self.stats = stats

    def run(self):
        with mido.open_input() as inport:
            for message in inport:
                self.stats.push(message)
