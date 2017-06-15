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

class TimeFormatted(object):
    """ Mixin. Implements time formatting """

    def format(self):
        idur = int(self.value())
        return '%02i:%02i' % (idur / 60, idur % 60)

class FloatFormatted(object):
    """ Mixin. Implements float formatting """

    def format(self):
        return '%.2f' % self.value()

class TotalDuration(TimeFormatted, Metric):
    """ Duration in seconds, as float """

    name = 'duration'
    subscribe_to = []

    def __init__(self):
        self._started_at = time.time()

    def value(self):
        now = time.time()
        return now - self._started_at

class PlayingDuration(TimeFormatted, Metric):
    """ Time when some note was being played, in seconds, as float """

    name = "playing_duration"
    subscribe_to = ['note_on', 'note_off']

    def __init__(self):
        self._buffer = 0.0
        self._started_at = None
        self._notes_playing = 0

    def value(self):
        now = time.time()
        running = 0
        if self._playing():
            running = now - self._started_at

        return self._buffer + running

    def push(self, message):
        now = time.time()

        if message.type == 'note_on':
            if not self._playing():
                self._started_at = now
            self._notes_playing += 1
        elif message.type == 'note_off':
            if self._notes_playing > 0:
                self._notes_playing -= 1
                if self._notes_playing == 0:
                    self._buffer += (now - self._started_at)
                    self._started_at = None
        else:
            raise TypeError('Unexpected message type %s' % message.type)

    def _playing(self):
        return self._notes_playing > 0

class DurationMinutes(Metric):
    name = 'minutes'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, total_duration):
        pass

    def value(self):
        return self._total_duration.value() / 60

class PlayingDurationMinutes(Metric):
    name = 'minutes'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, playing_duration):
        pass

    def value(self):
        return self._playing_duration.value() / 60

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

class NotesPerMinute(FloatFormatted, Metric):
    name = 'npm'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, note_count, duration_minutes):
        pass

    def value(self):
        return self._note_count.value() / self._duration_minutes.value()

class NotesPerPlayingMinute(FloatFormatted, Metric):
    name = 'nppm'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, note_count, playing_duration_minutes):
        pass

    def value(self):
        if self._playing_duration_minutes.value() == 0.0:
            return 0

        return self._note_count.value() / self._playing_duration_minutes.value()
