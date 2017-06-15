import time

import pinject

"""
Each metric class subscribes to zero or more message types
and exposes a method returning the metric value.
It can also depend on other metrics. Dependencies are resolved
automatically by pinject.
"""

class Metric(object):
    """ Abstract class """

    def format(self):
        return self.value()

class TotalDuration(Metric):
    """ Duration in seconds, as float """

    name = 'duration'
    subscribe_to = []

    def __init__(self):
        self._started_at = time.time()

    def value(self):
        now = time.time()
        return now - self._started_at

    def format(self):
        idur = int(self.value())
        return '%02i:%02i' % (idur / 60, idur % 60)

class DurationMinutes(Metric):
    name = 'minutes'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, total_duration):
        pass

    def value(self):
        return self._total_duration.value() / 60

class MessageCount(Metric):
    name = 'messages'
    subscribe_to = ['*']

    def __init__(self):
        self._counter = 0

    def push(self, message):
        self._counter += 1

    def value(self):
        return self._counter

class NoteCount(MessageCount):
    name = 'notes'
    subscribe_to = ['note_on']

class NotesPerMinute(Metric):
    name = 'npm'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, note_count, duration_minutes):
        pass

    def value(self):
        return self._note_count.value() / self._duration_minutes.value()

    def format(self):
        return '%.2f' % self.value()
