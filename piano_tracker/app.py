from stats import Stats
from threads import DisplayThread, IOThread

def main():
    stats = Stats()

    threads = [
        DisplayThread(stats),
        IOThread(stats)
    ]

    map(lambda x: x.start(), threads)
    map(lambda x: x.join(), threads)
