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
text(kd + 12, 24, "EIGHT STORIES, FOUR CONTINENTS, ONE DAY", kick, GREY, spacing=1.0)
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

# ---------------------------------------------------------------- hero
HX, HY, HW, HH = 38, 344, 948, 236
rect(HX, HY, HW, HH, (223, 228, 231))
# sky gradient
for i in range(HH):
    t = i / HH
    c = tuple(int(214 + (247 - 214) * t) for _ in range(3))
    d.line([(HX * S, (HY + i) * S), ((HX + HW) * S, (HY + i) * S)], fill=c, width=S)

# skyline (fixed hand-tuned towers)
random.seed(20261119)
x = HX - 4
sky = (176, 184, 192)
while x < HX + HW:
    bw = random.choice([34, 44, 54, 62, 74])
    bh = random.choice([46, 66, 88, 104, 124, 142])
    top = HY + 190 - bh
    d.rectangle([x * S, top * S, (x + bw) * S, (HY + 190) * S], fill=sky)
    if random.random() < 0.5:
        sx = x + bw // 2
        d.line([(sx * S, (top - 16) * S), (sx * S, top * S)], fill=sky, width=2 * S)
    x += bw + random.choice([3, 6, 10])
# haze band over skyline
rect(HX, HY + 176, HW, 16, (223, 228, 231))

# summit hall floor
d.rectangle([HX * S, (HY + 190) * S, (HX + HW) * S, (HY + HH) * S], fill=(232, 226, 214))

# flags hanging from a rod
rod_y = HY + 18
d.line([((HX + 300) * S, rod_y * S), ((HX + 648) * S, rod_y * S)], fill=(60, 55, 48), width=3 * S)

def flag_us(x, y, w, h):
    rect(x, y, w, h, (255, 255, 255), (120, 120, 120), 0.5)
    sh = h / 13
    for i in range(1, 13, 2):
        rect(x, y + i * sh, w, sh, (190, 45, 52))
    rect(x, y, w * 0.42, sh * 7, (37, 55, 95))
    for r in range(3):
        for c in range(4):
            d.ellipse([(x + 6 + c * w * 0.1) * S, (y + 6 + r * 10) * S,
                       (x + 9 + c * w * 0.1) * S, (y + 9 + r * 10) * S], fill=(255, 255, 255))

def flag_cn(x, y, w, h):
    rect(x, y, w, h, (206, 45, 45), (150, 30, 30), 0.5)
    cx, cy = x + 18, y + 17
    star = []
    for k in range(10):
        r = 11 if k % 2 == 0 else 4.6
        a = -math.pi / 2 + k * math.pi / 5
        star.append(((cx + r * math.cos(a)) * S, (cy + r * math.sin(a)) * S))
    d.polygon(star, fill=(250, 220, 90))
    for (ox, oy) in [(34, 8), (42, 16), (42, 27), (34, 34)]:
        s = 4.2
        pts = []
        for k in range(10):
            r = s if k % 2 == 0 else s / 2.4
            a = -math.pi / 2 + k * math.pi / 5
            pts.append(((x + ox + r * math.cos(a)) * S, (y + oy + r * math.sin(a)) * S))
        d.polygon(pts, fill=(250, 220, 90))

def flag_ru(x, y, w, h):
    rect(x, y, w, h / 3, (250, 250, 250), (150, 150, 150), 0.4)
    rect(x, y + h / 3, w, h / 3, (38, 62, 125))
    rect(x, y + 2 * h / 3, w, h / 3, (190, 45, 52))
    rect(x, y, w, h, None, (110, 110, 110), 0.4)

FW, FH = 104, 62
for fx, fn in [(HX + 306, flag_us), (HX + 424, flag_cn), (HX + 542, flag_ru)]:
    d.line([(fx * S, rod_y * S), (fx * S, (rod_y + 8) * S)], fill=(60, 55, 48), width=int(1.5 * S))
    fn(fx, rod_y + 8, FW, FH)

# negotiating table
d.ellipse([(HX + 120) * S, (HY + 154) * S, (HX + 828) * S, (HY + 242) * S],
          fill=(70, 58, 45))
d.ellipse([(HX + 120) * S, (HY + 148) * S, (HX + 828) * S, (HY + 234) * S],
          fill=(108, 90, 68))
d.ellipse([(HX + 148) * S, (HY + 158) * S, (HX + 800) * S, (HY + 220) * S],
          fill=(124, 105, 79))
d.arc([(HX + 148) * S, (HY + 158) * S, (HX + 800) * S, (HY + 220) * S],
      200, 340, fill=(150, 129, 99), width=2 * S)

# place cards
names = [("TRUMP", 396), ("XI", 514), ("PUTIN", 632)]
for nm, cx in names:
    cw = 90 if nm != "XI" else 58
    rect(cx - cw / 2, HY + 178, cw, 26, (250, 247, 239), (60, 50, 40), 0.8, 2)
    text(cx, HY + 184, nm, f(SEGOE_B, 11), INK, anchor="ma", spacing=1.2)

# microphones
for mx in (450, 514, 578):
    d.line([(mx * S, (HY + 236) * S), (mx * S, (HY + 206) * S)], fill=(40, 36, 30), width=2 * S)
    d.ellipse([(mx - 5) * S, (HY + 198) * S, (mx + 5) * S, (HY + 208) * S], fill=(40, 36, 30))

# hero caption / labels
rect(HX, HY + HH, 948, 22, INK)
text(HX + 10, HY + HH + 4, "SHENZHEN", f(SEGOE_B, 9.5), PAPER, spacing=1.6)
text(HX + 104, HY + HH + 4, "Three leaders, one table: the war in Ukraine is the first item.", f(SEGOE, 11.5), (232, 226, 214))

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
    ("EUROPE", "KERCH BRIDGE CUT", "Ukraine breaks the Crimea road link with drones and Flamingo missiles; Russia blames Dutch arms.", "bridge"),
    ("MIDDLE EAST", "IRAN: STRIKES WEIGHED", "Trump considers a joint attack with Israel, which warns of chemical weapons. Oil near $92.", "missile"),
    ("SOUTH ASIA", "BANGLADESH SHUT DOWN", "Hasina's protests close cities; Yunus's ancestral home burned; two killed.", "protest"),
    ("ARCTIC", "GREENLAND DEAL", "Denmark ratifies a security pact with Trump; the US plans a \"Golden Dome\" in the Arctic.", "arctic"),
    ("MARKETS", "ANTHROPIC'S RECORD IPO", "Priced at $83 a share, the biggest listing ever; Nasdaq futures jump 2%.", "chart"),
    ("PACIFIC", "FIJI: DROUGHT DISASTER", "An El Niño drought prompts a national state of disaster; water is rationed.", "drought"),
]

for i, (cat, head, body, icon) in enumerate(stories):
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
    para(tx, hy + 5, body, f(SEGOE, 11.8), tw, (60, 54, 46), 1.26)

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
