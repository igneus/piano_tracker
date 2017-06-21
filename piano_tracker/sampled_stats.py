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

    def push(self, data):
        values = tuple(map(lambda x: data[x[0]], self._metric_columns()))
        placeholders = ','.join(['?'] * len(values))
        self.db.execute("INSERT INTO samples VALUES (datetime('now'), %s)" % placeholders, values)

    def results(self):
        cols = ', '.join(['avg(%s)' % c for c in self._metric_column_names()])
        group_by = "strftime('%Y-%m-%d %H:%M:%S', created_at)"
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
