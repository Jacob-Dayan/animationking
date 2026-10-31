"""Unit tests for the Animation King 24-bit TrueColor shader and palette module."""

from __future__ import annotations

import pytest

from animationking.core.colors import (
    _SCHEME_CACHE,
    BLACK,
    Color,
    cosine_palette,
    gradient_multi,
    hsv_to_rgb,
    rgb_lerp,
    rgb_to_hsv,
    transform_color,
)
from animationking.core.config import COLOR_SCHEMES, SCHEME_KEYS


def test_hsv_rgb_roundtrip() -> None:
    samples: list[Color] = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 255),
        (255, 0, 255),
        (128, 64, 192),
        (255, 255, 255),
        (0, 0, 0),
    ]
    for r, g, b in samples:
        h, s, v = rgb_to_hsv(r, g, b)
        r2, g2, b2 = hsv_to_rgb(h, s, v)
        assert abs(r - r2) <= 2
        assert abs(g - g2) <= 2
        assert abs(b - b2) <= 2


def test_cosine_palette_bounds() -> None:
    a = (0.5, 0.5, 0.5)
    b = (0.5, 0.5, 0.5)
    c = (1.0, 1.0, 1.0)
    d = (0.0, 0.33, 0.67)
    for step in range(25):
        t = step / 24.0
        r, g, bl = cosine_palette(t, a, b, c, d)
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= bl <= 255


def test_gradient_multi() -> None:
    stops: list[Color] = [(10, 20, 30), (100, 150, 200), (250, 240, 230)]
    assert gradient_multi(stops, 0.0) == (10, 20, 30)
    assert gradient_multi(stops, 1.0) == (250, 240, 230)
    mid = gradient_multi(stops, 0.5)
    assert mid == (100, 150, 200)
    assert gradient_multi([], 0.5) == BLACK
    assert gradient_multi([(42, 43, 44)], 0.5) == (42, 43, 44)


def test_rgb_lerp() -> None:
    assert rgb_lerp((0, 0, 0), (100, 200, 50), 0.5) == (50, 100, 25)
    assert rgb_lerp((10, 20, 30), (100, 200, 50), -1.0) == (10, 20, 30)
    assert rgb_lerp((10, 20, 30), (100, 200, 50), 2.0) == (100, 200, 50)


@pytest.mark.parametrize("scheme", SCHEME_KEYS)
def test_transform_color_schemes_and_cache(scheme: str) -> None:
    assert len(COLOR_SCHEMES) == 11
    assert transform_color(BLACK, scheme) == BLACK

    sample: Color = (180, 90, 240)
    _SCHEME_CACHE.clear()
    out1 = transform_color(sample, scheme, vivid_boost=1.0)
    assert 0 <= out1[0] <= 255
    assert 0 <= out1[1] <= 255
    assert 0 <= out1[2] <= 255

    assert len(_SCHEME_CACHE) == 1
    out2 = transform_color(sample, scheme, vivid_boost=1.0)
    assert out2 == out1
    assert len(_SCHEME_CACHE) == 1
    if scheme == "default":
        assert out1 == sample
