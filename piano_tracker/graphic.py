from PIL import Image, ImageDraw

def generate(stats, filename):
    """ generates graphic summarizing the recorded stats """

    size = (640, 480)
    bgcolour = '#fcc'
    image = Image.new('RGB', size, bgcolour)

    draw = ImageDraw.Draw(image)

    hit_values = stats['keys'].values()
    min_hits = min(hit_values)
    max_hits = max(hit_values)

    heatmap_colour = lambda hits: 'hsl(%i, 100%%, 50%%)' % (360 * (1.0 - (float(hits - min_hits) / (max_hits - min_hits))))

    def colour_hit_keys(key, default):
        lowest_key = 24
        midi_key = key + lowest_key # zero based to MIDI numbering
        if midi_key not in stats['keys']:
            return default

        return heatmap_colour(stats['keys'][midi_key])

    draw_keyboard(draw, size[0], colour_hit_keys)

    image.save(filename)

def default_colour_func(key, default):
    return default

def draw_keyboard(draw, width, colour_func=default_colour_func):
    w = 20
    h = 5 * w

    # white keys
    key = 0
    for i, x in enumerate(xrange(0, width - w, w)):
        step = i % 7
        draw.rectangle([x, 0, x + w, h], colour_func(key, '#fff'), '#000')

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

        draw.rectangle([x - w/4, 0, x + w/4, h/2], colour_func(key, '#000'), '#000')

        key += 2
