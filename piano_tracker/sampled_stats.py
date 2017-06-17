import sqlite3

class SampledStats:
    columns = [
        ['id', 'INTEGER PRIMARY KEY'],
        ['notes_playing', 'INTEGER'],
        ['recent_notes', 'INTEGER'],
    ]

    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        column_spec = ', '.join(map(lambda x: '%s %s' % (x[0], x[1]), self.columns[1:]))
        self.db.execute('CREATE TABLE samples (%s)' % column_spec)

    def push(self, data):
        values = tuple(map(lambda x: data[x[0]], self.columns[1:]))
        placeholders = ','.join(['?'] * len(values))
        self.db.execute('INSERT INTO samples VALUES (%s)' % placeholders, values)

    def results(self):
        items = self.db.execute('SELECT * FROM samples')
        intensity = map(self._intensity, items)

        while intensity[0] == 0 and intensity[1] == 0:
            intensity.pop(0)
        while intensity[-1] == 0 and intensity[-2] == 0:
            intensity.pop()

        return {'intensity': intensity}

    def _intensity(self, record):
        # counts in polyphony and speed
        return record[0] + record[1]
