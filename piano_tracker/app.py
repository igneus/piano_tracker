import time
import threading

from . import graphic
from .stats import Stats
from .threads import DisplayThread, SamplingThread, IOThread
from queue import Queue

def main():
    try:
        stats = Stats()
        terminate = threading.Event()
        hand_over_data = Queue(maxsize=1)

        threads = [
            DisplayThread(stats, terminate),
            SamplingThread(stats, terminate, hand_over_data),
            IOThread(stats, terminate)
        ]

        for x in threads:
            x.start()

        while threading.active_count() > 0:
            time.sleep(0.1)

    except KeyboardInterrupt:
        terminate.set()
        for x in threads:
            x.join()

        final_stats = stats.final_stats()
        print
        print(final_stats)

        sampled_stats = hand_over_data.get()

        graphic.generate(final_stats, sampled_stats, 'piano_tracker_graphic.png')
