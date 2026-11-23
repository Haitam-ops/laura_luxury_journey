"""Prepare the existing static export without reading or modifying the CMS database."""
import json
import shutil
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from public_content import publish_payload


def main():
    for original, target, bounds in [
        ('manystarstravel-arch-star-light.png', 'manystarstravel-emblem-192.webp', (192, 192)),
        ('manystarstravel-arch-star.png', 'manystarstravel-emblem-dark-192.webp', (192, 192)),
        ('manystarstravel-favicon.png', 'manystarstravel-icon-96.png', (96, 96)),
        ('manystarstravel-favicon.png', 'manystarstravel-icon-16.png', (16, 16)),
        ('manystarstravel-favicon.png', 'manystarstravel-icon-32.png', (32, 32)),
        ('manystarstravel-favicon.png', 'manystarstravel-touch-180.png', (180, 180)),
    ]:
        image = Image.open(ROOT / 'assets/branding' / original).convert('RGBA')
        image.thumbnail(bounds, Image.Resampling.LANCZOS)
        output = ROOT / 'assets/branding' / target
        image.save(output, quality=88, method=6, optimize=True)
        shutil.copy2(output, ROOT / 'dist/assets/branding' / target)
        print(f'{target}: {output.stat().st_size} bytes')
    for name in ['manystarstravel-primary-logo.png', 'manystarstravel-social.jpg']:
        shutil.copy2(ROOT / 'assets/branding' / name, ROOT / 'dist/assets/branding' / name)
    for path in (ROOT / 'dist/data').glob('content.*.json'):
        payload = publish_payload(json.loads(path.read_text('utf-8')))
        path.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), 'utf-8')
    english = (ROOT / 'dist/data/content.en.json').read_bytes()
    (ROOT / 'dist/data/content.json').write_bytes(english)
    (ROOT / 'data/content.json').write_bytes(english)
    for name in ['index.html', 'styles.css', 'boot.js', 'app.js', 'gallery.js', 'route-map.js', 'seo.js', 'trip-finder.js']:
        shutil.copy2(ROOT / name, ROOT / 'dist' / name)
    # These are redundant export copies, never the editorial source files.
    # Keep the public data directory limited to the eight runtime payloads.
    export = (ROOT / 'dist').resolve()
    obsolete = [p for p in (export / 'data').rglob('*') if p.is_file()
                and not (p.parent == export / 'data' and (p.name == 'content.json' or p.name.startswith('content.')))]
    obsolete += [export / 'PHOTO-SOURCES.md', export / 'assets/sources.txt']
    removed = 0
    for path in obsolete:
        assert path.resolve().is_relative_to(export)
        if path.is_file():
            path.unlink()
            removed += 1
    print(f'Removed {removed} unused public research/source files; editorial originals retained.')


if __name__ == '__main__':
    main()
