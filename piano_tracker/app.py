import time
import threading

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
            time.sleep(0.5)

    except KeyboardInterrupt:
        terminate.set()
        map(lambda x: x.join(), threads)

        print
        print stats.final_stats()
