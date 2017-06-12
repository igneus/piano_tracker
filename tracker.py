import mido
import threading
import time

class Stats:
    """ thread-safe message aggregator """

    def __init__(self):
        self._lock = threading.Lock()
        self._messages = 0
        self._notes = 0
        self._started_at = time.time()

    def push(self, midi_msg):
        with self._lock:
            self._messages += 1

            if midi_msg.type == 'note_on':
                self._notes += 1

    def stats(self):
        with self._lock:
            duration = self._duration()
            minutes = duration / 60

            return {
                'messages': self._messages,
                'notes': self._notes,
                'time': self._format_duration(duration),
                'npm': (self._notes / minutes)
            }

    def _duration(self):
        now = time.time()
        return now - self._started_at

    def _format_duration(self, duration):
        idur = int(duration)
        return '%i:%i' % (idur / 60, idur % 60)


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

stats = Stats()
threads = [
    DisplayThread(stats),
    IOThread(stats)
]

map(lambda x: x.start(), threads)
map(lambda x: x.join(), threads)
