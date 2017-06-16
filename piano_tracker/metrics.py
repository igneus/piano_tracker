import time

import pinject

"""
Each metric class subscribes to zero or more message types
and exposes a method returning the metric value.
It can also depend on other metrics. Dependencies are autowired
by MetricsProvider.
"""

class Metric(object):
    """ Abstract class """

    def value(self):
        """ current value of the metric """
        return None

    def format(self):
        """ value formatted for displaying to the user """
        return self.value()

    def push(self, message):
        """ processes incoming messages """
        pass

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
    subscribe_to = ['note_on', 'note_off']

    def __init__(self):
        self._started_at = None
        self._ended_at = None

    def value(self):
        if self._started_at is None:
            return 0.0

        if self._ended_at is None:
            now = time.time();
            return now - self._started_at

        return self._ended_at - self._started_at

    def push(self, message):
        now = time.time()
        if message.type == 'note_on' and self._started_at is None:
            self._started_at = now
        elif message.type == 'note_off':
            self._ended_at = now

class PlayingDuration(TimeFormatted, Metric):
    """ Time when some note was being played, in seconds, as float """

    name = "playing_duration"
    subscribe_to = ['note_on', 'note_off']

    def __init__(self):
        self._buffer = 0.0
        self._started_at = None
        self._ended_at = None
        self._notes_playing = 0

        self.max_short_pause = 5 # seconds

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
                if self._ended_at is not None and (now - self._ended_at) < self.max_short_pause:
                    # short pause - include it in playing time
                    self._started_at = self._ended_at
                    self._ended_at = None
                else:
                    self._started_at = now
            self._notes_playing += 1
        elif message.type == 'note_off':
            if self._notes_playing > 0:
                self._notes_playing -= 1
                if self._notes_playing == 0:
                    self._buffer += (now - self._started_at)
                    self._started_at = None
                    self._ended_at = now
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
        if self._duration_minutes.value() == 0.0:
            return 0.0

        return self._note_count.value() / self._duration_minutes.value()

class NotesPerPlayingMinute(FloatFormatted, Metric):
    name = 'nppm'
    subscribe_to = []

    @pinject.copy_args_to_internal_fields
    def __init__(self, note_count, playing_duration_minutes):
        pass

    def value(self):
        if self._playing_duration_minutes.value() == 0.0:
            return 0.0

        return self._note_count.value() / self._playing_duration_minutes.value()

class NoteCountPerPitch(Metric):
    name = 'keys'
    subscribe_to = ['note_on']

    def __init__(self):
        self._keys = {}

    def push(self, message):
        note = message.note
        if note not in self._keys:
            self._keys[note] = 1
        else:
            self._keys[note] += 1

    def value(self):
        return self._keys
