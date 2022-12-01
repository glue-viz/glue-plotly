from re import sub

__all__ = ['cleaned_labels', 'ticks_values']


def cleaned_labels(labels):
    cleaned = [sub(r'\\math(default|regular)', r'\\mathrm', label) for label in labels]
    for j in range(len(cleaned)):
        label = cleaned[j]
        if '$' in label:
            cleaned[j] = '${0}$'.format(label.replace('$', ''))
    return cleaned


def ticks_values(axes, axis):
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