#!/usr/bin/env python3
"""Compose entry.png: one front page that sums up the world news of 19 Nov 2026.

Deterministic: fixed RNG seed, no network, no clock.  Renders at 2x and
downsamples to 1024x1024 so type and hairlines stay crisp.

Twenty-nine stories, six continents, one day: three illustrated leads, a band of
figures, eight briefs, a dotted world map with numbered datelines, eighteen
one-line reports, and a date-check strip naming what was reported earlier and
so is left out.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                      # supersample factor
W = H = 1024               # final size
PAPER = (243, 238, 228)
INK = (24, 21, 17)
RED = (176, 33, 27)
BLUE = (35, 62, 104)
GREY = (110, 101, 90)
LIGHT = (203, 196, 183)
TILE = (233, 227, 215)
SEA = (216, 226, 233)
FONT = "C:/Windows/Fonts/"

def f(name, size):
    return ImageFont.truetype(FONT + name, int(size * S))

GEORGIA_B = "georgiab.ttf"
GEORGIA_I = "georgiai.ttf"
NARROW_B = "ARIALNB.TTF"
SEGOE = "segoeui.ttf"
SEGOE_B = "segoeuib.ttf"

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
    lines = wrap(s, font, maxw)
    for i, ln in enumerate(lines):
        text(x, y + i * lh, ln, font, fill)
    return y + len(lines) * lh

# ---------------------------------------------------------------- paper, rules
rect(0, 0, W, 9, RED)
rect(0, 9, W, 2, INK)

# ---------------------------------------------------------------- kicker
kick = f(SEGOE_B, 9.5)
text(38, 20, "THE WORLD · ONE DAY · ONE PAGE", kick, INK, spacing=1.5)
text(986, 20, "TWENTY-NINE STORIES · SIX CONTINENTS", kick, GREY, anchor="ra", spacing=1.4)

# ---------------------------------------------------------------- masthead
text(36, 32, "THE WORLD", f(GEORGIA_B, 44), INK)
text(986, 50, "THE DAY IN ONE IMAGE", f(SEGOE_B, 9), RED, anchor="ra", spacing=1.8)

text(36, 80, "THURSDAY 19 NOVEMBER 2026", f(GEORGIA_B, 46), INK)
para(38, 138, "Everything on this page happened, or was first reported, on Thursday "
              "19 November 2026: twenty-nine stories, six continents, one day.",
     f(GEORGIA_I, 14.5), 900, (60, 54, 46), 1.2)

rect(38, 168, 948, 2, INK)

# ---------------------------------------------------------------- the day by hours
BAND_Y = 176
band = [
    ("OVERNIGHT", "GTA VI unlocks in New Zealand"),
    ("MORNING", "Trump, Xi and Putin meet in Shenzhen"),
    ("09:00 UTC", "ICJ delivers its Rohingya judgment"),
    ("14:30 UTC", "Anthropic opens on the Nasdaq"),
    ("ALL DAY", "Road link on the Kerch bridge stays shut"),
]
bw = 948 / 5
for i, (lab, line) in enumerate(band):
    bx = 38 + i * bw
    if i:
        d.line([(bx * S, BAND_Y * S), (bx * S, (BAND_Y + 30) * S)], fill=LIGHT, width=1 * S)
    text(bx + (10 if i else 0), BAND_Y + 1, lab, f(SEGOE_B, 7.5), RED, spacing=1.2)
    para(bx + (10 if i else 0), BAND_Y + 13, line, f(SEGOE, 9.2), bw - 20, INK, 1.12)

# ---------------------------------------------------------------- hero art
def flag_us(x, y, w, h):
    rect(x, y, w, h, (255, 255, 255), (120, 120, 120), 0.4)
    sh = h / 13
    for i in range(1, 13, 2):
        rect(x, y + i * sh, w, sh, (190, 45, 52))
    rect(x, y, w * 0.42, sh * 7, (37, 55, 95))
    for r in range(3):
        for c in range(4):
            d.ellipse([(x + 4 + c * w * 0.09) * S, (y + 5 + r * 6) * S,
                       (x + 6 + c * w * 0.09) * S, (y + 7 + r * 6) * S], fill=(255, 255, 255))

def flag_cn(x, y, w, h):
    rect(x, y, w, h, (206, 45, 45), (150, 30, 30), 0.4)
    cx, cy = x + 12, y + 12
    star = []
    for k in range(10):
        r = 7 if k % 2 == 0 else 3
        a = -math.pi / 2 + k * math.pi / 5
        star.append(((cx + r * math.cos(a)) * S, (cy + r * math.sin(a)) * S))
    d.polygon(star, fill=(250, 220, 90))
    for (ox, oy) in [(22, 5), (27, 10), (27, 18), (22, 23)]:
        pts = []
        for k in range(10):
            r = 2.6 if k % 2 == 0 else 1.2
            a = -math.pi / 2 + k * math.pi / 5
            pts.append(((x + ox + r * math.cos(a)) * S, (y + oy + r * math.sin(a)) * S))
        d.polygon(pts, fill=(250, 220, 90))

def flag_ru(x, y, w, h):
    rect(x, y, w, h / 3, (250, 250, 250), (150, 150, 150), 0.3)
    rect(x, y + h / 3, w, h / 3, (38, 62, 125))
    rect(x, y + 2 * h / 3, w, h / 3, (190, 45, 52))

def hero_summit(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = tuple(int(214 + (247 - 214) * t) for _ in range(3))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    rod = y + 10
    d.line([((x + 26) * S, rod * S), ((x + w - 26) * S, rod * S)], fill=(60, 55, 48), width=int(1.6 * S))
    fw, fh = 54, 30
    for fx, fn in [(x + 30, flag_us), (x + 92, flag_cn), (x + 154, flag_ru)]:
        d.line([(fx * S, rod * S), (fx * S, (rod + 4) * S)], fill=(60, 55, 48), width=int(1.4 * S))
        fn(fx, rod + 4, fw, fh)
    d.ellipse([(x + 24) * S, (y + 54) * S, (x + w - 24) * S, (y + 78) * S], fill=(70, 58, 45))
    d.ellipse([(x + 24) * S, (y + 50) * S, (x + w - 24) * S, (y + 72) * S], fill=(116, 98, 74))
    for cx, nm in [(x + 82, "TRUMP"), (x + 142, "XI"), (x + 200, "PUTIN")]:
        cw = 46 if nm != "XI" else 26
        rect(cx - cw / 2, y + 52, cw, 13, (250, 247, 239), (60, 50, 40), 0.5, 1)
        text(cx, y + 55, nm, f(SEGOE_B, 6.4), INK, anchor="ma", spacing=0.4)

def hero_court(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = tuple(int(216 + (243 - 216) * t) for _ in range(3))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    d.polygon([((x + 34) * S, (y + 40) * S), ((x + w / 2) * S, (y + 12) * S),
               ((x + w - 34) * S, (y + 40) * S)], fill=(250, 247, 239), outline=INK)
    d.line([((x + 34) * S, (y + 44) * S), ((x + w - 34) * S, (y + 44) * S)], fill=INK, width=2 * S)
    for i in range(5):
        cx = x + 50 + i * ((w - 100) / 4)
        rect(cx - 7, y + 47, 14, 26, (250, 247, 239), INK, 1)
        d.line([(cx * S, (y + 52) * S), (cx * S, (y + 70) * S)], fill=(190, 183, 170), width=1 * S)
    rect(x + 38, y + 73, w - 76, 5, (250, 247, 239), INK, 1)
    rect(x + 32, y + 78, w - 64, 5, (250, 247, 239), INK, 1)
    sx = x + w - 52
    d.line([(sx * S, (y + 12) * S), (sx * S, (y + 32) * S)], fill=INK, width=2 * S)
    d.line([((sx - 13) * S, (y + 16) * S), ((sx + 13) * S, (y + 16) * S)], fill=INK, width=2 * S)
    for dx in (-13, 13):
        d.arc([((sx + dx - 6) * S), ((y + 16) * S), ((sx + dx + 6) * S), ((y + 26) * S)],
              0, 180, fill=INK, width=2 * S)

def hero_city(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = (int(46 + 150 * t), int(32 + 60 * t), int(54 + 40 * t))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    d.ellipse([(x + w - 84) * S, (y + 12) * S, (x + w - 26) * S, (y + 70) * S], fill=(247, 176, 84))
    random.seed(19)
    bx = x
    while bx < x + w:
        bwid = random.choice([16, 22, 28, 34])
        bhei = random.choice([22, 32, 42, 52])
        top = y + h - 14 - bhei
        d.rectangle([bx * S, top * S, (bx + bwid) * S, (y + h - 14) * S],
                    fill=(28, 22, 34))
        for wy in range(int(top) + 6, int(y + h - 20), 9):
            for wx in range(int(bx) + 4, int(bx + bwid) - 3, 8):
                if random.random() < 0.5:
                    d.rectangle([wx * S, wy * S, (wx + 3) * S, (wy + 4) * S], fill=(240, 196, 110))
        bx += bwid + random.choice([2, 4, 6])
    rect(x, y + h - 14, w, 14, (18, 16, 24))
    text(x + 10, y + 5, "VICE CITY", f(GEORGIA_B, 10), (250, 230, 190), spacing=1.6)

# ---------------------------------------------------------------- leads
HERO_Y, HERO_H = 212, 202
HW3 = (948 - 24) / 3
heroes = [
    ("1", "ASIA · SUMMIT", "Trump, Xi and Putin meet in a first three-way summit",
     "The nuclear powers sit down at APEC in Shenzhen on Ukraine, Iran and trade. "
     "Trump also meets Putin alone.", hero_summit),
    ("2", "EUROPE · LAW", "World Court rules on Myanmar's Rohingya case",
     "The ICJ delivers its final judgment in The Gambia's genocide case over the 2017 "
     "crackdown that displaced 730,000.", hero_court),
    ("3", "AMERICAS · GAMES", "GTA VI ends a 13-year wait",
     "Rockstar's Vice City sequel unlocks worldwide, ending a 13-year wait for the series.",
     hero_city),
]
for i, (num, cat, head, body, art) in enumerate(heroes):
    hx = 38 + i * (HW3 + 12)
    rect(hx, HERO_Y, HW3, HERO_H, (250, 247, 239), (150, 142, 128), 0.8)
    art(hx + 1, HERO_Y + 1, HW3 - 2, 82)
    rect(hx, HERO_Y + 82, HW3, 2, RED)
    text(hx + 12, HERO_Y + 90, num, f(GEORGIA_B, 15), RED)
    text(hx + 28, HERO_Y + 94, cat, f(SEGOE_B, 7.6), GREY, spacing=1.2)
    hf = f(NARROW_B, 23)
    hy = HERO_Y + 114
    for ln in wrap(head, hf, HW3 - 24):
        text(hx + 12, hy, ln, hf, INK)
        hy += 24
    para(hx + 12, hy + 2, body, f(SEGOE, 9.8), HW3 - 24, (56, 50, 43), 1.16)

# ---------------------------------------------------------------- figures
FIG_Y = 422
figures = [
    ("$81.3bn", "raised by Anthropic, the largest IPO on record"),
    ("47,000", "evacuated as Cyclone Akvan nears Odisha"),
    ("551,864", "sitting Korea's college entrance exam"),
    ("4.9%", "Australia's unemployment rate, up from 4.8%"),
    ("730,000", "Rohingya displaced by the 2017 crackdown"),
]
rect(38, FIG_Y, 948, 42, INK)
fw = 948 / 5
for i, (big, small) in enumerate(figures):
    fx = 38 + i * fw
    if i:
        d.line([(fx * S, (FIG_Y + 6) * S), (fx * S, (FIG_Y + 36) * S)], fill=(90, 84, 76), width=1 * S)
    text(fx + 10, FIG_Y + 3, big, f(GEORGIA_B, 20), (250, 232, 214))
    para(fx + 10, FIG_Y + 26, small, f(SEGOE, 7.8), fw - 20, (200, 192, 180), 1.05)

# ---------------------------------------------------------------- briefs 4-11
def icon(kind, x, y, s=32):
    """Draw a 32-unit icon at (x, y)."""
    col = INK
    if kind == "bridge":
        d.line([(x * S, (y + 21) * S), ((x + 12) * S, (y + 21) * S)], fill=col, width=2 * S)
        d.line([((x + 20) * S, (y + 21) * S), ((x + 32) * S, (y + 21) * S)], fill=col, width=2 * S)
        for px in (x + 4, x + 28):
            d.line([(px * S, (y + 21) * S), (px * S, (y + 31) * S)], fill=col, width=1 * S)
        for tx in (x + 7, x + 10, x + 22, x + 25):
            d.line([(tx * S, (y + 21) * S), (tx * S, (y + 15) * S)], fill=col, width=1 * S)
        d.line([((x + 5) * S, (y + 15) * S), ((x + 12) * S, (y + 15) * S)], fill=col, width=1 * S)
        d.line([((x + 20) * S, (y + 15) * S), ((x + 27) * S, (y + 15) * S)], fill=col, width=1 * S)
        d.polygon([((x + 16) * S, (y + 5) * S), ((x + 20) * S, (y + 13) * S), ((x + 17) * S, (y + 14) * S),
                   ((x + 20) * S, (y + 21) * S), ((x + 13) * S, (y + 13) * S), ((x + 16) * S, (y + 13) * S)],
                  fill=RED)
    elif kind == "missile":
        d.polygon([((x + 24) * S, (y + 3) * S), ((x + 29) * S, (y + 8) * S), ((x + 9) * S, (y + 26) * S),
                   ((x + 5) * S, (y + 22) * S)], fill=col)
        d.polygon([((x + 5) * S, (y + 22) * S), ((x + 1) * S, (y + 29) * S), ((x + 6) * S, (y + 28) * S),
                   ((x + 9) * S, (y + 26) * S)], fill=RED)
        d.arc([(x + 7) * S, (y + 10) * S, (x + 28) * S, (y + 31) * S], 180, 330, fill=col, width=2 * S)
    elif kind == "tank":
        rect(x + 2, y + 19, 27, 8, col)
        rect(x + 6, y + 13, 13, 7, col)
        d.line([((x + 19) * S, (y + 16) * S), ((x + 31) * S, (y + 12) * S)], fill=col, width=2 * S)
        for wx in (x + 8, x + 16, x + 24):
            d.ellipse([(wx - 2) * S, (y + 25) * S, (wx + 4) * S, (y + 31) * S], fill=PAPER)
    elif kind == "protest":
        d.ellipse([(x + 4) * S, (y + 5) * S, (x + 12) * S, (y + 13) * S], fill=col)
        d.line([((x + 8) * S, (y + 13) * S), ((x + 8) * S, (y + 29) * S)], fill=col, width=2 * S)
        d.line([((x + 8) * S, (y + 19) * S), ((x + 1) * S, (y + 12) * S)], fill=col, width=1 * S)
        d.line([((x + 8) * S, (y + 19) * S), ((x + 15) * S, (y + 11) * S)], fill=col, width=1 * S)
        d.line([((x + 17) * S, (y + 31) * S), ((x + 17) * S, (y + 11) * S)], fill=col, width=1 * S)
        d.polygon([((x + 18) * S, (y + 11) * S), ((x + 32) * S, (y + 15) * S), ((x + 18) * S, (y + 21) * S)], fill=RED)
    elif kind == "arctic":
        d.polygon([((x + 3) * S, (y + 29) * S), ((x + 13) * S, (y + 9) * S), ((x + 19) * S, (y + 21) * S),
                   ((x + 25) * S, (y + 13) * S), ((x + 32) * S, (y + 29) * S)], fill=col)
        d.arc([(x + 9) * S, (y + 1) * S, (x + 27) * S, (y + 17) * S], 200, 340, fill=BLUE, width=2 * S)
    elif kind == "euro":
        text(x + 3, y + 1, "\u20ac", f(GEORGIA_B, 25), INK)
        d.line([((x + 1) * S, (y + 12) * S), ((x + 22) * S, (y + 12) * S)], fill=RED, width=2 * S)
        d.line([((x + 1) * S, (y + 18) * S), ((x + 22) * S, (y + 18) * S)], fill=RED, width=2 * S)
    elif kind == "border":
        d.line([((x + 16) * S, (y + 3) * S), ((x + 16) * S, (y + 31) * S)], fill=col, width=2 * S)
        for yy in (y + 9, y + 18, y + 27):
            d.line([((x + 4) * S, yy * S), ((x + 28) * S, yy * S)], fill=col, width=1 * S)
        d.polygon([((x + 3) * S, (y + 6) * S), ((x + 8) * S, (y + 11) * S), ((x + 3) * S, (y + 16) * S)], fill=RED)
        d.polygon([((x + 30) * S, (y + 16) * S), ((x + 25) * S, (y + 21) * S), ((x + 30) * S, (y + 26) * S)], fill=RED)
    elif kind == "strike":
        d.polygon([((x + 8) * S, (y + 17) * S), ((x + 14) * S, (y + 5) * S), ((x + 17) * S, (y + 7) * S),
                   ((x + 14) * S, (y + 17) * S), ((x + 20) * S, (y + 6) * S), ((x + 23) * S, (y + 8) * S),
                   ((x + 18) * S, (y + 19) * S), ((x + 24) * S, (y + 11) * S), ((x + 27) * S, (y + 13) * S),
                   ((x + 20) * S, (y + 23) * S), ((x + 20) * S, (y + 31) * S), ((x + 8) * S, (y + 31) * S)], fill=col)
        d.line([((x + 8) * S, (y + 17) * S), ((x + 3) * S, (y + 25) * S)], fill=RED, width=2 * S)

briefs = [
    ("4", "EUROPE", "Third Kerch strike in four days", "Drones cut the bridge's road link again.", "bridge"),
    ("5", "MIDDLE EAST", "Iran widens its Gulf attacks", "Brent crude holds near $92 a barrel.", "missile"),
    ("6", "MIDDLE EAST", "Israeli tanks cross the line", "Forces pass the Gaza ceasefire boundary.", "tank"),
    ("7", "SOUTH ASIA", "Hasina's party shuts Bangladesh", "Protests; Yunus's ancestral home burned.", "protest"),
    ("8", "ARCTIC", "Denmark backs the Greenland deal", "The Folketing ratifies a US security pact.", "arctic"),
    ("9", "EUROPE", "EU proposes a \u20ac45bn loan", "Brussels moves to fund Kyiv into next year.", "euro"),
    ("10", "AFRICA", "Ethiopia and Eritrea mass troops", "Forces gather along their shared border.", "border"),
    ("11", "AMERICAS", "Colombia strikes over tax bill", "Unions march in Bogot\u00e1, Medell\u00edn, Cali.", "strike"),
]

BRIEF_Y = 472
BW, BH, BG = (948 - 30) / 4, 108, 10
for i, (num, cat, head, det, kind) in enumerate(briefs):
    bx = 38 + (i % 4) * (BW + BG)
    by = BRIEF_Y + (i // 4) * (BH + 10)
    rect(bx, by, BW, BH, TILE)
    rect(bx, by, BW, 2, RED)
    text(bx + 9, by + 7, num, f(GEORGIA_B, 12), RED)
    text(bx + 30, by + 10, cat, f(SEGOE_B, 6.9), GREY, spacing=0.9)
    icon(kind, bx + 9, by + 26)
    hf = f(NARROW_B, 17)
    hy = by + 27
    for ln in wrap(head, hf, BW - 58):
        text(bx + 48, hy, ln, hf, INK)
        hy += 17.5
    para(bx + 48, hy + 4, det, f(SEGOE, 9.0), BW - 56, (78, 70, 60), 1.12)

# ---------------------------------------------------------------- map + also list
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

MX, MY, MW, MH = 38, 708, 448, 210
LAT_T, LAT_B = 80.0, -56.0

def _px(lon):
    return MX + (lon + 180) / 360 * MW

def _py(lat):
    return MY + (LAT_T - lat) / (LAT_T - LAT_B) * MH

rect(MX, MY, MW, MH - 14, SEA)
for lon in range(-180, 181, 30):
    d.line([(_px(lon) * S, MY * S), (_px(lon) * S, (MY + MH - 14) * S)], fill=(206, 217, 225), width=1 * S)
for lat in range(-60, 81, 30):
    d.line([(MX * S, _py(lat) * S), ((MX + MW) * S, _py(lat) * S)], fill=(206, 217, 225), width=1 * S)

STEP = 5
for gy in range(3, MH - 16, STEP):
    lat = LAT_T - (gy + 0.5) / (MH - 14) * (LAT_T - LAT_B)
    for gx in range(3, MW - 2, STEP):
        lon = (gx + 0.5) / MW * 360 - 180
        if _on_land(lon, lat):
            r = 1.15
            d.ellipse([(MX + gx - r) * S, (MY + gy - r) * S, (MX + gx + r) * S, (MY + gy + r) * S],
                      fill=(64, 74, 86))

pins = [
    ("1", 114.06, 22.54), ("2", 4.3, 52.1), ("3", -80.2, 25.8), ("4", 36.5, 45.3),
    ("5", 56.5, 26.5), ("6", 34.4, 31.4), ("7", 90.4, 23.8), ("8", -51.7, 64.2),
]
fpin = f(SEGOE_B, 8)
for nm, lon, lat in pins:
    x, y = _px(lon), _py(lat)
    d.ellipse([(x - 7) * S, (y - 7) * S, (x + 7) * S, (y + 7) * S],
              fill=PAPER, outline=RED, width=int(1.6 * S))
    text(x, y, nm, fpin, RED, anchor="mm")

text(MX, MY + MH - 11, "PINS MARK STORIES 1\u20138  ·  DOTS ARE LAND", f(SEGOE_B, 6.8), GREY, spacing=0.8)

AX, AY, AW = 500, 708, 486
rect(AX, AY, AW, 22, INK)
text(AX + 8, AY + 6, "ALSO ON THURSDAY 19 NOVEMBER", f(SEGOE_B, 8.6), PAPER, spacing=1.4)
text(AX + AW - 8, AY + 6, "12\u201329", f(SEGOE_B, 8.6), (230, 210, 190), anchor="ra", spacing=1.2)

also = [
    ("12", "RIYADH", "Houthi missiles fired at the capital"),
    ("13", "CARACAS", "Hegseth signs a military deal"),
    ("14", "TOKYO", "India and Japan hold 2+2 talks"),
    ("15", "WASHINGTON", "Trump frustrated with Vance on Iran"),
    ("16", "NEW YORK", "Musk regrets $445m of spending"),
    ("17", "DARFUR", "Joint force repels RSF attack on Kornoi"),
    ("18", "DANANG", "Russian Tu-95s land in Vietnam"),
    ("19", "ANTALYA", "COP31 nears close, finance unresolved"),
    ("20", "MIAMI", "Pastor guilty in Haiti murder plot"),
    ("21", "JAKARTA", "Rates rise as the rupiah slides"),
    ("22", "ISLAMABAD", "Rivals call Khan a political prisoner"),
    ("23", "JERUSALEM", "Court extends Abu Safia's detention"),
    ("24", "WASHINGTON", "New bid to end Venezuelan TPS"),
    ("25", "MEXICO CITY", "Measles vaccination drive begins"),
    ("26", "SAN FRANCISCO", "Anthropic shares jump on debut"),
    ("27", "NAIROBI", "Drought deepens milk shortage"),
    ("28", "BANGKOK", "Floods displace 200,000 in the south"),
    ("29", "GLOBAL", "Islam forecast to pass Christianity"),
]
colw = (AW - 8) / 2
for i, (num, place, line) in enumerate(also):
    col = i // 9
    row = i % 9
    x = AX + 8 + col * (colw + 4)
    y = AY + 30 + row * 21
    text(x, y, num, f(SEGOE_B, 7.6), RED)
    text(x + 16, y, place + " \u2014 ", f(SEGOE_B, 7.4), INK, spacing=0.3)
    off = 16 + f(SEGOE_B, 7.4).getlength(place + " \u2014 ") / S
    text(x + off + 4, y, line, f(SEGOE, 9.0), (52, 47, 41))

# ---------------------------------------------------------------- date check
DY = 928
rect(38, DY, 948, 30, None, RED, 1)
text(46, DY + 8, "DATE CHECK", f(SEGOE_B, 7.8), RED, spacing=1.4)
para(112, DY + 7,
     "First reported before Thursday, so not counted above: Fiji's drought disaster (Wed 18)  \u00b7  "
     "US measles-elimination loss (Tue 17)  \u00b7  Voyager 1 at one light-day (Wed 18)  \u00b7  "
     "Delhi schools reopening (Wed 18).",
     f(SEGOE, 7.6), 866, (52, 47, 41), 1.12)

# ---------------------------------------------------------------- footer
rect(38, 966, 948, 1, INK)
para(38, 971,
     "Every story here happened, or was first reported, on Thursday 19 November 2026. "
     "Claims are attributed, not stated as fact.",
     f(SEGOE, 7.4), 620, GREY, 1.05)
text(986, 971, "SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 GUARDIAN \u00b7 BLOOMBERG \u00b7 AL JAZEERA \u00b7 YONHAP \u00b7 ABC \u00b7 NYT \u00b7 PEW \u00b7 ICJ",
     f(SEGOE_B, 6.4), GREY, anchor="ra", spacing=0.4)

# ---------------------------------------------------------------- texture + vignette
random.seed(7)
noise = Image.effect_noise((W * S, H * S), 14).convert("L")
noise = noise.point(lambda v: 128 + (v - 128) // 3)
img = Image.blend(img, Image.merge("RGB", (noise, noise, noise)), 0.03)

vig = Image.new("L", (W * S, H * S), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-W * S * 0.25, -H * S * 0.25, W * S * 1.25, H * S * 1.25], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(90 * S))
dark = Image.new("RGB", (W * S, H * S), (62, 52, 40))
img = Image.composite(img, dark, vig.point(lambda v: 255 - (255 - v) // 5))

img = img.resize((W, H), Image.LANCZOS)
img.save("entry.png", optimize=True)
print("saved", img.size)
