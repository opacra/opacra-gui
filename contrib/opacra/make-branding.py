#!/usr/bin/env python3
"""Opacra Wallet: draw the wallet's logo images in the current Opacra look (opacra.org, Nov 2026).

The mark is the site's: an amber ring (#ffc98b) on night (#070a12); the wordmark is
"Opacra" in Hanken Grotesk 500, ivory (#f6efe3).

    python3 contrib/opacra/make-branding.py <path to hanken-500.ttf>

Writes into images/ (same file names the wallet already loads).
"""
import io, os, struct, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

NIGHT = (7, 10, 18)
NIGHT2 = (12, 17, 28)
PANEL = (17, 23, 37)
AMBER = (255, 201, 139)
EMBER = (255, 157, 92)
IVORY = (246, 239, 227)
INK = (17, 17, 17)
DARK_AMBER = (163, 92, 26)  # for the light theme (readable on white)

SS = 8  # supersampling
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
IMG = os.path.join(ROOT, "images")
font_path = sys.argv[1]


def ring(draw, cx, cy, r, w, colour):
    draw.ellipse([cx - r - w / 2, cy - r - w / 2, cx + r + w / 2, cy + r + w / 2], fill=colour)
    draw.ellipse([cx - r + w / 2, cy - r + w / 2, cx + r - w / 2, cy + r - w / 2], fill=(0, 0, 0, 0))


def ring_layer(size, cx, cy, r, w, colour):
    """A ring on its own transparent layer (so the hole stays transparent)."""
    W, H = size
    layer = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = colour if len(colour) == 4 else colour + (255,)
    d.ellipse([(cx - r - w / 2) * SS, (cy - r - w / 2) * SS, (cx + r + w / 2) * SS, (cy + r + w / 2) * SS], fill=c)
    d.ellipse([(cx - r + w / 2) * SS, (cy - r + w / 2) * SS, (cx + r - w / 2) * SS, (cy + r - w / 2) * SS], fill=(0, 0, 0, 0))
    return layer.resize((W, H), Image.LANCZOS)


def mark(px):
    """The app icon: rounded night square with the amber ring (site's mark.svg, 64-unit grid)."""
    k = px / 64.0
    big = Image.new("RGBA", (px * SS, px * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, px * SS - 1, px * SS - 1], radius=14 * k * SS, fill=NIGHT + (255,))
    im = big.resize((px, px), Image.LANCZOS)
    im.alpha_composite(ring_layer((px, px), 32 * k, 32 * k, 19 * k, 7 * k, AMBER))
    return im


def save_ico(path, sizes):
    imgs = [mark(s) for s in sizes]
    imgs[-1].save(path, format="ICO", sizes=[(s, s) for s in sizes], append_images=imgs[:-1])


def save_icns(path):
    # ICNS with PNG payloads: ic07 128, ic08 256, ic09 512, ic10 1024
    chunks = b""
    for tag, s in ((b"ic07", 128), (b"ic08", 256), (b"ic09", 512), (b"ic10", 1024)):
        buf = io.BytesIO(); mark(s).save(buf, "PNG"); data = buf.getvalue()
        chunks += tag + struct.pack(">I", len(data) + 8) + data
    with open(path, "wb") as f:
        f.write(b"icns" + struct.pack(">I", len(chunks) + 8) + chunks)


def wordmark(w, h, ring_colour, text_colour, with_ring=True):
    """Titlebar logo: ring + 'Opacra' (like the site header), transparent background."""
    big = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    font = ImageFont.truetype(font_path, int(h * 0.62 * SS))
    x = 0
    if with_ring:
        r = h * 0.30; sw = h * 0.11
        cx, cy = r + sw / 2 + h * 0.06, h / 2
        lay = ring_layer((w, h), cx, cy, r, sw, ring_colour).resize((w * SS, h * SS), Image.LANCZOS)
        big.alpha_composite(lay)
        x = (cx + r + sw / 2 + h * 0.24) * SS
    bbox = d.textbbox((0, 0), "Opacra", font=font)
    ty = (h * SS - (bbox[3] - bbox[1])) / 2 - bbox[1]
    d.text((x, ty), "Opacra", font=font, fill=text_colour + (255,))
    return big.resize((w, h), Image.LANCZOS)


TINTS = [  # one per account card; night base, gently warm/cool variations
    (34, 26, 18), (18, 28, 40), (22, 34, 32), (36, 22, 24),
    (28, 24, 38), (30, 30, 22), (16, 30, 36), (30, 26, 30),
]


def card(w, h, tint, light=False):
    s = w / 260.0
    base = Image.new("RGBA", (w, h))
    px = base.load()
    top = (250, 247, 241) if light else tuple(min(255, NIGHT2[i] + tint[i]) for i in range(3))
    bot = (240, 235, 226) if light else NIGHT
    for y in range(h):
        for x in range(w):
            t = (x / w * 0.45 + y / h * 0.55)
            px[x, y] = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
    # rounded corners
    mask = Image.new("L", (w * SS, h * SS), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], radius=10 * s * SS, fill=255)
    base.putalpha(mask.resize((w, h), Image.LANCZOS))
    # big faint ring on the right (the eclipse motif, kept quiet)
    faint = (163, 92, 26, 40) if light else AMBER + (30,)
    ring_big = ring_layer((w, h), 208 * s, 85 * s, 62 * s, 26 * s, faint)
    glow = ring_big.filter(ImageFilter.GaussianBlur(6 * s))
    clip = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    clip.alpha_composite(glow); clip.alpha_composite(ring_big)
    a = clip.getchannel("A"); a = Image.composite(a, Image.new("L", (w, h), 0), base.getchannel("A"))
    clip.putalpha(a)
    base.alpha_composite(clip)
    # small mark top left
    base.alpha_composite(ring_layer((w, h), 22 * s, 22 * s, 7 * s, 3 * s, DARK_AMBER if light else AMBER))
    return base


def main():
    for s in (16, 24, 32, 48, 64, 96, 128, 256):
        mark(s).save(os.path.join(IMG, "appicons", f"{s}x{s}.png"))
    save_ico(os.path.join(IMG, "appicon.ico"), [16, 24, 32, 48, 64, 128, 256])
    save_icns(os.path.join(IMG, "appicon.icns"))

    for suffix, k in (("", 1), ("@2x", 2)):
        wordmark(125 * k, 28 * k, AMBER, IVORY).save(os.path.join(IMG, f"titlebarLogo{suffix}.png"))
        wordmark(125 * k, 28 * k, DARK_AMBER, INK).save(os.path.join(IMG, "themes", "white", f"titlebarLogo{suffix}.png"))
        for i, t in enumerate(TINTS):
            card(260 * k, 135 * k, t).save(os.path.join(IMG, f"card-background-black{i}{suffix}.png"))
        card(260 * k, 135 * k, (0, 0, 0), light=True).save(os.path.join(IMG, f"card-background-white{suffix}.png"))
    # merchant page header logo (on an amber band): dark wordmark, no ring
    wordmark(132, 22, NIGHT, NIGHT, with_ring=False).save(os.path.join(IMG, "moneroLogo_white.png"))

    with open(os.path.join(IMG, "monero-vector.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">\n'
                '  <circle cx="32" cy="32" r="24" fill="none" stroke="#ffc98b" stroke-width="9"/>\n</svg>\n')
    print("branding images written to", IMG)


main()


def recolour_purple_to_amber():
    """The interface icons were tinted purple in the first rebrand; turn that purple into the site's amber."""
    import colorsys, glob
    names = []
    for f in sorted(glob.glob(os.path.join(IMG, "**", "*.png"), recursive=True)):
        rel = os.path.relpath(f, IMG)
        if rel.startswith(("appicons", "card-background", "titlebarLogo", "themes")) or rel == "moneroLogo_white.png":
            continue
        im = Image.open(f).convert("RGBA")
        px = im.load(); changed = 0
        for y in range(im.height):
            for x in range(im.width):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                if s > 0.12 and 0.62 <= h <= 0.85:  # purple/violet
                    nr, ng, nb = colorsys.hsv_to_rgb(31 / 360, min(1.0, s * 1.35), v)
                    px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a); changed += 1
        if changed:
            im.save(f); names.append(rel)
    print("recoloured:", len(names), "images")


recolour_purple_to_amber()
