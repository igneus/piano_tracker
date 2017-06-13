import time
import threading

import mido

class Base(threading.Thread):
    """ abstract class; functionality common to all app threads """

    def __init__(self, stats, terminate):
        threading.Thread.__init__(self)

        # Thead property modifying it's behaviour
        self.daemon = True

        self.stats = stats
        self.terminate = terminate

class DisplayThread(Base):
    """ displays current stats """

    def run(self):
        while not self.terminate.is_set():
            print self.stats.stats()
            time.sleep(3)

class IOThread(Base):
    """ reads MIDI events, computes stats """

    def run(self):
        with mido.open_input() as inport:
            while not self.terminate.is_set():
                for message in inport.iter_pending():
                    self.stats.push(message)

                time.sleep(0.1)
