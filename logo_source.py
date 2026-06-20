import struct
import math
import os

SIZES = [256, 64, 48, 32, 16]


def _make_bmp(w, h, pixels_4byte):
    row_size = w * 4
    padding = b"\x00" * 0
    raw = bytearray()
    for y in range(h - 1, -1, -1):
        start = y * w * 4
        row = pixels_4byte[start : start + w * 4]
        raw.extend(row)
        raw.extend(padding)

    header_size = 40
    file_size = 14 + header_size + len(raw)
    bmp = bytearray()
    bmp.extend(b"BM")
    bmp.extend(struct.pack("<I", file_size))
    bmp.extend(b"\x00\x00")
    bmp.extend(b"\x00\x00")
    bmp.extend(struct.pack("<I", 14 + header_size))
    bmp.extend(struct.pack("<I", header_size))
    bmp.extend(struct.pack("<i", w))
    bmp.extend(struct.pack("<i", h))
    bmp.extend(struct.pack("<H", 1))
    bmp.extend(struct.pack("<H", 32))
    bmp.extend(b"\x00\x00\x00\x00")
    bmp.extend(struct.pack("<I", len(raw)))
    bmp.extend(b"\x00\x00\x00\x00" * 2)
    bmp.extend(b"\x00\x00\x00\x00")
    bmp.extend(b"\x00\x00\x00\x00")
    bmp.extend(raw)
    return bmp


def _draw_logo(w, h):
    pixels = bytearray(w * h * 4)

    bg = (10, 10, 10, 255)
    border = (40, 40, 40, 255)
    bar_color = (140, 140, 140, 255)
    bar_bright = (180, 180, 180, 255)

    margin = max(2, w // 30)
    radius = max(4, w // 16)

    def _set(px, py, color):
        if 0 <= px < w and 0 <= py < h:
            idx = (py * w + px) * 4
            pixels[idx] = color[0]
            pixels[idx + 1] = color[1]
            pixels[idx + 2] = color[2]
            pixels[idx + 3] = color[3]

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
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if not _is_inside_rounded(x + dx, y + dy, rad):
                    return True
        return False

    for y in range(h):
        for x in range(w):
            inside = _is_inside_rounded(x, y, radius)
            on_border = _is_border(x, y, radius)
            if on_border:
                _set(x, y, border)
            elif inside:
                _set(x, y, bg)

    cx = w // 2
    cy = h // 2
    bar_count = 5
    bar_width = max(1, w // 40)
    bar_gap = max(2, w // 30)
    bar_area_width = bar_count * bar_width + (bar_count - 1) * bar_gap
    start_x = cx - bar_area_width // 2
    max_height = h * 0.45
    min_height = h * 0.12

    for i in range(bar_count):
        t = (i + 0.5) / bar_count
        height = int(min_height + max_height * (0.3 + 0.7 * math.sin(t * math.pi)))
        color = bar_bright if i in (0, bar_count - 1) else bar_color
        bar_x = start_x + i * (bar_width + bar_gap)
        for by in range(cy - height // 2, cy + height // 2 + 1):
            for bx in range(bar_x, bar_x + bar_width):
                _set(bx, by, color)

    return pixels


def _make_ico(sizes_data):
    count = len(sizes_data)
    header = struct.pack("<HHH", 0, 1, count)
    dir_entries = bytearray()
    image_data = bytearray()
    for (w, h), bmp_data in sizes_data:
        raw = bmp_data[14:]
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
