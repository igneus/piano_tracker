import time
import threading

from .metrics_provider import MetricsProvider

class Stats:
    """ thread-safe message aggregator """

    def __init__(self):
        self._lock = threading.Lock()
        self._listeners = {}

        provider = MetricsProvider(observable=self)
        metrics = [
            'total_duration',
            'playing_duration',
            #'message_count',
            'note_count',
            'notes_per_minute',
            'notes_per_playing_minute',
            'notes_playing',
            'recent_notes',
        ]
        self._metrics = [provider.provide(x) for x in metrics]

        final_metrics = [
            'total_duration',
            'playing_duration',
            'message_count',
            'note_count',
            'notes_per_minute',
            'notes_per_playing_minute',
            'note_count_per_pitch',
        ]
        self._final_metrics = [provider.provide(x) for x in final_metrics]

    def add_listener(self, listener, message_types):
        """ registers a listener """
        for message_type in message_types:
            if message_type not in self._listeners:
                self._listeners[message_type] = []
            self._listeners[message_type].append(listener)

    def push(self, midi_msg):
        """ entry-point for incoming messages """
        with self._lock:
            self._push_to_listeners(midi_msg.type, midi_msg)
            self._push_to_listeners('*', midi_msg)

    def _push_to_listeners(self, listened_to, midi_msg):
        if listened_to in self._listeners:
            for l in self._listeners[listened_to]:
                l.push(midi_msg)

    def stats(self):
        """ stats displayed repeatedly during the session """
        with self._lock:
            return {m.name:m.format() for m in self._metrics}

    def final_stats(self):
        """ summary stats displayed at the end of the session """
        with self._lock:
            return {m.name:m.format() for m in self._final_metrics}
