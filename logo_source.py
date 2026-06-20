"""Generate Transcript logo — minimalist wave in a dark square.
Outputs: logo.bmp, logo.ico (multi-size)

Usage: python logo_source.py
"""

import struct
import math
import os

SIZES = [256, 64, 48, 32, 16]


def _make_bmp(w, h, pixels_4byte):
    """Pack a 4-byte-per-pixel BGRA bytearray into a BMP + optional ICO data."""
    row_size = w * 4
    padding = b"\x00" * 0  # 4-byte aligned already
    raw = bytearray()
    for y in range(h - 1, -1, -1):  # BMP is bottom-up
        start = y * w * 4
        row = pixels_4byte[start : start + w * 4]
        raw.extend(row)
        raw.extend(padding)

    header_size = 40
    file_size = 14 + header_size + len(raw)
    bmp = bytearray()
    # BITMAPFILEHEADER
    bmp.extend(b"BM")
    bmp.extend(struct.pack("<I", file_size))
    bmp.extend(b"\x00\x00")
    bmp.extend(b"\x00\x00")
    bmp.extend(struct.pack("<I", 14 + header_size))
    # BITMAPINFOHEADER
    bmp.extend(struct.pack("<I", header_size))
    bmp.extend(struct.pack("<i", w))
    bmp.extend(struct.pack("<i", h))
    bmp.extend(struct.pack("<H", 1))
    bmp.extend(struct.pack("<H", 32))  # 32-bit RGBA
    bmp.extend(b"\x00\x00\x00\x00")  # no compression
    bmp.extend(struct.pack("<I", len(raw)))
    bmp.extend(b"\x00\x00\x00\x00" * 2)  # resolution
    bmp.extend(b"\x00\x00\x00\x00")  # colors used
    bmp.extend(b"\x00\x00\x00\x00")  # important colors
    bmp.extend(raw)
    return bmp


def _draw_logo(w, h):
    """Return BGRA bytearray of the logo at given size."""
    pixels = bytearray(w * h * 4)

    bg = (10, 10, 10, 255)       # #0a0a0a
    border = (30, 30, 30, 255)    # #1e1e1e
    wave_color = (136, 136, 136, 255)  # #888888
    dot_color = (170, 170, 170, 255)    # #aaaaaa

    margin = max(2, w // 40)
    radius = max(4, w // 20)

    def _set(px, py, color):
        if 0 <= px < w and 0 <= py < h:
            idx = (py * w + px) * 4
            pixels[idx] = color[0]      # B
            pixels[idx + 1] = color[1]  # G
            pixels[idx + 2] = color[2]  # R
            pixels[idx + 3] = color[3]  # A

    def _is_inside_rounded(x, y, rad):
        x -= margin
        y -= margin
        size = w - 2 * margin
        if x < 0 or y < 0 or x >= size or y >= size:
            return False
        if x < rad and y < rad:
            return (x - rad) ** 2 + (y - rad) ** 2 <= rad ** 2
        if x < rad and y >= size - rad:
            return (x - rad) ** 2 + (y - (size - rad)) ** 2 <= rad ** 2
        if x >= size - rad and y < rad:
            return (x - (size - rad)) ** 2 + (y - rad) ** 2 <= rad ** 2
        if x >= size - rad and y >= size - rad:
            return (x - (size - rad)) ** 2 + (y - (size - rad)) ** 2 <= rad ** 2
        return True

    def _is_border(x, y, rad):
        if not _is_inside_rounded(x, y, rad + 1):
            return False
        # Check if it's within 1px of the outer edge
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if not _is_inside_rounded(x + dx, y + dy, rad):
                    return True
        return False

    # Draw background + border
    for y in range(h):
        for x in range(w):
            inside = _is_inside_rounded(x, y, radius)
            on_border = _is_border(x, y, radius)
            if on_border:
                _set(x, y, border)
            elif inside:
                _set(x, y, bg)

    # Draw wave (sine curve)
    cx = w // 2
    cy = h // 2
    wave_amp = h * 0.18
    wave_freq = 2.5 * math.pi / (w - 2 * margin)
    wave_half = max(1, w // 180)
    dot_radius = max(2, w // 50)
    dot_start_x = margin + (w - 2 * margin) * 0.12
    wave_start_x = dot_start_x + dot_radius + 2

    for x in range(int(wave_start_x), w - margin):
        t = (x - margin) / (w - 2 * margin)
        y_offset = int(cy + wave_amp * math.sin(t * wave_freq * (w - 2 * margin)))
        for dy in range(-wave_half, wave_half + 1):
            _set(x, y_offset + dy, wave_color)

    # Draw dot at start
    dot_start_y = cy
    for dy in range(-dot_radius, dot_radius + 1):
        for dx in range(-dot_radius, dot_radius + 1):
            if dx * dx + dy * dy <= dot_radius * dot_radius:
                _set(int(dot_start_x + dx), dot_start_y + dy, dot_color)

    return pixels


def _make_ico(sizes_data):
    """Pack multiple BMPs into a single .ico file."""
    count = len(sizes_data)
    header = struct.pack("<HHH", 0, 1, count)
    dir_entries = bytearray()
    image_data = bytearray()
    offsets = []
    for (w, h), bmp_data in sizes_data:
        # BMP data without file header (starting from BITMAPINFOHEADER)
        # bmp_data includes file header, so we strip first 14 bytes
        raw = bmp_data[14:]
        offsets.append(14 + count * 16 + len(image_data))
        ico_w = 0 if w >= 256 else w
        ico_h = 0 if h >= 256 else h
        dir_entries.extend(struct.pack("<BBBBHHII", ico_w, ico_h, 0, 0, 1, 32, len(raw), 0))
        image_data.extend(raw)

    return bytes(header) + bytes(dir_entries) + bytes(image_data)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    sizes_data = []

    for size in SIZES:
        px = _draw_logo(size, size)
        bmp = _make_bmp(size, size, px)
        sizes_data.append(((size, size), bmp))

        if size == 256:
            bmp_path = os.path.join(out_dir, "logo.bmp")
            with open(bmp_path, "wb") as f:
                f.write(bmp)
            print(f"logo.bmp ({size}x{size})")

    ico_path = os.path.join(out_dir, "logo.ico")
    ico_data = _make_ico(sizes_data)
    with open(ico_path, "wb") as f:
        f.write(ico_data)
    print(f"logo.ico ({len(sizes_data)} sizes)")


if __name__ == "__main__":
    main()
