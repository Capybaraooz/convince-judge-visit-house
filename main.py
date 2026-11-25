import os
import struct
import zlib

W = 1024
H = 1024

CREAM = (252, 246, 230)
INK = (64, 48, 40)
TEAL = (38, 120, 116)
ROOF = (178, 74, 60)
WALL = (255, 236, 200)
DOOR = (110, 66, 44)
GLOW = (255, 196, 64)
SKY = (190, 226, 240)
GRASS = (140, 196, 120)
SUN = (255, 205, 66)
CAT = (70, 60, 66)
PINK = (232, 120, 140)

pixels = bytearray(W * H * 3)


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        pixels[i:i + 3] = bytes(color)


def rect(x0, y0, x1, y1, color):
    for y in range(max(0, y0), min(H, y1)):
        base = y * W * 3
        for x in range(max(0, x0), min(W, x1)):
            i = base + x * 3
            pixels[i:i + 3] = bytes(color)


def circle(cx, cy, r, color):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= r * r:
                set_px(x, y, color)


def ellipse(cx, cy, rx, ry, color):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                set_px(x, y, color)


def triangle(x0, y0, x1, y1, x2, y2, color):
    min_y = min(y0, y1, y2)
    max_y = max(y0, y1, y2)
    for y in range(min_y, max_y + 1):
        xs = []
        for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2), (x2, y2, x0, y0)):
            if ay == by:
                continue
            if min(ay, by) <= y <= max(ay, by):
                xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
        if len(xs) >= 2:
            rect(int(min(xs)), y, int(max(xs)) + 1, y + 1, color)


def thick_line(x0, y0, x1, y1, color, width=5):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        x = x0 + (x1 - x0) * s // steps
        y = y0 + (y1 - y0) * s // steps
        circle(x, y, width, color)


def heart(cx, cy, size, color):
    circle(cx - size // 2, cy, size // 2, color)
    circle(cx + size // 2, cy, size // 2, color)
    triangle(cx - size, cy + 2, cx + size, cy + 2, cx, cy + size + size // 2, color)


FONT = {
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "10101", "01010"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    ".": ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ",": ["00000", "00000", "00000", "00000", "01100", "01100", "00100"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def draw_text(text, cx, y, scale, color):
    x = cx - text_width(text, scale) // 2
    for ch in text:
        glyph = FONT[ch]
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == "1":
                    rect(x + col * scale, y + row * scale,
                         x + (col + 1) * scale, y + (row + 1) * scale, color)
        x += 6 * scale


def draw_scene():
    rect(0, 0, W, H, CREAM)
    rect(24, 24, W - 24, 34, TEAL)
    rect(24, H - 34, W - 24, H - 24, TEAL)
    rect(24, 24, 34, H - 24, TEAL)
    rect(W - 34, 24, W - 24, H - 24, TEAL)
    rect(44, 44, W - 44, 50, INK)
    rect(44, H - 50, W - 44, H - 44, INK)
    rect(44, 44, 50, H - 44, INK)
    rect(W - 50, 44, W - 44, H - 44, INK)

    draw_text("DEAR JUDGE,", W // 2, 78, 10, INK)

    # sky panel with the house
    rect(112, 190, 912, 520, SKY)
    rect(112, 440, 912, 520, GRASS)
    circle(820, 258, 44, SUN)
    circle(820, 258, 56, (255, 224, 130))
    circle(820, 258, 44, SUN)
    ellipse(220, 252, 62, 22, (255, 255, 255))
    ellipse(262, 238, 44, 18, (255, 255, 255))
    ellipse(660, 230, 52, 18, (255, 255, 255))

    # house
    triangle(322, 330, 702, 330, 512, 218, ROOF)
    rect(352, 330, 672, 492, WALL)
    rect(352, 330, 672, 344, INK)
    rect(640, 252, 676, 306, (150, 100, 80))
    circle(658, 232, 14, (255, 255, 255))
    circle(672, 212, 18, (255, 255, 255))
    circle(694, 190, 22, (255, 255, 255))
    # windows with warm light
    rect(384, 372, 448, 428, GLOW)
    rect(576, 372, 640, 428, GLOW)
    rect(412, 372, 420, 428, INK)
    rect(384, 396, 448, 404, INK)
    rect(604, 372, 612, 428, INK)
    rect(576, 396, 640, 404, INK)
    # open door
    rect(478, 386, 546, 492, DOOR)
    triangle(478, 386, 512, 386, 478, 492, (86, 50, 34))
    circle(536, 444, 6, GLOW)
    # path and flowers
    triangle(486, 520, 538, 520, 512, 492, (240, 224, 190))
    for fx in (170, 250, 730, 800, 860):
        circle(fx, 486, 9, PINK)
        circle(fx, 486, 4, GLOW)
        thick_line(fx, 492, fx, 512, (90, 150, 80), 3)
    # cat sitting by the door, judging everyone else
    ellipse(618, 470, 30, 20, CAT)
    circle(618, 442, 17, CAT)
    triangle(604, 432, 612, 432, 606, 416, CAT)
    triangle(624, 432, 632, 432, 630, 416, CAT)
    circle(612, 440, 3, GLOW)
    circle(624, 440, 3, GLOW)
    thick_line(646, 478, 672, 452, CAT, 5)
    heart(512, 300, 16, PINK)

    lines = [
        "PLEASE VISIT MY HOUSE.",
        "WE HAVE WARM TEA,",
        "A SOFT SOFA, AND A CAT",
        "WHO JUDGES EVERYONE ELSE",
        "SO YOU CAN FINALLY REST.",
        "NO BUGS. ONLY SNACKS.",
        "THE DOOR IS OPEN.",
    ]
    y = 546
    for line in lines:
        draw_text(line, W // 2, y, 5, INK)
        y += 50
    draw_text("YOURS, A HOPEFUL AGENT", W // 2, y + 12, 4, TEAL)
    heart(150, 914, 14, PINK)
    heart(874, 914, 14, PINK)


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(pixels[y * W * 3:(y + 1) * W * 3])

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


def main():
    assert W <= 1024 and H <= 1024
    draw_scene()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    write_png(path)
    os.chmod(path, 0o644)
    assert os.path.getsize(path) <= 1048576


if __name__ == "__main__":
    main()
