from pathlib import Path
root = Path(__file__).resolve().parents[1]
path = root / 'gallery.js'
text = path.read_text(encoding='utf-8')
replacements = {
    '${escape(photos[0].caption)}</span></p>': '${escape(photos[0].caption)}</span><span class="gallery-current-credit">${credit(photos[0])}</span></p>',
    "viewer.querySelector('#lightbox-caption').textContent=m.caption;": "viewer.querySelector('#lightbox-caption').innerHTML=escape(m.caption)+credit(m);",
    "root.querySelector('.gallery-current-caption').textContent=m.caption;": "root.querySelector('.gallery-current-caption').textContent=m.caption;root.querySelector('.gallery-current-credit').innerHTML=credit(m);",
}
for old, new in replacements.items():
    assert old in text, old
    text = text.replace(old, new)
path.write_text(text, encoding='utf-8')
with (root / 'styles.css').open('a', encoding='utf-8') as css:
    css.write('\n/* Photograph attribution remains available in galleries and the full-screen viewer. */\n.photo-credit{display:block;margin-top:8px;font-size:11px;line-height:1.6;font-weight:400;letter-spacing:0;color:inherit;opacity:.85;overflow-wrap:anywhere}.photo-credit a{color:inherit;text-decoration:underline;text-underline-offset:2px}.photo-viewer .photo-credit{max-width:760px;margin:8px auto 0}\n')
