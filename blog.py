"""Blog helpers: clean the HTML written in Pages CMS, and shrink uploaded images."""
import html
from html.parser import HTMLParser
from pathlib import Path

ALLOWED = {
    "p", "br", "h2", "h3", "h4", "strong", "b", "em", "i", "u", "s", "ul", "ol", "li",
    "a", "img", "blockquote", "table", "thead", "tbody", "tr", "th", "td", "hr", "figure", "figcaption", "code", "pre",
}
VOID = {"br", "img", "hr"}
DROP_WITH_CONTENT = {"script", "style", "iframe", "object", "embed", "form"}
ATTRS = {"a": {"href", "title"}, "img": {"src", "alt", "width", "height"}, "th": {"colspan", "rowspan"}, "td": {"colspan", "rowspan"}}
RENAME = {"h1": "h2", "h5": "h4", "h6": "h4"}


class _Cleaner(HTMLParser):
    def __init__(self, img_src, img_dims):
        super().__init__(convert_charrefs=True)
        self.out, self.skip, self.img_src, self.img_dims = [], 0, img_src, img_dims

    def handle_starttag(self, tag, attrs):
        if tag in DROP_WITH_CONTENT:
            self.skip += 1
            return
        tag = RENAME.get(tag, tag)
        if self.skip or tag not in ALLOWED:
            return
        keep = []
        for k, v in attrs:
            if k not in ATTRS.get(tag, ()) or v is None:
                continue
            if k == "href":
                if v.strip().lower().startswith(("javascript:", "data:", "vbscript:")):
                    continue
            if k == "src":
                if v.strip().lower().startswith(("javascript:", "data:")):
                    continue
                v = self.img_src(v)
            keep.append(f' {k}="{html.escape(v, quote=True)}"')
        if tag == "a" and any(a.startswith(' href="http') for a in keep):
            keep.append(' rel="noopener"')
        if tag == "img":
            src = next((a[6:-1] for a in keep if a.startswith(' src="')), "")
            if not any(a.startswith(" width=") for a in keep):
                keep.append(self.img_dims(html.unescape(src)))
            keep.append(' loading="lazy" decoding="async"')
        self.out.append(f"<{tag}{''.join(keep)}>")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag in DROP_WITH_CONTENT:
            self.skip = max(0, self.skip - 1)
            return
        tag = RENAME.get(tag, tag)
        if self.skip or tag not in ALLOWED or tag in VOID:
            return
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(html.escape(data, quote=False))


def clean_html(raw, img_src=lambda s: s, img_dims=lambda s: ""):
    c = _Cleaner(img_src, img_dims)
    c.feed(raw or "")
    c.close()
    return "".join(c.out)


def optimize_images(folder: Path, max_width=1400, quality=82):
    """Resize and recompress uploaded blog images in the build output (same file names, so links stay valid)."""
    if not folder.exists():
        return
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("Pillow absent: images du blog copiées sans optimisation")
        return
    for f in folder.rglob("*"):
        if f.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        try:
            im = ImageOps.exif_transpose(Image.open(f))
            if im.width > max_width:
                im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
            before = f.stat().st_size
            if f.suffix.lower() in {".jpg", ".jpeg"}:
                im.convert("RGB").save(f, "JPEG", quality=quality, optimize=True, progressive=True)
            elif f.suffix.lower() == ".webp":
                im.save(f, "WEBP", quality=quality, method=6)
            else:
                im.save(f, "PNG", optimize=True)
            print(f"image {f.name}: {before // 1024} Ko -> {f.stat().st_size // 1024} Ko")
        except Exception as e:  # never fail the build on one bad image
            print(f"image {f.name} non optimisée: {e}")
