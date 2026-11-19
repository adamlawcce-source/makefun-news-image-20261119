#!/usr/bin/env python3
"""Compose entry.png: one front page that sums up the world news of 19 Nov 2026.

Deterministic: fixed RNG seed, no network, no clock.  Renders at 2x and
downsamples to 1024x1024 so type and hairlines stay crisp.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2                      # supersample factor
W = H = 1024               # final size
PAPER = (243, 238, 228)
INK = (24, 21, 17)
RED = (176, 33, 27)
BLUE = (35, 62, 104)
GREY = (110, 101, 90)
LIGHT = (203, 196, 183)
FONT = "C:/Windows/Fonts/"

def f(name, size):
    return ImageFont.truetype(FONT + name, int(size * S))

GEORGIA_B = "georgiab.ttf"
NARROW_B = "ARIALNB.TTF"
SEGOE = "segoeui.ttf"
SEGOE_B = "segoeuib.ttf"
SEGOE_SL = "segoeuisl.ttf"
CONSOLA = "consola.ttf"

img = Image.new("RGB", (W * S, H * S), PAPER)
d = ImageDraw.Draw(img)

def rect(x, y, w, h, fill=None, outline=None, width=1, r=0):
    box = [x * S, y * S, (x + w) * S, (y + h) * S]
    if r:
        d.rounded_rectangle(box, radius=r * S, fill=fill, outline=outline,
                            width=max(1, int(width * S)))
    else:
        d.rectangle(box, fill=fill, outline=outline,
                    width=max(1, int(width * S)))

def text(x, y, s, font, fill=INK, anchor="la", spacing=0):
    if spacing:
        total = sum(font.getlength(ch) for ch in s) + spacing * S * max(0, len(s) - 1)
        cur = x * S
        if anchor[0] == "r":
            cur -= total
        elif anchor[0] == "m":
            cur -= total / 2
        for ch in s:
            d.text((cur, y * S), ch, font=font, fill=fill, anchor="l" + anchor[1])
            cur += font.getlength(ch) + spacing * S
        return
    d.text((x * S, y * S), s, font=font, fill=fill, anchor=anchor)

def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if font.getlength(t) <= maxw * S:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def para(x, y, s, font, maxw, fill=INK, lead=1.22):
    lh = font.size / S * lead
    for i, ln in enumerate(wrap(s, font, maxw)):
        text(x, y + i * lh, ln, font, fill)
    return y + len(wrap(s, font, maxw)) * lh

# ---------------------------------------------------------------- paper, rules
rect(0, 0, W, 9, RED)
rect(0, 9, W, 2, INK)

# ---------------------------------------------------------------- kicker
kick = f(SEGOE_B, 11)
text(40, 24, "WORLD EDITION", kick, INK, spacing=1.6)
kd = 40 + (kick.getlength("WORLD EDITION") / S + 1.6 * 12) + 14
text(kd, 24, "·", kick, GREY)
text(kd + 12, 24, "SEVEN STORIES, FOUR CONTINENTS, ONE DAY", kick, GREY, spacing=1.0)
text(984, 24, "THURSDAY 19 NOVEMBER 2026", kick, INK, anchor="ra", spacing=1.0)

# ---------------------------------------------------------------- masthead
text(38, 44, "THE WORLD", f(GEORGIA_B, 74), INK)
# red date block, right
rect(806, 52, 178, 62, RED)
text(895, 60, "19 NOV", f(GEORGIA_B, 27), PAPER, anchor="ma")
text(895, 90, "2026", f(SEGOE_B, 14), PAPER, anchor="ma", spacing=2.2)

rect(38, 124, 948, 3, INK)
rect(38, 130, 948, 1, INK)

# ---------------------------------------------------------------- lead
lead = f(NARROW_B, 59)
l1, l2 = "TRUMP, XI AND PUTIN", "MEET IN SHENZHEN"
text(38, 142, l1, lead, INK)
text(38, 142 + 59, l2, lead, INK)

subi = f(SEGOE_SL, 15.5)
para(40, 268, "The first three-way US–China–Russia summit caps Trump's Asia trip, with Washington and Beijing offering to help end the war in Ukraine.", subi, 560, INK, 1.28)

# byline / stamp right of the subhead
rect(628, 266, 358, 44, None, INK, 1)
text(640, 273, "THE SUMMIT", f(SEGOE_B, 9), RED, spacing=1.6)
text(640, 288, "APEC, Shenzhen · Trump also meets Putin alone", f(SEGOE, 11.5), INK)
text(628, 316, "Kyiv strikes the Kerch bridge hours before the talks.", f(SEGOE, 11.5), GREY)

# ---------------------------------------------------------------- hero: map
import json, os

HX, HY, HW, HH = 38, 344, 948, 236
MX, MY, MW, MH = HX, HY, 624, HH
LAT_T, LAT_B = 78.0, -58.0
SEA = (216, 226, 233)

_here = os.path.dirname(os.path.abspath(__file__))
_geo = json.load(open(os.path.join(_here, "world.geojson"), encoding="utf-8"))
_polys = []
for _f in _geo["features"]:
    _g = _f["geometry"]
    _cs = _g["coordinates"]
    if _g["type"] == "Polygon":
        _cs = [_cs]
    for _poly in _cs:
        _ring = _poly[0]
        _bx = [p[0] for p in _ring]
        _by = [p[1] for p in _ring]
        _polys.append((min(_bx), min(_by), max(_bx), max(_by), _poly))

def _in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside

def _on_land(lon, lat):
    for (x1, y1, x2, y2, poly) in _polys:
        if not (x1 - 1 <= lon <= x2 + 1 and y1 - 1 <= lat <= y2 + 1):
            continue
        if _in_ring(lon, lat, poly[0]) and not any(_in_ring(lon, lat, h) for h in poly[1:]):
            return True
    return False

def _px(lon):
    return MX + (lon + 180) / 360 * MW

def _py(lat):
    return MY + (LAT_T - lat) / (LAT_T - LAT_B) * MH

rect(MX, MY, MW, MH, SEA)
for lon in range(-180, 181, 30):
    d.line([(_px(lon) * S, MY * S), (_px(lon) * S, (MY + MH) * S)], fill=(210, 221, 228), width=1 * S)
for lat in range(-60, 79, 30):
    d.line([(MX * S, _py(lat) * S), ((MX + MW) * S, _py(lat) * S)], fill=(210, 221, 228), width=1 * S)

STEP = 5
for gy in range(4, MH - 3, STEP):
    lat = LAT_T - (gy + 0.5) / MH * (LAT_T - LAT_B)
    for gx in range(4, MW - 3, STEP):
        lon = (gx + 0.5) / MW * 360 - 180
        if _on_land(lon, lat):
            r = 1.4
            d.ellipse([(MX + gx - r) * S, (MY + gy - r) * S, (MX + gx + r) * S, (MY + gy + r) * S],
                      fill=(60, 70, 82))

pins = [
    ("1", -51.7, 64.2),
    ("2", 36.5, 45.3),
    ("3", 51.4, 35.7),
    ("4", 90.4, 23.8),
    ("5", 114.06, 22.54),
    ("6", 178.4, -18.1),
]
fnum = f(SEGOE_B, 9.5)
for nm, lon, lat in pins:
    x, y = _px(lon), _py(lat)
    d.ellipse([(x - 9) * S, (y - 9) * S, (x + 9) * S, (y + 9) * S], fill=PAPER, outline=RED, width=int(2 * S))
    text(x, y, nm, fnum, RED, anchor="mm")

# quote panel
PX, PY, PW, PH = HX + 636, HY, HW - 636, HH
rect(PX, PY, PW, PH, INK)
text(PX + PW - 44, PY + 2, "\u201d", f(GEORGIA_B, 44), RED)
text(PX + 18, PY + 16, "THE LINE", f(SEGOE_B, 9), (230, 210, 190), spacing=1.6)
qf = f("georgiai.ttf", 17.5)
qy = PY + 44
for ln in wrap("We're looking to both help with respect to the war with Russia and Ukraine.", qf, PW - 36):
    text(PX + 18, qy, ln, qf, (247, 242, 232))
    qy += 24
rect(PX + 18, PY + 168, 42, 2, RED)
text(PX + 18, PY + 178, "DONALD TRUMP", f(SEGOE_B, 9), RED, spacing=1.4)
text(PX + 18, PY + 192, "APEC summit, Shenzhen", f(SEGOE, 10), (180, 174, 164))

# caption bar
rect(HX, HY + HH, HW, 22, INK)
text(HX + 10, HY + HH + 4, "THE DAY, MAPPED", f(SEGOE_B, 9.5), PAPER, spacing=1.6)
leg = "1 NUUK   2 KERCH   3 TEHRAN   4 DHAKA   5 SHENZHEN   6 SUVA"
text(HX + 150, HY + HH + 4, leg, f(SEGOE_B, 9.5), (232, 226, 214), spacing=0.6)

# ---------------------------------------------------------------- tiles
TILE_Y = 632
TW, TH, GAP = 300, 154, 16
COLX = [38, 38 + TW + 20, 38 + 2 * (TW + 20)]

def draw_icon(kind, x, y):
    col = INK
    if kind == "bridge":
        # two deck spans with a gap, piers below, blast at the break
        d.line([(x * S, (y + 36) * S), ((x + 21) * S, (y + 36) * S)], fill=col, width=3 * S)
        d.line([((x + 35) * S, (y + 36) * S), ((x + 56) * S, (y + 36) * S)], fill=col, width=3 * S)
        d.line([((x + 8) * S, (y + 36) * S), ((x + 8) * S, (y + 54) * S)], fill=col, width=2 * S)
        d.line([((x + 48) * S, (y + 36) * S), ((x + 48) * S, (y + 54) * S)], fill=col, width=2 * S)
        for tx in (x + 12, x + 16, x + 40, x + 44):
            d.line([(tx * S, (y + 36) * S), (tx * S, (y + 26) * S)], fill=col, width=1 * S)
        d.line([((x + 10) * S, (y + 26) * S), ((x + 18) * S, (y + 26) * S)], fill=col, width=2 * S)
        d.line([((x + 38) * S, (y + 26) * S), ((x + 46) * S, (y + 26) * S)], fill=col, width=2 * S)
        d.polygon([((x + 28) * S, (y + 14) * S), ((x + 34) * S, (y + 26) * S), ((x + 30) * S, (y + 27) * S),
                   ((x + 34) * S, (y + 38) * S), ((x + 24) * S, (y + 26) * S), ((x + 28) * S, (y + 25) * S)],
                  fill=RED)
    elif kind == "missile":
        d.polygon([((x + 44) * S, (y + 6) * S), ((x + 52) * S, (y + 14) * S), ((x + 14) * S, (y + 44) * S),
                   ((x + 8) * S, (y + 38) * S)], fill=col)
        d.polygon([((x + 8) * S, (y + 38) * S), ((x + 2) * S, (y + 48) * S), ((x + 10) * S, (y + 46) * S),
                   ((x + 14) * S, (y + 44) * S)], fill=RED)
        d.ellipse([(x + 18) * S, (y + 18) * S, (x + 46) * S, (y + 46) * S], outline=col, width=2 * S)
        d.ellipse([(x + 28) * S, (y + 28) * S, (x + 36) * S, (y + 36) * S], fill=RED)
    elif kind == "protest":
        d.ellipse([(x + 14) * S, (y + 6) * S, (x + 24) * S, (y + 16) * S], fill=col)
        d.line([((x + 19) * S, (y + 16) * S), ((x + 19) * S, (y + 38) * S)], fill=col, width=3 * S)
        d.line([((x + 19) * S, (y + 24) * S), ((x + 4) * S, (y + 14) * S)], fill=col, width=2 * S)
        d.line([((x + 19) * S, (y + 24) * S), ((x + 34) * S, (y + 12) * S)], fill=col, width=2 * S)
        d.polygon([((x + 36) * S, (y + 4) * S), ((x + 47) * S, (y + 30) * S), ((x + 39) * S, (y + 28) * S),
                   ((x + 33) * S, (y + 44) * S), ((x + 30) * S, (y + 30) * S), ((x + 24) * S, (y + 26) * S)], fill=RED)
    elif kind == "arctic":
        d.polygon([((x + 4) * S, (y + 46) * S), ((x + 20) * S, (y + 16) * S), ((x + 30) * S, (y + 34) * S),
                   ((x + 40) * S, (y + 22) * S), ((x + 54) * S, (y + 46) * S)], fill=col)
        d.arc([(x + 12) * S, (y + 2) * S, (x + 44) * S, (y + 30) * S], 200, 340, fill=BLUE, width=2 * S)
    elif kind == "chart":
        for i, hh in enumerate([12, 20, 30, 42, 52]):
            d.rectangle([(x + 4 + i * 10) * S, (y + 52 - hh) * S, (x + 10 + i * 10) * S, (y + 52) * S], fill=col)
        d.line([((x + 2) * S, (y + 44) * S), ((x + 54) * S, (y + 4) * S)], fill=RED, width=3 * S)
        d.polygon([((x + 54) * S, (y + 4) * S), ((x + 44) * S, (y + 6) * S), ((x + 52) * S, (y + 14) * S)], fill=RED)
    elif kind == "drought":
        d.ellipse([(x + 14) * S, (y + 4) * S, (x + 42) * S, (y + 32) * S], fill=RED)
        for a in range(0, 360, 45):
            r1, r2 = 17, 24
            d.line([((x + 28 + r1 * math.cos(math.radians(a))) * S, (y + 18 + r1 * math.sin(math.radians(a))) * S),
                    ((x + 28 + r2 * math.cos(math.radians(a))) * S, (y + 18 + r2 * math.sin(math.radians(a))) * S)],
                   fill=RED, width=2 * S)
        d.line([((x + 2) * S, (y + 46) * S), ((x + 16) * S, (y + 38) * S), ((x + 26) * S, (y + 50) * S),
                ((x + 38) * S, (y + 40) * S), ((x + 54) * S, (y + 48) * S)], fill=col, width=2 * S)

stories = [
    ("EUROPE", "KERCH BRIDGE CUT", "Ukraine breaks the Crimea road link with drones and Flamingo missiles; Russia blames Dutch arms.", "bridge", "KERCH, CRIMEA"),
    ("MIDDLE EAST", "IRAN: STRIKES WEIGHED", "Trump considers a joint attack with Israel, which warns of chemical weapons. Oil near $92.", "missile", "WASHINGTON"),
    ("SOUTH ASIA", "BANGLADESH SHUT DOWN", "Protests by Hasina's party close cities; Yunus's ancestral home burned; two killed.", "protest", "DHAKA"),
    ("ARCTIC", "GREENLAND DEAL", "Denmark ratifies a security pact with Trump; the US plans a \"Golden Dome\" in the Arctic.", "arctic", "COPENHAGEN"),
    ("MARKETS", "ANTHROPIC'S RECORD IPO", "Priced at $83 a share, the biggest listing ever; Nasdaq futures jump 2%.", "chart", "NEW YORK"),
    ("PACIFIC", "FIJI: DROUGHT DISASTER", "An El Niño drought prompts a national state of disaster; water is rationed.", "drought", "SUVA"),
]

for i, (cat, head, body, icon, place) in enumerate(stories):
    cx = COLX[i % 3]
    cy = TILE_Y + (i // 3) * (TH + 18)
    rect(cx, cy, TW, TH, (233, 227, 215))
    rect(cx, cy, TW, 3, RED)
    text(cx + 12, cy + 12, cat, f(SEGOE_B, 8.5), RED, spacing=1.4)
    draw_icon(icon, cx + 12, cy + 30)
    tx = cx + 82
    tw = TW - 82 - 12
    hy = cy + 30
    hsize, hlines = 19, None
    for cand in (19, 18, 17, 16, 15.5, 15):
        hf = f(NARROW_B, cand)
        hl = wrap(head, hf, tw)
        if len(hl) == 1:
            hsize, hlines = cand, hl
            break
    if hlines is None:
        for cand in (19, 18, 17, 16):
            hf = f(NARROW_B, cand)
            hl = wrap(head, hf, tw)
            if len(hl) <= 2 and max(hf.getlength(z) for z in hl) / S <= tw:
                hsize, hlines = cand, hl
                break
    if hlines is None:
        hsize = 16
        hlines = wrap(head, f(NARROW_B, hsize), tw)
    hf = f(NARROW_B, hsize)
    for ln in hlines:
        text(tx, hy, ln, hf, INK)
        hy += hsize + 1
    para(tx, hy + 6, body, f(SEGOE, 12.4), tw, (60, 54, 46), 1.28)
    # dateline footer
    rect(cx + 12, cy + TH - 26, TW - 24, 1, LIGHT)
    text(cx + 12, cy + TH - 20, place, f(SEGOE_B, 8), GREY, spacing=1.2)
    text(cx + TW - 12, cy + TH - 20, "P.%d" % (i + 2), f(SEGOE_B, 8), GREY, anchor="ra", spacing=1.2)

# ---------------------------------------------------------------- bottom rule + ticker
rect(38, 966, 948, 1, INK)
text(38, 976, "ALSO", f(SEGOE_B, 9), RED, spacing=1.6)
text(74, 976, "Houthi missile fired at Riyadh  ·  Brooklyn collapse kills two  ·  Dollar at a 19-month high  ·  Floods hit both US coasts", f(SEGOE, 10.5), INK)
text(984, 992, "EDITED FROM REUTERS · AP · BLOOMBERG · THE GUARDIAN", f(SEGOE, 7.5), GREY, anchor="ra", spacing=1.0)

# ---------------------------------------------------------------- texture + vignette
random.seed(7)
noise = Image.effect_noise((W * S, H * S), 14).convert("L")
noise = noise.point(lambda v: 128 + (v - 128) // 3)
img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.035)

vig = Image.new("L", (W * S, H * S), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * S * 0.25, -H * S * 0.25, W * S * 1.25, H * S * 1.25], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(90 * S))
dark = Image.new("RGB", (W * S, H * S), (60, 50, 38))
img = Image.composite(img, dark, vig.point(lambda v: 255 - (255 - v) // 4))

img = img.resize((W, H), Image.LANCZOS)
img.save("entry.png", optimize=True)
print("saved", img.size)


