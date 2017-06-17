import time
import threading

import mido

from .sampled_stats import SampledStats

class Base(threading.Thread):
    """ abstract class; functionality common to all app threads """

    def __init__(self, stats, terminate):
        super().__init__()

        # Thead property modifying it's behaviour
        self.daemon = True

        self.stats = stats
        self.terminate = terminate

class DisplayThread(Base):
    """ displays current stats """

    def run(self):
        while not self.terminate.is_set():
            print(self.stats.stats())
            time.sleep(3)

class SamplingThread(Base):
    def __init__(self, stats, terminate, result_queue):
        super().__init__(stats, terminate)
        self._result_queue = result_queue

    def run(self):
        sampled_stats = SampledStats()
        while not self.terminate.is_set():
            sampled_stats.push(self.stats.stats())
            time.sleep(0.3)

        self._result_queue.put(sampled_stats.results())

class IOThread(Base):
    """ reads MIDI events, computes stats """

    def run(self):
        with mido.open_input() as inport:
            while not self.terminate.is_set():
                for message in inport.iter_pending():
                    self.stats.push(message)

                time.sleep(0.1)
