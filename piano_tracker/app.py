import time
import threading

import graphic
from stats import Stats
from threads import DisplayThread, IOThread

def main():
    try:
        stats = Stats()
        terminate = threading.Event()

        threads = [
            DisplayThread(stats, terminate),
            IOThread(stats, terminate)
        ]

        map(lambda x: x.start(), threads)

        while threading.active_count() > 0:
            time.sleep(0.1)

    except KeyboardInterrupt:
        terminate.set()
        map(lambda x: x.join(), threads)

        final_stats = stats.final_stats()
        print
        print final_stats

        graphic.generate(final_stats, 'piano_tracker_graphic.png')
