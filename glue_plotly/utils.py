from re import match, sub

__all__ = ['cleaned_labels', 'mpl_ticks_values']


def cleaned_labels(labels):
    cleaned = [sub(r'\\math(default|regular)', r'\\mathrm', label) for label in labels]
    for j in range(len(cleaned)):
        label = cleaned[j]
        if '$' in label:
            cleaned[j] = '${0}$'.format(label.replace('$', ''))
    return cleaned


def mpl_ticks_values(axes, axis):
    index = 1 if axis == 'y' else 0
    minor_getters = [axes.get_xminorticklabels, axes.get_yminorticklabels]
    minor_ticks = minor_getters[index]()
    if not (minor_ticks and any(t.get_text() for t in minor_ticks)):
        return [], []
    major_getters = [axes.get_xticklabels, axes.get_yticklabels]
    major_ticks = major_getters[index]()
    vals, text = [], []
    for tick in major_ticks + minor_ticks:
        txt = tick.get_text()
        if txt:
            vals.append(tick.get_position()[index])
            text.append(txt)
        text = cleaned_labels(text)
    return vals, text


def opacity_value_string(a):
    asint = int(a)
    asfloat = float(a)
    n = asint if asint == asfloat else asfloat
    return str(n)


DECIMAL_PATTERN = "\\d+\\.?\\d*"
RGBA_PATTERN = f"rgba\\(({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN})\\)"


def rgba_string_to_values(rgba_str):
    m = match(RGBA_PATTERN, rgba_str)
    if not m or len(m.groups()) != 4:
        raise ValueError("Invalid RGBA expression")
    r, g, b, a = m.groups()
    return [r, g, b, a]


def is_rgba_hex(color):
    return color.startswith("#") and len(color) == 9


def is_rgb_hex(color):
    return color.starswith("#") and len(color) == 7


def rgba_hex_to_rgb_hex(color):
    return color[:-2]
