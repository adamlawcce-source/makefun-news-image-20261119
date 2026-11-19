#!/usr/bin/env python3
"""Compose entry.png: one front page that sums up the world news of 19 Nov 2026.

Deterministic: fixed RNG seed, no network, no clock.  Renders at 2x and
downsamples to 1024x1024 so type and hairlines stay crisp.

Thirty-one stories, six continents, one day: three illustrated leads, a region
tally, six figures, ten briefs, a dotted world map with thirteen numbered
datelines, eighteen one-line reports, and a date-check strip naming what was
reported earlier and so is left out.
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

GOLD = (183, 124, 30)
GREEN = (32, 108, 84)
TEAL = (26, 108, 116)
PLUM = (104, 56, 104)

REGIONS = {
    "ASIA-PACIFIC": RED,
    "EUROPE": BLUE,
    "THE AMERICAS": GREEN,
    "MIDDLE EAST": GOLD,
    "AFRICA": PLUM,
    "OCEANIA": TEAL,
    "WORLD": GREY,
}
ORDER = ["EUROPE", "THE AMERICAS", "ASIA-PACIFIC", "MIDDLE EAST", "AFRICA",
         "OCEANIA", "WORLD"]

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

def tint(col, k=0.86):
    return tuple(int(c + (255 - c) * k) for c in col)

# ---------------------------------------------------------------- stories
heroes = [
    ("1", "ASIA-PACIFIC", "SHENZHEN · SUMMIT",
     "Trump, Xi and Putin hold a first three-way summit",
     "The three nuclear powers sit down at APEC on Ukraine, Iran and trade; "
     "Trump also meets Putin alone.", "REUTERS · AP"),
    ("2", "EUROPE", "THE HAGUE · LAW",
     "World Court rules on Myanmar's Rohingya case",
     "The ICJ's final judgment in The Gambia's genocide case covers the 2017 "
     "crackdown that displaced 730,000.", "ICJ · REUTERS"),
    ("3", "THE AMERICAS", "MIAMI · GAMES",
     "GTA VI goes on sale worldwide",
     "Rockstar's Vice City sequel unlocks worldwide at midnight local time, on "
     "PS5 and Xbox.", "AP · REUTERS"),
]

briefs = [
    ("4", "EUROPE", "KERCH · UKRAINE", "Third bridge strike in four days",
     "Drones cut the road link again; Russia blames Dutch missiles.", "bridge"),
    ("5", "MIDDLE EAST", "HORMUZ · CONFLICT", "Iran widens its Gulf attacks",
     "Brent crude holds near $92 a barrel as the attacks widen.", "missile"),
    ("6", "MIDDLE EAST", "GAZA · CEASEFIRE", "Israeli tanks cross the line",
     "Armour passes the Yellow Line, a rare breach of the truce.", "tank"),
    ("7", "ASIA-PACIFIC", "DHAKA · PROTESTS", "Hasina's party shuts Bangladesh",
     "Two killed; Yunus's ancestral home is burned.", "protest"),
    ("8", "EUROPE", "NUUK · ARCTIC", "Denmark backs the Greenland deal",
     "The Folketing ratifies a security pact with Washington.", "arctic"),
    ("9", "EUROPE", "BRUSSELS · FINANCE", "EU proposes a \u20ac45bn loan",
     "The money would keep Kyiv funded into next year.", "euro"),
    ("10", "AFRICA", "HORN · BORDER", "Ethiopia and Eritrea mass troops",
     "Forces gather along a frontier that has been quiet for years.", "border"),
    ("11", "THE AMERICAS", "BOGOT\u00c1 · LABOUR", "Colombia strikes over tax bill",
     "Unions march in Bogot\u00e1, Medell\u00edn and Cali.", "strike"),
    ("12", "ASIA-PACIFIC", "SEOUL · EDUCATION", "551,864 sit the college exam",
     "Flights pause and offices open late for the test.", "exam"),
    ("13", "OCEANIA", "CANBERRA · ECONOMY", "Australia's jobless rate rises",
     "Unemployment climbs to 4.9%, from 4.8% a month before.", "chart"),
]

also = [
    ("14", "MIDDLE EAST", "RIYADH", "Houthi missiles fired at the capital"),
    ("15", "THE AMERICAS", "CARACAS", "Hegseth signs a military deal"),
    ("16", "ASIA-PACIFIC", "TOKYO", "India and Japan hold 2+2 talks"),
    ("17", "THE AMERICAS", "WASHINGTON", "Trump frustrated with Vance on Iran"),
    ("18", "THE AMERICAS", "NEW YORK", "Musk regrets $445m of spending"),
    ("19", "AFRICA", "DARFUR", "Joint force repels RSF attack on Kornoi"),
    ("20", "ASIA-PACIFIC", "DANANG", "Russian Tu-95s land in Vietnam"),
    ("21", "EUROPE", "ANTALYA", "COP31 nears close, finance unresolved"),
    ("22", "THE AMERICAS", "MIAMI", "Pastor guilty in Haiti murder plot"),
    ("23", "ASIA-PACIFIC", "JAKARTA", "Rates rise as the rupiah slides"),
    ("24", "ASIA-PACIFIC", "ISLAMABAD", "Rivals call Khan a political prisoner"),
    ("25", "MIDDLE EAST", "JERUSALEM", "Court extends Abu Safia's detention"),
    ("26", "THE AMERICAS", "WASHINGTON", "New bid to end Venezuelan TPS"),
    ("27", "THE AMERICAS", "MEXICO CITY", "Measles vaccination drive begins"),
    ("28", "THE AMERICAS", "SAN FRANCISCO", "Anthropic shares jump on debut"),
    ("29", "AFRICA", "NAIROBI", "Drought deepens milk shortage"),
    ("30", "ASIA-PACIFIC", "BANGKOK", "Floods displace 200,000 in the south"),
    ("31", "WORLD", "GLOBAL", "Islam forecast to pass Christianity"),
]

counts = {k: 0 for k in ORDER}
for _n, _r, *_ in heroes + briefs + also:
    counts[_r] += 1
total = sum(counts.values())

# ---------------------------------------------------------------- paper, rules
rect(0, 0, W, 9, RED)
rect(0, 9, W, 2, INK)

# ---------------------------------------------------------------- kicker
kick = f(SEGOE_B, 9.5)
text(38, 18, "THE WORLD · ONE DAY · ONE PAGE", kick, INK, spacing=1.5)
text(986, 18, f"{total} STORIES · SIX CONTINENTS", kick, GREY, anchor="ra", spacing=1.4)

# ---------------------------------------------------------------- masthead
text(34, 26, "Thursday 19 November 2026", f(GEORGIA_B, 54), INK)
para(38, 92, "Three leaders meet in Shenzhen  \u00b7  a court rules on Myanmar  \u00b7  "
             "GTA VI arrives  \u00b7  the biggest IPO yet",
     f(GEORGIA_I, 15), 960, (68, 58, 46), 1.15)

# ---------------------------------------------------------------- region tally
REG_Y = 118
seg = 948 / len(ORDER)
for i, key in enumerate(ORDER):
    x = 38 + i * seg
    rect(x, REG_Y, seg - 4, 18, REGIONS[key])
    lf = f(SEGOE_B, 7.2)
    text(x + 7, REG_Y + 5, key, lf, PAPER, spacing=0.8)
    lw = sum(lf.getlength(ch) for ch in key) / S + 0.8 * (len(key) - 1) / S
    text(x + 13 + lw, REG_Y + 3, str(counts[key]), f(GEORGIA_B, 12), PAPER)

# ---------------------------------------------------------------- hero art
def hero_summit(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = (int(30 + 26 * t), int(42 + 34 * t), int(66 + 42 * t))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    # floor
    rect(x, y + h - 20, w, 20, (92, 78, 60))
    d.line([((x) * S, (y + h - 20) * S), ((x + w) * S, (y + h - 20) * S)], fill=(60, 50, 40), width=1 * S)
    # flags
    fw, fh = 46, 27
    for fx, col, band in [(x + 26, (190, 45, 52), None),
                          (x + 96, (206, 45, 45), None),
                          (x + 166, (250, 250, 250), (38, 62, 125))]:
        d.line([(fx * S, (y + 8) * S), (fx * S, (y + 44) * S)], fill=(214, 208, 196), width=int(1.4 * S))
        rect(fx, y + 8, fw, fh, col, (60, 60, 60), 0.4)
        if col == (250, 250, 250):
            rect(fx, y + 8 + fh / 3, fw, fh / 3, (38, 62, 125))
            rect(fx, y + 8 + 2 * fh / 3, fw, fh / 3, (190, 45, 52))
        elif col == (206, 45, 45):
            cx, cy = fx + 11, y + 19
            star = []
            for k in range(10):
                rr = 5.5 if k % 2 == 0 else 2.4
                a = -math.pi / 2 + k * math.pi / 5
                star.append(((cx + rr * math.cos(a)) * S, (cy + rr * math.sin(a)) * S))
            d.polygon(star, fill=(250, 220, 90))
        else:
            rect(fx, y + 8, fw * 0.44, fh * 0.55, (37, 55, 95))
            for r in range(2):
                for cc in range(3):
                    d.ellipse([(fx + 4 + cc * fw * 0.1) * S, (y + 12 + r * 6) * S,
                               (fx + 6 + cc * fw * 0.1) * S, (y + 14 + r * 6) * S], fill=(255, 255, 255))
    # table + microphones
    rect(x + 18, y + h - 34, w - 36, 14, (108, 84, 58), (58, 44, 30), 0.6, 2)
    for mx in (x + w / 2 - 26, x + w / 2, x + w / 2 + 26):
        d.line([(mx * S, (y + h - 34) * S), (mx * S, (y + h - 44) * S)], fill=(40, 36, 32), width=int(1.6 * S))
        d.ellipse([(mx - 3) * S, (y + h - 48) * S, (mx + 3) * S, (y + h - 42) * S], fill=(40, 36, 32))
    text(x + w / 2, y + h - 31, "SHENZHEN", f(SEGOE_B, 6.2), (238, 226, 208), anchor="ma", spacing=1.4)

def hero_court(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = (int(126 + 96 * t), int(166 + 70 * t), int(204 + 40 * t))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    rect(x, y + h - 16, w, 16, (96, 122, 82))
    # palace
    px, pw = x + 26, w - 52
    d.polygon([((px) * S, (y + 44) * S), ((px + pw / 2) * S, (y + 16) * S),
               ((px + pw) * S, (y + 44) * S)], fill=(250, 247, 239), outline=(70, 70, 70))
    d.line([(px * S, (y + 47) * S), ((px + pw) * S, (y + 47) * S)], fill=(70, 70, 70), width=2 * S)
    for i in range(5):
        cx = px + 12 + i * ((pw - 24) / 4)
        rect(cx - 8, y + 50, 16, 22, (252, 250, 243), (90, 90, 90), 0.8)
        d.line([(cx * S, (y + 55) * S), (cx * S, (y + 67) * S)], fill=(196, 190, 176), width=1 * S)
    rect(px - 4, y + 72, pw + 8, 4, (245, 242, 232), (90, 90, 90), 0.8)
    # scales
    sx = x + w - 40
    d.line([(sx * S, (y + 14) * S), (sx * S, (y + 34) * S)], fill=(60, 48, 30), width=2 * S)
    d.line([((sx - 12) * S, (y + 18) * S), ((sx + 12) * S, (y + 18) * S)], fill=(60, 48, 30), width=2 * S)
    for dx in (-12, 12):
        d.arc([((sx + dx - 6) * S), ((y + 18) * S), ((sx + dx + 6) * S), ((y + 28) * S)],
              0, 180, fill=(188, 146, 44), width=2 * S)

def hero_city(x, y, w, h):
    for i in range(int(h)):
        t = i / h
        c = (int(58 + 190 * t), int(34 + 120 * t), int(70 + 70 * t))
        d.line([(x * S, (y + i) * S), ((x + w) * S, (y + i) * S)], fill=c, width=S)
    d.ellipse([(x + w - 74) * S, (y + 8) * S, (x + w - 20) * S, (y + 62) * S], fill=(250, 196, 120))
    random.seed(19)
    bx = x
    while bx < x + w:
        bwid = random.choice([15, 20, 26, 32])
        bhei = random.choice([20, 30, 40, 50])
        top = y + h - 16 - bhei
        d.rectangle([bx * S, top * S, (bx + bwid) * S, (y + h - 16) * S], fill=(46, 30, 52))
        for wy in range(int(top) + 5, int(y + h - 22), 8):
            for wx in range(int(bx) + 3, int(bx + bwid) - 2, 7):
                if random.random() < 0.55:
                    d.rectangle([wx * S, wy * S, (wx + 3) * S, (wy + 4) * S], fill=(248, 198, 112))
        bx += bwid + random.choice([2, 4, 6])
    rect(x, y + h - 16, w, 16, (36, 22, 40))
    # palms
    for px in (x + 22, x + w - 30):
        d.line([(px * S, (y + h - 16) * S), (px * S, (y + h - 44) * S)], fill=(38, 24, 34), width=2 * S)
        for a in (-1.9, -1.2, -0.5, 0.3):
            d.line([(px * S, (y + h - 44) * S), ((px + 12 * math.cos(a)) * S, (y + h - 44 + 9 * math.sin(a)) * S)],
                   fill=(38, 24, 34), width=2 * S)
    # neon VI
    text(x + w - 16, y + 10, "VI", f(GEORGIA_B, 22), (255, 120, 150), anchor="ra", spacing=1.0)

# ---------------------------------------------------------------- leads
HERO_Y, HERO_H = 146, 212
HW3 = (948 - 24) / 3
arts = [hero_summit, hero_court, hero_city]
for i, (num, region, cat, head, body, src) in enumerate(heroes):
    hx = 38 + i * (HW3 + 12)
    rect(hx, HERO_Y, HW3, HERO_H, (250, 247, 239), (150, 142, 128), 0.8)
    arts[i](hx + 1, HERO_Y + 1, HW3 - 2, 74)
    rect(hx, HERO_Y + 74, HW3, 2.5, REGIONS[region])
    text(hx + 12, HERO_Y + 82, num, f(GEORGIA_B, 13), REGIONS[region])
    text(hx + 27, HERO_Y + 85, cat, f(SEGOE_B, 7.0), REGIONS[region], spacing=1.0)
    text(hx + HW3 - 12, HERO_Y + 85, src, f(SEGOE_B, 6.0), GREY, anchor="ra", spacing=0.5)
    hf = f(GEORGIA_B, 21)
    hy = HERO_Y + 104
    for ln in wrap(head, hf, HW3 - 24):
        text(hx + 12, hy, ln, hf, INK)
        hy += 21.5
    para(hx + 12, hy + 3, body, f(SEGOE, 9.4), HW3 - 24, (58, 52, 45), 1.16)

# ---------------------------------------------------------------- figures
FIG_Y = 366
figures = [
    ("$81.3bn", "raised by Anthropic, the largest IPO on record", GREEN),
    ("47,000", "evacuated as Cyclone Akvan nears Odisha", GOLD),
    ("551,864", "sitting Korea's college entrance exam", RED),
    ("4.9%", "Australia's unemployment rate, up from 4.8%", TEAL),
    ("$92", "a barrel of Brent crude, as the Gulf attacks widen", GOLD),
    ("730,000", "Rohingya displaced by the 2017 crackdown", BLUE),
]
rect(38, FIG_Y, 948, 40, INK)
fw = 948 / 6
for i, (big, small, col) in enumerate(figures):
    fx = 38 + i * fw
    if i:
        d.line([(fx * S, (FIG_Y + 5) * S), (fx * S, (FIG_Y + 35) * S)], fill=(86, 80, 72), width=1 * S)
    text(fx + 9, FIG_Y + 3, big, f(GEORGIA_B, 17.5), (250, 232, 214))
    para(fx + 9, FIG_Y + 24, small, f(SEGOE, 7.0), fw - 18, (198, 190, 178), 1.05)

# ---------------------------------------------------------------- briefs 4-13
def icon(kind, x, y):
    """Draw a 30-unit icon at (x, y)."""
    col = INK
    if kind == "bridge":
        d.line([(x * S, (y + 19) * S), ((x + 11) * S, (y + 19) * S)], fill=col, width=2 * S)
        d.line([((x + 19) * S, (y + 19) * S), ((x + 30) * S, (y + 19) * S)], fill=col, width=2 * S)
        for px in (x + 3, x + 26):
            d.line([(px * S, (y + 19) * S), (px * S, (y + 28) * S)], fill=col, width=1 * S)
        for tx in (x + 6, x + 9, x + 21, x + 24):
            d.line([(tx * S, (y + 19) * S), (tx * S, (y + 13) * S)], fill=col, width=1 * S)
        d.line([((x + 4) * S, (y + 13) * S), ((x + 11) * S, (y + 13) * S)], fill=col, width=1 * S)
        d.line([((x + 19) * S, (y + 13) * S), ((x + 26) * S, (y + 13) * S)], fill=col, width=1 * S)
        d.polygon([((x + 15) * S, (y + 4) * S), ((x + 19) * S, (y + 12) * S), ((x + 16) * S, (y + 13) * S),
                   ((x + 19) * S, (y + 19) * S), ((x + 12) * S, (y + 12) * S), ((x + 15) * S, (y + 12) * S)],
                  fill=RED)
    elif kind == "missile":
        d.polygon([((x + 22) * S, (y + 3) * S), ((x + 27) * S, (y + 8) * S), ((x + 8) * S, (y + 24) * S),
                   ((x + 4) * S, (y + 20) * S)], fill=col)
        d.polygon([((x + 4) * S, (y + 20) * S), ((x + 1) * S, (y + 27) * S), ((x + 6) * S, (y + 26) * S),
                   ((x + 8) * S, (y + 24) * S)], fill=RED)
        d.arc([(x + 7) * S, (y + 9) * S, (x + 27) * S, (y + 29) * S], 180, 330, fill=col, width=2 * S)
    elif kind == "tank":
        rect(x + 2, y + 18, 26, 8, col)
        rect(x + 6, y + 12, 12, 6, col)
        d.line([((x + 18) * S, (y + 15) * S), ((x + 30) * S, (y + 11) * S)], fill=col, width=2 * S)
        for wx in (x + 7, x + 15, x + 23):
            d.ellipse([(wx - 2) * S, (y + 24) * S, (wx + 4) * S, (y + 30) * S], fill=(238, 232, 220))
    elif kind == "protest":
        d.ellipse([(x + 4) * S, (y + 5) * S, (x + 12) * S, (y + 13) * S], fill=col)
        d.line([((x + 8) * S, (y + 13) * S), ((x + 8) * S, (y + 28) * S)], fill=col, width=2 * S)
        d.line([((x + 8) * S, (y + 18) * S), ((x + 1) * S, (y + 12) * S)], fill=col, width=1 * S)
        d.line([((x + 8) * S, (y + 18) * S), ((x + 15) * S, (y + 11) * S)], fill=col, width=1 * S)
        d.line([((x + 17) * S, (y + 30) * S), ((x + 17) * S, (y + 11) * S)], fill=col, width=1 * S)
        d.polygon([((x + 18) * S, (y + 11) * S), ((x + 31) * S, (y + 15) * S), ((x + 18) * S, (y + 20) * S)], fill=RED)
    elif kind == "arctic":
        d.polygon([((x + 3) * S, (y + 28) * S), ((x + 12) * S, (y + 9) * S), ((x + 18) * S, (y + 20) * S),
                   ((x + 24) * S, (y + 13) * S), ((x + 31) * S, (y + 28) * S)], fill=col)
        d.arc([(x + 8) * S, (y + 1) * S, (x + 26) * S, (y + 16) * S], 200, 340, fill=BLUE, width=2 * S)
    elif kind == "euro":
        text(x + 2, y + 1, "\u20ac", f(GEORGIA_B, 24), INK)
        d.line([((x + 1) * S, (y + 12) * S), ((x + 21) * S, (y + 12) * S)], fill=RED, width=2 * S)
        d.line([((x + 1) * S, (y + 18) * S), ((x + 21) * S, (y + 18) * S)], fill=RED, width=2 * S)
    elif kind == "border":
        d.line([((x + 15) * S, (y + 3) * S), ((x + 15) * S, (y + 30) * S)], fill=col, width=2 * S)
        for yy in (y + 9, y + 18, y + 27):
            d.line([((x + 4) * S, yy * S), ((x + 27) * S, yy * S)], fill=col, width=1 * S)
        d.polygon([((x + 3) * S, (y + 6) * S), ((x + 8) * S, (y + 11) * S), ((x + 3) * S, (y + 16) * S)], fill=RED)
        d.polygon([((x + 29) * S, (y + 16) * S), ((x + 24) * S, (y + 21) * S), ((x + 29) * S, (y + 26) * S)], fill=RED)
    elif kind == "strike":
        d.polygon([((x + 8) * S, (y + 17) * S), ((x + 14) * S, (y + 5) * S), ((x + 17) * S, (y + 7) * S),
                   ((x + 14) * S, (y + 17) * S), ((x + 20) * S, (y + 6) * S), ((x + 23) * S, (y + 8) * S),
                   ((x + 18) * S, (y + 19) * S), ((x + 24) * S, (y + 11) * S), ((x + 27) * S, (y + 13) * S),
                   ((x + 20) * S, (y + 23) * S), ((x + 20) * S, (y + 30) * S), ((x + 8) * S, (y + 30) * S)], fill=col)
        d.line([((x + 8) * S, (y + 17) * S), ((x + 3) * S, (y + 24) * S)], fill=RED, width=2 * S)
    elif kind == "exam":
        rect(x + 4, y + 2, 19, 26, (252, 250, 243), col, 0.9)
        for yy in (y + 8, y + 14, y + 20):
            d.line([((x + 8) * S, yy * S), ((x + 19) * S, yy * S)], fill=(150, 143, 130), width=1 * S)
        d.line([((x + 21) * S, (y + 24) * S), ((x + 29) * S, (y + 15) * S)], fill=RED, width=2 * S)
        d.polygon([((x + 21) * S, (y + 24) * S), ((x + 22) * S, (y + 29) * S), ((x + 19) * S, (y + 27) * S)], fill=RED)
    elif kind == "chart":
        for i, hh in enumerate([7, 12, 18, 24, 30]):
            d.rectangle([(x + 2 + i * 5.5) * S, (y + 30 - hh) * S, (x + 6 + i * 5.5) * S, (y + 30) * S], fill=col)
        d.line([((x + 1) * S, (y + 25) * S), ((x + 30) * S, (y + 3) * S)], fill=RED, width=2 * S)
        d.polygon([((x + 30) * S, (y + 3) * S), ((x + 23) * S, (y + 5) * S), ((x + 28) * S, (y + 10) * S)], fill=RED)

BRIEF_Y = 414
BW, BH, BG = (948 - 40) / 5, 112, 10
for i, (num, region, cat, head, det, kind) in enumerate(briefs):
    bx = 38 + (i % 5) * (BW + BG)
    by = BRIEF_Y + (i // 5) * (BH + 10)
    rect(bx, by, BW, BH, (250, 247, 239), (170, 162, 148), 0.7)
    rect(bx, by, BW, 34, tint(REGIONS[region], 0.80))
    rect(bx, by + 34, BW, 1, REGIONS[region])
    text(bx + BW - 7, by + 4, num, f(GEORGIA_B, 11.5), REGIONS[region], anchor="ra")
    icon(kind, bx + 8, by + 2)
    text(bx + 8, by + 39, cat, f(SEGOE_B, 6.2), REGIONS[region], spacing=0.9)
    hf = f(GEORGIA_B, 14.5)
    hy = by + 50
    for ln in wrap(head, hf, BW - 16):
        text(bx + 8, hy, ln, hf, INK)
        hy += 15
    para(bx + 8, hy + 2, det, f(SEGOE, 8.0), BW - 14, (78, 70, 60), 1.1)

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

MX, MY, MW, MH = 38, 650, 448, 240
LAT_T, LAT_B = 80.0, -56.0

def _px(lon):
    return MX + (lon + 180) / 360 * MW

def _py(lat):
    return MY + (LAT_T - lat) / (LAT_T - LAT_B) * (MH - 16)

rect(MX, MY, MW, MH - 16, SEA)
for lon in range(-180, 181, 30):
    d.line([(_px(lon) * S, MY * S), (_px(lon) * S, (MY + MH - 16) * S)], fill=(206, 217, 225), width=1 * S)
for lat in range(-60, 81, 30):
    d.line([(MX * S, _py(lat) * S), ((MX + MW) * S, _py(lat) * S)], fill=(206, 217, 225), width=1 * S)

STEP = 5
for gy in range(3, MH - 19, STEP):
    lat = LAT_T - (gy + 0.5) / (MH - 16) * (LAT_T - LAT_B)
    for gx in range(3, MW - 2, STEP):
        lon = (gx + 0.5) / MW * 360 - 180
        if _on_land(lon, lat):
            r = 1.1
            d.ellipse([(MX + gx - r) * S, (MY + gy - r) * S, (MX + gx + r) * S, (MY + gy + r) * S],
                      fill=(74, 82, 92))

pins = [
    ("1", 114.06, 22.54, "ASIA-PACIFIC"), ("2", 4.3, 52.1, "EUROPE"),
    ("3", -80.2, 25.8, "THE AMERICAS"), ("4", 36.5, 45.3, "EUROPE"),
    ("5", 56.5, 26.5, "MIDDLE EAST"), ("6", 34.4, 31.4, "MIDDLE EAST"),
    ("7", 90.4, 23.8, "ASIA-PACIFIC"), ("8", -51.7, 64.2, "EUROPE"),
    ("9", 4.4, 50.8, "EUROPE"), ("10", 37.9, 14.9, "AFRICA"),
    ("11", -74.1, 4.7, "THE AMERICAS"), ("12", 127.0, 37.5, "ASIA-PACIFIC"),
    ("13", 149.1, -35.3, "OCEANIA"),
]
fpin = f(SEGOE_B, 8)
placed = []
for nm, lon, lat, region in pins:
    x, y = _px(lon), _py(lat)
    ty = y
    for (ox, oy) in placed:
        while abs(x - ox) < 14 and abs(y - oy) < 14:
            y += 15
    if abs(y - ty) > 1:
        d.line([(x * S, ty * S), (x * S, y * S)], fill=REGIONS[region], width=1 * S)
    d.ellipse([(x - 7) * S, (y - 7) * S, (x + 7) * S, (y + 7) * S],
              fill=REGIONS[region], outline=PAPER, width=int(1.2 * S))
    text(x, y, nm, fpin, PAPER, anchor="mm")
    placed.append((x, y))

text(MX + 4, MY + MH - 13, "NUMBERS MARK STORIES 1\u201313  ·  GREY DOTS ARE LAND",
     f(SEGOE_B, 6.6), GREY, spacing=0.7)

AX, AY, AW = 500, 650, 486
rect(AX, AY, AW, 22, INK)
text(AX + 8, AY + 6, "ALSO ON THURSDAY 19 NOVEMBER", f(SEGOE_B, 8.4), PAPER, spacing=1.3)
text(AX + AW - 8, AY + 6, "14\u201331", f(SEGOE_B, 8.4), (230, 210, 190), anchor="ra", spacing=1.1)

colw = (AW - 8) / 2
for i, (num, region, place, line) in enumerate(also):
    col = i // 9
    row = i % 9
    x = AX + 8 + col * (colw + 4)
    y = AY + 30 + row * 23
    d.rectangle([x * S, (y + 1) * S, (x + 2.5) * S, (y + 8) * S], fill=REGIONS[region])
    text(x + 6, y, num, f(SEGOE_B, 7.4), RED)
    text(x + 21, y, place + " \u2014 ", f(SEGOE_B, 7.4), INK, spacing=0.3)
    off = 21 + f(SEGOE_B, 7.4).getlength(place + " \u2014 ") / S
    text(x + off + 3, y, line, f(SEGOE, 9.0), (52, 47, 41))

# ---------------------------------------------------------------- date check
DY = 906
rect(38, DY, 948, 34, None, RED, 1)
text(46, DY + 10, "DATE CHECK", f(SEGOE_B, 7.8), RED, spacing=1.4)
para(112, DY + 8,
     "First reported before Thursday, so not counted above: Fiji's drought disaster (Wed 18)  \u00b7  "
     "US measles-elimination loss (Tue 17)  \u00b7  Voyager 1 at one light-day (Wed 18)  \u00b7  "
     "Delhi schools reopening (Wed 18).",
     f(SEGOE, 7.4), 866, (52, 47, 41), 1.12)

# ---------------------------------------------------------------- footer
rect(38, 948, 948, 1, INK)
para(38, 953,
     "Every story here happened, or was first reported, on Thursday 19 November 2026. "
     "Claims are attributed, not stated as fact.",
     f(SEGOE, 7.2), 600, GREY, 1.05)
text(986, 953, "SOURCES: REUTERS \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 GUARDIAN \u00b7 BLOOMBERG \u00b7 AL JAZEERA \u00b7 YONHAP \u00b7 ABC \u00b7 NYT \u00b7 PEW \u00b7 ICJ",
     f(SEGOE_B, 6.2), GREY, anchor="ra", spacing=0.4)

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
print("saved", img.size, "stories", total)
