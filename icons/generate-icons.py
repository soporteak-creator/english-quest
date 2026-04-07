#!/usr/bin/env python3
"""
Genera todos los íconos PNG para el PWA usando solo la librería estándar.
Crea íconos con fondo degradado morado y el símbolo ⚔️ en blanco.
"""
import struct, zlib, math, os

def write_png(filename, width, height, pixels):
    """pixels: lista de (r,g,b,a) por fila"""
    def chunk(name, data):
        c = zlib.crc32(name + data) & 0xffffffff
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', c)

    raw = b''
    for row in pixels:
        raw += b'\x00'
        for r,g,b,a in row:
            raw += bytes([r,g,b,a])

    compressed = zlib.compress(raw, 9)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    # RGBA = color type 6
    ihdr = struct.pack('>II', width, height) + bytes([8, 6, 0, 0, 0])

    png  = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', compressed)
    png += chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(png)
    print(f'  ✓ {filename} ({width}x{height})')

def make_icon(size):
    pixels = []
    cx = cy = size / 2
    r  = size / 2

    for y in range(size):
        row = []
        for x in range(size):
            # Circular mask
            dx = x - cx
            dy = y - cy
            dist = math.sqrt(dx*dx + dy*dy)

            if dist > r:
                row.append((0, 0, 0, 0))
                continue

            # Gradient background: top-left purple → bottom-right deep purple
            t = (x + y) / (size * 2)
            bg_r = int(108 + (36  - 108) * t)   # 6c → 24
            bg_g = int(99  + (0   - 99)  * t)   # 63 → 00
            bg_b = int(255 + (70  - 255) * t)   # ff → 46

            # Draw a simple sword cross symbol
            # Vertical blade
            vw  = max(2, size // 14)
            vh  = int(size * 0.55)
            vx1 = int(cx - vw/2)
            vx2 = int(cx + vw/2)
            vy1 = int(cy - vh/2)
            vy2 = int(cy + vh/2)

            # Horizontal guard
            gw = int(size * 0.45)
            gh = max(2, size // 14)
            gx1 = int(cx - gw/2)
            gx2 = int(cx + gw/2)
            gy1 = int(cy - gh/2)
            gy2 = int(cy + gh/2)

            # Handle (below center)
            hw  = max(2, size // 18)
            hh  = int(size * 0.22)
            hx1 = int(cx - hw/2)
            hx2 = int(cx + hw/2)
            hy1 = int(cy + gh/2)
            hy2 = int(cy + gh/2 + hh)

            in_blade  = vx1 <= x <= vx2 and vy1 <= y <= vy2
            in_guard  = gx1 <= x <= gx2 and gy1 <= y <= gy2
            in_handle = hx1 <= x <= hx2 and hy1 <= y <= hy2
            in_pommel = (abs(x - cx) < size//16 and abs(y - (hy2 + size//20)) < size//16)

            if in_blade or in_guard or in_handle or in_pommel:
                # White with slight gold tint
                row.append((255, 240, 180, 255))
            else:
                row.append((bg_r, bg_g, bg_b, 255))
        pixels.append(row)
    return pixels

sizes = [72, 96, 128, 144, 152, 192, 384, 512]
os.makedirs('icons', exist_ok=True)

print('Generating icons...')
for s in sizes:
    write_png(f'icons/icon-{s}.png', s, s, make_icon(s))

# Screenshot placeholder (390x844 — iPhone size)
print('Generating screenshot placeholder...')
pix = []
for y in range(844):
    row = []
    for x in range(390):
        t = y / 844
        r = int(13  + (36  - 13)  * t)
        g = int(13  + (0   - 13)  * t)
        b = int(43  + (70  - 43)  * t)
        row.append((r, g, b, 255))
    pix.append(row)
write_png('icons/screenshot.png', 390, 844, pix)

print('Done! All icons generated.')
