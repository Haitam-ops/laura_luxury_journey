"""Keep place names exactly as supplied in the original trip copy."""
from pathlib import Path
from collections import Counter
import json
import re
import unicodedata

PLACES = json.loads((Path(__file__).parent / 'data/itinerary-place-names.json').read_text('utf-8'))
LOCAL_NAMES = json.loads((Path(__file__).parent / 'data/place-names-localized.json').read_text('utf-8'))


def normalized(text):
    chars, offsets = [], []
    for i, char in enumerate(text):
        char = char.replace('’', "'").replace('‘', "'").replace('–', '-').replace('‑', '-')
        for c in unicodedata.normalize('NFKD', char).casefold():
            if not unicodedata.combining(c):
                chars.append(c)
                offsets.append(i)
    return ''.join(chars), offsets


def matches(text, aliases):
    value, offsets = normalized(text)
    candidates = []
    for name, forms in aliases.items():
        for form in set([name, *forms]):
            needle = normalized(form)[0]
            for match in re.finditer(r'(?<!\w)' + re.escape(needle) + r'(?!\w)', value):
                candidates.append((offsets[match.start()], offsets[match.end()-1]+1, name))
    selected = []
    for start, end, name in sorted(candidates, key=lambda m: (-(m[1]-m[0]), m[0])):
        if not any(start < b and end > a for a, b, _ in selected):
            selected.append((start, end, name))
    return sorted(selected)


def source_places(source):
    return Counter(name for _, _, name in matches(source, {n: [] for n in PLACES}))


def protect(source, translated, code='en'):
    expected = source_places(source)
    aliases = {n: PLACES[n] + [values[n] for values in LOCAL_NAMES.values() if n in values] for n in expected}
    found = matches(translated, aliases)
    for start, end, name in reversed(found):
        if start and translated[start-1] == '"' and end < len(translated) and translated[end] == '"':
            start -= 1
            end += 1
        # Local forms are recognized only to restore the original name.
        translated = translated[:start] + name + translated[end:]
    return translated, expected, Counter(n for _, _, n in found)


def restore_tree(source, translated):
    if isinstance(source, str) and isinstance(translated, str):
        return protect(source, translated)[0]
    if isinstance(source, list) and isinstance(translated, list):
        return [restore_tree(a, b) for a, b in zip(source, translated)] if len(source) == len(translated) else translated
    return translated
