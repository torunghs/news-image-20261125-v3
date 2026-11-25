#!/usr/bin/env python3
"""GLOBAL DAILY -- front page renderer (25 November 2026).

Draws a 1024x1024 newspaper front page and writes it as ``entry.png``
into ``$MAKEFUN_OUTPUT_DIR`` (default ``/output``).

Standard library only; fully deterministic: no clock, no randomness,
no network access, no sibling imports. The PNG bytes are written with
a hand-rolled encoder (zlib + struct) and the lettering uses a small
hand-drawn 5x7 bitmap font defined below.
"""

import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

# Palette.
PAPER = (247, 243, 232)
INK = (20, 20, 20)
GREY = (112, 110, 102)
RULE = (60, 58, 52)
NIGHT = (12, 20, 52)
NIGHT_DEEP = (8, 12, 34)
GROUND = (18, 24, 48)
MOON = (238, 228, 178)
CRATER = (205, 192, 140)
BODY_WHITE = (240, 240, 238)
ROCKET_RED = (198, 44, 36)
PANEL_BLUE = (52, 96, 168)
PANEL_LINE = (180, 200, 225)
FLAME = (244, 164, 40)
FLAME_CORE = (252, 222, 90)
SMOKE = (196, 198, 204)
STAR = (245, 245, 230)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------------------
# Hand-drawn 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink.
# Only the characters the page needs are defined (capitals, digits and a
# handful of punctuation marks); anything else renders as a blank.
# ---------------------------------------------------------------------------

FONT = {
    "A": (" ##  ", "#  # ", "#  # ", "#### ", "#  # ", "#  # ", "#  # "),
    "B": ("#### ", "#  # ", "#  # ", "#### ", "#  # ", "#  # ", "#### "),
    "C": (" ### ", "#    ", "#    ", "#    ", "#    ", "#    ", " ### "),
    "D": ("#### ", "#  # ", "#  # ", "#  # ", "#  # ", "#  # ", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ### ", "#    ", "#    ", "# ## ", "#  # ", "#  # ", " ##  "),
    "H": ("#  # ", "#  # ", "#  # ", "#### ", "#  # ", "#  # ", "#  # "),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#  # ", "#  # "),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#  # ", "## ##", "# # #", "# # #", "#  # ", "#  # ", "#  # "),
    "N": ("#  # ", "## # ", "# ## ", "#  ##", "#  # ", "#  # ", "#  # "),
    "O": (" ### ", "#  # ", "#  # ", "#  # ", "#  # ", "#  # ", " ### "),
    "P": ("#### ", "#  # ", "#  # ", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#  # ", "#  # ", "#  # ", "# ## ", "#  # ", " ## #"),
    "R": ("#### ", "#  # ", "#  # ", "#### ", "# #  ", "#  # ", "#  # "),
    "S": (" ####", "#    ", "#    ", " ##  ", "   # ", "   # ", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#  # ", "#  # ", "#  # ", "#  # ", "#  # ", "#  # ", " ### "),
    "V": ("#  # ", "#  # ", "#  # ", "#  # ", "#  # ", " # # ", "  #  "),
    "W": ("#  # ", "#  # ", "#  # ", "# ## ", "# # #", "## ##", "#  # "),
    "X": ("#  # ", "#  # ", " # # ", "  #  ", " # # ", "#  # ", "#  # "),
    "Y": ("#  # ", "#  # ", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "   # ", "  #  ", " #   ", "#    ", "#    ", "#####"),
    "0": (" ### ", "#  # ", "#  ##", "# # #", "##  #", "#  # ", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#  # ", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "3": ("#### ", "   # ", "   # ", " ### ", "   # ", "   # ", "#### "),
    "4": ("  #  ", " ##  ", "# #  ", "#  # ", "#####", "  #  ", "  #  "),
    "5": ("#####", "#    ", "#### ", "   # ", "   # ", "#  # ", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#  # ", "#  # ", " ### "),
    "7": ("#####", "   # ", "   # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#  # ", "#  # ", " ### ", "#  # ", "#  # ", " ### "),
    "9": (" ### ", "#  # ", "#  # ", " ####", "   # ", "   # ", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#  # ", "   # ", "  #  ", "  #  ", "     ", "  #  "),
    "/": ("   # ", "   # ", "  #  ", "  #  ", " #   ", "#    ", "#    "),
    "%": ("#  # ", "#  # ", "  #  ", "  #  ", " #   ", "#  # ", "#  # "),
    "(": ("  #  ", " #   ", "#    ", "#    ", "#    ", " #   ", "  #  "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# #  ", "#  # ", " ## #"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
}

# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray plus small shape helpers.
# ---------------------------------------------------------------------------

canvas = bytearray(WIDTH * HEIGHT * 3)


def fill_rect(x, y, w, h, color):
    """Fill an axis-aligned rectangle, clipped to the page."""
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(WIDTH, x + w)
    y1 = min(HEIGHT, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        start = (yy * WIDTH + x0) * 3
        canvas[start:start + len(row)] = row


def fill_circle(cx, cy, r, color):
    """Fill a disc of radius r centred on (cx, cy)."""
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def fill_triangle(a, b, c, color):
    """Fill a triangle given as three (x, y) points, scanline by scanline."""
    pts = sorted([a, b, c], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    for y in range(ay, cy + 1):
        xs = []
        for (x1, y1), (x2, y2) in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[0], pts[2])):
            if y1 == y2:
                continue
            lo, hi = (y1, y2) if y1 < y2 else (y2, y1)
            if lo <= y < hi or (y == cy and y == hi):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        if len(xs) >= 2:
            x0 = int(round(min(xs)))
            x1 = int(round(max(xs)))
            fill_rect(x0, y, x1 - x0 + 1, 1, color)


# ---------------------------------------------------------------------------
# Text: measuring, drawing and word-wrapping with the bitmap font.
# ---------------------------------------------------------------------------

CHAR_ADVANCE = 6  # 5 glyph columns + 1 blank column


def text_width(text, scale):
    """Pixel width of text at the given integer scale."""
    if not text:
        return 0
    return len(text) * CHAR_ADVANCE * scale - scale


def draw_text(x, y, text, scale, color):
    """Draw text with its top-left corner at (x, y)."""
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row, line in enumerate(glyph):
            for col, cell in enumerate(line):
                if cell == "#":
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += CHAR_ADVANCE * scale


def draw_text_centred(x, y, width, text, scale, color):
    """Draw text centred inside the horizontal span [x, x + width)."""
    tw = text_width(text, scale)
    draw_text(x + max(0, (width - tw) // 2), y, text, scale, color)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# PNG writer (8-bit RGB, no filtering) built on zlib.
# ---------------------------------------------------------------------------

def _png_chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    """Encode the canvas as a PNG file."""
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)  # filter type 0 (None) for every scanline
        start = y * WIDTH * 3
        raw.extend(canvas[start:start + WIDTH * 3])
    blob = b"\x89PNG\r\n\x1a\n"
    blob += _png_chunk(b"IHDR",
                       struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0))
    blob += _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    blob += _png_chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(blob)


# ---------------------------------------------------------------------------
# Hero panel: night sky, moon, stars, rocket on its pad, space station.
# ---------------------------------------------------------------------------

STARS = [
    (66, 168, 2), (128, 214, 2), (178, 156, 3), (238, 236, 2),
    (408, 158, 2), (512, 208, 3), (636, 152, 2), (748, 214, 2),
    (872, 292, 2), (946, 306, 3), (96, 306, 2), (196, 336, 2),
    (556, 258, 2), (692, 158, 3), (818, 336, 2), (956, 386, 2),
    (62, 412, 2), (476, 296, 2), (344, 182, 2), (606, 372, 2),
    (780, 176, 2), (160, 396, 2),
]


def draw_hero(x, y, w, h):
    """Paint the night-sky hero panel inside [x, x+w) x [y, y+h)."""
    fill_rect(x, y, w, h, NIGHT)
    fill_rect(x, y + h - 42, w, 42, GROUND)
    # Caption strip along the top of the sky.
    draw_text(x + 16, y + 12, "SHENZHOU-24 LIFTS OFF FROM JIUQUAN",
              2, STAR)
    # Stars.
    for sx, sy, sr in STARS:
        fill_circle(x + sx, y + sy, sr, STAR)
    # Moon, top right, with craters.
    mx, my = x + 878, y + 58
    fill_circle(mx, my, 34, MOON)
    fill_circle(mx - 12, my - 8, 7, CRATER)
    fill_circle(mx + 10, my + 10, 9, CRATER)
    fill_circle(mx + 14, my - 14, 5, CRATER)
    # Space station, right of centre: core module, node, solar wings.
    fill_rect(x + 596, y + 158, 190, 30, BODY_WHITE)
    fill_rect(x + 596, y + 158, 190, 4, GREY)
    fill_rect(x + 640, y + 188, 102, 22, BODY_WHITE)
    fill_circle(x + 691, y + 173, 12, BODY_WHITE)
    fill_rect(x + 688, y + 140, 6, 20, BODY_WHITE)  # antenna mast
    fill_circle(x + 691, y + 136, 4, FLAME_CORE)
    for wing_x in (x + 500, x + 790):
        fill_rect(wing_x, y + 150, 92, 46, PANEL_BLUE)
        for gx in range(wing_x + 12, wing_x + 92, 12):
            fill_rect(gx, y + 150, 1, 46, PANEL_LINE)
        fill_rect(wing_x, y + 172, 92, 1, PANEL_LINE)
    fill_rect(x + 592, y + 168, 4, 10, GREY)  # docking port
    # Rocket on its pad, left of centre.
    rx = x + 300  # centre line of the rocket
    base = y + h - 42
    # Exhaust flame and smoke.
    fill_triangle((rx - 16, base), (rx + 16, base), (rx, base + 34), FLAME)
    fill_triangle((rx - 8, base), (rx + 8, base), (rx, base + 22), FLAME_CORE)
    fill_circle(rx - 44, base + 12, 14, SMOKE)
    fill_circle(rx + 46, base + 16, 16, SMOKE)
    fill_circle(rx - 62, base + 26, 10, SMOKE)
    fill_circle(rx + 66, base + 28, 11, SMOKE)
    # Fins.
    fill_triangle((rx - 20, base), (rx - 20, base - 42), (rx - 48, base), ROCKET_RED)
    fill_triangle((rx + 20, base), (rx + 20, base - 42), (rx + 48, base), ROCKET_RED)
    # Body and nose cone.
    fill_rect(rx - 20, base - 118, 40, 118, BODY_WHITE)
    fill_triangle((rx - 20, base - 118), (rx + 20, base - 118),
                  (rx, base - 164), ROCKET_RED)
    # Port window and hull band.
    fill_circle(rx, base - 88, 9, PANEL_BLUE)
    fill_circle(rx, base - 88, 4, WHITE)
    fill_rect(rx - 20, base - 46, 40, 6, ROCKET_RED)
    # Launch pad deck and legs.
    fill_rect(rx - 70, base, 140, 8, GREY)
    fill_rect(rx - 66, base + 8, 8, 34, RULE)
    fill_rect(rx + 58, base + 8, 8, 34, RULE)


# ---------------------------------------------------------------------------
# Page layout: masthead, hero, headline, stories, cards, strip, footer.
# ---------------------------------------------------------------------------

MARGIN = 40
CONTENT = WIDTH - 2 * MARGIN  # 944 px of text width


def draw_page():
    fill_rect(0, 0, WIDTH, HEIGHT, PAPER)

    # Masthead.
    draw_text_centred(0, 22, WIDTH, "GLOBAL DAILY", 8, INK)
    fill_rect(MARGIN, 92, CONTENT, 3, INK)
    fill_rect(MARGIN, 99, CONTENT, 1, INK)
    draw_text_centred(0, 108, WIDTH, "WEDNESDAY 25 NOVEMBER 2026", 2, INK)

    # Hero panel.
    draw_hero(MARGIN, 132, CONTENT, 338)

    # Main headline, two lines.
    draw_text_centred(0, 484, WIDTH, "FIRST FOREIGN ASTRONAUT", 5, INK)
    draw_text_centred(0, 524, WIDTH, "FLIES TO TIANGONG", 5, INK)

    # Main story body.
    main_body = (
        "PAKISTAN'S MUHAMMAD ZEESHAN ALI, 40, JOINS THE CREW OF "
        "SHENZHOU-24, BECOMING THE FIRST PAKISTANI IN ORBIT AND THE "
        "FIRST FOREIGN ASTRONAUT ABOARD TIANGONG. THE CREW LIFTED OFF "
        "FROM JIUQUAN AT 00:18 UTC ON A LONG MARCH 2F ROCKET."
    )
    y = 574
    for line in wrap_text(main_body, 2, CONTENT):
        draw_text(MARGIN, y, line, 2, INK)
        y += 20

    # Second story.
    fill_rect(MARGIN, 662, CONTENT, 2, INK)
    draw_text(MARGIN, 674, "US SPY AGENCIES HACKED", 3, INK)
    second_body = (
        "THE UNCLASSIFIED NETWORKS OF THE CIA AND THE OFFICE OF THE "
        "DIRECTOR OF NATIONAL INTELLIGENCE WERE BREACHED. OFFICIALS "
        "SAID NO CLASSIFIED DATA WAS EXPOSED."
    )
    y = 702
    for line in wrap_text(second_body, 2, CONTENT):
        draw_text(MARGIN, y, line, 2, INK)
        y += 20

    # Three news cards in a row.
    fill_rect(MARGIN, 752, CONTENT, 2, INK)
    cards = [
        ("RIYADH DRONE STRIKE",
         "A HOUTHI DRONE HIT THE 385 M PIF TOWER FOR THE SECOND TIME "
         "IN A WEEK. 11 PEOPLE WERE HURT."),
        ("EBOLA EVACUATION",
         "WHO PULLED ITS STAFF FROM AKWE HOSPITAL AFTER THREE DAYS "
         "SHELTERING FROM FIGHTING."),
        ("UKRAINE STRIKES AT SEA",
         "ZELENSKIY CONFIRMED UKRAINIAN STRIKES ON RUSSIAN SHIPS IN "
         "THE GULF OF FINLAND."),
    ]
    card_w = 300
    for i, (title, body) in enumerate(cards):
        cx = MARGIN + i * (card_w + 22)
        draw_text(cx, 764, title, 2, INK)
        fill_rect(cx, 784, 64, 3, ROCKET_RED)
        cy = 794
        for line in wrap_text(body, 2, card_w):
            draw_text(cx, cy, line, 2, INK)
            cy += 18

    # "Also today" strip.
    fill_rect(MARGIN, 892, CONTENT, 56, INK)
    strip = (
        "ALSO TODAY: HUAWEI GUILTY IN US COURT - NEPAL QUAKE 5.6 - "
        "GIULIANI MEDAL - SARKOZY IN COURT - NVIDIA DOWN 6%"
    )
    y = 902
    for line in wrap_text(strip, 2, CONTENT - 24):
        draw_text_centred(MARGIN, y, CONTENT, line, 2, WHITE)
        y += 18

    # Footer.
    draw_text_centred(0, 966, WIDTH, "GLOBAL DAILY - PAGE 1", 2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    draw_page()
    write_png(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
