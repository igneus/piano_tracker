from PIL import Image, ImageDraw

def generate(stats, filename):
    """ generates graphic summarizing the recorded stats """

    size = (640, 480)
    bgcolour = '#fcc'
    image = Image.new('RGB', size, bgcolour)

    draw = ImageDraw.Draw(image)

    keys = stats['keys'].keys()
    key_range = (min(keys), max(keys))
    heatmap = KeyHeatmap(stats['keys'])
    KeyboardDraw(key_range, size[0])(draw, heatmap)

    image.save(filename)

def default_colour_func(key, default):
    return default

class KeyboardDraw(object):
    """ draws part of a keyboard """

    def __init__(self, key_range, max_width):
        self._min_key = key_range[0]
        if self._black_key(self._min_key):
            self._min_key -= 1

        self._max_key = key_range[1]
        if self._black_key(self._max_key):
            self._max_key += 1

        self._max_width = max_width

    def __call__(self, draw, colour_func=default_colour_func):
        # white key dimensions
        white_keys = self._white_keys_in_range()
        w = self._max_width / white_keys
        w = min(w, 40)
        h = 5 * w

        offset = (self._max_width - (w * white_keys)) / 2

        # white keys
        i = 0
        for key in xrange(self._min_key, self._max_key + 1):
            x = offset + i * w
            if not self._black_key(key):
                draw.rectangle([x, 0, x + w, h], colour_func(key, '#fff'), '#000')
                i += 1

        # black keys
        i = 0
        for key in xrange(self._min_key, self._max_key + 1):
            x = offset + i * w
            if self._black_key(key):
                draw.rectangle([x - w/4, 0, x + w/4, h/2], colour_func(key, '#000'), '#000')
            else:
                i += 1

    def _black_key(self, key):
        return (key % 12) in (1, 3, 6, 8, 10)

    def _white_keys_in_range(self):
        whites = 0
        for i in xrange(self._min_key, self._max_key + 1):
            if not self._black_key(i):
                whites += 1
        return whites

class KeyHeatmap(object):
    """
    callable which can be used as colouring callback for KeyboardDraw;
    generates heatmap-like colours based on a dict mapping
    key ids to hit counts
    """

    def __init__(self, key_stats):
        self._key_stats = key_stats

        hit_values = self._key_stats.values()
        self._min_hits = min(hit_values)
        self._max_hits = max(hit_values)
        self._hit_range = self._max_hits - self._min_hits

    def __call__(self, key, default):
        """ colour of the given key """

        if key not in self._key_stats:
            return default

        return self._heatmap_colour(self._key_stats[key])

    def _heatmap_colour(self, hits):
        if self._hit_range == 0:
            hue_ratio = 1.0
        else:
            hue_ratio = 1.0 - (float(hits - self._min_hits) / self._hit_range)

        return 'hsl(%i, 100%%, 50%%)' % (360 * hue_ratio)
