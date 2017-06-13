import time
import threading

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
