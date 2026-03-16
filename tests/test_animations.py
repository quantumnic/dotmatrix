"""Tests for built-in animations."""

from __future__ import annotations

import pytest

from dotmatrix.animations import (
    ANIMATIONS,
    rainbow,
    fire,
    matrix_rain,
    pulse,
    checkerboard,
)
from dotmatrix.utils import create_solid_frame, resize_image, image_to_pixel_data, blend_frames

from PIL import Image


# ---------------------------------------------------------------------------
# Animation generators
# ---------------------------------------------------------------------------

class TestRainbow:
    def test_frame_count(self):
        frames = list(rainbow(size=8, frames=10))
        assert len(frames) == 10

    def test_frame_size(self):
        frames = list(rainbow(size=8, frames=1))
        assert len(frames[0]) == 8 * 8 * 3

    def test_frames_differ(self):
        frames = list(rainbow(size=8, frames=3))
        assert frames[0] != frames[1]


class TestFire:
    def test_frame_count(self):
        frames = list(fire(size=8, frames=5))
        assert len(frames) == 5

    def test_frame_size(self):
        frames = list(fire(size=8, frames=1))
        assert len(frames[0]) == 8 * 8 * 3


class TestMatrixRain:
    def test_frame_count(self):
        frames = list(matrix_rain(size=8, frames=5))
        assert len(frames) == 5

    def test_mostly_dark_pixels(self):
        """Matrix rain should have mostly black pixels (sparse drops)."""
        frames = list(matrix_rain(size=16, frames=1))
        data = frames[0]
        black_count = sum(1 for i in range(0, len(data), 3) if data[i] == 0 and data[i+1] == 0 and data[i+2] == 0)
        total = 16 * 16
        assert black_count > total * 0.3  # at least 30% black


class TestPulse:
    def test_frame_count(self):
        frames = list(pulse(size=4, frames=10))
        assert len(frames) == 10

    def test_uniform_color(self):
        """Each frame of pulse should be a single solid color."""
        frames = list(pulse(color=(255, 0, 0), size=4, frames=1))
        data = frames[0]
        # All pixels should be the same
        pixel = data[:3]
        for i in range(0, len(data), 3):
            assert data[i:i+3] == pixel


class TestCheckerboard:
    def test_frame_count(self):
        frames = list(checkerboard(size=8, frames=4))
        assert len(frames) == 4

    def test_alternation(self):
        frames = list(checkerboard(size=8, frames=2, block_size=4))
        assert frames[0] != frames[1]  # offset flips


class TestAnimationRegistry:
    def test_all_registered(self):
        assert "rainbow" in ANIMATIONS
        assert "fire" in ANIMATIONS
        assert "matrix" in ANIMATIONS
        assert "pulse" in ANIMATIONS
        assert "checkerboard" in ANIMATIONS

    def test_callable(self):
        for name, func in ANIMATIONS.items():
            assert callable(func)


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

class TestUtils:
    def test_create_solid_frame(self):
        frame = create_solid_frame(4, 255, 0, 0)
        assert len(frame) == 4 * 4 * 3
        assert frame[:3] == bytes([255, 0, 0])

    def test_resize_image_square(self):
        img = Image.new("RGB", (100, 100), (255, 0, 0))
        result = resize_image(img, 32)
        assert result.size == (32, 32)

    def test_resize_image_wide(self):
        img = Image.new("RGB", (200, 100), (0, 255, 0))
        result = resize_image(img, 32)
        assert result.size == (32, 32)

    def test_image_to_pixel_data_length(self):
        img = Image.new("RGB", (8, 8), (128, 128, 128))
        data = image_to_pixel_data(img)
        assert len(data) == 8 * 8 * 3

    def test_blend_frames_midpoint(self):
        a = bytes([0, 0, 0] * 4)
        b = bytes([100, 200, 50] * 4)
        result = blend_frames(a, b, 0.5)
        assert result[0] == 50
        assert result[1] == 100
        assert result[2] == 25

    def test_blend_frames_alpha_zero(self):
        a = bytes([10, 20, 30])
        b = bytes([200, 200, 200])
        result = blend_frames(a, b, 0.0)
        assert result == a

    def test_blend_frames_alpha_one(self):
        a = bytes([10, 20, 30])
        b = bytes([200, 200, 200])
        result = blend_frames(a, b, 1.0)
        assert result == b
