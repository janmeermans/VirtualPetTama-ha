"""Pure-stdlib PNG renderer for the 16×16 Tamagotchi display.

No external dependencies — uses only struct and zlib.
Upscales the 16×16 logical grid to 144×144 px (8 px/cell + 8 px border).

Sleep mode: colours are inverted (dark background, light creature) to simulate
the light being switched off, matching the original Tamagotchi behaviour.

Palette support: four named colour themes (classic, amber, blue, sakura).
"""
from __future__ import annotations

import struct
import zlib

from .const import PALETTES, DEFAULT_PALETTE
from .core import TamagotchiCore
from .sprites import (
    get_sprite, pixel,
    ZZZ_OVERLAY, ATTENTION_OVERLAY, POOP_ROWS,
)

CELL_PX  = 8
BORDER   = 8
GRID_W   = 16
GRID_H   = 16
IMG_W    = GRID_W * CELL_PX + 2 * BORDER   # 144
IMG_H    = GRID_H * CELL_PX + 2 * BORDER   # 144


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render(tama: TamagotchiCore, palette_name: str = DEFAULT_PALETTE) -> bytes:
    """Return PNG bytes for the current Tamagotchi state.

    Args:
        tama:         Game state object.
        palette_name: One of the keys in PALETTES (e.g. "classic", "amber").
    """
    pal = PALETTES.get(palette_name, PALETTES[DEFAULT_PALETTE])
    bg     = pal["bg"]
    dark   = pal["dark"]
    mid    = pal["mid"]
    border = pal["border"]

    if tama.is_sleeping:
        # Invert: dark background, light creature
        palette_list  = [dark, bg,   mid]
        border_colour = dark
    else:
        palette_list  = [bg,   dark, mid]
        border_colour = border

    grid = _build_grid(tama)
    raw  = _grid_to_raw(grid, palette_list, border_colour)
    return _encode_png(raw, IMG_W, IMG_H)


# ---------------------------------------------------------------------------
# Grid construction
# ---------------------------------------------------------------------------

def _build_grid(tama: TamagotchiCore) -> list[list[int]]:
    grid: list[list[int]] = [[0] * GRID_W for _ in range(GRID_H)]

    # Creature — use sick sprite variant when awake and sick (X-eyes in sprite)
    use_sick = tama.is_sick and not tama.is_sleeping
    sprite = get_sprite(
        tama.stage,
        tama.animation_frame,
        creature_type=tama.creature_type,
        sick=use_sick,
    )
    for row in range(GRID_H):
        rv = sprite[row] if row < len(sprite) else 0
        for col in range(GRID_W):
            if pixel(rv, col):
                grid[row][col] = 1

    if tama.is_sleeping:
        _apply_overlay(grid, ZZZ_OVERLAY, color=1)
        return grid   # no poop or attention while sleeping

    if tama.needs_attention and not tama.is_sick:
        # Exclamation mark at right edge — never overlaps creature body
        _apply_overlay(grid, ATTENTION_OVERLAY, color=1)

    if tama.poop_count > 0:
        for i in range(min(tama.poop_count, 4)):
            _apply_poop(grid, i)

    return grid


def _apply_overlay(grid: list[list[int]], overlay: tuple, color: int = 1) -> None:
    for row_idx, rv in enumerate(overlay):
        if row_idx >= GRID_H or not rv:
            continue
        for col in range(GRID_W):
            if pixel(rv, col):
                grid[row_idx][col] = color


def _apply_poop(grid: list[list[int]], index: int) -> None:
    x_offset = index * 4
    for row_idx, rv in enumerate(POOP_ROWS):
        if row_idx >= GRID_H or not rv:
            continue
        for col in range(GRID_W):
            if pixel(rv, col):
                shifted = col + x_offset
                if shifted < GRID_W:
                    grid[row_idx][shifted] = 2


# ---------------------------------------------------------------------------
# Raw scan-line builder
# ---------------------------------------------------------------------------

def _grid_to_raw(
    grid: list[list[int]],
    palette: list[tuple],
    border_colour: tuple,
) -> bytes:
    raw = bytearray()
    for py in range(IMG_H):
        raw.append(0)           # PNG filter type: None
        gy = (py - BORDER) // CELL_PX
        for px_ in range(IMG_W):
            gx = (px_ - BORDER) // CELL_PX
            if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                r, g, b = palette[grid[gy][gx]]
            else:
                r, g, b = border_colour
            raw += bytes([r, g, b])
    return bytes(raw)


# ---------------------------------------------------------------------------
# Minimal PNG encoder  (no external libs)
# ---------------------------------------------------------------------------

def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    return (
        struct.pack(">I", len(data))
        + payload
        + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
    )


def _encode_png(raw_data: bytes, width: int, height: int) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw_data, level=6))
        + _chunk(b"IEND", b"")
    )
