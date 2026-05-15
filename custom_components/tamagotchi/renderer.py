"""Pure-stdlib PNG renderer for the 16×16 Tamagotchi display.

No external dependencies — uses only struct and zlib from the standard library.
The 16×16 logical grid is upscaled to a 144×144 image (8 px per cell + 8 px border)
to give a readable LCD-screen feel.
"""
from __future__ import annotations

import struct
import zlib

from .core import TamagotchiCore
from .sprites import (
    get_sprite, pixel,
    ZZZ_OVERLAY, SICK_OVERLAY, POOP_OVERLAY, ATTENTION_OVERLAY,
)

# ---------------------------------------------------------------------------
# Palette — classic Game Boy Pocket / Tamagotchi LCD colours
# ---------------------------------------------------------------------------

_LCD_BG      = (155, 188,  15)   # light yellow-green background
_LCD_DARK    = ( 15,  56,  15)   # creature body / dark pixels
_LCD_MID     = ( 48,  98,  48)   # poop overlay colour
_LCD_BORDER  = ( 80, 120,  10)   # outer bezel
_LCD_SCREEN  = (139, 172,  15)   # screen inner fill (slightly lighter than bg)

PALETTE = [_LCD_BG, _LCD_DARK, _LCD_MID, _LCD_SCREEN]

# Rendering constants
GRID_W = 16
GRID_H = 16
CELL_PX = 8          # pixels per grid cell
BORDER_PX = 8        # border around the grid

IMG_W = GRID_W * CELL_PX + 2 * BORDER_PX   # 144
IMG_H = GRID_H * CELL_PX + 2 * BORDER_PX   # 144


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------

def render(tama: TamagotchiCore) -> bytes:
    """Return PNG bytes for the current Tamagotchi state."""
    grid = _build_grid(tama)
    raw = _grid_to_raw(grid)
    return _encode_png(raw, IMG_W, IMG_H)


def _build_grid(tama: TamagotchiCore) -> list[list[int]]:
    """Build a 16×16 colour-index grid."""
    # Start with screen fill
    grid: list[list[int]] = [[0] * GRID_W for _ in range(GRID_H)]

    # Base creature sprite
    sprite = get_sprite(tama.stage, tama.animation_frame)
    for row in range(GRID_H):
        sprite_row = sprite[row] if row < len(sprite) else 0
        for col in range(GRID_W):
            if pixel(sprite_row, col):
                grid[row][col] = 1

    # Overlays
    if tama.is_sleeping:
        _apply_overlay(grid, ZZZ_OVERLAY, color=1)
    elif tama.is_sick:
        _apply_overlay(grid, SICK_OVERLAY, color=1)
    elif tama.needs_attention and not tama.is_sleeping:
        _apply_overlay(grid, ATTENTION_OVERLAY, color=1)

    # Poop icons (bottom-left, stack up for each pile)
    if tama.poop_count > 0:
        for i in range(min(tama.poop_count, 4)):
            _apply_poop(grid, i)

    return grid


def _apply_overlay(grid: list[list[int]], overlay: tuple, color: int = 1) -> None:
    for row_idx, row_val in enumerate(overlay):
        if row_idx >= GRID_H:
            break
        if not row_val:
            continue
        for col in range(GRID_W):
            if pixel(row_val, col):
                grid[row_idx][col] = color


def _apply_poop(grid: list[list[int]], index: int) -> None:
    """Draw a small poop pile; index=0 is leftmost, each shifts 4 px right."""
    x_offset = index * 4
    for row_idx, row_val in enumerate(POOP_OVERLAY):
        if row_idx >= GRID_H:
            break
        if not row_val:
            continue
        for col in range(GRID_W):
            if pixel(row_val, col):
                shifted = col + x_offset
                if shifted < GRID_W:
                    grid[row_idx][shifted] = 2   # poop colour index


# ---------------------------------------------------------------------------
# Raw image data builder
# ---------------------------------------------------------------------------

def _grid_to_raw(grid: list[list[int]]) -> bytes:
    """Convert colour-index grid → raw PNG scan lines (RGB, filter byte 0 per row)."""
    raw = bytearray()
    for py in range(IMG_H):
        raw.append(0)   # PNG filter type: None
        gy = (py - BORDER_PX) // CELL_PX
        for px in range(IMG_W):
            gx = (px - BORDER_PX) // CELL_PX
            if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                r, g, b = PALETTE[grid[gy][gx]]
            else:
                r, g, b = _LCD_BORDER
            raw += bytes([r, g, b])
    return bytes(raw)


# ---------------------------------------------------------------------------
# Minimal PNG encoder (no external dependencies)
# ---------------------------------------------------------------------------

def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + payload + struct.pack(">I", crc)


def _encode_png(raw_data: bytes, width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw_data, level=6)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )
