from PIL import Image, ImageDraw

def generate(stats, filename):
    """ generates graphic summarizing the recorded stats """

    size = (640, 480)
    bgcolour = '#fcc'
    image = Image.new('RGB', size, bgcolour)

    draw = ImageDraw.Draw(image)

    draw_keyboard(draw, size[0], KeyHeatmap(stats['keys']))

    image.save(filename)

def default_colour_func(key, default):
    return default

def draw_keyboard(draw, width, colour_func=default_colour_func):
    w = 20
    h = 5 * w

    midi_key = lambda x: x + 24

    # white keys
    key = 0
    for i, x in enumerate(xrange(0, width - w, w)):
        step = i % 7
        draw.rectangle([x, 0, x + w, h], colour_func(midi_key(key), '#fff'), '#000')

        if step == 2 or step == 6:
            key += 1
        else:
            key += 2

    # black keys
    key = 0
    for i, x in enumerate(xrange(0, width - w, w)):
        step = i % 7
        if step == 0 or step == 3:
            key += 1
            continue

        draw.rectangle([x - w/4, 0, x + w/4, h/2], colour_func(midi_key(key), '#000'), '#000')

        key += 2

class KeyHeatmap(object):
    """
    callable which can be used as colouring callback for draw_keyboard;
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
