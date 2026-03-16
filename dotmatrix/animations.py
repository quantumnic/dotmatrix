"""Built-in pixel animations for iDotMatrix displays."""

from __future__ import annotations

import colorsys
import math
import random
from typing import Generator

from dotmatrix.utils import create_solid_frame


def rainbow(size: int = 32, frames: int = 60) -> Generator[bytes, None, None]:
    """Generate cycling rainbow color frames.

    Each frame shifts the hue across the display diagonally.
    """
    for f in range(frames):
        data = bytearray()
        for y in range(size):
            for x in range(size):
                hue = ((x + y) / (size * 2) + f / frames) % 1.0
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                data.extend([int(r * 255), int(g * 255), int(b * 255)])
        yield bytes(data)


def fire(size: int = 32, frames: int = 60) -> Generator[bytes, None, None]:
    """Generate a fire effect animation.

    Uses a simple heat propagation model with random sparks at the bottom.
    """
    heat = [[0.0] * size for _ in range(size)]

    for _ in range(frames):
        # Spark the bottom row
        for x in range(size):
            if random.random() < 0.6:
                heat[size - 1][x] = min(1.0, heat[size - 1][x] + random.uniform(0.5, 1.0))

        # Propagate heat upward with cooling
        new_heat = [[0.0] * size for _ in range(size)]
        for y in range(size):
            for x in range(size):
                if y == size - 1:
                    new_heat[y][x] = heat[y][x] * 0.7
                else:
                    # Average of neighbors below
                    below = heat[min(y + 1, size - 1)][x]
                    left = heat[min(y + 1, size - 1)][max(0, x - 1)]
                    right = heat[min(y + 1, size - 1)][min(size - 1, x + 1)]
                    new_heat[y][x] = max(0, (below + left + right) / 3.0 - 0.02)
        heat = new_heat

        # Convert heat to RGB (black → red → yellow → white)
        data = bytearray()
        for y in range(size):
            for x in range(size):
                h = heat[y][x]
                if h < 0.33:
                    r, g, b = int(h * 3 * 255), 0, 0
                elif h < 0.66:
                    r, g, b = 255, int((h - 0.33) * 3 * 255), 0
                else:
                    r, g, b = 255, 255, int((h - 0.66) * 3 * 255)
                data.extend([r, g, b])
        yield bytes(data)


def matrix_rain(size: int = 32, frames: int = 60) -> Generator[bytes, None, None]:
    """Generate a Matrix-style green falling characters effect."""
    # Initialize columns with random drop positions
    columns = [{"pos": random.randint(-size, 0), "speed": random.randint(1, 3)} for _ in range(size)]
    trail_length = size // 3

    for _ in range(frames):
        data = bytearray()
        for y in range(size):
            for x in range(size):
                col = columns[x]
                dist = col["pos"] - y
                if 0 <= dist < trail_length:
                    # Brightness fades along trail
                    brightness = 1.0 - (dist / trail_length)
                    g = int(brightness * 255)
                    r = int(brightness * 40) if dist == 0 else 0
                    b = 0
                else:
                    r, g, b = 0, 0, 0
                data.extend([r, g, b])

        # Advance drops
        for col in columns:
            col["pos"] += col["speed"]
            if col["pos"] - trail_length > size:
                col["pos"] = random.randint(-size // 2, 0)
                col["speed"] = random.randint(1, 3)

        yield bytes(data)


def pulse(
    color: tuple[int, int, int] = (0, 128, 255),
    size: int = 32,
    frames: int = 60,
) -> Generator[bytes, None, None]:
    """Generate a pulsing single-color animation."""
    for f in range(frames):
        # Sine wave brightness
        brightness = (math.sin(2 * math.pi * f / frames) + 1) / 2  # 0..1
        r = int(color[0] * brightness)
        g = int(color[1] * brightness)
        b = int(color[2] * brightness)
        yield create_solid_frame(size, r, g, b)


def checkerboard(
    size: int = 32,
    frames: int = 30,
    block_size: int = 4,
    color_a: tuple[int, int, int] = (255, 255, 255),
    color_b: tuple[int, int, int] = (0, 0, 255),
) -> Generator[bytes, None, None]:
    """Generate an alternating checkerboard animation."""
    for f in range(frames):
        data = bytearray()
        offset = f % 2
        for y in range(size):
            for x in range(size):
                cell = ((x // block_size) + (y // block_size) + offset) % 2
                c = color_a if cell == 0 else color_b
                data.extend(c)
        yield bytes(data)


# Registry of built-in animations
ANIMATIONS: dict[str, callable] = {
    "rainbow": rainbow,
    "fire": fire,
    "matrix": matrix_rain,
    "pulse": pulse,
    "checkerboard": checkerboard,
}
