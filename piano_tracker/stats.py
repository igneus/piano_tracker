import time
import threading

import pinject

from metrics import *

class Stats(object):
    """ thread-safe message aggregator """

    def __init__(self):
        self._lock = threading.Lock()

        metric_classes = [
            TotalDuration,
            MessageCount,
            NoteCount,
            NotesPerMinute,
        ]
        obj_graph = pinject.new_object_graph()
        self._metrics = map(lambda x: obj_graph.provide(x), metric_classes)

        self._listeners = {}
        for metric in self._metrics:
            for message_type in metric.subscribe_to:
                if message_type not in self._listeners:
                    self._listeners[message_type] = []
                self._listeners[message_type].append(metric)

    def push(self, midi_msg):
        with self._lock:
            self.push_to_listeners(midi_msg.type, midi_msg)
            self.push_to_listeners('*', midi_msg)

    def push_to_listeners(self, listened_to, midi_msg):
        if listened_to in self._listeners:
            for l in self._listeners[listened_to]:
                l.push(midi_msg)

    def stats(self):
        with self._lock:
            return {m.name:m.format() for m in self._metrics}

    def final_stats(self):
        return self.stats() # TODO
