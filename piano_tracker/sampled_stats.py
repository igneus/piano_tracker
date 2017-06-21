import time
import sqlite3

class SampledStats:
    columns = [
        ['id', 'INTEGER PRIMARY KEY'],
        ['created_at', 'TEXT'],
        ['notes_playing', 'INTEGER'],
        ['recent_notes', 'INTEGER'],
    ]

    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        column_spec = ', '.join(map(lambda x: '%s %s' % (x[0], x[1]), self.columns[1:]))
        self.db.execute('CREATE TABLE samples (%s)' % column_spec)

        self._started_at = time.time()

    def push(self, data):
        values = tuple(map(lambda x: data[x[0]], self._metric_columns()))
        placeholders = ','.join(['?'] * len(values))
        self.db.execute("INSERT INTO samples VALUES (datetime('now'), %s)" % placeholders, values)

    def results(self, granularity=None):
        cols = ', '.join(['avg(%s)' % c for c in self._metric_column_names()])

        if granularity is None:
            granularity = 'seconds'

            time_span = time.time() - self._started_at # in seconds
            if time_span > 360:
                granularity = 'tenseconds'
            elif time_span > 1000:
                granularity = 'minutes'
            elif time_span > 7200:
                granularity = 'tenminutes'
            elif time_span > 36000:
                granularity = 'hours'

        timestamp = "strftime('%Y-%m-%d %H:%M:%S', created_at)"
        tstamp_substr = lambda cut_end: 'substr(%s, 1, %i)' % (timestamp, 19 - cut_end)
        if granularity == 'seconds':
            group_by = timestamp
        elif granularity == 'tenseconds':
            group_by = tstamp_substr(1)
        elif granularity == 'minutes':
            group_by = tstamp_substr(3)
        elif granularity == 'tenminutes':
            group_by = tstamp_substr(4)
        elif granularity == 'hours':
            group_by = tstamp_substr(6)
        else:
            raise ValueError('unsupported granularity %s' % granularity)

        items = self.db.execute('SELECT %s FROM samples GROUP BY %s ORDER BY created_at ASC' % (cols, group_by))
        intensity = [self._intensity(i) for i in items]

        while len(intensity) > 2 and intensity[0] == 0 and intensity[1] == 0:
            intensity.pop(0)
        while len(intensity) > 2 and intensity[-1] == 0 and intensity[-2] == 0:
            intensity.pop()

        return {'intensity': intensity}

    def _intensity(self, record):
        # counts in polyphony and speed
        return record[0] + record[1]

    def _metric_columns(self):
        return self.columns[2:]

    def _metric_column_names(self):
        for i in self._metric_columns():
            yield i[0]
