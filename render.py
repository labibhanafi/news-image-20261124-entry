#!/usr/bin/env python3
"""Render news-image-20261124 entry.png — 1024x1024 front page.

Own work, written in-session for make.fun news-image-20261124.
46 stories, 7 regions + global, all first reported Tue 24 Nov 2026.
Deterministic: fixed seed grain, fixed fonts, fixed layout.
Run: python3 render.py  -> writes entry.png next to this script.
"""
import hashlib
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = Path(__file__).resolve().parent / "entry.png"
SEED = 20261124

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF_B = f"{FONT_DIR}/DejaVuSerif-Bold.ttf"
SERIF = f"{FONT_DIR}/DejaVuSerif.ttf"
SANS_B = f"{FONT_DIR}/DejaVuSans-Bold.ttf"
SANS = f"{FONT_DIR}/DejaVuSans.ttf"

PAPER = (247, 242, 231)
INK = (26, 26, 26)
NAVY = (20, 38, 63)
NAVY_LT = (38, 62, 96)
RED = (179, 39, 30)
GOLD = (201, 162, 39)
GRAY = (90, 90, 90)
RULE = (180, 172, 155)

REGION_COLORS = {
    "MIDDLE EAST": (140, 47, 47),
    "AFRICA": (122, 90, 31),
    "EUROPE": (31, 78, 121),
    "EAST ASIA": (179, 39, 30),
    "N. AMERICA": (20, 83, 45),
    "SOUTH ASIA": (107, 63, 160),
    "LATIN AMERICA": (14, 116, 144),
    "GLOBAL": (85, 85, 85),
}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_flame(draw, x, y, s):
    """Layered flame above (x, y) — base point, scale s."""
    layers = [
        ((255, 90, 0), [(x - 16 * s, y), (x - 6 * s, y - 34 * s),
                        (x + 2 * s, y - 18 * s), (x + 10 * s, y - 40 * s),
                        (x + 18 * s, y - 6 * s), (x + 8 * s, y)]),
        ((255, 160, 20), [(x - 11 * s, y), (x - 4 * s, y - 24 * s),
                          (x + 3 * s, y - 12 * s), (x + 8 * s, y - 28 * s),
                          (x + 13 * s, y - 4 * s), (x + 5 * s, y)]),
        ((255, 220, 90), [(x - 6 * s, y), (x - 2 * s, y - 14 * s),
                          (x + 2 * s, y - 7 * s), (x + 5 * s, y - 16 * s),
                          (x + 8 * s, y - 2 * s), (x + 3 * s, y)]),
    ]
    for color, pts in layers:
        draw.polygon(pts, fill=color)


def draw_tanker(draw, x, y, w, h, hull=(24, 24, 28), deck=(214, 205, 190)):
    """Simple tanker silhouette; (x, y) top-left of hull."""
    draw.rectangle([x, y, x + w, y + h], fill=hull)
    draw.rectangle([x, y - 8, x + w, y], fill=deck)
    # bow
    draw.polygon([(x + w, y), (x + w + 18, y + h // 2), (x + w, y + h)],
                 fill=hull)
    # superstructure + funnel
    draw.rectangle([x + w - 52, y - 30, x + w - 12, y - 8], fill=(232, 226, 212))
    draw.rectangle([x + 14, y - 22, x + 30, y - 8], fill=(179, 39, 30))
    # containers
    for i in range(4):
        cx = x + 44 + i * 26
        draw.rectangle([cx, y - 16, cx + 22, y - 8],
                       fill=(90 + i * 18, 110 - i * 8, 120))
    # portholes
    for i in range(6):
        draw.ellipse([x + 12 + i * 16, y + h // 2 - 3, x + 18 + i * 16,
                      y + h // 2 + 3], fill=(255, 220, 120))


def draw_mine(draw, x, y, r=7):
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(20, 20, 20))
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1),
                   (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7), (0.7, 0.7)]:
        draw.line([x + dx * r, y + dy * r, x + dx * (r + 5), y + dy * (r + 5)],
                  fill=(20, 20, 20), width=2)


def draw_scene(draw, x0, y0, w, h):
    """Strait of Hormuz at dusk: sky, sun, sea, 3 tankers, fire, mines."""
    # sky gradient bands
    sky_top = (43, 58, 85)
    sky_bot = (198, 110, 48)
    bands = 14
    for i in range(bands):
        t = i / (bands - 1)
        c = tuple(int(sky_top[j] + (sky_bot[j] - sky_top[j]) * t)
                  for j in range(3))
        draw.rectangle([x0, y0 + i * h // 3 // bands, x0 + w,
                        y0 + (i + 1) * h // 3 // bands + 1], fill=c)
    # sun
    draw.ellipse([x0 + w - 150, y0 + 18, x0 + w - 96, y0 + 72],
                 fill=(255, 214, 130))
    # distant shore
    draw.polygon([(x0, y0 + h // 3), (x0 + 180, y0 + h // 3 - 14),
                  (x0 + 420, y0 + h // 3 - 4), (x0 + w, y0 + h // 3 - 10),
                  (x0 + w, y0 + h // 3 + 6), (x0, y0 + h // 3 + 6)],
                 fill=(52, 48, 60))
    # sea bands
    sea_top = (28, 68, 78)
    sea_bot = (12, 32, 40)
    for i in range(10):
        t = i / 9
        c = tuple(int(sea_top[j] + (sea_bot[j] - sea_top[j]) * t)
                  for j in range(3))
        draw.rectangle([x0, y0 + h // 3 + i * (2 * h // 3) // 10, x0 + w,
                        y0 + h // 3 + (i + 1) * (2 * h // 3) // 10 + 1],
                       fill=c)
    # sun reflection
    for i in range(6):
        yy = y0 + h // 3 + 14 + i * 16
        ww = 60 - i * 6
        draw.rectangle([x0 + w - 150 + i * 4, yy, x0 + w - 150 + ww, yy + 4],
                       fill=(255, 190, 90))
    # wave strokes
    rng = random.Random(SEED)
    for _ in range(26):
        wx = x0 + rng.randint(0, w - 60)
        wy = y0 + h // 3 + rng.randint(8, 2 * h // 3 - 8)
        draw.line([wx, wy, wx + rng.randint(20, 55), wy],
                  fill=(120, 170, 180), width=2)
    # tankers (back to front)
    draw_tanker(draw, x0 + 330, y0 + h - 118, 200, 26)
    draw_flame(draw, x0 + 400, y0 + h - 118, 0.9)
    draw_flame(draw, x0 + 470, y0 + h - 118, 0.7)
    draw_tanker(draw, x0 + 60, y0 + h - 96, 230, 30)
    draw_flame(draw, x0 + 150, y0 + h - 96, 1.15)
    draw_flame(draw, x0 + 230, y0 + h - 96, 0.8)
    # smoke (kept inside the scene frame)
    for sx, sy, sr in [(x0 + 150, y0 + 62, 14), (x0 + 168, y0 + 44, 17),
                       (x0 + 138, y0 + 28, 20), (x0 + 400, y0 + 70, 12),
                       (x0 + 415, y0 + 52, 15)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(70, 70, 74))
    # mines
    draw_mine(draw, x0 + 300, y0 + h - 40)
    draw_mine(draw, x0 + 560, y0 + h - 28, 6)
    # frame
    draw.rectangle([x0, y0, x0 + w - 1, y0 + h - 1], outline=INK, width=2)


# ---------------------------------------------------------------- stories
LEAD = {
    "kicker": "LEAD  •  MIDDLE EAST",
    "headline": "THREE TANKERS ABLAZE IN THE STRAIT OF HORMUZ",
    "deck": ("Iran's Revolutionary Guard says three oil tankers hit mines "
             "in the Strait of Hormuz; a fourth blaze was reported."),
    "source": "Al Jazeera live, 24 Nov 00:00 UTC  •  IRGC / JPost",
}

SECONDARY = [
    ("EAST ASIA", "KOREA ON ALERT AS RUSSIAN JETS NEAR ULLEUNG",
     "Alert issued 07:52, lifted 07:55; fighters scrambled."),
    ("TECH  •  MARKETS", "HUANG BACK AT NVIDIA; SHARES SOAR 31%",
     "Board reinstates Jensen Huang as CEO; AI stocks rally."),
]

# (region, headline) — 43 grid stories
GRID = [
    ("MIDDLE EAST", "GAZA DRONE STRIKE KILLS THREE AT POLICE POST"),
    ("MIDDLE EAST", "A THIRD OF CHILD ATTACKS WORLDWIDE IN PALESTINE"),
    ("MIDDLE EAST", "IRAN WARNS EU BASES: MISSILES \u2018REACH 4,500 KM\u2019"),
    ("MIDDLE EAST", "IRAN FILES RIGHTS CASES IN US AND EU COURTS"),
    ("MIDDLE EAST", "FRANCE CONDEMNS SETTLER ATTACKS ON VILLAGES"),
    ("MIDDLE EAST", "SYRIA LANDMINE BLAST KILLS FIVE CHILDREN"),
    ("AFRICA", "LIBYA DEMANDS ANSWERS ON BENGHAZI SHIP ATTACKS"),
    ("AFRICA", "SUDAN\u2019S WOMEN LEFT ALONE AMID WAR"),
    ("EUROPE", "RUSSIAN DRONE BRIEFLY VIOLATES POLISH AIRSPACE"),
    ("EUROPE", "ESTONIA REJECTS RUSSIAN AIRSPACE CLAIM"),
    ("EUROPE", "MURMANSK GOVERNOR HELD ON EMBEZZLEMENT CLAIM"),
    ("EUROPE", "MOSCOW HINTS AT RESUMING TALKS WITH US, KYIV"),
    ("EUROPE", "KYIV REGION TOLL RISES TO 12 AFTER DYMER STRIKE"),
    ("EUROPE", "ODESA STILL WITHOUT POWER, HEAT OR WATER"),
    ("EUROPE", "EU ACADEMY HIT BY CYBERATTACK; DATA EXPOSED"),
    ("EUROPE", "DENMARK TOP COURT BACKS \u2018GHETTO LAW\u2019 EVICTIONS"),
    ("EUROPE", "UK TO BUILD UKRAINE\u2019S DRONE DESIGNS IN BRITAIN"),
    ("EUROPE", "EU LISTS \u2018THE BASE\u2019 FOUNDER NAZZARO"),
    ("EUROPE", "BRITAIN NAMES ENERGY CHIEF TO LEAD REVIVAL"),
    ("EUROPE", "KING CHARLES REACHES OUT TO MEGHAN"),
    ("EUROPE", "DUTCH ACTIVIST, 28, DIES BY EUTHANASIA"),
    ("EUROPE", "ERDOGAN: COP31 LAID GROUNDWORK DESPITE NO DEAL"),
    ("EUROPE", "LION ON THE LOOSE NEAR ISTANBUL; HUGE SEARCH"),
    ("EAST ASIA", "KOREA NAMES NEW FOREIGN MINISTER, INTEL CHIEF"),
    ("EAST ASIA", "KOREA EDUCATION MINISTER QUITS OVER AI RULES"),
    ("EAST ASIA", "CHINA: OFFICIAL SENTENCED TO DEATH FOR LEAKS"),
    ("EAST ASIA", "SK HYNIX JUMPS 20% ON HUANG\u2019S RETURN"),
    ("EAST ASIA", "TAIWAN FLAGS 2,700 CHINA-LINKED ACCOUNTS"),
    ("N. AMERICA", "TRUMP HITS NEWSOM OVER 548 COMMUTATIONS"),
    ("N. AMERICA", "O\u2019HARE BRIEF GROUND STOP IN HOLIDAY RUSH"),
    ("N. AMERICA", "EX-MISSISSIPPI MAYOR JAILED 37 MONTHS"),
    ("N. AMERICA", "MINNESOTA CHILD CENTRES RAIDED IN $41M PROBE"),
    ("N. AMERICA", "BESSENT: US SEEKS ANSWERS ON NVIDIA CHIPS"),
    ("N. AMERICA", "MOSSAD SAVED SWIFT\u2019S VIENNA SHOWS, EX-CHIEF SAYS"),
    ("SOUTH ASIA", "LAHORE TOPS WORLD POLLUTION LIST; AQI OVER 500"),
    ("SOUTH ASIA", "PAKISTAN QUAKE 4.0 NEAR AFGHAN BORDER"),
    ("SOUTH ASIA", "BANGLADESH GARMENT WORKERS REJECT PAY OFFER"),
    ("SOUTH ASIA", "YUNUS BLAMES \u2018HIGHER LEVEL\u2019 FOR GRAMEEN ATTACKS"),
    ("SOUTH ASIA", "PAKISTAN TO INVITE INDIA TO SCO MEETING"),
    ("LATIN AMERICA", "MEXICO: \u2018CHAPO ISIDRO\u2019 TO FACE TRIAL"),
    ("LATIN AMERICA", "PANAMA, FIRST QUANTUM RESUME COBRE TALKS"),
    ("LATIN AMERICA", "COLOMBIA DRONE STRIKE HITS POLICE POST"),
    ("GLOBAL", "UN CHIEF: AI SAFETY FRAMEWORK WITHIN A YEAR"),
]


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ------------------------------------------------------
    d.rectangle([0, 0, W, 100], fill=NAVY)
    d.rectangle([0, 100, W, 104], fill=GOLD)
    title_f = font(SERIF_B, 44)
    d.text((24, 26), "THE WORLD IN ONE DAY", font=title_f, fill=(247, 242, 231))
    date_f = font(SANS_B, 30)
    date2_f = font(SANS_B, 21)
    d.text((W - 24 - d.textlength("TUESDAY", font=date_f), 14),
           "TUESDAY", font=date_f, fill=GOLD)
    d.text((W - 24 - d.textlength("24 NOVEMBER 2026", font=date2_f), 52),
           "24 NOVEMBER 2026", font=date2_f, fill=(247, 242, 231))

    # ---- sub-bar -------------------------------------------------------
    sub_f = font(SANS_B, 16)
    sub = "46 STORIES  •  7 REGIONS + THE WORLD  •  ALL FIRST REPORTED TUESDAY, 24 NOVEMBER 2026"
    d.text(((W - d.textlength(sub, font=sub_f)) / 2, 112), sub,
           font=sub_f, fill=NAVY)
    d.line([24, 134, W - 24, 134], fill=RULE, width=1)

    # ---- lead ----------------------------------------------------------
    scene_x, scene_y, scene_w, scene_h = 24, 146, 600, 200
    draw_scene(d, scene_x, scene_y, scene_w, scene_h)

    tx = 648
    d.text((tx, 146), LEAD["kicker"], font=font(SANS_B, 15), fill=RED)
    hl_f = font(SERIF_B, 30)
    lines = wrap(d, LEAD["headline"], hl_f, W - 24 - tx)
    y = 168
    for line in lines:
        d.text((tx, y), line, font=hl_f, fill=INK)
        y += 36
    deck_f = font(SANS, 15)
    dlines = wrap(d, LEAD["deck"], deck_f, W - 24 - tx)
    y += 4
    for line in dlines:
        d.text((tx, y), line, font=deck_f, fill=(40, 40, 40))
        y += 19
    y += 4
    d.text((tx, y), LEAD["source"], font=font(SANS, 11), fill=GRAY)

    # ---- secondary row -------------------------------------------------
    sec_y, sec_h = 400, 56
    sec_w = (W - 48 - 16) // 2
    for i, (region, head, deck) in enumerate(SECONDARY):
        x = 24 + i * (sec_w + 16)
        d.rectangle([x, sec_y, x + sec_w, sec_y + sec_h],
                    outline=RULE, width=1)
        d.rectangle([x, sec_y, x + 6, sec_y + sec_h],
                    fill=REGION_COLORS.get(region.split("  ")[0], RED))
        d.text((x + 16, sec_y + 5), region, font=font(SANS_B, 11),
               fill=RED)
        d.text((x + 16, sec_y + 20), head, font=font(SANS_B, 16), fill=INK)
        d.text((x + 16, sec_y + 39), deck, font=font(SANS, 12), fill=GRAY)

    # ---- grid ----------------------------------------------------------
    grid_y0, grid_y1 = 468, 968
    cols = [GRID[i::3] for i in range(3)]
    col_w = (W - 48 - 2 * 16) // 3
    head_f = font(SANS_B, 12)
    for ci, col in enumerate(cols):
        x = 24 + ci * (col_w + 16)
        n = len(col)
        row_h = (grid_y1 - grid_y0) / n
        for ri, (region, head) in enumerate(col):
            y = grid_y0 + ri * row_h
            color = REGION_COLORS[region]
            d.rectangle([x, y + 4, x + 4, y + row_h - 6], fill=color)
            tag = f"{region} \u2014 "
            # region tag + headline, wrapped to 2 lines
            full = tag + head
            lines = wrap(d, full, head_f, col_w - 14)
            ly = y + 2
            for li, line in enumerate(lines[:2]):
                if li == 0 and line.startswith(region):
                    # paint the region tag in its color
                    tw = d.textlength(tag, font=head_f)
                    d.text((x + 12, ly), tag, font=head_f, fill=color)
                    d.text((x + 12 + tw, ly), line[len(tag):], font=head_f,
                           fill=INK)
                else:
                    d.text((x + 12, ly), line, font=head_f, fill=INK)
                ly += 14
            d.line([x, y + row_h - 2, x + col_w, y + row_h - 2],
                   fill=(220, 214, 200), width=1)
        if ci < 2:
            d.line([x + col_w + 8, grid_y0, x + col_w + 8, grid_y1],
                   fill=RULE, width=1)

    # ---- footer --------------------------------------------------------
    d.rectangle([0, 972, W, H], fill=NAVY)
    foot_f = font(SANS, 12)
    f1 = ("Sources: Al Jazeera  •  Reuters  •  AP  •  BBC  •  Times of India  •  "
          "AJU Press  •  Yonhap  •  UKMTO")
    d.text(((W - d.textlength(f1, font=foot_f)) / 2, 980), f1,
           font=foot_f, fill=(200, 205, 215))
    f2 = "THE WORLD IN ONE DAY  —  TUESDAY, 24 NOVEMBER 2026"
    d.text(((W - d.textlength(f2, font=font(SANS_B, 12))) / 2, 998), f2,
           font=font(SANS_B, 12), fill=GOLD)

    # ---- deterministic paper grain (fixed seed) -----------------------
    rng = random.Random(SEED)
    noise = Image.frombytes("L", (W, H), rng.randbytes(W * H))
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, noise_rgb, 0.004)

    img.save(OUT, format="PNG", compress_level=9)
    data = OUT.read_bytes()
    print(f"wrote {OUT} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"stories={1 + len(SECONDARY) + len(GRID)} "
          f"regions=7+global grid_rows={[len(c) for c in cols]}")


if __name__ == "__main__":
    main()
