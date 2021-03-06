import tempfile
from PIL import Image, ImageDraw, ImageFont
from matplotlib.font_manager import FontManager, FontProperties
import matplotlib.pyplot as plot

def generate(stats, sampled_stats, filename):
    """ generates graphic summarizing the recorded stats """

    size = (640, 480)
    bgcolour = '#ddddeeff'
    image = Image.new('RGBA', size, bgcolour)

    draw = ImageDraw.Draw(image)

    keys = stats['keys'].keys()
    if len(keys) == 0:
        keys = [0]
    key_range = (min(keys), max(keys))
    heatmap = KeyHeatmap(stats['keys'])
    KeyboardDraw(key_range, size[0])(draw, heatmap)

    font_size = 16
    font_prop = FontProperties(('Open Sans', 'Liberation Sans', 'Arial', 'sans-serif'), size=font_size)
    font_path = FontManager().findfont(font_prop)
    font = ImageFont.truetype(font_path, font_size)

    draw.text((30, 400), 'total time: %s' % stats['duration'], font=font, fill='#000')
    draw.text((320, 400), 'playing time: %s' % stats['playing_duration'], font=font, fill='#000')
    draw.text((30, 430), 'notes per minute: %s' % stats['nppm'], font=font, fill='#000')

    intensity = sampled_stats['intensity']
    figure = plot.figure(figsize=(size[0] / 100.0, 1.5), dpi=100)
    plot.axis('off')
    plot.plot(intensity)

    with tempfile.NamedTemporaryFile(suffix='.png') as fp:
        figure.savefig(fp.name, transparent=True)

        graph_img = Image.open(fp.name)

    image.paste(graph_img, (0, 220), graph_img)

    image.save(filename)

def default_colour_func(key, default):
    return default

class KeyboardDraw:
    """ draws part of a keyboard """

    # default colours
    white = '#fff'
    black = '#000'
    outline = '#000'

    def __init__(self, key_range, max_width):
        self._min_key = key_range[0]
        if self._black_key(self._min_key):
            self._min_key -= 1

        self._max_key = key_range[1]
        if self._black_key(self._max_key):
            self._max_key += 1

        # at least one octave should be drawn:
        while (self._max_key - self._min_key) < 11:
            if (self._min_key % 12) != 0:
                self._min_key -= 1
            else:
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
        for key in range(self._min_key, self._max_key + 1):
            x = offset + i * w
            if not self._black_key(key):
                draw.rectangle([x, 0, x + w, h], colour_func(key, self.white), self.outline)
                i += 1

        # black keys
        i = 0
        for key in range(self._min_key, self._max_key + 1):
            x = offset + i * w
            if self._black_key(key):
                draw.rectangle([x - w/4, 0, x + w/4, h * 0.6], colour_func(key, self.black), self.outline)
            else:
                i += 1

    def _black_key(self, key):
        return (key % 12) in (1, 3, 6, 8, 10)

    def _white_keys_in_range(self):
        whites = 0
        for i in range(self._min_key, self._max_key + 1):
            if not self._black_key(i):
                whites += 1
        return whites

class KeyHeatmap:
    """
    callable which can be used as colouring callback for KeyboardDraw;
    generates heatmap-like colours based on a dict mapping
    key ids to hit counts
    """

    def __init__(self, key_stats):
        self._key_stats = key_stats

        hit_values = self._key_stats.values()
        if len(hit_values) == 0:
            hit_values = [0]
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

        return 'hsl(%i, 90%%, 50%%)' % (360 * hue_ratio)
