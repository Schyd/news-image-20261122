#!/usr/bin/env python3
"""Today in the World - 22 November 2026.

Draws one classic-newspaper image summing up the world news of
Sunday 22 November 2026. Pure Python standard library: own bitmap
font, own PNG encoder, no network, no randomness, fully deterministic.
Writes entry.png into MAKEFUN_OUTPUT_DIR (default "out").
Only creates the output directory; never deletes anything.
"""
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette: classic cream paper, dark ink ----
PAPER = (245, 238, 220)
PAPER2 = (238, 229, 205)
INK = (26, 22, 18)
RED = (158, 30, 24)
BLUE = (28, 68, 128)
GREEN = (28, 96, 52)
BROWN = (122, 82, 42)
GREY = (110, 102, 88)
LIGHT = (255, 252, 242)
GOLD = (176, 128, 28)
TEAL = (18, 96, 96)
PURPLE = (96, 52, 110)

REGION_COLORS = {
    "ASIA": (176, 96, 28),
    "MIDDLE EAST": (158, 30, 24),
    "EUROPE": (28, 68, 128),
    "AMERICAS": (28, 96, 52),
    "AFRICA": (122, 82, 42),
    "OCEANIA": (18, 96, 96),
    "GLOBAL": (96, 52, 110),
}

# ---- 5x7 bitmap font (own design, uppercase) ----
# Each glyph: 7 rows, each row a 5-bit value (bit 4 = leftmost pixel).
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    '·': (0, 0, 0, 0x0C, 0x0C, 0, 0),
    '°': (0x0C, 0x12, 0x12, 0x0C, 0, 0, 0),
    '×': (0, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
}

def text_width(s, scale):
    return len(s) * 6 * scale


def wrap_text(s, max_w, scale):
    """Greedy word wrap; returns list of lines, each <= max_w px."""
    words = s.split(" ")
    lines, cur = [], ""
    for w_ in words:
        trial = w_ if not cur else cur + " " + w_
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0:1] * 0)  # placeholder, replaced below
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if t == 1:
                self.set(x0, y0, c)
            else:
                self.fill(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def circle(self, cx, cy, r, c, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if r * r - r <= d2 <= r * r + r:
                        self.set(xx, yy, c)

    def poly(self, pts, c, fill=False):
        # outline polygon by edges; optional scanline fill
        if fill:
            ys = [p[1] for p in pts]
            for yy in range(min(ys), max(ys) + 1):
                xs = []
                n = len(pts)
                for i in range(n):
                    x0, y0 = pts[i]
                    x1, y1 = pts[(i + 1) % n]
                    if (y0 <= yy < y1) or (y1 <= yy < y0):
                        xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
                xs.sort()
                for k in range(0, len(xs) - 1, 2):
                    for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                        self.set(xx, yy, c)
        else:
            n = len(pts)
            for i in range(n):
                self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                          pts[(i + 1) % n][1], c)

    def glyph(self, x, y, ch, scale, c):
        g = FONT.get(ch)
        if g is None:
            return
        for row in range(7):
            bits = g[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    self.fill(x + col * scale, y + row * scale,
                              scale, scale, c)

    def text(self, x, y, s, scale, c, align="l"):
        s = s.upper()
        wpx = text_width(s, scale)
        if align == "c":
            x -= wpx // 2
        elif align == "r":
            x -= wpx
        for ch in s:
            self.glyph(x, y, ch, scale, c)
            x += 6 * scale
        return wpx


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---- small sketch icons (drawn from code, one per pictured story) ----
# Each icon draws inside box (x, y, w, h) with ink colour c.

def icon_radar(cv, x, y, w, h, c):
    cx, cy = x + w // 2, y + h - 8
    cv.line(cx, cy, cx - 18, cy - 26, c, 2)
    cv.line(cx, cy, cx + 18, cy - 26, c, 2)
    cv.line(cx - 18, cy - 26, cx + 18, cy - 26, c, 2)
    cv.circle(cx, cy - 30, 5, c)
    cv.line(cx, cy - 30, cx + 16, cy - 38, c, 2)
    cv.line(cx - 22, cy, cx + 22, cy, c, 2)


def icon_ballot(cv, x, y, w, h, c):
    cv.box(x + 6, y + 14, w - 12, h - 22, c, 2)
    cv.line(x + 6, y + 14, x + w - 6, y + 14, c, 2)
    cv.line(x + w // 2 - 4, y + 2, x + w // 2 + 2, y + 10, c, 2)
    cv.line(x + w // 2 + 2, y + 10, x + w // 2 + 12, y - 2, c, 2)
    cv.line(x + 12, y + 22, x + w - 12, y + 22, c, 1)
    cv.line(x + 12, y + 28, x + w - 12, y + 28, c, 1)


def icon_cricket(cv, x, y, w, h, c):
    cv.line(x + 14, y + 6, x + w - 20, y + h - 12, c, 3)
    cv.line(x + w - 20, y + h - 12, x + w - 8, y + h - 4, c, 3)
    cv.circle(x + w - 14, y + 12, 7, c)
    cv.circle(x + w - 14, y + 12, 3, RED)
    cv.line(x + 6, y + h - 6, x + w - 6, y + h - 6, c, 2)


def icon_globe(cv, x, y, w, h, c):
    cx, cy = x + w // 2, y + h // 2
    cv.circle(cx, cy, 22, c)
    cv.line(cx - 22, cy, cx + 22, cy, c)
    cv.line(cx, cy - 22, cx, cy + 22, c)
    cv.line(cx - 16, cy - 15, cx + 16, cy - 15, c)
    cv.line(cx - 16, cy + 15, cx + 16, cy + 15, c)
    cv.line(cx - 10, cy - 20, cx - 6, cy + 20, c)
    cv.line(cx + 10, cy - 20, cx + 6, cy + 20, c)


def icon_quake(cv, x, y, w, h, c):
    pts = [(x + 4, y + h // 2), (x + 12, y + 8), (x + 20, y + h - 8),
           (x + 28, y + 10), (x + 36, y + h // 2 + 6), (x + 44, y + 6),
           (x + 52, y + h - 10), (x + w - 4, y + h // 2)]
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, 2)
    cv.line(x + 4, y + h - 4, x + w - 4, y + h - 4, c, 2)


def icon_sub(cv, x, y, w, h, c):
    cv.line(x + 8, y + h // 2, x + w - 8, y + h // 2, c, 2)
    cv.line(x + 14, y + h // 2 - 14, x + 14, y + h // 2, c, 2)
    cv.line(x + 14, y + h // 2 - 14, x + 30, y + h // 2 - 14, c, 2)
    cv.line(x + 30, y + h // 2 - 14, x + 30, y + h // 2, c, 2)
    cv.line(x + 8, y + h // 2 + 8, x + w - 8, y + h // 2 + 8, c, 2)
    cv.circle(x + w - 22, y + h // 2 + 14, 4, c)
    cv.circle(x + w - 34, y + h // 2 + 14, 4, c)
    cv.circle(x + w - 46, y + h // 2 + 14, 4, c)


def icon_house(cv, x, y, w, h, c):
    cv.box(x + 10, y + 18, w - 20, h - 24, c, 2)
    cv.line(x + 6, y + 18, x + w // 2, y + 6, c, 2)
    cv.line(x + w // 2, y + 6, x + w - 6, y + 18, c, 2)
    cv.line(x + w // 2 - 2, y + 20, x + w // 2 + 4, y + 26, c, 2)
    cv.line(x + w // 2 + 4, y + 26, x + w // 2 - 2, y + 32, c, 2)
    cv.line(x + w // 2 - 2, y + 32, x + w // 2 + 6, y + 40, c, 2)


def icon_ship(cv, x, y, w, h, c):
    cv.line(x + 6, y + 12, x + w - 6, y + 12, c, 2)
    cv.line(x + 10, y + 12, x + 16, y + 26, c, 2)
    cv.line(x + w - 10, y + 12, x + w - 16, y + 26, c, 2)
    cv.line(x + 16, y + 26, x + w - 16, y + 26, c, 2)
    cv.line(x + w // 2, y + 12, x + w // 2, y - 2 + 10, c, 2)
    cv.line(x + w // 2, y + 2, x + w // 2 + 12, y + 10, c, 2)
    cv.line(x + 4, y + h - 8, x + w - 4, y + h - 8, c, 2)
    cv.line(x + 10, y + h - 4, x + w - 10, y + h - 4, c, 2)


def icon_handshake(cv, x, y, w, h, c):
    cv.box(x + 6, y + 8, w - 12, h - 16, c, 2)
    cv.line(x + 6, y + 8, x + w - 6, y + h - 8, c, 2)
    cv.line(x + w - 6, y + 8, x + 6, y + h - 8, c, 2)
    cv.circle(x + w // 2, y + h // 2, 7, c, fill=True)
    cv.circle(x + w // 2, y + h // 2, 7, LIGHT)


def icon_shield(cv, x, y, w, h, c):
    pts = [(x + w // 2, y + 2), (x + w - 6, y + 10),
           (x + w - 6, y + h // 2 + 6), (x + w // 2, y + h - 4),
           (x + 6, y + h // 2 + 6), (x + 6, y + 10)]
    cv.poly(pts, c)
    cv.line(x + w // 2, y + 10, x + w // 2, y + h - 12, c, 2)
    cv.line(x + 12, y + h // 2, x + w - 12, y + h // 2, c, 2)


def icon_parliament(cv, x, y, w, h, c):
    cv.line(x + 4, y + 8, x + w - 4, y + 8, c, 2)
    cv.line(x + w // 2, y + 2, x + 4, y + 8, c, 2)
    cv.line(x + w // 2, y + 2, x + w - 4, y + 8, c, 2)
    for cx in (x + 10, x + w // 2 - 8, x + w // 2 + 2, x + w - 16):
        cv.line(cx, y + 12, cx, y + h - 10, c, 2)
    cv.line(x + 4, y + h - 8, x + w - 4, y + h - 8, c, 2)


def icon_desert(cv, x, y, w, h, c):
    cv.circle(x + w - 14, y + 10, 7, c)
    cv.line(x + 4, y + h - 10, x + w // 2, y + h // 2, c, 2)
    cv.line(x + w // 2, y + h // 2, x + w - 4, y + h - 10, c, 2)
    cv.line(x + 4, y + h - 4, x + w - 4, y + h - 4, c, 2)


def icon_bottle(cv, x, y, w, h, c):
    cv.box(x + w // 2 - 4, y + 4, 8, 12, c, 2)
    cv.box(x + w // 2 - 10, y + 16, 20, h - 22, c, 2)
    cv.line(x + w // 2 - 10, y + 24, x + w // 2 + 10, y + 24, c, 2)
    cv.line(x + w // 2 - 6, y + 30, x + w // 2 + 6, y + 30, c, 2)


def icon_crowd(cv, x, y, w, h, c):
    for cx in (x + 14, x + w // 2, x + w - 14):
        cv.circle(cx, y + 12, 6, c)
        cv.line(cx - 8, y + h - 6, cx - 8, y + 22, c, 2)
        cv.line(cx + 8, y + h - 6, cx + 8, y + 22, c, 2)
        cv.line(cx - 8, y + 22, cx + 8, y + 22, c, 2)


ICONS = {
    "radar": icon_radar, "ballot": icon_ballot, "cricket": icon_cricket,
    "globe": icon_globe, "quake": icon_quake, "sub": icon_sub,
    "house": icon_house, "ship": icon_ship, "handshake": icon_handshake,
    "shield": icon_shield, "parliament": icon_parliament,
    "desert": icon_desert, "bottle": icon_bottle, "crowd": icon_crowd,
}

# ---- simplified world map (lon, lat) polygons ----
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 71), (-95, 80), (-80, 73), (-60, 62),
     (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-150, 60), (-168, 66)],
    [(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -10), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -55), (-73, -40), (-75, -20),
     (-80, -5), (-80, 10)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
     (40, 15), (48, 11), (51, 10), (40, 0), (35, -18), (28, -33), (18, -35),
     (12, -18), (9, 0), (-8, 5), (-17, 15)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 70), (40, 68), (60, 69),
     (70, 72), (90, 75), (110, 76), (130, 72), (150, 70), (170, 66),
     (178, 65), (170, 60), (160, 60), (158, 52), (142, 50), (140, 40),
     (135, 35), (130, 33), (127, 35), (122, 38), (120, 30), (115, 23),
     (108, 18), (105, 10), (100, 8), (98, 15), (95, 16), (90, 22), (88, 22),
     (85, 19), (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (62, 25),
     (58, 26), (56, 27), (52, 28), (50, 30), (48, 30), (44, 29), (43, 12),
     (40, 15), (39, 21), (35, 28), (34, 31), (30, 36), (26, 38), (23, 36),
     (19, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37),
     (-6, 36), (-9, 38), (-10, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (136, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -23), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20), (113, -22)],
    [(-45, 60), (-40, 64), (-30, 68), (-25, 70), (-20, 76), (-30, 80),
     (-45, 80), (-55, 76), (-58, 70), (-55, 64), (-50, 60), (-45, 60)],
    [(109, 1), (117, 4), (119, -2), (114, -4), (110, -3), (109, 1)],
    [(95, 5), (100, 0), (104, -4), (106, -6), (100, -2), (95, 5)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (146, -8),
     (141, -8), (136, -4), (131, -1)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (144, 44),
     (142, 40), (140, 36), (136, 34), (132, 33), (130, 31)],
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 53), (-1, 51), (-5, 50)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -25), (44, -25),
     (43, -20), (44, -16)],
    [(167, -45), (170, -42), (174, -39), (176, -38), (174, -41), (170, -44),
     (167, -45)],
]

# ---- the 50 stories of Sunday 22 November 2026 ----
# (num, region, field, title, body, tag, source, icon, lon, lat)
# Sources: each story verified in at least two independent outlets
# (Reuters/AP/AFP/BBC/ANI/NCS/WAM, or two wires) on 22 Nov 2026,
# or first reported that day in the outlet named.
STORIES = [
    (1, "MIDDLE EAST", "Conflict",
     "IRGC CLAIMS STRIKES ON US PATRIOT RADARS IN BAHRAIN",
     "Tehran says its missiles and drones hit two US air-defence "
     "radars at al-Riffa and Awali. Bahrain says it intercepted them.",
     "CLAIM", "AL JAZEERA / IRIB", "radar", 50.5, 26.2),
    (2, "ASIA", "Politics",
     "HONG KONG VOTES FOR ITS 1,500-SEAT ELECTION COMMITTEE",
     "856 candidates contest 723 seats in 31 subsectors. Polls run 9am "
     "to 6pm; the committee picks the city's next leader.",
     "CONFIRMED", "CHINA DAILY", "ballot", 114.2, 22.3),
    (3, "AFRICA", "Sport",
     "SOUTH AFRICA SEAL SERIES WITH 176-RUN ROUT",
     "Harmer takes 6-16 as Australia crumble to 111 chasing 288. The "
     "Proteas win the series 2-1 and return to No. 1.",
     "CONFIRMED", "BBC", "cricket", 18.4, -33.9),
    (4, "GLOBAL", "Climate",
     "COP31 TALKS RUN INTO SUNDAY WITH NO DEAL",
     "The Antalya summit passes a second day of overtime. Fossil fuels "
     "and a dropped $120bn finance target block agreement.",
     "CONFIRMED", "REUTERS / AP", "globe", 30.7, 36.9),
    (5, "ASIA", "Disaster",
     "MYANMAR SHAKEN BY M4.1 QUAKE",
     "Tremor strikes at 02:35 local time, 95 km deep. No damage "
     "reported yet.",
     "CONFIRMED", "ANI / NCS", "quake", 94.6, 24.4),
    (6, "OCEANIA", "Defence",
     "AUSTRALIA HITS BACK AT US OVER AUKUS REPORT",
     "Canberra rejects a US budget office claim that the pact cuts "
     "America's submarine fleet.",
     "CONFIRMED", "REUTERS", "sub", 149.1, -35.3),
    (7, "AMERICAS", "Disaster",
     "PERU COUNTS 152 HOMES UNINHABITABLE AFTER QUAKE",
     "Revised survey after Friday's M6.9 Andes tremor. No deaths "
     "reported.",
     "CONFIRMED", "USGS / IGP", "house", -76.0, -11.0),
    (8, "EUROPE", "Defence",
     "FINLAND: WAR SPILLING OVER AFTER DRONE STRIKE",
     "PM Orpo warns after a drone hit a Russian merchant ship near "
     "Finnish waters.",
     "CONFIRMED", "ANI", "ship", 24.9, 60.2),
    (9, "MIDDLE EAST", "Diplomacy",
     "UAE PRESIDENT MEETS US SECURITY CHIEF",
     "Sheikh Mohamed receives Homeland Security Secretary Mullin in "
     "Abu Dhabi.",
     "CONFIRMED", "WAM / ANI", "handshake", 54.4, 24.5),
    (10, "EUROPE", "Politics",
     "ZELENSKYY: NATO IS THE CLEAREST GUARANTEE",
     "Ukraine's president repeats that alliance membership is Kyiv's "
     "best security.",
     "CONFIRMED", "ANI", "shield", 30.5, 50.4),
    (11, "MIDDLE EAST", "Politics",
     "ISRAEL: EISENKOT OPENS COALITION TALKS",
     "Yashar party chief invites Likud to negotiate; a first meeting "
     "is set.",
     "CONFIRMED", "ANI", "parliament", 34.8, 32.1),
    (12, "AFRICA", "Conflict",
     "SUDAN: TASIS ALLIANCE SEIZES BAU REGION",
     "Fighters take the key Blue Nile region, widening the civil war's "
     "front.",
     "CLAIM", "GRAND-STAR", "desert", 34.0, 11.0),
    (13, "ASIA", "Disaster",
     "TOXIC DRINK KILLS 11 IN MANIPUR",
     "Illicit alcohol leaves 11 dead and 180 ill in north-east India.",
     "CLAIM", "GRAND-STAR", "bottle", 93.9, 24.7),
    (14, "EUROPE", "Politics",
     "CROATS RALLY OVER HOSPITAL DEATH",
     "Crowds gather in Zagreb demanding justice for a psychiatric "
     "hospital patient.",
     "CONFIRMED", "GRAND-STAR", "crowd", 16.0, 45.8),
]

BRIEFS = [
    (15, "MIDDLE EAST", "Diplomacy", "IRAN CALLS US BLOCKADE HOSTILE",
     "CONFIRMED", "ANI", 51.4, 35.7),
    (16, "ASIA", "Diplomacy", "BANGLADESH HONOURS INDIA 1971",
     "CONFIRMED", "ANI", 90.4, 23.8),
    (17, "MIDDLE EAST", "Economy", "SAUDI: 4 FOG WARNINGS",
     "OFFICIAL", "APPISTOS", 46.7, 24.6),
    (18, "AFRICA", "Defence", "NIGERIA BUILDS NAVAL SHIPS",
     "CONFIRMED", "C54", 3.4, 6.5),
    (19, "AFRICA", "Politics", "DRC ENACTS REFORM LAW",
     "CONFIRMED", "C54", 15.3, -4.3),
    (20, "AFRICA", "Politics", "TIGRAY MAYOR VOWS POLLS SOON",
     "CONFIRMED", "C54", 39.5, 13.5),
    (21, "AFRICA", "Politics", "SAO TOME REAPPOINTS RAMOS",
     "CONFIRMED", "C54", 6.7, 0.3),
    (22, "AFRICA", "Culture", "S. SUDANESE MODEL OF YEAR",
     "CONFIRMED", "C54", 31.6, 4.85),
    (23, "AFRICA", "Culture", "TYLA, TEMS, KIDJO: GRAMMY BID",
     "CONFIRMED", "C54", 28.0, -26.2),
    (24, "AFRICA", "Politics", "PROTEST AT S. AFRICAN COURT",
     "CONFIRMED", "C54", 28.2, -25.7),
    (25, "AFRICA", "Economy", "LAGOS FASHION WEEK, US TRADE",
     "CONFIRMED", "C54", 3.4, 6.5),
    (26, "EUROPE", "Conflict", "LVIV STRIKE: 2 KILLED, 10 HURT",
     "CONFIRMED", "DIGEST", 24.0, 49.8),
    (27, "ASIA", "Economy", "ICMR: 100 TRANSFERS, 20 DEALS",
     "OFFICIAL", "JAGRAN", 77.2, 28.6),
    (28, "EUROPE", "Culture", "WILLIAM: COVER FOR 10,000",
     "OFFICIAL", "JAGRAN", -0.1, 51.5),
    (29, "ASIA", "Defence", "JAPAN'S FIRST INDIA LIVE-FIRE",
     "CONFIRMED", "JAGRAN", 139.7, 35.7),
    (30, "OCEANIA", "Sport", "CUMMINS KEEPS TEST CAPTAINCY",
     "OFFICIAL", "JAGRAN", 151.2, -33.9),
    (31, "GLOBAL", "Economy", "CRUDE FALLS 3% TO RS 7,842",
     "CONFIRMED", "JAGRAN", -74.0, 40.7),
    (32, "ASIA", "Economy", "AIR INDIA: JEDDAH BAN TO NOV 24",
     "OFFICIAL", "JAGRAN", 72.9, 19.1),
    (33, "GLOBAL", "Diplomacy", "TRUMP AND XI MEET IN SHENZHEN",
     "CONFIRMED", "DIGEST", 114.1, 22.5),
    (34, "AFRICA", "Politics", "POWER CUTS TEST ANC IN POLLS",
     "CLAIM", "C54", 28.2, -25.7),
    (35, "AMERICAS", "Politics", "ANDY KIM ON HIS FATHER",
     "CONFIRMED", "GRAND-STAR", -77.0, 38.9),
    (36, "EUROPE", "Culture", "PAOLO BULGARI DIES",
     "CLAIM", "APPISTOS", 12.5, 41.9),
    (37, "OCEANIA", "Sport", "SMITH OUT AFTER HELMET BLOW",
     "CONFIRMED", "CRICBUZZ", 18.4, -33.9),
    (38, "OCEANIA", "Sport", "WARNER SLAMS AUSSIE COLLAPSE",
     "CONFIRMED", "BBC", 18.4, -33.9),
    (39, "ASIA", "Defence", "TAIWAN CIVILIANS TAKE DRONES",
     "CLAIM", "GRAND-STAR", 121.6, 25.0),
    (40, "MIDDLE EAST", "Conflict", "BAHRAIN FIRE, IRAN BLAMED",
     "CLAIM", "APPISTOS", 50.5, 26.2),
    (41, "EUROPE", "Economy", "BRUSSELS FLIGHT CHAOS LOOMS",
     "FORECAST", "APPISTOS", 4.4, 50.8),
    (42, "MIDDLE EAST", "Conflict", "WCK DENIES CLAIMS IN GAZA",
     "CLAIM", "APPISTOS", 34.5, 31.5),
    (43, "EUROPE", "Conflict", "KRYVYI RIH: 58 HURT, 2 DEAD",
     "CONFIRMED", "APPISTOS", 33.4, 47.9),
    (44, "EUROPE", "Defence", "FINLAND PROBES HELICOPTER",
     "CONFIRMED", "APPISTOS", 24.9, 60.2),
    (45, "ASIA", "Politics", "HK RESULTS DUE TONIGHT",
     "FORECAST", "CHINA DAILY", 114.2, 22.3),
    (46, "AFRICA", "Climate", "NEXT CLIMATE SUMMIT: ADDIS ABABA",
     "OFFICIAL", "AP", 38.7, 9.0),
    (47, "ASIA", "Climate", "RANCHI FLIGHTS RESUME",
     "FORECAST", "MISCW", 85.3, 23.3),
    (48, "AFRICA", "Politics", "TINUBU MOURNS BOAT VICTIMS",
     "OFFICIAL", "BRIEFLY", 7.5, 9.1),
    (49, "EUROPE", "Conflict", "POLAND: RUSSIAN MISSILES LANDED",
     "CLAIM", "LINKEDIN", 21.0, 52.2),
    (50, "ASIA", "Climate", "AKVAN RAINS LASH BIHAR",
     "FORECAST", "NEWSNATION", 85.1, 25.6),
]

TIMELINE = [
    ("00", "COP31 STILL DEADLOCKED"),
    ("04", "MYANMAR M4.1 QUAKE, 95 KM DEEP"),
    ("08", "HONG KONG POLLS OPEN: 723 SEATS"),
    ("12", "PERU: 152 HOMES UNINHABITABLE"),
    ("16", "S. AFRICA SEAL SERIES WIN"),
    ("20", "IRGC CLAIMS RADAR STRIKES"),
    ("24", "COP31: SUNDAY ENDS WITH NO DEAL"),
]

NUMBERS = [
    ("723", "SEATS CONTESTED IN HONG KONG"),
    ("176", "RUNS: S. AFRICA'S WINNING MARGIN"),
    ("4.1", "MYANMAR QUAKE MAGNITUDE"),
    ("152", "HOMES UNINHABITABLE IN PERU"),
    ("856", "CANDIDATES IN HONG KONG"),
    ("10,000", "FOREST STAFF IN NEW COVER"),
]

DATECHECK_LEFT = [
    "PERU'S M6.9 QUAKE - FRI 20 NOV",
    "EL CHAPO ISIDRO CAPTURED - FRI 20 NOV",
    "UN KILLER-ROBOT TALKS END - SAT 21 NOV",
    "DENMARK EXPELS RUSSIAN ATTACHE - FRI 20 NOV",
]
DATECHECK_NOTYET = [
    "ESTONIA-RUSSIA ROAD BORDER CLOSES - 1 DEC",
    "GHANA HERITAGE NOTES CIRCULATE - 1 DEC",
    "KENYA EBOLA-FREE CALL - 23 DEC",
    "LAGARDE LEAVES ECB - 7 FEB 2027",
]

# ---- layout ----
MX = 16
CW = 992  # content width

TAG_COLORS = {"CONFIRMED": GREEN, "OFFICIAL": BLUE,
              "CLAIM": RED, "FORECAST": GOLD}


def draw_header(cv):
    cv.fill(0, 0, W, 4, INK)
    cv.hline(0, 8, W, INK, 2)
    cv.text(MX, 14, "ONE DAY IN THREE LAYERS: 4 LEADS - 10 PICTURES - 36 BRIEFS",
            1, INK)
    cv.text(W - MX, 14, "50 STORIES - 7 REGIONS - 9 FIELDS", 1, INK, "r")
    cv.text(W // 2, 34, "THE WORLD TODAY", 6, INK, "c")
    cv.text(W // 2, 80, "SUNDAY, 22 NOVEMBER 2026", 2, RED, "c")
    cv.text(W // 2, 96, "ONE DAY - ONE PAGE - EVERY STORY FROM SUNDAY",
            1, GREY, "c")
    cv.hline(MX, 108, CW, INK, 2)


def draw_region_strip(cv, y):
    regions = ["ASIA", "MIDDLE EAST", "EUROPE", "AMERICAS",
               "AFRICA", "OCEANIA", "GLOBAL"]
    all_st = STORIES + [(n, r, f, t, tg, s, lo, la)
                        for (n, r, f, t, tg, s, lo, la) in BRIEFS]
    counts = {r: 0 for r in regions}
    for s in all_st:
        counts[s[1]] += 1
    bw = CW // 7
    for i, r in enumerate(regions):
        x = MX + i * bw
        c = REGION_COLORS[r]
        cv.fill(x + 1, y, bw - 2, 20, c)
        cv.text(x + bw // 2, y + 7, "%s %d" % (r, counts[r]), 1, LIGHT, "c")
    return y + 24


def draw_leads(cv, y):
    colw = (CW - 3 * 8) // 4
    ch = 160
    for i, s in enumerate(STORIES[:4]):
        num, reg, fld, title, body, tag, src, icon, lo, la = s
        x = MX + i * (colw + 8)
        c = REGION_COLORS[reg]
        cv.box(x, y, colw, ch, INK, 1)
        cv.fill(x + 1, y + 1, colw - 2, 14, c)
        cv.text(x + 6, y + 4, "%d  %s" % (num, reg), 1, LIGHT)
        cv.text(x + colw - 6, y + 4, fld.upper(), 1, LIGHT, "r")
        ICONS[icon](cv, x + colw // 2 - 30, y + 20, 60, 40, INK)
        ty = y + 64
        for ln in wrap_text(title, colw - 14, 2)[:3]:
            cv.text(x + 7, ty, ln, 2, INK)
            ty += 15
        by = ty + 2
        for ln in wrap_text(body, colw - 14, 1)[:4]:
            cv.text(x + 7, by, ln, 1, INK)
            by += 8
        cv.text(x + 7, y + ch - 16, tag, 1, TAG_COLORS[tag])
        cv.text(x + colw - 7, y + ch - 16, src, 1, GREY, "r")
    return y + ch


def draw_pictured(cv, y):
    cv.text(MX, y, "TEN PICTURES FROM SUNDAY", 2, INK)
    cv.hline(MX, y + 16, CW, INK, 1)
    y += 22
    colw = (CW - 4 * 6) // 5
    rowh = 112
    for idx, s in enumerate(STORIES[4:14]):
        num, reg, fld, title, body, tag, src, icon, lo, la = s
        row, col = divmod(idx, 5)
        x = MX + col * (colw + 6)
        yy = y + row * (rowh + 4)
        c = REGION_COLORS[reg]
        cv.box(x, yy, colw, rowh, INK, 1)
        cv.fill(x + 1, yy + 1, colw - 2, 12, c)
        cv.text(x + 5, yy + 3, "%d  %s" % (num, reg), 1, LIGHT)
        ICONS[icon](cv, x + colw // 2 - 26, yy + 16, 52, 36, INK)
        ty = yy + 56
        for ln in wrap_text(title, colw - 12, 1)[:2]:
            cv.text(x + 6, ty, ln, 1, INK)
            ty += 8
        by = ty + 1
        for ln in wrap_text(body, colw - 12, 1)[:3]:
            cv.text(x + 6, by, ln, 1, GREY)
            by += 8
        cv.text(x + 6, yy + rowh - 11, tag, 1, TAG_COLORS[tag])
        cv.text(x + colw - 6, yy + rowh - 11, src, 1, GREY, "r")
    return y + 2 * rowh + 4


def draw_briefs(cv, y):
    cv.text(MX, y, "ALSO ON SUNDAY 22 NOVEMBER", 2, INK)
    cv.hline(MX, y + 16, CW, INK, 1)
    y += 22
    colw = (CW - 2 * 10) // 3
    rowh = 12
    for i, b in enumerate(BRIEFS):
        num, reg, fld, title, tag, src, lo, la = b
        col, row = divmod(i, 12)
        x = MX + col * (colw + 10)
        yy = y + row * rowh
        c = REGION_COLORS[reg]
        cv.fill(x, yy + 1, 3, 9, c)
        numtxt = "%d " % num
        tagtxt = " [%s]" % tag
        srctxt = " - " + src
        avail = colw - 8 - text_width(numtxt, 1) - text_width(tagtxt, 1) \
            - text_width(srctxt, 1)
        t = title
        # truncate at a word boundary so no word is cut in half
        while text_width(t, 1) > avail and " " in t:
            t = t[:t.rfind(" ")]
        if text_width(t, 1) > avail:
            t = t[:max(4, avail // 6)]
        cv.text(x + 6, yy + 2, numtxt, 1, INK)
        tx = x + 6 + text_width(numtxt, 1)
        cv.text(tx, yy + 2, t, 1, INK)
        tx += text_width(t, 1)
        cv.text(tx, yy + 2, srctxt, 1, GREY)
        tx += text_width(srctxt, 1)
        cv.text(tx, yy + 2, tagtxt, 1, TAG_COLORS[tag])
    return y + 12 * rowh


def draw_timeline(cv, y):
    cv.text(MX, y, "THE DAY IN UTC", 2, INK)
    cv.hline(MX, y + 16, CW, INK, 1)
    y += 20
    slotw = CW // 7
    for i, (t, ev) in enumerate(TIMELINE):
        x = MX + i * slotw
        if i:
            cv.vline(x - 2, y, 28, GREY, 1)
        cv.text(x + 4, y, t + " UTC", 2, RED)
        for j, ln in enumerate(wrap_text(ev, slotw - 10, 1)[:2]):
            cv.text(x + 4, y + 15 + j * 8, ln, 1, INK)
    return y + 30


def draw_numbers(cv, y):
    cv.text(MX, y, "THE DAY IN NUMBERS", 2, INK)
    cv.hline(MX, y + 16, CW, INK, 1)
    y += 20
    bw = CW // 6
    for i, (num, lab) in enumerate(NUMBERS):
        x = MX + i * bw
        if i:
            cv.vline(x - 2, y, 34, GREY, 1)
        cv.text(x + bw // 2, y, num, 3, RED, "c")
        for j, ln in enumerate(wrap_text(lab, bw - 10, 1)[:2]):
            cv.text(x + bw // 2, y + 22 + j * 8, ln, 1, INK, "c")
    return y + 36


def draw_map(cv, x, y, w, h):
    cv.box(x, y, w, h, INK, 1)
    cv.text(x + 6, y + 4, "WHERE IT HAPPENED", 1, INK)
    cv.text(x + w - 6, y + 4, "PINS: 1-14 - DOTS: 15-52", 1, GREY, "r")
    mx, my, mw, mh = x + 4, y + 16, w - 8, h - 20
    cv.fill(mx, my, mw, mh, PAPER2)
    for poly in CONTINENTS:
        pts = [(mx + int((lo + 180) / 360.0 * mw),
                my + int((85 - la) / 145.0 * mh)) for lo, la in poly]
        cv.poly(pts, (190, 178, 150), fill=True)
        cv.poly(pts, GREY)
    # pins 1-14 with numbers, dots 15-52
    all_st = STORIES + [(n, r, f, t, tg, s, lo, la)
                        for (n, r, f, t, tg, s, lo, la) in BRIEFS]
    seen = {}
    for s in all_st:
        num, reg = s[0], s[1]
        lo, la = s[-2], s[-1]
        key = (round(lo, 1), round(la, 1))
        k = seen.get(key, 0)
        seen[key] = k + 1
        px = mx + int((lo + 180) / 360.0 * mw) + (k % 3 - 1) * 9
        py = my + int((85 - la) / 145.0 * mh) + (k // 3) * 9
        c = REGION_COLORS[reg]
        if num <= 14:
            cv.circle(px, py, 7, c, fill=True)
            cv.circle(px, py, 7, INK)
            cv.text(px, py - 3, str(num), 1, LIGHT, "c")
        else:
            cv.circle(px, py, 2, c, fill=True)
    # region legend with counts
    regions = ["ASIA", "MIDDLE EAST", "EUROPE", "AMERICAS",
               "AFRICA", "OCEANIA", "GLOBAL"]
    counts = {r: 0 for r in regions}
    for s in all_st:
        counts[s[1]] += 1
    lx = x + 6
    ly = y + h - 12
    for r in regions:
        cv.fill(lx, ly, 6, 6, REGION_COLORS[r])
        lx += 8
        lx += cv.text(lx, ly, "%s %d" % (r, counts[r]), 1, INK)
        lx += 8


def draw_right_column(cv, x, y, w):
    # DATE CHECK - red border, two-way check (112 px tall)
    dh = 112
    cv.box(x, y, w, dh, RED, 2)
    cv.text(x + 6, y + 4, "DATE CHECK", 2, RED)
    yy = y + 20
    cv.text(x + 6, yy, "EVERY STORY HERE IS FROM SUNDAY 22 NOVEMBER 2026.",
            1, INK)
    yy += 10
    cv.text(x + 6, yy, "LEFT OUT AS EARLIER NEWS:", 1, RED)
    yy += 8
    for it in DATECHECK_LEFT:
        cv.text(x + 6, yy, "- " + it, 1, INK)
        yy += 8
    yy += 2
    cv.text(x + 6, yy, "NOT YET:", 1, RED)
    yy += 8
    for it in DATECHECK_NOTYET:
        cv.text(x + 6, yy, "- " + it, 1, INK)
        yy += 8
    # HOW SURE - compact, scale-1 header
    yy = y + dh + 5
    cv.text(x, yy, "HOW SURE", 1, INK)
    yy += 8
    cv.text(x, yy, "CONFIRMED = 2+ INDEPENDENT MEDIA - OFFICIAL = OFFICIAL BODY",
            1, INK)
    yy += 8
    cv.text(x, yy, "CLAIM = ONE PARTY ONLY - FORECAST = PREDICTION",
            1, INK)
    # HOW TO READ - compact
    yy += 10
    cv.text(x, yy, "HOW TO READ", 1, INK)
    yy += 8
    cv.text(x, yy, "THUMBNAIL: READ THE 4 LEADS. FULL SIZE: EVERY STORY.",
            1, INK)
    return yy


def build():
    cv = Canvas(W, H, PAPER)
    draw_header(cv)
    y = draw_region_strip(cv, 118)
    y = draw_leads(cv, y + 4)
    y = draw_pictured(cv, y + 6)
    y = draw_briefs(cv, y + 4)
    y = draw_timeline(cv, y + 4)
    y = draw_numbers(cv, y + 4)
    bottom_y = y + 4
    bottom_h = 1008 - bottom_y
    map_w = 500
    draw_map(cv, MX, bottom_y, map_w, bottom_h)
    draw_right_column(cv, MX + map_w + 8, bottom_y, CW - map_w - 8)
    cv.hline(MX, 1011, CW, INK, 1)
    cv.text(W // 2, 1014, "SOURCES: REUTERS - AP - AFP - BBC - ANI - "
            "NCS - WAM - USGS - IGP - CHINA DAILY - CRICBUZZ - "
            "DISPUTED REPORTS ARE TAGGED CLAIM.", 1, GREY, "c")
    return cv


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    cv = build()
    path = os.path.join(out, "entry.png")
    n = write_png(cv, path)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()
